# coding: utf-8
try:
    import unittest2
except ImportError, e:
    import unittest as unittest2

import datetime
import os

from pelican import readers

CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, 'content')

def _filename(*args):
    return os.path.join(CONTENT_PATH, *args)


class RstReaderTest(unittest2.TestCase):

    def test_article_with_metadata(self):
        reader = readers.RstReader()
        content, metadata = reader.read(_filename('article_with_metadata.rst'))
        expected = {
            'category': 'yeah',
            'author': u'Alexis Métaireau',
            'title': 'This is a super article !',
            'summary': 'Multi-line metadata should be supported\nas well as <strong>inline markup</strong>.',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
        }
        self.assertDictEqual(metadata, expected)
