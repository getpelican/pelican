# -*- coding: utf-8 -*-
try:
    import docutils
    import docutils.core
    import docutils.io
    from docutils.writers.html4css1 import HTMLTranslator

    # import the directives to have pygments support
    from pelican import rstdirectives
except ImportError:
    core = False
try:
    from markdown import Markdown
except ImportError:
    Markdown = False
import re

from pelican.contents import Category
from pelican.utils import get_date, open


_METADATA_PROCESSORS = {
    'tags': lambda x: map(unicode.strip, unicode(x).split(',')),
    'date': lambda x: get_date(x),
    'status': unicode.strip,
    'category': Category,
}

def _process_metadata(name, value):
    if name.lower() in _METADATA_PROCESSORS:
        return _METADATA_PROCESSORS[name.lower()](value)
    return value


class Reader(object):
    enabled = True
    extensions = None

class _FieldBodyTranslator(HTMLTranslator):

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

def get_metadata(document):
    """Return the dict containing document metadata"""
    output = {}
    for docinfo in document.traverse(docutils.nodes.docinfo):
        for element in docinfo.children:
            if element.tagname == 'field': # custom fields (e.g. summary)
                name_elem, body_elem = element.children
                name = name_elem.astext()
                value = render_node_to_html(document, body_elem)
            else: # standard fields (e.g. address)
                name = element.tagname
                value = element.astext()

            output[name] = _process_metadata(name, value)
    return output


class RstReader(Reader):
    enabled = bool(docutils)
    extension = "rst"

    def _parse_metadata(self, document):
        return get_metadata(document)

    def _get_publisher(self, filename):
        extra_params = {'initial_header_level': '2'}
        pub = docutils.core.Publisher(destination_class=docutils.io.StringOutput)
        pub.set_components('standalone', 'restructuredtext', 'html')
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
    extension = "md"
    extensions = ['codehilite', 'extra']

    def read(self, filename):
        """Parse content and metadata of markdown files"""
        text = open(filename)
        md = Markdown(extensions=set(self.extensions + ['meta']))
        content = md.convert(text)

        metadata = {}
        for name, value in md.Meta.items():
            name = name.lower()
            metadata[name] = _process_metadata(name, value[0])
        return content, metadata


class HtmlReader(Reader):
    extension = "html"
    _re = re.compile('\<\!\-\-\#\s?[A-z0-9_-]*\s?\:s?[A-z0-9\s_-]*\s?\-\-\>')

    def read(self, filename):
        """Parse content and metadata of (x)HTML files"""
        content = open(filename)
        metadata = {'title':'unnamed'}
        for i in self._re.findall(content):
            key = i.split(':')[0][5:].strip()
            value = i.split(':')[-1][:-3].strip()
            name = key.lower()
            metadata[name] = _process_metadata(name, value)

        return content, metadata



_EXTENSIONS = dict((cls.extension, cls) for cls in Reader.__subclasses__())

def read_file(filename, fmt=None, settings=None):
    """Return a reader object using the given format."""
    if not fmt:
        fmt = filename.split('.')[-1]
    if fmt not in _EXTENSIONS.keys():
        raise TypeError('Pelican does not know how to parse %s' % filename)
    reader = _EXTENSIONS[fmt]()
    settings_key = '%s_EXTENSIONS' % fmt.upper()
    if settings and settings_key in settings:
        reader.extensions = settings[settings_key]
    if not reader.enabled:
        raise ValueError("Missing dependencies for %s" % fmt)
    return reader.read(filename)
