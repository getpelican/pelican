import copy
import datetime
import locale
import logging
import os
import re
from datetime import timezone
from html import unescape
from typing import Any, Dict, Optional, Set, Tuple
from urllib.parse import ParseResult, unquote, urljoin, urlparse, urlunparse

try:
    from zoneinfo import ZoneInfo
except ModuleNotFoundError:
    from backports.zoneinfo import ZoneInfo


from pelican.plugins import signals
from pelican.settings import DEFAULT_CONFIG, Settings

# Import these so that they're available when you import from pelican.contents.
from pelican.urlwrappers import Author, Category, Tag, URLWrapper  # NOQA
from pelican.utils import (
    deprecated_attribute,
    memoized,
    path_to_url,
    posixize_path,
    sanitised_join,
    set_date_tzinfo,
    slugify,
    truncate_html_paragraphs,
    truncate_html_words,
)

logger = logging.getLogger(__name__)


class Content:
    """Represents a content.

    :param content: the string to parse, containing the original content.
    :param metadata: the metadata associated to this page (optional).
    :param settings: the settings dictionary (optional).
    :param source_path: The location of the source of this content (if any).
    :param context: The shared context between generators.

    """

    default_template: Optional[str] = None
    mandatory_properties: Tuple[str, ...] = ()

    @deprecated_attribute(old="filename", new="source_path", since=(3, 2, 0))
    def filename():
        return None

    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        settings: Optional[Settings] = None,
        source_path: Optional[str] = None,
        context: Optional[Dict[Any, Any]] = None,
    ):
        if metadata is None:
            metadata = {}
        if settings is None:
            settings = copy.deepcopy(DEFAULT_CONFIG)

        self.settings = settings
        self._content = content
        if context is None:
            context = {}
        self._context = context
        self.translations = []

        local_metadata = {}
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            if key in ("save_as", "url"):
                key = "override_" + key
            setattr(self, key.lower(), value)

        # also keep track of the metadata attributes available
        self.metadata = local_metadata

        # default template if it's not defined in page
        self.template = self._get_template()

        # First, read the authors from "authors", if not, fallback to "author"
        # and if not use the settings defined one, if any.
        if not hasattr(self, "author"):
            if hasattr(self, "authors"):
                self.author = self.authors[0]
            elif "AUTHOR" in settings:
                self.author = Author(settings["AUTHOR"], settings)

        if not hasattr(self, "authors") and hasattr(self, "author"):
            self.authors = [self.author]

        # XXX Split all the following code into pieces, there is too much here.

        # manage languages
        self.in_default_lang = True
        if "DEFAULT_LANG" in settings:
            default_lang = settings["DEFAULT_LANG"].lower()
            if not hasattr(self, "lang"):
                self.lang = default_lang

            self.in_default_lang = self.lang == default_lang

        # create the slug if not existing, generate slug according to
        # setting of SLUG_ATTRIBUTE
        if not hasattr(self, "slug"):
            if settings["SLUGIFY_SOURCE"] == "title" and hasattr(self, "title"):
                value = self.title
            elif settings["SLUGIFY_SOURCE"] == "basename" and source_path is not None:
                value = os.path.basename(os.path.splitext(source_path)[0])
            else:
                value = None
            if value is not None:
                self.slug = slugify(
                    value,
                    regex_subs=settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
                    preserve_case=settings.get("SLUGIFY_PRESERVE_CASE", False),
                    use_unicode=settings.get("SLUGIFY_USE_UNICODE", False),
                )

        self.source_path = source_path
        self.relative_source_path = self.get_relative_source_path()

        # manage the date format
        if not hasattr(self, "date_format"):
            if hasattr(self, "lang") and self.lang in settings["DATE_FORMATS"]:
                self.date_format = settings["DATE_FORMATS"][self.lang]
            else:
                self.date_format = settings["DEFAULT_DATE_FORMAT"]

        if isinstance(self.date_format, tuple):
            locale_string = self.date_format[0]
            locale.setlocale(locale.LC_ALL, locale_string)
            self.date_format = self.date_format[1]

        # manage timezone
        default_timezone = settings.get("TIMEZONE", "UTC")
        timezone = getattr(self, "timezone", default_timezone)
        self.timezone = ZoneInfo(timezone)

        if hasattr(self, "date"):
            self.date = set_date_tzinfo(self.date, timezone)
            self.locale_date = self.date.strftime(self.date_format)

        if hasattr(self, "modified"):
            self.modified = set_date_tzinfo(self.modified, timezone)
            self.locale_modified = self.modified.strftime(self.date_format)

        # manage status
        if not hasattr(self, "status"):
            # Previous default of None broke comment plugins and perhaps others
            self.status = getattr(self, "default_status", "")

        # store the summary metadata if it is set
        if "summary" in metadata:
            self._summary = metadata["summary"]

        signals.content_object_init.send(self)

    def __str__(self) -> str:
        return self.source_path or repr(self)

    def _has_valid_mandatory_properties(self) -> bool:
        """Test mandatory properties are set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                logger.error(
                    "Skipping %s: could not find information about '%s'", self, prop
                )
                return False
        return True

    def _has_valid_save_as(self) -> bool:
        """Return true if save_as doesn't write outside output path, false
        otherwise."""
        try:
            output_path = self.settings["OUTPUT_PATH"]
        except KeyError:
            # we cannot check
            return True

        try:
            sanitised_join(output_path, self.save_as)
        except RuntimeError:  # outside output_dir
            logger.error(
                "Skipping %s: file %r would be written outside output path",
                self,
                self.save_as,
            )
            return False

        return True

    def _has_valid_status(self) -> bool:
        if hasattr(self, "allowed_statuses"):
            if self.status not in self.allowed_statuses:
                logger.error(
                    "Unknown status '%s' for file %s, skipping it. (Not in %s)",
                    self.status,
                    self,
                    self.allowed_statuses,
                )
                return False

        # if undefined we allow all
        return True

    def is_valid(self) -> bool:
        """Validate Content"""
        # Use all() to not short circuit and get results of all validations
        return all(
            [
                self._has_valid_mandatory_properties(),
                self._has_valid_save_as(),
                self._has_valid_status(),
            ]
        )

    @property
    def url_format(self) -> Dict[str, Any]:
        """Returns the URL, formatted with the proper values"""
        metadata = copy.copy(self.metadata)
        path = self.metadata.get("path", self.get_relative_source_path())
        metadata.update(
            {
                "path": path_to_url(path),
                "slug": getattr(self, "slug", ""),
                "lang": getattr(self, "lang", "en"),
                "date": getattr(self, "date", datetime.datetime.now()),
                "author": self.author.slug if hasattr(self, "author") else "",
                "category": self.category.slug if hasattr(self, "category") else "",
            }
        )
        return metadata

    def _expand_settings(self, key: str, klass: Optional[str] = None) -> str:
        if not klass:
            klass = self.__class__.__name__
        fq_key = (f"{klass}_{key}").upper()
        return str(self.settings[fq_key]).format(**self.url_format)

    def get_url_setting(self, key: str) -> str:
        if hasattr(self, "override_" + key):
            return getattr(self, "override_" + key)
        key = key if self.in_default_lang else f"lang_{key}"
        return self._expand_settings(key)

    def _link_replacer(self, siteurl: str, m: re.Match) -> str:
        what = m.group("what")
        value = urlparse(m.group("value"))
        path = value.path
        origin = m.group("path")

        # urllib.parse.urljoin() produces `a.html` for urljoin("..", "a.html")
        # so if RELATIVE_URLS are enabled, we fall back to os.path.join() to
        # properly get `../a.html`. However, os.path.join() produces
        # `baz/http://foo/bar.html` for join("baz", "http://foo/bar.html")
        # instead of correct "http://foo/bar.html", so one has to pick a side
        # as there is no silver bullet.
        if self.settings["RELATIVE_URLS"]:
            joiner = os.path.join
        else:
            joiner = urljoin

            # However, it's not *that* simple: urljoin("blog", "index.html")
            # produces just `index.html` instead of `blog/index.html` (unlike
            # os.path.join()), so in order to get a correct answer one needs to
            # append a trailing slash to siteurl in that case. This also makes
            # the new behavior fully compatible with Pelican 3.7.1.
            if not siteurl.endswith("/"):
                siteurl += "/"

        # XXX Put this in a different location.
        if what in {"filename", "static", "attach"}:

            def _get_linked_content(key: str, url: ParseResult) -> Optional[Content]:
                nonlocal value

                def _find_path(path: str) -> Optional[Content]:
                    if path.startswith("/"):
                        path = path[1:]
                    else:
                        # relative to the source path of this content
                        path = self.get_relative_source_path(  # type: ignore
                            os.path.join(self.relative_dir, path)
                        )
                    return self._context[key].get(path, None)

                # try path
                result = _find_path(url.path)
                if result is not None:
                    return result

                # try unquoted path
                result = _find_path(unquote(url.path))
                if result is not None:
                    return result

                # try html unescaped url
                unescaped_url = urlparse(unescape(url.geturl()))
                result = _find_path(unescaped_url.path)
                if result is not None:
                    value = unescaped_url
                    return result

                # check if a static file is linked with {filename}
                if what == "filename" and key == "generated_content":
                    linked_content = _get_linked_content("static_content", value)
                    if linked_content:
                        logger.warning(
                            "{filename} used for linking to static"
                            " content %s in %s. Use {static} instead",
                            value.path,
                            self.get_relative_source_path(),
                        )
                        return linked_content

                return None

            if what == "filename":
                key = "generated_content"
            else:
                key = "static_content"

            linked_content = _get_linked_content(key, value)
            if linked_content:
                if what == "attach":
                    linked_content.attach_to(self)  # type: ignore
                origin = joiner(siteurl, linked_content.url)
                origin = origin.replace("\\", "/")  # for Windows paths.
            else:
                logger.warning(
                    "Unable to find '%s', skipping url replacement.",
                    value.geturl(),
                    extra={
                        "limit_msg": (
                            "Other resources were not found "
                            "and their urls not replaced"
                        )
                    },
                )
        elif what == "category":
            origin = joiner(siteurl, Category(path, self.settings).url)
        elif what == "tag":
            origin = joiner(siteurl, Tag(path, self.settings).url)
        elif what == "index":
            origin = joiner(siteurl, self.settings["INDEX_SAVE_AS"])
        elif what == "author":
            origin = joiner(siteurl, Author(path, self.settings).url)
        else:
            logger.warning(
                "Replacement Indicator '%s' not recognized, skipping replacement",
                what,
            )

        # keep all other parts, such as query, fragment, etc.
        parts = list(value)
        parts[2] = origin
        origin = urlunparse(parts)

        return "".join((m.group("markup"), m.group("quote"), origin, m.group("quote")))

    def _get_intrasite_link_regex(self) -> re.Pattern:
        intrasite_link_regex = self.settings["INTRASITE_LINK_REGEX"]
        regex = rf"""
            (?P<markup><[^\>]+  # match tag with all url-value attributes
                (?:href|src|poster|data|cite|formaction|action|content)\s*=\s*)

            (?P<quote>["\'])      # require value to be quoted
            (?P<path>{intrasite_link_regex}(?P<value>.*?))  # the url value
            (?P=quote)"""
        return re.compile(regex, re.X)

    def _update_content(self, content: str, siteurl: str) -> str:
        """Update the content attribute.

        Change all the relative paths of the content to relative paths
        suitable for the output content.

        :param content: content resource that will be passed to the templates.
        :param siteurl: siteurl which is locally generated by the writer in
                        case of RELATIVE_URLS.
        """
        if not content:
            return content

        hrefs = self._get_intrasite_link_regex()
        return hrefs.sub(lambda m: self._link_replacer(siteurl, m), content)

    def get_static_links(self) -> Set[str]:
        static_links = set()
        hrefs = self._get_intrasite_link_regex()
        for m in hrefs.finditer(self._content):
            what = m.group("what")
            value = urlparse(m.group("value"))
            path = value.path
            if what not in {"static", "attach"}:
                continue
            if path.startswith("/"):
                path = path[1:]
            else:
                # relative to the source path of this content
                path = self.get_relative_source_path(
                    os.path.join(self.relative_dir, path)
                )
            path = path.replace("%20", " ")  # type: ignore
            static_links.add(path)
        return static_links

    def get_siteurl(self) -> str:
        return self._context.get("localsiteurl", "")

    @memoized
    def get_content(self, siteurl: str) -> str:
        if hasattr(self, "_get_content"):
            content = self._get_content()
        else:
            content = self._content
        return self._update_content(content, siteurl)

    @property
    def content(self) -> str:
        return self.get_content(self.get_siteurl())

    @memoized
    def get_summary(self, siteurl: str) -> str:
        """Returns the summary of an article.

        This is based on the summary metadata if set, otherwise truncate the
        content.
        """
        if "summary" in self.metadata:
            return self.metadata["summary"]

        content = self.content
        max_paragraphs = self.settings.get("SUMMARY_MAX_PARAGRAPHS")
        if max_paragraphs is not None:
            content = truncate_html_paragraphs(self.content, max_paragraphs)

        if self.settings["SUMMARY_MAX_LENGTH"] is None:
            return content

        return truncate_html_words(
            self.content,
            self.settings["SUMMARY_MAX_LENGTH"],
            self.settings["SUMMARY_END_SUFFIX"],
        )

    @property
    def summary(self) -> str:
        return self.get_summary(self.get_siteurl())

    def _get_summary(self) -> str:
        """deprecated function to access summary"""

        logger.warning(
            "_get_summary() has been deprecated since 3.6.4. "
            "Use the summary decorator instead"
        )
        return self.summary

    @summary.setter
    def summary(self, value: str):
        """Dummy function"""

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        # TODO maybe typecheck
        self._status = value.lower()

    @property
    def url(self) -> str:
        return self.get_url_setting("url")

    @property
    def save_as(self) -> str:
        return self.get_url_setting("save_as")

    def _get_template(self) -> str:
        if hasattr(self, "template") and self.template is not None:
            return self.template
        else:
            return self.default_template

    def get_relative_source_path(
        self, source_path: Optional[str] = None
    ) -> Optional[str]:
        """Return the relative path (from the content path) to the given
        source_path.

        If no source path is specified, use the source path of this
        content object.
        """
        if not source_path:
            source_path = self.source_path
        if source_path is None:
            return None

        return posixize_path(
            os.path.relpath(
                os.path.abspath(os.path.join(self.settings["PATH"], source_path)),
                os.path.abspath(self.settings["PATH"]),
            )
        )

    @property
    def relative_dir(self) -> str:
        return posixize_path(
            os.path.dirname(
                os.path.relpath(
                    os.path.abspath(self.source_path),
                    os.path.abspath(self.settings["PATH"]),
                )
            )
        )

    def refresh_metadata_intersite_links(self) -> None:
        for key in self.settings["FORMATTED_FIELDS"]:
            if key in self.metadata and key != "summary":
                value = self._update_content(self.metadata[key], self.get_siteurl())
                self.metadata[key] = value
                setattr(self, key.lower(), value)

        # _summary is an internal variable that some plugins may be writing to,
        # so ensure changes to it are picked up, and write summary back to it
        if "summary" in self.settings["FORMATTED_FIELDS"]:
            if hasattr(self, "_summary"):
                self.metadata["summary"] = self._summary

            if "summary" in self.metadata:
                self.metadata["summary"] = self._update_content(
                    self.metadata["summary"], self.get_siteurl()
                )
                self._summary = self.metadata["summary"]


class SkipStub(Content):
    """Stub class representing content that should not be processed in any way."""

    def __init__(
        self, content, metadata=None, settings=None, source_path=None, context=None
    ):
        self.source_path = source_path

    def is_valid(self):
        return False

    @property
    def content(self):
        raise NotImplementedError("Stub content should not be read")

    @property
    def save_as(self):
        raise NotImplementedError("Stub content cannot be saved")


class Page(Content):
    mandatory_properties = ("title",)
    allowed_statuses = ("published", "hidden", "draft", "skip")
    default_status = "published"
    default_template = "page"

    def _expand_settings(self, key: str) -> str:
        klass = "draft_page" if self.status == "draft" else None
        return super()._expand_settings(key, klass)


class Article(Content):
    mandatory_properties = ("title", "date", "category")
    allowed_statuses = ("published", "hidden", "draft", "skip")
    default_status = "published"
    default_template = "article"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # handle WITH_FUTURE_DATES (designate article to draft based on date)
        if not self.settings["WITH_FUTURE_DATES"] and hasattr(self, "date"):
            if self.date.tzinfo is None:
                now = datetime.datetime.now()
            else:
                now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
            if self.date > now:
                self.status = "draft"

        # if we are a draft and there is no date provided, set max datetime
        if not hasattr(self, "date") and self.status == "draft":
            self.date = datetime.datetime.max.replace(tzinfo=self.timezone)

    def _expand_settings(self, key: str) -> str:
        klass = "draft" if self.status == "draft" else "article"
        return super()._expand_settings(key, klass)


class Static(Content):
    mandatory_properties = ("title",)
    default_status = "published"
    default_template = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._output_location_referenced = False

    @deprecated_attribute(old="filepath", new="source_path", since=(3, 2, 0))
    def filepath():
        return None

    @deprecated_attribute(old="src", new="source_path", since=(3, 2, 0))
    def src():
        return None

    @deprecated_attribute(old="dst", new="save_as", since=(3, 2, 0))
    def dst():
        return None

    @property
    def url(self) -> str:
        # Note when url has been referenced, so we can avoid overriding it.
        self._output_location_referenced = True
        return super().url

    @property
    def save_as(self) -> str:
        # Note when save_as has been referenced, so we can avoid overriding it.
        self._output_location_referenced = True
        return super().save_as

    def attach_to(self, content: Content) -> None:
        """Override our output directory with that of the given content object."""

        # Determine our file's new output path relative to the linking
        # document. If it currently lives beneath the linking
        # document's source directory, preserve that relationship on output.
        # Otherwise, make it a sibling.

        linking_source_dir = os.path.dirname(content.source_path)
        tail_path = os.path.relpath(self.source_path, linking_source_dir)
        if tail_path.startswith(os.pardir + os.sep):
            tail_path = os.path.basename(tail_path)
        new_save_as = os.path.join(os.path.dirname(content.save_as), tail_path)

        # We do not build our new url by joining tail_path with the linking
        # document's url, because we cannot know just by looking at the latter
        # whether it points to the document itself or to its parent directory.
        # (An url like 'some/content' might mean a directory named 'some'
        # with a file named 'content', or it might mean a directory named
        # 'some/content' with a file named 'index.html'.) Rather than trying
        # to figure it out by comparing the linking document's url and save_as
        # path, we simply build our new url from our new save_as path.

        new_url = path_to_url(new_save_as)

        def _log_reason(reason: str) -> None:
            logger.warning(
                "The {attach} link in %s cannot relocate "
                "%s because %s. Falling back to "
                "{filename} link behavior instead.",
                content.get_relative_source_path(),
                self.get_relative_source_path(),
                reason,
                extra={"limit_msg": "More {attach} warnings silenced."},
            )

        # We never override an override, because we don't want to interfere
        # with user-defined overrides that might be in EXTRA_PATH_METADATA.
        if hasattr(self, "override_save_as") or hasattr(self, "override_url"):
            if new_save_as != self.save_as or new_url != self.url:
                _log_reason("its output location was already overridden")
            return

        # We never change an output path that has already been referenced,
        # because we don't want to break links that depend on that path.
        if self._output_location_referenced:
            if new_save_as != self.save_as or new_url != self.url:
                _log_reason("another link already referenced its location")
            return

        self.override_save_as = new_save_as
        self.override_url = new_url
