# -*- coding: utf-8 -*-
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

from pelican.contents import Category, Tag, Author
from pelican.utils import get_date, pelican_open


_METADATA_PROCESSORS = {
    'tags': lambda x, y: [Tag(tag, y) for tag in unicode(x).split(',')],
    'date': lambda x, y: get_date(x),
    'status': lambda x, y: unicode.strip(x),
    'category': Category,
    'author': Author,
}


class Reader(object):
    enabled = True
    extensions = None

    def __init__(self, settings):
        self.settings = settings

    def process_metadata(self, name, value):
        if name in _METADATA_PROCESSORS:
            return _METADATA_PROCESSORS[name](value, self.settings)
        return value


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

    def _get_publisher(self, filename):
        extra_params = {'initial_header_level': '2'}
        pub = docutils.core.Publisher(
            destination_class=docutils.io.StringOutput)
        pub.set_components('standalone', 'restructuredtext', 'html')
        pub.writer.translator_class = PelicanHTMLTranslator
        pub.process_programmatic_settings(None, extra_params, None)
        pub.set_source(source_path=filename)
        pub.publish()
        return pub

    def read(self, filename):
        """Parses restructured text"""
        pub = self._get_publisher(filename)
        parts = pub.writer.parts
        content = parts.get('body')

        metadata = self._parse_metadata(pub.document)
        metadata.setdefault('title', parts.get('title'))

        return content, metadata


class MarkdownReader(Reader):
    enabled = bool(Markdown)
    file_extensions = ['md', 'markdown', 'mkd']
    extensions = ['codehilite', 'extra']

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        md = Markdown(extensions=set(self.extensions + ['meta']))
        output = {}
        for name, value in meta.items():
            name = name.lower()
            if name == "summary":
                summary_values = "\n".join(str(item) for item in value)
                summary = md.convert(summary_values)
                output[name] = self.process_metadata(name, summary)
            else:
                output[name] = self.process_metadata(name, value[0])
        return output

    def read(self, filename):
        """Parse content and metadata of markdown files"""
        text = pelican_open(filename)
        md = Markdown(extensions=set(self.extensions + ['meta']))
        content = md.convert(text)

        metadata = self._parse_metadata(md.Meta)
        return content, metadata


class HtmlReader(Reader):
    file_extensions = ['html', 'htm']
    _re = re.compile('\<\!\-\-\#\s?[A-z0-9_-]*\s?\:s?[A-z0-9\s_-]*\s?\-\-\>')

    def read(self, filename):
        """Parse content and metadata of (x)HTML files"""
        with open(filename) as content:
            metadata = {'title': 'unnamed'}
            for i in self._re.findall(content):
                key = i.split(':')[0][5:].strip()
                value = i.split(':')[-1][:-3].strip()
                name = key.lower()
                metadata[name] = self.process_metadata(name, value)

            return content, metadata


class AsciiDocReader(Reader):
    enabled = bool(asciidoc)
    file_extensions = ['asc']
    default_options = ["--no-header-footer", "-a newline=\\n"]

    def read(self, filename):
        """Parse content and metadata of asciidoc files"""
        from cStringIO import StringIO
        text = StringIO(pelican_open(filename))
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


_EXTENSIONS = {}

for cls in Reader.__subclasses__():
    for ext in cls.file_extensions:
        _EXTENSIONS[ext] = cls


def read_file(filename, fmt=None, settings=None):
    """Return a reader object using the given format."""
    base, ext = os.path.splitext(os.path.basename(filename))
    if not fmt:
        fmt = ext[1:]

    if fmt not in _EXTENSIONS:
        raise TypeError('Pelican does not know how to parse %s' % filename)

    reader = _EXTENSIONS[fmt](settings)
    settings_key = '%s_EXTENSIONS' % fmt.upper()

    if settings and settings_key in settings:
        reader.extensions = settings[settings_key]

    if not reader.enabled:
        raise ValueError("Missing dependencies for %s" % fmt)

    content, metadata = reader.read(filename)

    # eventually filter the content with typogrify if asked so
    if settings and settings.get('TYPOGRIFY'):
        from typogrify.filters import typogrify
        content = typogrify(content)
        metadata['title'] = typogrify(metadata['title'])

    filename_metadata = settings and settings.get('FILENAME_METADATA')
    if filename_metadata:
        match = re.match(filename_metadata, base)
        if match:
            for k, v in match.groupdict().iteritems():
                if k not in metadata:
                    k = k.lower()  # metadata must be lowercase
                    metadata[k] = reader.process_metadata(k, v)

    return content, metadata
