from __future__ import annotations

import datetime
import fnmatch
import locale
import logging
import os
import pathlib
import re
import shutil
import sys
import traceback
import urllib
from collections.abc import Hashable
from contextlib import contextmanager
from functools import partial
from html import entities
from html.parser import HTMLParser
from itertools import groupby
from operator import attrgetter
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Generator,
    Iterable,
    Sequence,
)

import dateutil.parser
from watchfiles import Change

try:
    from zoneinfo import ZoneInfo
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo
import watchfiles
from markupsafe import Markup

if TYPE_CHECKING:
    from pelican.contents import Content
    from pelican.settings import Settings

logger = logging.getLogger(__name__)


def sanitised_join(base_directory: str, *parts: str) -> str:
    joined = posixize_path(os.path.abspath(os.path.join(base_directory, *parts)))
    base = posixize_path(os.path.abspath(base_directory))
    if not joined.startswith(base):
        raise RuntimeError(f"Attempted to break out of output directory to {joined}")

    return joined


def strftime(date: datetime.datetime, date_format: str) -> str:
    """
    Enhanced replacement for built-in strftime with zero stripping

    This works by 'grabbing' possible format strings (those starting with %),
    formatting them with the date, stripping any leading zeros if - prefix is
    used and replacing formatted output back.
    """

    def strip_zeros(x):
        return x.lstrip("0") or "0"

    # includes ISO date parameters added by Python 3.6
    c89_directives = "aAbBcdfGHIjmMpSUuVwWxXyYzZ%"

    # grab candidate format options
    format_options = "%[-]?."
    candidates = re.findall(format_options, date_format)

    # replace candidates with placeholders for later % formatting
    template = re.sub(format_options, "%s", date_format)

    formatted_candidates = []
    for candidate in candidates:
        # test for valid C89 directives only
        if candidate[-1] in c89_directives:
            # check for '-' prefix
            if len(candidate) == 3:  # noqa: PLR2004
                # '-' prefix
                candidate = f"%{candidate[-1]}"
                conversion = strip_zeros
            else:
                conversion = None

            # format date
            if isinstance(date, SafeDatetime):
                formatted = date.strftime(candidate, safe=False)
            else:
                formatted = date.strftime(candidate)

            # strip zeros if '-' prefix is used
            if conversion:
                formatted = conversion(formatted)
        else:
            formatted = candidate
        formatted_candidates.append(formatted)

    # put formatted candidates back and return
    return template % tuple(formatted_candidates)


class SafeDatetime(datetime.datetime):
    """Subclass of datetime that works with utf-8 format strings on PY2"""

    def strftime(self, fmt, safe=True):
        """Uses our custom strftime if supposed to be *safe*"""
        if safe:
            return strftime(self, fmt)
        else:
            return super().strftime(fmt)


class DateFormatter:
    """A date formatter object used as a jinja filter

    Uses the `strftime` implementation and makes sure jinja uses the locale
    defined in LOCALE setting
    """

    def __init__(self) -> None:
        self.locale = locale.setlocale(locale.LC_TIME)
        # python has issue with Turkish_Türkiye.1254 locale, replace it to
        # something accepted: Turkish
        if self.locale == "Turkish_Türkiye.1254":
            self.locale = "Turkish"

    def __call__(self, date: datetime.datetime, date_format: str) -> str:
        # on OSX, encoding from LC_CTYPE determines the unicode output in PY3
        # make sure it's same as LC_TIME
        with temporary_locale(self.locale, locale.LC_TIME), temporary_locale(
            self.locale, locale.LC_CTYPE
        ):
            formatted = strftime(date, date_format)

        return formatted


class memoized:
    """Function decorator to cache return values.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    """

    def __init__(self, func: Callable) -> None:
        self.func = func
        self.cache: dict[Any, Any] = {}

    def __call__(self, *args) -> Any:
        if not isinstance(args, Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self) -> str | None:
        return self.func.__doc__

    def __get__(self, obj: Any, objtype):
        """Support instance methods."""
        fn = partial(self.__call__, obj)
        fn.cache = self.cache
        return fn


def deprecated_attribute(
    old: str,
    new: str,
    since: tuple[int, ...],
    remove: tuple[int, ...] | None = None,
    doc: str | None = None,
):
    """Attribute deprecation decorator for gentle upgrades

    For example:

        class MyClass (object):
            @deprecated_attribute(
                old='abc', new='xyz', since=(3, 2, 0), remove=(4, 1, 3))
            def abc(): return None

            def __init__(self):
                xyz = 5

    Note that the decorator needs a dummy method to attach to, but the
    content of the dummy method is ignored.
    """

    def _warn():
        version = ".".join(str(x) for x in since)
        message = [f"{old} has been deprecated since {version}"]
        if remove:
            version = ".".join(str(x) for x in remove)
            message.append(f" and will be removed by version {version}")
        message.append(f".  Use {new} instead.")
        logger.warning("".join(message))
        logger.debug("".join(str(x) for x in traceback.format_stack()))

    def fget(self):
        _warn()
        return getattr(self, new)

    def fset(self, value):
        _warn()
        setattr(self, new, value)

    def decorator(dummy):
        return property(fget=fget, fset=fset, doc=doc)

    return decorator


def get_date(string: str) -> datetime.datetime:
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValueError.
    """
    string = re.sub(" +", " ", string)
    default = SafeDatetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        return dateutil.parser.parse(string, default=default)
    except (TypeError, ValueError):
        raise ValueError(f"{string!r} is not a valid date") from None


@contextmanager
def pelican_open(
    filename: str, mode: str = "r", strip_crs: bool = (sys.platform == "win32")
) -> Generator[str, None, None]:
    """Open a file and return its content"""

    # utf-8-sig will clear any BOM if present
    with open(filename, mode, encoding="utf-8-sig") as infile:
        content = infile.read()
    yield content


def slugify(
    value: str,
    regex_subs: Iterable[tuple[str, str]] = (),
    preserve_case: bool = False,
    use_unicode: bool = False,
) -> str:
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from Django sources.

    For a set of sensible default regex substitutions to pass to regex_subs
    look into pelican.settings.DEFAULT_CONFIG['SLUG_REGEX_SUBSTITUTIONS'].
    """

    import unicodedata

    import unidecode

    def normalize_unicode(text: str) -> str:
        # normalize text by compatibility composition
        # see: https://en.wikipedia.org/wiki/Unicode_equivalence
        return unicodedata.normalize("NFKC", text)

    # strip tags from value
    value = Markup(value).striptags()

    # normalization
    value = normalize_unicode(value)

    if not use_unicode:
        # ASCII-fy
        value = unidecode.unidecode(value)

    # perform regex substitutions
    for src, dst in regex_subs:
        value = re.sub(
            normalize_unicode(src), normalize_unicode(dst), value, flags=re.IGNORECASE
        )

    if not preserve_case:
        value = value.lower()

    return value.strip()


def copy(source: str, destination: str, ignores: Iterable[str] | None = None) -> None:
    """Recursively copy source into destination.

    If source is a file, destination has to be a file as well.
    The function is able to copy either files or directories.

    :param source: the source file or directory
    :param destination: the destination file or directory
    :param ignores: either None, or a list of glob patterns;
        files matching those patterns will _not_ be copied.
    """

    def walk_error(err):
        logger.warning("While copying %s: %s: %s", source_, err.filename, err.strerror)

    source_ = os.path.abspath(os.path.expanduser(source))
    destination_ = os.path.abspath(os.path.expanduser(destination))

    if ignores is None:
        ignores = []

    if any(fnmatch.fnmatch(os.path.basename(source), ignore) for ignore in ignores):
        logger.info("Not copying %s due to ignores", source_)
        return

    if os.path.isfile(source_):
        dst_dir = os.path.dirname(destination_)
        if not os.path.exists(dst_dir):
            logger.info("Creating directory %s", dst_dir)
            os.makedirs(dst_dir)
        logger.info("Copying %s to %s", source_, destination_)
        copy_file(source_, destination_)

    elif os.path.isdir(source_):
        if not os.path.exists(destination_):
            logger.info("Creating directory %s", destination_)
            os.makedirs(destination_)
        if not os.path.isdir(destination_):
            logger.warning(
                "Cannot copy %s (a directory) to %s (a file)", source_, destination_
            )
            return

        for src_dir, subdirs, others in os.walk(source_, followlinks=True):
            dst_dir = os.path.join(destination_, os.path.relpath(src_dir, source_))

            subdirs[:] = (
                s for s in subdirs if not any(fnmatch.fnmatch(s, i) for i in ignores)
            )
            others[:] = (
                o for o in others if not any(fnmatch.fnmatch(o, i) for i in ignores)
            )

            if not os.path.isdir(dst_dir):
                logger.info("Creating directory %s", dst_dir)
                # Parent directories are known to exist, so 'mkdir' suffices.
                os.mkdir(dst_dir)

            for o in others:
                src_path = os.path.join(src_dir, o)
                dst_path = os.path.join(dst_dir, o)
                if os.path.isfile(src_path):
                    logger.info("Copying %s to %s", src_path, dst_path)
                    copy_file(src_path, dst_path)
                else:
                    logger.warning(
                        "Skipped copy %s (not a file or directory) to %s",
                        src_path,
                        dst_path,
                    )


def copy_file(source: str, destination: str) -> None:
    """Copy a file"""
    try:
        shutil.copyfile(source, destination)
    except OSError as e:
        logger.warning(
            "A problem occurred copying file %s to %s; %s", source, destination, e
        )


def clean_output_dir(path: str, retention: Iterable[str]) -> None:
    """Remove all files from output directory except those in retention list"""

    if not os.path.exists(path):
        logger.debug("Directory already removed: %s", path)
        return

    if not os.path.isdir(path):
        try:
            os.remove(path)
        except Exception as e:
            logger.error("Unable to delete file %s; %s", path, e)
        return

    # remove existing content from output folder unless in retention list
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if any(filename == retain for retain in retention):
            logger.debug(
                "Skipping deletion; %s is on retention list: %s", filename, file
            )
        elif os.path.isdir(file):
            try:
                shutil.rmtree(file)
                logger.debug("Deleted directory %s", file)
            except Exception as e:
                logger.error("Unable to delete directory %s; %s", file, e)
        elif os.path.isfile(file) or os.path.islink(file):
            try:
                os.remove(file)
                logger.debug("Deleted file/link %s", file)
            except Exception as e:
                logger.error("Unable to delete file %s; %s", file, e)
        else:
            logger.error("Unable to delete %s, file type unknown", file)


def get_relative_path(path: str) -> str:
    """Return the relative path from the given path to the root path."""
    components = split_all(path)
    if components is None or len(components) <= 1:
        return os.curdir
    else:
        parents = [os.pardir] * (len(components) - 1)
        return os.path.join(*parents)


def path_to_url(path: str) -> str:
    """Return the URL corresponding to a given path."""
    if path is not None:
        path = posixize_path(path)
    return path


def posixize_path(rel_path: str) -> str:
    """Use '/' as path separator, so that source references,
    like '{static}/foo/bar.jpg' or 'extras/favicon.ico',
    will work on Windows as well as on Mac and Linux."""
    return rel_path.replace(os.sep, "/")


class _HTMLWordTruncator(HTMLParser):
    _word_regex = re.compile(
        r"{DBC}|(\w[\w'-]*)".format(
            # DBC means CJK-like characters. An character can stand for a word.
            DBC=(
                "([\u4e00-\u9fff])|"  # CJK Unified Ideographs
                "([\u3400-\u4dbf])|"  # CJK Unified Ideographs Extension A
                "([\uf900-\ufaff])|"  # CJK Compatibility Ideographs
                "([\U00020000-\U0002a6df])|"  # CJK Unified Ideographs Extension B
                "([\U0002f800-\U0002fa1f])|"  # CJK Compatibility Ideographs Supplement
                "([\u3040-\u30ff])|"  # Hiragana and Katakana
                "([\u1100-\u11ff])|"  # Hangul Jamo
                "([\uac00-\ud7ff])|"  # Hangul Compatibility Jamo
                "([\u3130-\u318f])"  # Hangul Syllables
            )
        ),
        re.UNICODE,
    )
    _word_prefix_regex = re.compile(r"\w", re.U)
    _singlets = ("br", "col", "link", "base", "img", "param", "area", "hr", "input")

    class TruncationCompleted(Exception):
        def __init__(self, truncate_at: int) -> None:
            super().__init__(truncate_at)
            self.truncate_at = truncate_at

    def __init__(self, max_words: int) -> None:
        super().__init__(convert_charrefs=False)

        self.max_words = max_words
        self.words_found = 0
        self.open_tags = []
        self.last_word_end = None
        self.truncate_at: int | None = None

    def feed(self, *args, **kwargs) -> None:
        try:
            super().feed(*args, **kwargs)
        except self.TruncationCompleted as exc:
            self.truncate_at = exc.truncate_at
        else:
            self.truncate_at = None

    def getoffset(self) -> int:
        line_start = 0
        lineno, line_offset = self.getpos()
        for _ in range(lineno - 1):
            line_start = self.rawdata.index("\n", line_start) + 1
        return line_start + line_offset

    def add_word(self, word_end: int) -> None:
        self.words_found += 1
        self.last_word_end = None
        if self.words_found == self.max_words:
            raise self.TruncationCompleted(word_end)

    def add_last_word(self) -> None:
        if self.last_word_end is not None:
            self.add_word(self.last_word_end)

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        self.add_last_word()
        if tag not in self._singlets:
            self.open_tags.insert(0, tag)

    def handle_endtag(self, tag: str) -> None:
        self.add_last_word()
        try:
            i = self.open_tags.index(tag)
        except ValueError:
            pass
        else:
            # SGML: An end tag closes, back to the matching start tag,
            # all unclosed intervening start tags with omitted end tags
            del self.open_tags[: i + 1]

    def handle_data(self, data: str) -> None:
        word_end = 0
        offset = self.getoffset()

        while self.words_found < self.max_words:
            match = self._word_regex.search(data, word_end)
            if not match:
                break

            if match.start(0) > 0:
                self.add_last_word()

            word_end = match.end(0)
            self.last_word_end = offset + word_end

        if word_end < len(data):
            self.add_last_word()

    def _handle_ref(self, name: str, char: str) -> None:
        """
        Called by handle_entityref() or handle_charref() when a ref like
        `&mdash;`, `&#8212;`, or `&#x2014` is found.

        The arguments for this method are:

        - `name`: the HTML entity name (such as `mdash` or `#8212` or `#x2014`)
        - `char`: the Unicode representation of the ref (such as `—`)

        This method checks whether the entity is considered to be part of a
        word or not and, if not, signals the end of a word.
        """
        # Compute the index of the character right after the ref.
        #
        # In a string like 'prefix&mdash;suffix', the end is the sum of:
        #
        # - `self.getoffset()` (the length of `prefix`)
        # - `1` (the length of `&`)
        # - `len(name)` (the length of `mdash`)
        # - `1` (the length of `;`)
        #
        # Note that, in case of malformed HTML, the ';' character may
        # not be present.

        offset = self.getoffset()
        ref_end = offset + len(name) + 1

        try:
            if self.rawdata[ref_end] == ";":
                ref_end += 1
        except IndexError:
            # We are at the end of the string and there's no ';'
            pass

        if self.last_word_end is None:
            if self._word_prefix_regex.match(char):
                self.last_word_end = ref_end
        elif self._word_regex.match(char):
            self.last_word_end = ref_end
        else:
            self.add_last_word()

    def handle_entityref(self, name: str) -> None:
        """
        Called when an entity ref like '&mdash;' is found

        `name` is the entity ref without ampersand and semicolon (e.g. `mdash`)
        """
        try:
            codepoint = entities.name2codepoint[name]
            char = chr(codepoint)
        except KeyError:
            char = ""
        self._handle_ref(name, char)

    def handle_charref(self, name: str) -> None:
        """
        Called when a char ref like '&#8212;' or '&#x2014' is found

        `name` is the char ref without ampersand and semicolon (e.g. `#8212` or
        `#x2014`)
        """
        try:
            if name.startswith("x"):
                codepoint = int(name[1:], 16)
            else:
                codepoint = int(name)
            char = chr(codepoint)
        except (ValueError, OverflowError):
            char = ""
        self._handle_ref("#" + name, char)


def truncate_html_words(s: str, num: int, end_text: str = "…") -> str:
    """Truncates HTML to a certain number of words.

    (not counting tags and comments). Closes opened tags if they were correctly
    closed in the given html. Takes an optional argument of what should be used
    to notify that the string has been truncated, defaulting to ellipsis (…).

    Newlines in the HTML are preserved. (From the django framework).
    """
    length = int(num)
    if length <= 0:
        return ""
    truncator = _HTMLWordTruncator(length)
    truncator.feed(s)
    if truncator.truncate_at is None:
        return s
    out = s[: truncator.truncate_at]
    if end_text:
        out += " " + end_text
    # Close any tags still open
    for tag in truncator.open_tags:
        out += f"</{tag}>"
    # Return string
    return out


def truncate_html_paragraphs(s, count):
    """Truncate HTML to a certain number of paragraphs.

    :param count: number of paragraphs to keep

    Newlines in the HTML are preserved.
    """
    paragraphs = []
    tag_stop = 0
    substr = s[:]
    for _ in range(count):
        substr = substr[tag_stop:]
        tag_start = substr.find("<p>")
        tag_stop = substr.find("</p>") + len("</p>")
        paragraphs.append(substr[tag_start:tag_stop])

    return "".join(paragraphs)


def process_translations(
    content_list: list[Content],
    translation_id: str | Collection[str] | None = None,
) -> tuple[list[Content], list[Content]]:
    """Finds translations and returns them.

    For each content_list item, populates the 'translations' attribute, and
    returns a tuple with two lists (index, translations). Index list includes
    items in default language or items which have no variant in default
    language. Items with the `translation` metadata set to something else than
    `False` or `false` will be used as translations, unless all the items in
    the same group have that metadata.

    Translations and original items are determined relative to one another
    amongst items in the same group. Items are in the same group if they
    have the same value(s) for the metadata attribute(s) specified by the
    'translation_id', which must be a string or a collection of strings.
    If 'translation_id' is falsy, the identification of translations is skipped
    and all items are returned as originals.
    """

    if not translation_id:
        return content_list, []

    if isinstance(translation_id, str):
        translation_id = {translation_id}

    index = []

    try:
        content_list.sort(key=attrgetter(*translation_id))
    except TypeError:
        raise TypeError(
            f"Cannot unpack {translation_id}, 'translation_id' must be falsy, a"
            " string or a collection of strings"
        ) from None
    except AttributeError:
        raise AttributeError(
            f"Cannot use {translation_id} as 'translation_id', there "
            "appear to be items without these metadata "
            "attributes"
        ) from None

    for id_vals, items in groupby(content_list, attrgetter(*translation_id)):
        # prepare warning string
        id_vals = (id_vals,) if len(translation_id) == 1 else id_vals
        with_str = "with" + ", ".join([' {} "{{}}"'] * len(translation_id)).format(
            *translation_id
        ).format(*id_vals)

        items = list(items)
        original_items = get_original_items(items, with_str)
        index.extend(original_items)
        for a in items:
            a.translations = [x for x in items if x != a]

    translations = [x for x in content_list if x not in index]

    return index, translations


def get_original_items(items: list[Content], with_str: str) -> list[Content]:
    def _warn_source_paths(msg, items, *extra):
        args = [len(items)]
        args.extend(extra)
        args.extend(x.source_path for x in items)
        logger.warning("{}: {}".format(msg, "\n%s" * len(items)), *args)

    # warn if several items have the same lang
    for lang, lang_items in groupby(items, attrgetter("lang")):
        lang_items = list(lang_items)
        if len(lang_items) > 1:
            _warn_source_paths(
                'There are %s items "%s" with lang %s', lang_items, with_str, lang
            )

    # items with `translation` metadata will be used as translations...
    candidate_items = [
        i for i in items if i.metadata.get("translation", "false").lower() == "false"
    ]

    # ...unless all items with that slug are translations
    if not candidate_items:
        _warn_source_paths('All items ("%s") "%s" are translations', items, with_str)
        candidate_items = items

    # find items with default language
    original_items = [i for i in candidate_items if i.in_default_lang]

    # if there is no article with default language, go back one step
    if not original_items:
        original_items = candidate_items

    # warn if there are several original items
    if len(original_items) > 1:
        _warn_source_paths(
            "There are %s original (not translated) items %s", original_items, with_str
        )
    return original_items


def order_content(
    content_list: list[Content],
    order_by: str | Callable[[Content], Any] | None = "slug",
) -> list[Content]:
    """Sorts content.

    order_by can be a string of an attribute or sorting function. If order_by
    is defined, content will be ordered by that attribute or sorting function.
    By default, content is ordered by slug.

    Different content types can have default order_by attributes defined
    in settings, e.g. PAGES_ORDER_BY='sort-order', in which case `sort-order`
    should be a defined metadata attribute in each page.
    """

    if order_by:
        if callable(order_by):
            try:
                content_list.sort(key=order_by)
            except Exception:
                logger.error("Error sorting with function %s", order_by)
        elif isinstance(order_by, str):
            if order_by.startswith("reversed-"):
                order_reversed = True
                order_by = order_by.replace("reversed-", "", 1)
            else:
                order_reversed = False

            if order_by == "basename":
                content_list.sort(
                    key=lambda x: os.path.basename(x.source_path or ""),
                    reverse=order_reversed,
                )
            else:
                try:
                    content_list.sort(key=attrgetter(order_by), reverse=order_reversed)
                except AttributeError:
                    for content in content_list:
                        try:
                            getattr(content, order_by)
                        except AttributeError:
                            logger.warning(
                                'There is no "%s" attribute in "%s". '
                                "Defaulting to slug order.",
                                order_by,
                                content.get_relative_source_path(),
                                extra={
                                    "limit_msg": (
                                        "More files are missing "
                                        "the needed attribute."
                                    )
                                },
                            )
        else:
            logger.warning(
                "Invalid *_ORDER_BY setting (%s). "
                "Valid options are strings and functions.",
                order_by,
            )

    return content_list


def wait_for_changes(
    settings_file: str,
    settings: Settings,
) -> set[tuple[Change, str]]:
    content_path = settings.get("PATH", "")
    theme_path = settings.get("THEME", "")
    ignore_files = {
        fnmatch.translate(pattern) for pattern in settings.get("IGNORE_FILES", [])
    }

    candidate_paths = [
        settings_file,
        theme_path,
        content_path,
    ]

    candidate_paths.extend(
        os.path.join(content_path, path) for path in settings.get("STATIC_PATHS", [])
    )

    watching_paths = []
    for path in candidate_paths:
        if not path:
            continue
        path = os.path.abspath(path)
        if not os.path.exists(path):
            logger.warning("Unable to watch path '%s' as it does not exist.", path)
        else:
            watching_paths.append(path)

    return next(
        watchfiles.watch(
            *watching_paths,
            watch_filter=watchfiles.DefaultFilter(ignore_entity_patterns=ignore_files),  # type: ignore
            rust_timeout=0,
        )
    )


def set_date_tzinfo(
    d: datetime.datetime, tz_name: str | None = None
) -> datetime.datetime:
    """Set the timezone for dates that don't have tzinfo"""
    if tz_name and not d.tzinfo:
        timezone = ZoneInfo(tz_name)
        d = d.replace(tzinfo=timezone)
        return SafeDatetime(
            d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, d.tzinfo
        )
    return d


def mkdir_p(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def split_all(path: str | pathlib.Path | None) -> Sequence[str] | None:
    """Split a path into a list of components

    While os.path.split() splits a single component off the back of
    `path`, this function splits all components:

    >>> split_all(os.path.join('a', 'b', 'c'))
    ['a', 'b', 'c']
    """
    if isinstance(path, str):
        components = []
        path = path.lstrip("/")
        while path:
            head, tail = os.path.split(path)
            if tail:
                components.insert(0, tail)
            elif head == path:
                components.insert(0, head)
                break
            path = head
        return components
    elif isinstance(path, pathlib.Path):
        return path.parts
    elif path is None:
        return None
    else:
        raise TypeError(
            f'"path" was {type(path)}, must be string, None, or pathlib.Path'
        )


def path_to_file_url(path: str) -> str:
    """Convert file-system path to file:// URL"""
    return urllib.parse.urljoin("file://", urllib.request.pathname2url(path))


def maybe_pluralize(count: int, singular: str, plural: str) -> str:
    """
    Returns a formatted string containing count and plural if count is not 1
    Returns count and singular if count is 1

    maybe_pluralize(0, 'Article', 'Articles') -> '0 Articles'
    maybe_pluralize(1, 'Article', 'Articles') -> '1 Article'
    maybe_pluralize(2, 'Article', 'Articles') -> '2 Articles'

    """
    selection = plural
    if count == 1:
        selection = singular
    return f"{count} {selection}"


@contextmanager
def temporary_locale(
    temp_locale: str | None = None, lc_category: int = locale.LC_ALL
) -> Generator[None, None, None]:
    """
    Enable code to run in a context with a temporary locale
    Resets the locale back when exiting context.

    Use tests.support.TestCaseWithCLocale if you want every unit test in a
    class to use the C locale.
    """
    orig_locale = locale.setlocale(lc_category)
    # python has issue with Turkish_Türkiye.1254 locale, replace it to
    # something accepted: Turkish
    if orig_locale == "Turkish_Türkiye.1254":
        orig_locale = "Turkish"
    if temp_locale:
        locale.setlocale(lc_category, temp_locale)
    yield
    locale.setlocale(lc_category, orig_locale)


def file_suffix(path: str) -> str:
    """Return the suffix of a filename in a path."""
    _, ext = os.path.splitext(os.path.basename(path))
    ret = ""
    if len(ext) > 1:
        # drop the ".", e.g., "exe", not ".exe"
        ret = ext[1:]
    return ret
