from docutils import core
import re

# import the directives to have pygments support
import rstdirectives

from pelican.utils import get_date, open


_METADATAS_FIELDS = {'tags': lambda x: x.split(', '),
                     'date': lambda x: get_date(x),
                     'category': lambda x: x,
                     'author': lambda x: x}


class RstReader(object):

    def _parse_metadata(self, content):
        """Return the dict containing metadatas"""
        output = {}
        for m in re.compile(':([a-z]+): (.*)\s', re.M).finditer(content):
            name, value = m.group(1).lower(), m.group(2)
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

_EXTENSIONS = {'rst': RstReader}  # supported formats


def read_file(filename, fmt=None):
    """Return a reader object using the given format."""
    if not fmt:
        fmt = 'rst'
    if fmt not in _EXTENSIONS.keys():
        raise TypeError('Pelican does not know how to parse %s files' % fmt)
    reader = _EXTENSIONS[fmt]()
    return reader.read(filename)
