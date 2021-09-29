import datetime
import fnmatch
import locale
import logging
import os
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

import dateutil.parser

from markupsafe import Markup

import pytz


logger = logging.getLogger(__name__)


def sanitised_join(base_directory, *parts):
    joined = posixize_path(
        os.path.abspath(os.path.join(base_directory, *parts)))
    base = posixize_path(os.path.abspath(base_directory))
    if not joined.startswith(base):
        raise RuntimeError(
            "Attempted to break out of output directory to {}".format(
                joined
            )
        )

    return joined


def strftime(date, date_format):
    '''
    Enhanced replacement for built-in strftime with zero stripping

    This works by 'grabbing' possible format strings (those starting with %),
    formatting them with the date, stripping any leading zeros if - prefix is
    used and replacing formatted output back.
    '''
    def strip_zeros(x):
        return x.lstrip('0') or '0'
    # includes ISO date parameters added by Python 3.6
    c89_directives = 'aAbBcdfGHIjmMpSUuVwWxXyYzZ%'

    # grab candidate format options
    format_options = '%[-]?.'
    candidates = re.findall(format_options, date_format)

    # replace candidates with placeholders for later % formatting
    template = re.sub(format_options, '%s', date_format)

    formatted_candidates = []
    for candidate in candidates:
        # test for valid C89 directives only
        if candidate[-1] in c89_directives:
            # check for '-' prefix
            if len(candidate) == 3:
                # '-' prefix
                candidate = '%{}'.format(candidate[-1])
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
    '''Subclass of datetime that works with utf-8 format strings on PY2'''

    def strftime(self, fmt, safe=True):
        '''Uses our custom strftime if supposed to be *safe*'''
        if safe:
            return strftime(self, fmt)
        else:
            return super().strftime(fmt)


class DateFormatter:
    '''A date formatter object used as a jinja filter

    Uses the `strftime` implementation and makes sure jinja uses the locale
    defined in LOCALE setting
    '''

    def __init__(self):
        self.locale = locale.setlocale(locale.LC_TIME)

    def __call__(self, date, date_format):
        old_lc_time = locale.setlocale(locale.LC_TIME)
        old_lc_ctype = locale.setlocale(locale.LC_CTYPE)

        locale.setlocale(locale.LC_TIME, self.locale)
        # on OSX, encoding from LC_CTYPE determines the unicode output in PY3
        # make sure it's same as LC_TIME
        locale.setlocale(locale.LC_CTYPE, self.locale)

        formatted = strftime(date, date_format)

        locale.setlocale(locale.LC_TIME, old_lc_time)
        locale.setlocale(locale.LC_CTYPE, old_lc_ctype)
        return formatted


class memoized:
    """Function decorator to cache return values.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
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

    def __repr__(self):
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return partial(self.__call__, obj)


def deprecated_attribute(old, new, since=None, remove=None, doc=None):
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
        version = '.'.join(str(x) for x in since)
        message = ['{} has been deprecated since {}'.format(old, version)]
        if remove:
            version = '.'.join(str(x) for x in remove)
            message.append(
                ' and will be removed by version {}'.format(version))
        message.append('.  Use {} instead.'.format(new))
        logger.warning(''.join(message))
        logger.debug(''.join(str(x) for x
                             in traceback.format_stack()))

    def fget(self):
        _warn()
        return getattr(self, new)

    def fset(self, value):
        _warn()
        setattr(self, new, value)

    def decorator(dummy):
        return property(fget=fget, fset=fset, doc=doc)

    return decorator


def get_date(string):
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValueError.
    """
    string = re.sub(' +', ' ', string)
    default = SafeDatetime.now().replace(hour=0, minute=0,
                                         second=0, microsecond=0)
    try:
        return dateutil.parser.parse(string, default=default)
    except (TypeError, ValueError):
        raise ValueError('{!r} is not a valid date'.format(string))


@contextmanager
def pelican_open(filename, mode='r', strip_crs=(sys.platform == 'win32')):
    """Open a file and return its content"""

    # utf-8-sig will clear any BOM if present
    with open(filename, mode, encoding='utf-8-sig') as infile:
        content = infile.read()
    yield content


def slugify(value, regex_subs=(), preserve_case=False, use_unicode=False):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from Django sources.
    """

    import unicodedata
    import unidecode

    def normalize_unicode(text):
        # normalize text by compatibility composition
        # see: https://en.wikipedia.org/wiki/Unicode_equivalence
        return unicodedata.normalize('NFKC', text)

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
            normalize_unicode(src),
            normalize_unicode(dst),
            value,
            flags=re.IGNORECASE)

    if not preserve_case:
        value = value.lower()

    return value.strip()


def copy(source, destination, ignores=None):
    """Recursively copy source into destination.

    If source is a file, destination has to be a file as well.
    The function is able to copy either files or directories.

    :param source: the source file or directory
    :param destination: the destination file or directory
    :param ignores: either None, or a list of glob patterns;
        files matching those patterns will _not_ be copied.
    """

    def walk_error(err):
        logger.warning("While copying %s: %s: %s",
                       source_, err.filename, err.strerror)

    source_ = os.path.abspath(os.path.expanduser(source))
    destination_ = os.path.abspath(os.path.expanduser(destination))

    if ignores is None:
        ignores = []

    if any(fnmatch.fnmatch(os.path.basename(source), ignore)
           for ignore in ignores):
        logger.info('Not copying %s due to ignores', source_)
        return

    if os.path.isfile(source_):
        dst_dir = os.path.dirname(destination_)
        if not os.path.exists(dst_dir):
            logger.info('Creating directory %s', dst_dir)
            os.makedirs(dst_dir)
        logger.info('Copying %s to %s', source_, destination_)
        copy_file_metadata(source_, destination_)

    elif os.path.isdir(source_):
        if not os.path.exists(destination_):
            logger.info('Creating directory %s', destination_)
            os.makedirs(destination_)
        if not os.path.isdir(destination_):
            logger.warning('Cannot copy %s (a directory) to %s (a file)',
                           source_, destination_)
            return

        for src_dir, subdirs, others in os.walk(source_, followlinks=True):
            dst_dir = os.path.join(destination_,
                                   os.path.relpath(src_dir, source_))

            subdirs[:] = (s for s in subdirs if not any(fnmatch.fnmatch(s, i)
                                                        for i in ignores))
            others[:] = (o for o in others if not any(fnmatch.fnmatch(o, i)
                                                      for i in ignores))

            if not os.path.isdir(dst_dir):
                logger.info('Creating directory %s', dst_dir)
                # Parent directories are known to exist, so 'mkdir' suffices.
                os.mkdir(dst_dir)

            for o in others:
                src_path = os.path.join(src_dir, o)
                dst_path = os.path.join(dst_dir, o)
                if os.path.isfile(src_path):
                    logger.info('Copying %s to %s', src_path, dst_path)
                    copy_file_metadata(src_path, dst_path)
                else:
                    logger.warning('Skipped copy %s (not a file or '
                                   'directory) to %s',
                                   src_path, dst_path)


def copy_file_metadata(source, destination):
    '''Copy a file and its metadata (perm bits, access times, ...)'''

    # This function is a workaround for Android python copystat
    # bug ([issue28141]) https://bugs.python.org/issue28141
    try:
        shutil.copy2(source, destination)
    except OSError as e:
        logger.warning("A problem occurred copying file %s to %s; %s",
                       source, destination, e)


def clean_output_dir(path, retention):
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
            logger.debug("Skipping deletion; %s is on retention list: %s",
                         filename, file)
        elif os.path.isdir(file):
            try:
                shutil.rmtree(file)
                logger.debug("Deleted directory %s", file)
            except Exception as e:
                logger.error("Unable to delete directory %s; %s",
                             file, e)
        elif os.path.isfile(file) or os.path.islink(file):
            try:
                os.remove(file)
                logger.debug("Deleted file/link %s", file)
            except Exception as e:
                logger.error("Unable to delete file %s; %s", file, e)
        else:
            logger.error("Unable to delete %s, file type unknown", file)


def get_relative_path(path):
    """Return the relative path from the given path to the root path."""
    components = split_all(path)
    if len(components) <= 1:
        return os.curdir
    else:
        parents = [os.pardir] * (len(components) - 1)
        return os.path.join(*parents)


def path_to_url(path):
    """Return the URL corresponding to a given path."""
    if path is not None:
        path = posixize_path(path)
    return path


def posixize_path(rel_path):
    """Use '/' as path separator, so that source references,
    like '{static}/foo/bar.jpg' or 'extras/favicon.ico',
    will work on Windows as well as on Mac and Linux."""
    return rel_path.replace(os.sep, '/')


class _HTMLWordTruncator(HTMLParser):

    _word_regex = re.compile(r"(({SBC})({SBC}|-|')*)|{DBC}".format(
        # SBC means Latin-like characters. A word contains a few characters.
        #         ASCII |Extended Latin | Cyrillic
        SBC="[0-9a-zA-Z]|[\u00C0-\u024f]|[\u0400-\u04FF]",
        # DBC means CJK-like characters. An character can stand for a word.
        DBC=("([\u4E00-\u9FFF])|"          # CJK Unified Ideographs
             "([\u3400-\u4DBF])|"          # CJK Unified Ideographs Extension A
             "([\uF900-\uFAFF])|"          # CJK Compatibility Ideographs
             "([\U00020000-\U0002A6DF])|"  # CJK Unified Ideographs Extension B
             "([\U0002F800-\U0002FA1F])|"  # CJK Compatibility Ideographs Supplement
             "([\u3040-\u30FF])|"          # Hiragana and Katakana
             "([\u1100-\u11FF])|"          # Hangul Jamo
             "([\uAC00-\uD7FF])|"          # Hangul Compatibility Jamo
             "([\u3130-\u318F])"           # Hangul Syllables
             )), re.UNICODE)
    _word_prefix_regex = re.compile(r'\w', re.U)
    _singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area',
                 'hr', 'input')

    class TruncationCompleted(Exception):

        def __init__(self, truncate_at):
            super().__init__(truncate_at)
            self.truncate_at = truncate_at

    def __init__(self, max_words):
        super().__init__(convert_charrefs=False)

        self.max_words = max_words
        self.words_found = 0
        self.open_tags = []
        self.last_word_end = None
        self.truncate_at = None

    def feed(self, *args, **kwargs):
        try:
            super().feed(*args, **kwargs)
        except self.TruncationCompleted as exc:
            self.truncate_at = exc.truncate_at
        else:
            self.truncate_at = None

    def getoffset(self):
        line_start = 0
        lineno, line_offset = self.getpos()
        for i in range(lineno - 1):
            line_start = self.rawdata.index('\n', line_start) + 1
        return line_start + line_offset

    def add_word(self, word_end):
        self.words_found += 1
        self.last_word_end = None
        if self.words_found == self.max_words:
            raise self.TruncationCompleted(word_end)

    def add_last_word(self):
        if self.last_word_end is not None:
            self.add_word(self.last_word_end)

    def handle_starttag(self, tag, attrs):
        self.add_last_word()
        if tag not in self._singlets:
            self.open_tags.insert(0, tag)

    def handle_endtag(self, tag):
        self.add_last_word()
        try:
            i = self.open_tags.index(tag)
        except ValueError:
            pass
        else:
            # SGML: An end tag closes, back to the matching start tag,
            # all unclosed intervening start tags with omitted end tags
            del self.open_tags[:i + 1]

    def handle_data(self, data):
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

    def _handle_ref(self, name, char):
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
            if self.rawdata[ref_end] == ';':
                ref_end += 1
        except IndexError:
            # We are at the end of the string and there's no ';'
            pass

        if self.last_word_end is None:
            if self._word_prefix_regex.match(char):
                self.last_word_end = ref_end
        else:
            if self._word_regex.match(char):
                self.last_word_end = ref_end
            else:
                self.add_last_word()

    def handle_entityref(self, name):
        """
        Called when an entity ref like '&mdash;' is found

        `name` is the entity ref without ampersand and semicolon (e.g. `mdash`)
        """
        try:
            codepoint = entities.name2codepoint[name]
            char = chr(codepoint)
        except KeyError:
            char = ''
        self._handle_ref(name, char)

    def handle_charref(self, name):
        """
        Called when a char ref like '&#8212;' or '&#x2014' is found

        `name` is the char ref without ampersand and semicolon (e.g. `#8212` or
        `#x2014`)
        """
        try:
            if name.startswith('x'):
                codepoint = int(name[1:], 16)
            else:
                codepoint = int(name)
            char = chr(codepoint)
        except (ValueError, OverflowError):
            char = ''
        self._handle_ref('#' + name, char)


def truncate_html_words(s, num, end_text='…'):
    """Truncates HTML to a certain number of words.

    (not counting tags and comments). Closes opened tags if they were correctly
    closed in the given html. Takes an optional argument of what should be used
    to notify that the string has been truncated, defaulting to ellipsis (…).

    Newlines in the HTML are preserved. (From the django framework).
    """
    length = int(num)
    if length <= 0:
        return ''
    truncator = _HTMLWordTruncator(length)
    truncator.feed(s)
    if truncator.truncate_at is None:
        return s
    out = s[:truncator.truncate_at]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in truncator.open_tags:
        out += '</%s>' % tag
    # Return string
    return out


def process_translations(content_list, translation_id=None):
    """ Finds translations and returns them.

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
        raise TypeError('Cannot unpack {}, \'translation_id\' must be falsy, a'
                        ' string or a collection of strings'
                        .format(translation_id))
    except AttributeError:
        raise AttributeError('Cannot use {} as \'translation_id\', there '
                             'appear to be items without these metadata '
                             'attributes'.format(translation_id))

    for id_vals, items in groupby(content_list, attrgetter(*translation_id)):
        # prepare warning string
        id_vals = (id_vals,) if len(translation_id) == 1 else id_vals
        with_str = 'with' + ', '.join([' {} "{{}}"'] * len(translation_id))\
            .format(*translation_id).format(*id_vals)

        items = list(items)
        original_items = get_original_items(items, with_str)
        index.extend(original_items)
        for a in items:
            a.translations = [x for x in items if x != a]

    translations = [x for x in content_list if x not in index]

    return index, translations


def get_original_items(items, with_str):
    def _warn_source_paths(msg, items, *extra):
        args = [len(items)]
        args.extend(extra)
        args.extend(x.source_path for x in items)
        logger.warning('{}: {}'.format(msg, '\n%s' * len(items)), *args)

    # warn if several items have the same lang
    for lang, lang_items in groupby(items, attrgetter('lang')):
        lang_items = list(lang_items)
        if len(lang_items) > 1:
            _warn_source_paths('There are %s items "%s" with lang %s',
                               lang_items, with_str, lang)

    # items with `translation` metadata will be used as translations...
    candidate_items = [
        i for i in items
        if i.metadata.get('translation', 'false').lower() == 'false']

    # ...unless all items with that slug are translations
    if not candidate_items:
        _warn_source_paths('All items ("%s") "%s" are translations',
                           items, with_str)
        candidate_items = items

    # find items with default language
    original_items = [i for i in candidate_items if i.in_default_lang]

    # if there is no article with default language, go back one step
    if not original_items:
        original_items = candidate_items

    # warn if there are several original items
    if len(original_items) > 1:
        _warn_source_paths('There are %s original (not translated) items %s',
                           original_items, with_str)
    return original_items


def order_content(content_list, order_by='slug'):
    """ Sorts content.

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
                logger.error('Error sorting with function %s', order_by)
        elif isinstance(order_by, str):
            if order_by.startswith('reversed-'):
                order_reversed = True
                order_by = order_by.replace('reversed-', '', 1)
            else:
                order_reversed = False

            if order_by == 'basename':
                content_list.sort(
                    key=lambda x: os.path.basename(x.source_path or ''),
                    reverse=order_reversed)
            else:
                try:
                    content_list.sort(key=attrgetter(order_by),
                                      reverse=order_reversed)
                except AttributeError:
                    for content in content_list:
                        try:
                            getattr(content, order_by)
                        except AttributeError:
                            logger.warning(
                                'There is no "%s" attribute in "%s". '
                                'Defaulting to slug order.',
                                order_by,
                                content.get_relative_source_path(),
                                extra={
                                    'limit_msg': ('More files are missing '
                                                  'the needed attribute.')
                                })
        else:
            logger.warning(
                'Invalid *_ORDER_BY setting (%s). '
                'Valid options are strings and functions.', order_by)

    return content_list


class FileSystemWatcher:
    def __init__(self, settings_file, reader_class, settings=None):
        self.watchers = {
            'settings': FileSystemWatcher.file_watcher(settings_file)
        }

        self.settings = None
        self.reader_class = reader_class
        self._extensions = None
        self._content_path = None
        self._theme_path = None
        self._ignore_files = None

        if settings is not None:
            self.update_watchers(settings)

    def update_watchers(self, settings):
        new_extensions = set(self.reader_class(settings).extensions)
        new_content_path = settings.get('PATH', '')
        new_theme_path = settings.get('THEME', '')
        new_ignore_files = set(settings.get('IGNORE_FILES', []))

        extensions_changed = new_extensions != self._extensions
        content_changed = new_content_path != self._content_path
        theme_changed = new_theme_path != self._theme_path
        ignore_changed = new_ignore_files != self._ignore_files

        # Refresh content watcher if related settings changed
        if extensions_changed or content_changed or ignore_changed:
            self.add_watcher('content',
                             new_content_path,
                             new_extensions,
                             new_ignore_files)

        # Refresh theme watcher if related settings changed
        if theme_changed or ignore_changed:
            self.add_watcher('theme',
                             new_theme_path,
                             [''],
                             new_ignore_files)

        # Watch STATIC_PATHS
        old_static_watchers = set(key
                                  for key in self.watchers
                                  if key.startswith('[static]'))

        for path in settings.get('STATIC_PATHS', []):
            key = '[static]{}'.format(path)
            if ignore_changed or (key not in self.watchers):
                self.add_watcher(
                    key,
                    os.path.join(new_content_path, path),
                    [''],
                    new_ignore_files)
            if key in old_static_watchers:
                old_static_watchers.remove(key)

        # cleanup removed static watchers
        for key in old_static_watchers:
            del self.watchers[key]

        # update values
        self.settings = settings
        self._extensions = new_extensions
        self._content_path = new_content_path
        self._theme_path = new_theme_path
        self._ignore_files = new_ignore_files

    def check(self):
        '''return a key:watcher_status dict for all watchers'''
        result = {key: next(watcher) for key, watcher in self.watchers.items()}

        # Various warnings
        if result.get('content') is None:
            reader_descs = sorted(
                {
                    '  | %s (%s)' % (type(r).__name__, ', '.join(r.file_extensions))
                    for r in self.reader_class(self.settings).readers.values()
                    if r.enabled
                }
            )
            logger.warning(
                'No valid files found in content for the active readers:\n'
                + '\n'.join(reader_descs))

        if result.get('theme') is None:
            logger.warning('Empty theme folder. Using `basic` theme.')

        return result

    def add_watcher(self, key, path, extensions=[''], ignores=[]):
        watcher = self.get_watcher(path, extensions, ignores)
        if watcher is not None:
            self.watchers[key] = watcher

    def get_watcher(self, path, extensions=[''], ignores=[]):
        '''return a watcher depending on path type (file or folder)'''
        if not os.path.exists(path):
            logger.warning("Watched path does not exist: %s", path)
            return None

        if os.path.isdir(path):
            return self.folder_watcher(path, extensions, ignores)
        else:
            return self.file_watcher(path)

    @staticmethod
    def folder_watcher(path, extensions, ignores=[]):
        '''Generator for monitoring a folder for modifications.

        Returns a boolean indicating if files are changed since last check.
        Returns None if there are no matching files in the folder'''

        def file_times(path):
            '''Return `mtime` for each file in path'''

            for root, dirs, files in os.walk(path, followlinks=True):
                dirs[:] = [x for x in dirs if not x.startswith(os.curdir)]

                for f in files:
                    valid_extension = f.endswith(tuple(extensions))
                    file_ignored = any(
                        fnmatch.fnmatch(f, ignore) for ignore in ignores
                    )
                    if valid_extension and not file_ignored:
                        try:
                            yield os.stat(os.path.join(root, f)).st_mtime
                        except OSError as e:
                            logger.warning('Caught Exception: %s', e)

        LAST_MTIME = 0
        while True:
            try:
                mtime = max(file_times(path))
                if mtime > LAST_MTIME:
                    LAST_MTIME = mtime
                    yield True
            except ValueError:
                yield None
            else:
                yield False

    @staticmethod
    def file_watcher(path):
        '''Generator for monitoring a file for modifications'''
        LAST_MTIME = 0
        while True:
            if path:
                try:
                    mtime = os.stat(path).st_mtime
                except OSError as e:
                    logger.warning('Caught Exception: %s', e)
                    continue

                if mtime > LAST_MTIME:
                    LAST_MTIME = mtime
                    yield True
                else:
                    yield False
            else:
                yield None


def set_date_tzinfo(d, tz_name=None):
    """Set the timezone for dates that don't have tzinfo"""
    if tz_name and not d.tzinfo:
        tz = pytz.timezone(tz_name)
        d = tz.localize(d)
        return SafeDatetime(d.year, d.month, d.day, d.hour, d.minute, d.second,
                            d.microsecond, d.tzinfo)
    return d


def mkdir_p(path):
    os.makedirs(path, exist_ok=True)


def split_all(path):
    """Split a path into a list of components

    While os.path.split() splits a single component off the back of
    `path`, this function splits all components:

    >>> split_all(os.path.join('a', 'b', 'c'))
    ['a', 'b', 'c']
    """
    components = []
    path = path.lstrip('/')
    while path:
        head, tail = os.path.split(path)
        if tail:
            components.insert(0, tail)
        elif head == path:
            components.insert(0, head)
            break
        path = head
    return components


def is_selected_for_writing(settings, path):
    '''Check whether path is selected for writing
    according to the WRITE_SELECTED list

    If WRITE_SELECTED is an empty list (default),
    any path is selected for writing.
    '''
    if settings['WRITE_SELECTED']:
        return path in settings['WRITE_SELECTED']
    else:
        return True


def path_to_file_url(path):
    '''Convert file-system path to file:// URL'''
    return urllib.parse.urljoin("file://", urllib.request.pathname2url(path))


def maybe_pluralize(count, singular, plural):
    '''
    Returns a formatted string containing count and plural if count is not 1
    Returns count and singular if count is 1

    maybe_pluralize(0, 'Article', 'Articles') -> '0 Articles'
    maybe_pluralize(1, 'Article', 'Articles') -> '1 Article'
    maybe_pluralize(2, 'Article', 'Articles') -> '2 Articles'

    '''
    selection = plural
    if count == 1:
        selection = singular
    return '{} {}'.format(count, selection)
