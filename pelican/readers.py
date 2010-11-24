from docutils import core
from markdown import Markdown
import re

# import the directives to have pygments support
import rstdirectives

from pelican.utils import get_date, open


_METADATAS_FIELDS = {'tags': lambda x: x.split(', '),
                     'date': lambda x: get_date(x),
                     'category': lambda x: x,
                     'author': lambda x: x,
                     'status': lambda x:x.strip(),}


class RstReader(object):

    def _parse_metadata(self, content):
        """Return the dict containing metadatas"""
        output = {}
        for m in re.compile(':([a-z]+): (.*)\s', re.M).finditer(content):
            name, value = m.group(1).lower(), m.group(2)
            if name in _METADATAS_FIELDS:
                output[name] = _METADATAS_FIELDS[name](value)
        return output

    def read(self, filename):
        """Parse restructured text"""
        text = open(filename)
        metadatas = self._parse_metadata(text)
        extra_params = {'input_encoding': 'unicode',
                        'initial_header_level': '2'}
        rendered_content = core.publish_parts(text, writer_name='html',
                                              settings_overrides=extra_params)
        title = rendered_content.get('title')
        content = rendered_content.get('body')
        if not metadatas.has_key('title'):
            metadatas['title'] = title
        return content, metadatas

class MarkdownReader(object):

    def read(self, filename):
        """Parse content and metadata of markdown files"""
        text = open(filename)
        md = Markdown(extensions = ['meta', 'codehilite'])
        content = md.convert(text)
        
        metadatas = {}
        for name, value in md.Meta.items():
            if name in _METADATAS_FIELDS:
                meta = _METADATAS_FIELDS[name](value[0])
            else:
                meta = value[0]
            metadatas[name.lower()] = meta
        return content, metadatas

_EXTENSIONS = {'rst': RstReader, 'md': MarkdownReader}  # supported formats


def read_file(filename, fmt=None):
    """Return a reader object using the given format."""
    if not fmt:
        fmt = filename.split('.')[-1]
    if fmt not in _EXTENSIONS.keys():
        raise TypeError('Pelican does not know how to parse %s' % filename)
    reader = _EXTENSIONS[fmt]()
    return reader.read(filename)
