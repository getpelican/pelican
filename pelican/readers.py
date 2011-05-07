# -*- coding: utf-8 -*-
try:
    from docutils import core

    # import the directives to have pygments support
    from pelican import rstdirectives
except ImportError:
    core = False
try:
    from markdown import Markdown
except ImportError:
    Markdown = False
import re

from pelican.utils import get_date, open


_METADATAS_PROCESSORS = {
    'tags': lambda x: map(unicode.strip, x.split(',')),
    'date': lambda x: get_date(x),
    'status': unicode.strip,
}


class Reader(object):
    enabled = True

class RstReader(Reader):
    enabled = bool(core)
    extension = "rst"

    def _parse_metadata(self, content):
        """Return the dict containing metadatas"""
        output = {}
        for m in re.compile('^:([a-z]+): (.*)\s', re.M).finditer(content):
            name, value = m.group(1).lower(), m.group(2)
            output[name] = _METADATAS_PROCESSORS.get(
                name, lambda x:x
            )(value)
        return output

    def read(self, filename):
        """Parse restructured text"""
        text = open(filename)
        metadatas = self._parse_metadata(text)
        extra_params = {'input_encoding': 'unicode',
                        'initial_header_level': '2'}
        rendered_content = core.publish_parts(text,
                                              source_path=filename,
                                              writer_name='html',
                                              settings_overrides=extra_params)
        title = rendered_content.get('title')
        content = rendered_content.get('body')
        if not metadatas.has_key('title'):
            metadatas['title'] = title
        return content, metadatas

class MarkdownReader(Reader):
    enabled = bool(Markdown)
    extension = "md"

    def read(self, filename):
        """Parse content and metadata of markdown files"""
        text = open(filename)
        md = Markdown(extensions = ['meta', 'codehilite'])
        content = md.convert(text)
        
        metadatas = {}
        for name, value in md.Meta.items():
            name = name.lower()
            metadatas[name] = _METADATAS_PROCESSORS.get(
                name, lambda x:x
            )(value[0])
        return content, metadatas


class HtmlReader(Reader):
    extension = "html"
    _re = re.compile('\<\!\-\-\#\s?[A-z0-9_-]*\s?\:s?[A-z0-9\s_-]*\s?\-\-\>')

    def read(self, filename):
        """Parse content and metadata of (x)HTML files"""
        content = open(filename)
        metadatas = {'title':'unnamed'}
        for i in self._re.findall(content):
            key = i.split(':')[0][5:].strip()
            value = i.split(':')[-1][:-3].strip()
            metadatas[key.lower()] = value

        return content, metadatas



_EXTENSIONS = dict((cls.extension, cls) for cls in Reader.__subclasses__())

def read_file(filename, fmt=None):
    """Return a reader object using the given format."""
    if not fmt:
        fmt = filename.split('.')[-1]
    if fmt not in _EXTENSIONS.keys():
        raise TypeError('Pelican does not know how to parse %s' % filename)
    reader = _EXTENSIONS[fmt]()
    if not reader.enabled:
        raise ValueError("Missing dependencies for %s" % fmt)
    return reader.read(filename)
