# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import codecs
import datetime
import logging
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
import re

from pelican.contents import Page, Category, Tag, Author
from pelican.utils import get_date, pelican_open


logger = logging.getLogger(__name__)


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


class RawReader(Reader):
    enabled = True
    file_extensions = ['raw']

    def read(self, source_path, encoding=None):
        "Read file contents into .content without processing"
        if not encoding:
            encoding = self.settings.get('CONTENT_ENCODING', None)
        if encoding:
            content = codecs.open(source_path, 'r', encoding=encoding).read()
        else:
            content = open(source_path, 'rb').read()
        metadata = {}
        return content, metadata


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
        extra_params = {'initial_header_level': '2'}
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

    def read(self, source_path):
        """Parse content and metadata of markdown files"""
        text = pelican_open(source_path)
        md = Markdown(extensions=set(self.extensions + ['meta']))
        content = md.convert(text)

        metadata = self._parse_metadata(md.Meta)
        return content, metadata


class HtmlReader(Reader):
    file_extensions = ['html', 'htm']
    _re = re.compile('\<\!\-\-\#\s?[A-z0-9_-]*\s?\:s?[A-z0-9\s_-]*\s?\-\-\>')

    def read(self, source_path):
        """Parse content and metadata of (x)HTML files"""
        with open(source_path) as content:
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

    def read(self, source_path):
        """Parse content and metadata of asciidoc files"""
        from cStringIO import StringIO
        text = StringIO(pelican_open(source_path))
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

for cls in [Reader] + Reader.__subclasses__():
    for ext in cls.file_extensions:
        _EXTENSIONS[ext] = cls


def read_file(base_path, path, content_class=Page, fmt=None,
              settings=None, context=None,
              preread_signal=None, preread_sender=None,
              context_signal=None, context_sender=None):
    """Return a content object parsed with the given format."""
    path = os.path.abspath(os.path.join(base_path, path))
    source_path = os.path.relpath(path, base_path)
    base, ext = os.path.splitext(os.path.basename(path))
    if not fmt:
        fmt = ext[1:]

    logger.debug(
        'read file {} -> {}'.format(source_path, content_class.__name__))

    if preread_signal:
        logger.debug(
            'signal {}.send({})'.format(preread_signal, preread_sender))
        preread_signal.send(preread_sender)

    if fmt not in _EXTENSIONS:
        raise TypeError('Pelican does not know how to parse {}'.format(path))

    reader = _EXTENSIONS[fmt](settings)
    settings_key = '%s_EXTENSIONS' % fmt.upper()

    if settings and settings_key in settings:
        reader.extensions = settings[settings_key]

    if not reader.enabled:
        raise ValueError("Missing dependencies for %s" % fmt)

    metadata = default_metadata(
        settings=settings, process=reader.process_metadata)
    metadata.update(path_metadata(
            full_path=path, source_path=source_path, settings=settings))
    metadata.update(parse_path_metadata(
            source_path=source_path, settings=settings,
            process=reader.process_metadata))
    content, reader_metadata = reader.read(path)
    metadata.update(reader_metadata)

    # eventually filter the content with typogrify if asked so
    if settings and settings.get('TYPOGRIFY'):
        from typogrify.filters import typogrify
        content = typogrify(content)
        metadata['title'] = typogrify(metadata['title'])

    if context_signal:
        logger.debug(
            'signal {}.send({}, <metadata>)'.format(
                context_signal, context_sender))
        context_signal.send(context_sender, metadata=metadata)
    return content_class(
        content=content,
        metadata=metadata,
        settings=settings,
        source_path=path,
        context=context)

def default_metadata(settings=None, process=None):
    metadata = {}
    if settings:
        if 'DEFAULT_CATEGORY' in settings:
            value = settings['DEFAULT_CATEGORY']
            if process:
                value = process('category', value)
            metadata['category'] = value
        if 'DEFAULT_DATE' in settings:
            metadata['date'] = datetime.datetime(*settings['DEFAULT_DATE'])
    return metadata

def path_metadata(full_path, source_path, settings=None):
    metadata = {}
    if settings:
        if settings.get('DEFAULT_DATE', None) == 'fs':
            metadata['date'] = datetime.datetime.fromtimestamp(
                os.stat(full_path).st_ctime)
        metadata.update(settings.get('EXTRA_PATH_METADATA', {}).get(
                source_path, {}))
    return metadata

def parse_path_metadata(source_path, settings=None, process=None):
    metadata = {}
    dirname, basename = os.path.split(source_path)
    base, ext = os.path.splitext(basename)
    subdir = os.path.basename(dirname)
    if settings:
        checks = []
        for key,data in [('FILENAME_METADATA', base),
                         ('PATH_METADATA', source_path),
                         ]:
            checks.append((settings.get(key, None), data))
        if settings.get('USE_FOLDER_AS_CATEGORY', None):
            checks.insert(0, ('(?P<category>.*)', subdir))
        for regexp,data in checks:
            if regexp and data:
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
