# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re
try:
    import docutils
    import docutils.core
    import docutils.io
    from docutils.writers.html4css1 import HTMLTranslator

    # import the directives to have pygments support
    from pelican import rstdirectives  # NOQA
except ImportError:
    core = False
try:
    from markdown import Markdown
except ImportError:
    Markdown = False  # NOQA
try:
    from asciidocapi import AsciiDocAPI
    asciidoc = True
except ImportError:
    asciidoc = False
try:
    from html import escape
except ImportError:
    from cgi import escape
try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

from pelican.contents import Category, Tag, Author
from pelican.utils import get_date, pelican_open


METADATA_PROCESSORS = {
    'tags': lambda x, y: [Tag(tag, y) for tag in x.split(',')],
    'date': lambda x, y: get_date(x),
    'status': lambda x, y: x.strip(),
    'category': Category,
    'author': Author,
}


class Reader(object):
    enabled = True
    file_extensions = ['static']
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


class _FieldBodyTranslator(HTMLTranslator):

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.compact_p = None

    def astext(self):
        return ''.join(self.body)

    def visit_field_body(self, node):
        pass

    def depart_field_body(self, node):
        pass


def render_node_to_html(document, node):
    visitor = _FieldBodyTranslator(document)
    node.walkabout(visitor)
    return visitor.astext()


class PelicanHTMLTranslator(HTMLTranslator):

    def visit_abbreviation(self, node):
        attrs = {}
        if node.hasattr('explanation'):
            attrs['title'] = node['explanation']
        self.body.append(self.starttag(node, 'abbr', '', **attrs))

    def depart_abbreviation(self, node):
        self.body.append('</abbr>')


class RstReader(Reader):
    enabled = bool(docutils)
    file_extensions = ['rst']

    def _parse_metadata(self, document):
        """Return the dict containing document metadata"""
        output = {}
        for docinfo in document.traverse(docutils.nodes.docinfo):
            for element in docinfo.children:
                if element.tagname == 'field':  # custom fields (e.g. summary)
                    name_elem, body_elem = element.children
                    name = name_elem.astext()
                    if name == 'summary':
                        value = render_node_to_html(document, body_elem)
                    else:
                        value = body_elem.astext()
                else:  # standard fields (e.g. address)
                    name = element.tagname
                    value = element.astext()
                name = name.lower()

                output[name] = self.process_metadata(name, value)
        return output

    def _get_publisher(self, source_path):
        extra_params = {'initial_header_level': '2',
                        'syntax_highlight': 'short',
                        'input_encoding': 'utf-8'}
        pub = docutils.core.Publisher(
            destination_class=docutils.io.StringOutput)
        pub.set_components('standalone', 'restructuredtext', 'html')
        pub.writer.translator_class = PelicanHTMLTranslator
        pub.process_programmatic_settings(None, extra_params, None)
        pub.set_source(source_path=source_path)
        pub.publish()
        return pub

    def read(self, source_path):
        """Parses restructured text"""
        pub = self._get_publisher(source_path)
        parts = pub.writer.parts
        content = parts.get('body')

        metadata = self._parse_metadata(pub.document)
        metadata.setdefault('title', parts.get('title'))

        return content, metadata


class MarkdownReader(Reader):
    enabled = bool(Markdown)
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']
    default_extensions = ['codehilite(css_class=highlight)', 'extra']

    def __init__(self, *args, **kwargs):
        super(MarkdownReader, self).__init__(*args, **kwargs)
        self.extensions = self.settings.get('MD_EXTENSIONS',
                                            self.default_extensions)
        self.extensions.append('meta')
        self._md = Markdown(extensions=self.extensions)

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        output = {}
        for name, value in meta.items():
            name = name.lower()
            if name == "summary":
                summary_values = "\n".join(value)
                summary = self._md.convert(summary_values)
                output[name] = self.process_metadata(name, summary)
            else:
                output[name] = self.process_metadata(name, value[0])
        return output

    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        with pelican_open(source_path) as text:
            content = self._md.convert(text)

        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata


class HTMLReader(Reader):
    """Parses HTML files as input, looking for meta, title, and body tags"""
    file_extensions = ['htm', 'html']
    enabled = True

    class _HTMLParser(HTMLParser):
        def __init__(self, settings):
            HTMLParser.__init__(self)
            self.body = ''
            self.metadata = {}
            self.settings = settings

            self._data_buffer = ''

            self._in_top_level = True
            self._in_head = False
            self._in_title = False
            self._in_body = False
            self._in_tags = False

        def handle_starttag(self, tag, attrs):
            if tag == 'head' and self._in_top_level:
                self._in_top_level = False
                self._in_head = True
            elif tag == 'title' and self._in_head:
                self._in_title = True
                self._data_buffer = ''
            elif tag == 'body' and self._in_top_level:
                self._in_top_level = False
                self._in_body = True
                self._data_buffer = ''
            elif tag == 'meta' and self._in_head:
                self._handle_meta_tag(attrs)

            elif self._in_body:
                self._data_buffer += self.build_tag(tag, attrs, False)

        def handle_endtag(self, tag):
            if tag == 'head':
                if self._in_head:
                    self._in_head = False
                    self._in_top_level = True
            elif tag == 'title':
                self._in_title = False
                self.metadata['title'] = self._data_buffer
            elif tag == 'body':
                self.body = self._data_buffer
                self._in_body = False
                self._in_top_level = True
            elif self._in_body:
                self._data_buffer += '</{}>'.format(escape(tag))

        def handle_startendtag(self, tag, attrs):
            if tag == 'meta' and self._in_head:
                self._handle_meta_tag(attrs)
            if self._in_body:
                self._data_buffer += self.build_tag(tag, attrs, True)

        def handle_comment(self, data):
            self._data_buffer += '<!--{}-->'.format(data)

        def handle_data(self, data):
            self._data_buffer += data

        def handle_entityref(self, data):
            self._data_buffer += '&{};'.format(data)

        def handle_charref(self, data):
            self._data_buffer += '&#{};'.format(data)

        def build_tag(self, tag, attrs, close_tag):
            result = '<{}'.format(escape(tag))
            for k, v in attrs:
                result += ' ' + escape(k)
                if v is not None:
                    result += '="{}"'.format(escape(v))
            if close_tag:
                return result + ' />'
            return result + '>'

        def _handle_meta_tag(self, attrs):
            name = self._attr_value(attrs, 'name').lower()
            contents = self._attr_value(attrs, 'contents', '')

            if name == 'keywords':
                name = 'tags'
            self.metadata[name] = contents

        @classmethod
        def _attr_value(cls, attrs, name, default=None):
            return next((x[1] for x in attrs if x[0] == name), default)

    def read(self, filename):
        """Parse content and metadata of HTML files"""
        with pelican_open(filename) as content:
            parser = self._HTMLParser(self.settings)
            parser.feed(content)
            parser.close()

        metadata = {}
        for k in parser.metadata:
            metadata[k] = self.process_metadata(k, parser.metadata[k])
        return parser.body, metadata


class AsciiDocReader(Reader):
    enabled = bool(asciidoc)
    file_extensions = ['asc']
    default_options = ["--no-header-footer", "-a newline=\\n"]

    def read(self, source_path):
        """Parse content and metadata of asciidoc files"""
        from cStringIO import StringIO
        with pelican_open(source_path) as source:
            text = StringIO(source)
        content = StringIO()
        ad = AsciiDocAPI()

        options = self.settings.get('ASCIIDOC_OPTIONS', [])
        if isinstance(options, (str, unicode)):
            options = [m.strip() for m in options.split(',')]
        options = self.default_options + options
        for o in options:
            ad.options(*o.split())

        ad.execute(text, content, backend="html4")
        content = content.getvalue()

        metadata = {}
        for name, value in ad.asciidoc.document.attributes.items():
            name = name.lower()
            metadata[name] = self.process_metadata(name, value)
        if 'doctitle' in metadata:
            metadata['title'] = metadata['doctitle']
        return content, metadata


EXTENSIONS = {}

for cls in [Reader] + Reader.__subclasses__():
    for ext in cls.file_extensions:
        EXTENSIONS[ext] = cls


def read_file(path, fmt=None, settings=None):
    """Return a reader object using the given format."""
    base, ext = os.path.splitext(os.path.basename(path))
    if not fmt:
        fmt = ext[1:]

    if fmt not in EXTENSIONS:
        raise TypeError('Pelican does not know how to parse {}'.format(path))

    reader = EXTENSIONS[fmt](settings)
    settings_key = '%s_EXTENSIONS' % fmt.upper()

    if settings and settings_key in settings:
        reader.extensions = settings[settings_key]

    if not reader.enabled:
        raise ValueError("Missing dependencies for %s" % fmt)

    metadata = parse_path_metadata(
        path=path, settings=settings, process=reader.process_metadata)
    content, reader_metadata = reader.read(path)
    metadata.update(reader_metadata)

    # eventually filter the content with typogrify if asked so
    if content and settings and settings.get('TYPOGRIFY'):
        from typogrify.filters import typogrify
        content = typogrify(content)
        metadata['title'] = typogrify(metadata['title'])

    return content, metadata

def parse_path_metadata(path, settings=None, process=None):
    """Extract a metadata dictionary from a file's path

    >>> import pprint
    >>> settings = {
    ...     'FILENAME_METADATA': '(?P<slug>[^.]*).*',
    ...     'PATH_METADATA':
    ...         '(?P<category>[^/]*)/(?P<date>\d{4}-\d{2}-\d{2})/.*',
    ...     }
    >>> reader = Reader(settings=settings)
    >>> metadata = parse_path_metadata(
    ...     path='my-cat/2013-01-01/my-slug.html',
    ...     settings=settings,
    ...     process=reader.process_metadata)
    >>> pprint.pprint(metadata)  # doctest: +ELLIPSIS
    {'category': <pelican.urlwrappers.Category object at ...>,
     'date': datetime.datetime(2013, 1, 1, 0, 0),
     'slug': 'my-slug'}
    """
    metadata = {}
    base, ext = os.path.splitext(os.path.basename(path))
    if settings:
        for key,data in [('FILENAME_METADATA', base),
                         ('PATH_METADATA', path),
                         ]:
            regexp = settings.get(key)
            if regexp:
                match = re.match(regexp, data)
                if match:
                    # .items() for py3k compat.
                    for k, v in match.groupdict().items():
                        if k not in metadata:
                            k = k.lower()  # metadata must be lowercase
                            if process:
                                v = process(k, v)
                            metadata[k] = v
    return metadata
