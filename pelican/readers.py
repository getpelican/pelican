import datetime
import logging
import os
import re
from collections import OrderedDict
from html import escape
from html.parser import HTMLParser
from io import StringIO

import docutils
import docutils.core
import docutils.io
from docutils.parsers.rst.languages import get_language as get_docutils_lang
from docutils.writers.html4css1 import HTMLTranslator, Writer

from pelican import rstdirectives  # NOQA
from pelican.cache import FileStampDataCacher
from pelican.contents import Author, Category, Page, SkipStub, Tag
from pelican.plugins import signals
from pelican.utils import file_suffix, get_date, pelican_open, posixize_path

try:
    from markdown import Markdown
except ImportError:
    Markdown = False

# Metadata processors have no way to discard an unwanted value, so we have
# them return this value instead to signal that it should be discarded later.
# This means that _filter_discardable_metadata() must be called on processed
# metadata dicts before use, to remove the items with the special value.
_DISCARD = object()

DUPLICATES_DEFINITIONS_ALLOWED = {
    "tags": False,
    "date": False,
    "modified": False,
    "status": False,
    "category": False,
    "author": False,
    "save_as": False,
    "url": False,
    "authors": False,
    "slug": False,
}

METADATA_PROCESSORS = {
    "tags": lambda x, y: ([Tag(tag, y) for tag in ensure_metadata_list(x)] or _DISCARD),
    "date": lambda x, y: get_date(x.replace("_", " ")),
    "modified": lambda x, y: get_date(x),
    "status": lambda x, y: x.strip() or _DISCARD,
    "category": lambda x, y: _process_if_nonempty(Category, x, y),
    "author": lambda x, y: _process_if_nonempty(Author, x, y),
    "authors": lambda x, y: (
        [Author(author, y) for author in ensure_metadata_list(x)] or _DISCARD
    ),
    "slug": lambda x, y: x.strip() or _DISCARD,
}

logger = logging.getLogger(__name__)


def ensure_metadata_list(text):
    """Canonicalize the format of a list of authors or tags.  This works
    the same way as Docutils' "authors" field: if it's already a list,
    those boundaries are preserved; otherwise, it must be a string;
    if the string contains semicolons, it is split on semicolons;
    otherwise, it is split on commas.  This allows you to write
    author lists in either "Jane Doe, John Doe" or "Doe, Jane; Doe, John"
    format.

    Regardless, all list items undergo .strip() before returning, and
    empty items are discarded.
    """
    if isinstance(text, str):
        if ";" in text:
            text = text.split(";")
        else:
            text = text.split(",")

    return list(OrderedDict.fromkeys([v for v in (w.strip() for w in text) if v]))


def _process_if_nonempty(processor, name, settings):
    """Removes extra whitespace from name and applies a metadata processor.
    If name is empty or all whitespace, returns _DISCARD instead.
    """
    name = name.strip()
    return processor(name, settings) if name else _DISCARD


def _filter_discardable_metadata(metadata):
    """Return a copy of a dict, minus any items marked as discardable."""
    return {name: val for name, val in metadata.items() if val is not _DISCARD}


class BaseReader:
    """Base class to read files.

    This class is used to process static files, and it can be inherited for
    other types of file. A Reader class must have the following attributes:

    - enabled: (boolean) tell if the Reader class is enabled. It
      generally depends on the import of some dependency.
    - file_extensions: a list of file extensions that the Reader will process.
    - extensions: a list of extensions to use in the reader (typical use is
      Markdown).

    """

    enabled = True
    file_extensions = ["static"]
    extensions = None

    def __init__(self, settings):
        self.settings = settings

    def process_metadata(self, name, value):
        if name in METADATA_PROCESSORS:
            return METADATA_PROCESSORS[name](value, self.settings)
        return value

    def read(self, source_path):
        "No-op parser"
        content = None
        metadata = {}
        return content, metadata

    def disabled_message(self) -> str:
        """Message about why this plugin was disabled."""
        return ""


class _FieldBodyTranslator(HTMLTranslator):
    def __init__(self, document):
        super().__init__(document)
        self.compact_p = None

    def astext(self):
        return "".join(self.body)

    def visit_field_body(self, node):
        pass

    def depart_field_body(self, node):
        pass


def render_node_to_html(document, node, field_body_translator_class):
    visitor = field_body_translator_class(document)
    node.walkabout(visitor)
    return visitor.astext()


class PelicanHTMLWriter(Writer):
    def __init__(self):
        super().__init__()
        self.translator_class = PelicanHTMLTranslator


class PelicanHTMLTranslator(HTMLTranslator):
    def visit_abbreviation(self, node):
        attrs = {}
        if node.hasattr("explanation"):
            attrs["title"] = node["explanation"]
        self.body.append(self.starttag(node, "abbr", "", **attrs))

    def depart_abbreviation(self, node):
        self.body.append("</abbr>")

    def visit_image(self, node):
        # set an empty alt if alt is not specified
        # avoids that alt is taken from src
        node["alt"] = node.get("alt", "")
        return HTMLTranslator.visit_image(self, node)


class RstReader(BaseReader):
    """Reader for reStructuredText files

    By default the output HTML is written using
    docutils.writers.html4css1.Writer and translated using a subclass of
    docutils.writers.html4css1.HTMLTranslator. If you want to override it with
    your own writer/translator (e.g. a HTML5-based one), pass your classes to
    these two attributes. Look in the source code for details.

        writer_class                    Used for writing contents
        field_body_translator_class     Used for translating metadata such
            as article summary

    """

    enabled = bool(docutils)
    file_extensions = ["rst"]

    writer_class = PelicanHTMLWriter
    field_body_translator_class = _FieldBodyTranslator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lang_code = self.settings.get("DEFAULT_LANG", "en")
        if get_docutils_lang(lang_code):
            self._language_code = lang_code
        else:
            logger.warning(
                "Docutils has no localization for '%s'. Using 'en' instead.",
                lang_code,
            )
            self._language_code = "en"

    def _parse_metadata(self, document, source_path):
        """Return the dict containing document metadata"""
        formatted_fields = self.settings["FORMATTED_FIELDS"]

        output = {}

        if document.first_child_matching_class(docutils.nodes.title) is None:
            logger.warning(
                "Document title missing in file %s: "
                "Ensure exactly one top level section",
                source_path,
            )

        try:
            # docutils 0.18.1+
            nodes = document.findall(docutils.nodes.docinfo)
        except AttributeError:
            # docutils 0.18.0 or before
            nodes = document.traverse(docutils.nodes.docinfo)

        for docinfo in nodes:
            for element in docinfo.children:
                if element.tagname == "field":  # custom fields (e.g. summary)
                    name_elem, body_elem = element.children
                    name = name_elem.astext()
                    if name.lower() in formatted_fields:
                        value = render_node_to_html(
                            document, body_elem, self.field_body_translator_class
                        )
                    else:
                        value = body_elem.astext()
                elif element.tagname == "authors":  # author list
                    name = element.tagname
                    value = [element.astext() for element in element.children]
                else:  # standard fields (e.g. address)
                    name = element.tagname
                    value = element.astext()
                name = name.lower()

                output[name] = self.process_metadata(name, value)
        return output

    def _get_publisher(self, source_path):
        extra_params = {
            "initial_header_level": "2",
            "syntax_highlight": "short",
            "input_encoding": "utf-8",
            "language_code": self._language_code,
            "halt_level": 2,
            "traceback": True,
            "warning_stream": StringIO(),
            "embed_stylesheet": False,
        }
        user_params = self.settings.get("DOCUTILS_SETTINGS")
        if user_params:
            extra_params.update(user_params)

        pub = docutils.core.Publisher(
            writer=self.writer_class(), destination_class=docutils.io.StringOutput
        )
        pub.set_components("standalone", "restructuredtext", "html")
        pub.process_programmatic_settings(None, extra_params, None)
        pub.set_source(source_path=source_path)
        pub.publish()
        return pub

    def read(self, source_path):
        """Parses restructured text"""
        pub = self._get_publisher(source_path)
        parts = pub.writer.parts
        content = parts.get("body")

        metadata = self._parse_metadata(pub.document, source_path)
        metadata.setdefault("title", parts.get("title"))

        return content, metadata


class MarkdownReader(BaseReader):
    """Reader for Markdown files"""

    enabled = bool(Markdown)
    file_extensions = ["md", "markdown", "mkd", "mdown"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = self.settings["MARKDOWN"]
        settings.setdefault("extension_configs", {})
        settings.setdefault("extensions", [])
        for extension in settings["extension_configs"].keys():
            if extension not in settings["extensions"]:
                settings["extensions"].append(extension)
        if "markdown.extensions.meta" not in settings["extensions"]:
            settings["extensions"].append("markdown.extensions.meta")
        self._source_path = None

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        formatted_fields = self.settings["FORMATTED_FIELDS"]

        # prevent metadata extraction in fields
        self._md.preprocessors.deregister("meta")

        output = {}
        for name, value in meta.items():
            name = name.lower()
            if name in formatted_fields:
                # formatted metadata is special case and join all list values
                formatted_values = "\n".join(value)
                # reset the markdown instance to clear any state
                self._md.reset()
                formatted = self._md.convert(formatted_values)
                output[name] = self.process_metadata(name, formatted)
            elif not DUPLICATES_DEFINITIONS_ALLOWED.get(name, True):
                if len(value) > 1:
                    logger.warning(
                        "Duplicate definition of `%s` for %s. Using first one.",
                        name,
                        self._source_path,
                    )
                output[name] = self.process_metadata(name, value[0])
            elif len(value) > 1:
                # handle list metadata as list of string
                output[name] = self.process_metadata(name, value)
            else:
                # otherwise, handle metadata as single string
                output[name] = self.process_metadata(name, value[0])
        return output

    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        self._source_path = source_path
        self._md = Markdown(**self.settings["MARKDOWN"])
        with pelican_open(source_path) as text:
            content = self._md.convert(text)

        if hasattr(self._md, "Meta"):
            metadata = self._parse_metadata(self._md.Meta)
        else:
            metadata = {}
        return content, metadata

    def disabled_message(self) -> str:
        return (
            "Could not import 'markdown.Markdown'. "
            "Have you installed the 'markdown' package?"
        )


class HTMLReader(BaseReader):
    """Parses HTML files as input, looking for meta, title, and body tags"""

    file_extensions = ["htm", "html"]
    enabled = True

    class _HTMLParser(HTMLParser):
        def __init__(self, settings, filename):
            super().__init__(convert_charrefs=False)
            self.body = ""
            self.metadata = {}
            self.settings = settings

            self._data_buffer = ""

            self._filename = filename

            self._in_top_level = True
            self._in_head = False
            self._in_title = False
            self._in_body = False
            self._in_tags = False

        def handle_starttag(self, tag, attrs):
            if tag == "head" and self._in_top_level:
                self._in_top_level = False
                self._in_head = True
            elif tag == "title" and self._in_head:
                self._in_title = True
                self._data_buffer = ""
            elif tag == "body" and self._in_top_level:
                self._in_top_level = False
                self._in_body = True
                self._data_buffer = ""
            elif tag == "meta" and self._in_head:
                self._handle_meta_tag(attrs)

            elif self._in_body:
                self._data_buffer += self.build_tag(tag, attrs, False)

        def handle_endtag(self, tag):
            if tag == "head":
                if self._in_head:
                    self._in_head = False
                    self._in_top_level = True
            elif self._in_head and tag == "title":
                self._in_title = False
                self.metadata["title"] = self._data_buffer
            elif tag == "body":
                self.body = self._data_buffer
                self._in_body = False
                self._in_top_level = True
            elif self._in_body:
                self._data_buffer += f"</{escape(tag)}>"

        def handle_startendtag(self, tag, attrs):
            if tag == "meta" and self._in_head:
                self._handle_meta_tag(attrs)
            if self._in_body:
                self._data_buffer += self.build_tag(tag, attrs, True)

        def handle_comment(self, data):
            self._data_buffer += f"<!--{data}-->"

        def handle_data(self, data):
            self._data_buffer += data

        def handle_entityref(self, data):
            self._data_buffer += f"&{data};"

        def handle_charref(self, data):
            self._data_buffer += f"&#{data};"

        def build_tag(self, tag, attrs, close_tag):
            result = f"<{escape(tag)}"
            for k, v in attrs:
                result += " " + escape(k)
                if v is not None:
                    # If the attribute value contains a double quote, surround
                    # with single quotes, otherwise use double quotes.
                    if '"' in v:
                        result += f"='{escape(v, quote=False)}'"
                    else:
                        result += f'="{escape(v, quote=False)}"'
            if close_tag:
                return result + " />"
            return result + ">"

        def _handle_meta_tag(self, attrs):
            name = self._attr_value(attrs, "name")
            if name is None:
                attr_list = [f'{k}="{v}"' for k, v in attrs]
                attr_serialized = ", ".join(attr_list)
                logger.warning(
                    "Meta tag in file %s does not have a 'name' "
                    "attribute, skipping. Attributes: %s",
                    self._filename,
                    attr_serialized,
                )
                return
            name = name.lower()
            contents = self._attr_value(attrs, "content", "")
            if not contents:
                contents = self._attr_value(attrs, "contents", "")
                if contents:
                    logger.warning(
                        "Meta tag attribute 'contents' used in file %s, should"
                        " be changed to 'content'",
                        self._filename,
                        extra={
                            "limit_msg": "Other files have meta tag "
                            "attribute 'contents' that should "
                            "be changed to 'content'"
                        },
                    )

            if name == "keywords":
                name = "tags"

            if name in self.metadata:
                # if this metadata already exists (i.e. a previous tag with the
                # same name has already been specified then either convert to
                # list or append to list
                if isinstance(self.metadata[name], list):
                    self.metadata[name].append(contents)
                else:
                    self.metadata[name] = [self.metadata[name], contents]
            else:
                self.metadata[name] = contents

        @classmethod
        def _attr_value(cls, attrs, name, default=None):
            return next((x[1] for x in attrs if x[0] == name), default)

    def read(self, filename):
        """Parse content and metadata of HTML files"""
        with pelican_open(filename) as content:
            parser = self._HTMLParser(self.settings, filename)
            parser.feed(content)
            parser.close()

        metadata = {}
        for k in parser.metadata:
            metadata[k] = self.process_metadata(k, parser.metadata[k])
        return parser.body, metadata


class Readers(FileStampDataCacher):
    """Interface for all readers.

    This class contains a mapping of file extensions / Reader classes, to know
    which Reader class must be used to read a file (based on its extension).
    This is customizable both with the 'READERS' setting, and with the
    'readers_init' signall for plugins.

    """

    def __init__(self, settings=None, cache_name=""):
        self.settings = settings or {}
        self.readers = {}
        self.disabled_readers = {}
        # extension => reader for readers that are enabled
        self.reader_classes = {}
        # extension => reader for readers that are not enabled
        disabled_reader_classes = {}

        for cls in [BaseReader] + BaseReader.__subclasses__():
            if not cls.enabled:
                logger.debug(
                    "Missing dependencies for %s", ", ".join(cls.file_extensions)
                )

            for ext in cls.file_extensions:
                if cls.enabled:
                    self.reader_classes[ext] = cls
                else:
                    disabled_reader_classes[ext] = cls

        if self.settings["READERS"]:
            self.reader_classes.update(self.settings["READERS"])

        signals.readers_init.send(self)

        for fmt, reader_class in self.reader_classes.items():
            if not reader_class:
                continue

            self.readers[fmt] = reader_class(self.settings)

        for fmt, reader_class in disabled_reader_classes.items():
            self.disabled_readers[fmt] = reader_class(self.settings)

        # set up caching
        cache_this_level = (
            cache_name != "" and self.settings["CONTENT_CACHING_LAYER"] == "reader"
        )
        caching_policy = cache_this_level and self.settings["CACHE_CONTENT"]
        load_policy = cache_this_level and self.settings["LOAD_CONTENT_CACHE"]
        super().__init__(settings, cache_name, caching_policy, load_policy)

    @property
    def extensions(self):
        """File extensions that will be processed by a reader."""
        return self.readers.keys()

    @property
    def disabled_extensions(self):
        return self.disabled_readers.keys()

    def read_file(
        self,
        base_path,
        path,
        content_class=Page,
        fmt=None,
        context=None,
        preread_signal=None,
        preread_sender=None,
        context_signal=None,
        context_sender=None,
    ):
        """Return a content object parsed with the given format."""

        path = os.path.abspath(os.path.join(base_path, path))
        source_path = posixize_path(os.path.relpath(path, base_path))
        logger.debug("Read file %s -> %s", source_path, content_class.__name__)

        if not fmt:
            fmt = file_suffix(path)

        if fmt not in self.readers:
            raise TypeError("Pelican does not know how to parse %s", path)

        if preread_signal:
            logger.debug("Signal %s.send(%s)", preread_signal.name, preread_sender)
            preread_signal.send(preread_sender)

        reader = self.readers[fmt]

        metadata = _filter_discardable_metadata(
            default_metadata(settings=self.settings, process=reader.process_metadata)
        )
        metadata.update(
            path_metadata(
                full_path=path, source_path=source_path, settings=self.settings
            )
        )
        metadata.update(
            _filter_discardable_metadata(
                parse_path_metadata(
                    source_path=source_path,
                    settings=self.settings,
                    process=reader.process_metadata,
                )
            )
        )
        reader_name = reader.__class__.__name__
        metadata["reader"] = reader_name.replace("Reader", "").lower()

        content, reader_metadata = self.get_cached_data(path, (None, None))
        if content is None:
            content, reader_metadata = reader.read(path)
            reader_metadata = _filter_discardable_metadata(reader_metadata)
            self.cache_data(path, (content, reader_metadata))
        metadata.update(reader_metadata)

        if content:
            # find images with empty alt
            find_empty_alt(content, path)

        # eventually filter the content with typogrify if asked so
        if self.settings["TYPOGRIFY"]:
            import smartypants
            from typogrify.filters import typogrify

            typogrify_dashes = self.settings["TYPOGRIFY_DASHES"]
            if typogrify_dashes == "oldschool":
                smartypants.Attr.default = smartypants.Attr.set2
            elif typogrify_dashes == "oldschool_inverted":
                smartypants.Attr.default = smartypants.Attr.set3
            else:
                smartypants.Attr.default = smartypants.Attr.set1

            # Tell `smartypants` to also replace &quot; HTML entities with
            # smart quotes. This is necessary because Docutils has already
            # replaced double quotes with said entities by the time we run
            # this filter.
            smartypants.Attr.default |= smartypants.Attr.w

            def typogrify_wrapper(text):
                """Ensures ignore_tags feature is backward compatible"""
                try:
                    return typogrify(text, self.settings["TYPOGRIFY_IGNORE_TAGS"])
                except TypeError:
                    return typogrify(text)

            if content:
                content = typogrify_wrapper(content)

            if "title" in metadata:
                metadata["title"] = typogrify_wrapper(metadata["title"])

            if "summary" in metadata:
                metadata["summary"] = typogrify_wrapper(metadata["summary"])

        if context_signal:
            logger.debug(
                "Signal %s.send(%s, <metadata>)", context_signal.name, context_sender
            )
            context_signal.send(context_sender, metadata=metadata)

        if metadata.get("status") == "skip":
            content_class = SkipStub

        return content_class(
            content=content,
            metadata=metadata,
            settings=self.settings,
            source_path=path,
            context=context,
        )

    def check_file(self, source_path: str) -> None:
        """Log a warning if a file is processed by a disabled reader."""
        reader = self.disabled_readers.get(file_suffix(source_path), None)
        if reader:
            logger.warning(f"{source_path}: {reader.disabled_message()}")


def find_empty_alt(content, path):
    """Find images with empty alt

    Create warnings for all images with empty alt (up to a certain number),
    as they are really likely to be accessibility flaws.

    """
    imgs = re.compile(
        r"""
        (?:
            # src before alt
            <img
            [^\>]*
            src=(['"])(.*?)\1
            [^\>]*
            alt=(['"])\3
        )|(?:
            # alt before src
            <img
            [^\>]*
            alt=(['"])\4
            [^\>]*
            src=(['"])(.*?)\5
        )
        """,
        re.X,
    )
    for match in re.findall(imgs, content):
        logger.warning(
            "Empty alt attribute for image %s in %s",
            os.path.basename(match[1] + match[5]),
            path,
            extra={"limit_msg": "Other images have empty alt attributes"},
        )


def default_metadata(settings=None, process=None):
    metadata = {}
    if settings:
        for name, value in dict(settings.get("DEFAULT_METADATA", {})).items():
            if process:
                value = process(name, value)
            metadata[name] = value
        if "DEFAULT_CATEGORY" in settings:
            value = settings["DEFAULT_CATEGORY"]
            if process:
                value = process("category", value)
            metadata["category"] = value
        if settings.get("DEFAULT_DATE", None) and settings["DEFAULT_DATE"] != "fs":
            if isinstance(settings["DEFAULT_DATE"], str):
                metadata["date"] = get_date(settings["DEFAULT_DATE"])
            else:
                metadata["date"] = datetime.datetime(*settings["DEFAULT_DATE"])
    return metadata


def path_metadata(full_path, source_path, settings=None):
    metadata = {}
    if settings:
        if settings.get("DEFAULT_DATE", None) == "fs":
            metadata["date"] = datetime.datetime.fromtimestamp(
                os.stat(full_path).st_mtime
            )
            metadata["modified"] = metadata["date"]

        # Apply EXTRA_PATH_METADATA for the source path and the paths of any
        # parent directories. Sorting EPM first ensures that the most specific
        # path wins conflicts.

        epm = settings.get("EXTRA_PATH_METADATA", {})
        for path, meta in sorted(epm.items()):
            # Enforce a trailing slash when checking for parent directories.
            # This prevents false positives when one file or directory's name
            # is a prefix of another's.
            dirpath = posixize_path(os.path.join(path, ""))
            if source_path == path or source_path.startswith(dirpath):
                metadata.update(meta)

    return metadata


def parse_path_metadata(source_path, settings=None, process=None):
    r"""Extract a metadata dictionary from a file's path

    >>> import pprint
    >>> settings = {
    ...     'FILENAME_METADATA': r'(?P<slug>[^.]*).*',
    ...     'PATH_METADATA':
    ...         r'(?P<category>[^/]*)/(?P<date>\d{4}-\d{2}-\d{2})/.*',
    ...     }
    >>> reader = BaseReader(settings=settings)
    >>> metadata = parse_path_metadata(
    ...     source_path='my-cat/2013-01-01/my-slug.html',
    ...     settings=settings,
    ...     process=reader.process_metadata)
    >>> pprint.pprint(metadata)  # doctest: +ELLIPSIS
    {'category': <pelican.urlwrappers.Category object at ...>,
     'date': datetime.datetime(2013, 1, 1, 0, 0),
     'slug': 'my-slug'}
    """
    metadata = {}
    dirname, basename = os.path.split(source_path)
    base, ext = os.path.splitext(basename)
    subdir = os.path.basename(dirname)
    if settings:
        checks = []
        for key, data in [("FILENAME_METADATA", base), ("PATH_METADATA", source_path)]:
            checks.append((settings.get(key, None), data))
        if settings.get("USE_FOLDER_AS_CATEGORY", None):
            checks.append(("(?P<category>.*)", subdir))
        for regexp, data in checks:
            if regexp and data:
                match = re.match(regexp, data)
                if match:
                    # .items() for py3k compat.
                    for k, v in match.groupdict().items():
                        k = k.lower()  # metadata must be lowercase
                        if v is not None and k not in metadata:
                            if process:
                                v = process(k, v)
                            metadata[k] = v
    return metadata
