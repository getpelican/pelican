# coding: utf-8
try:
    import unittest2 as unittest
except ImportError, e:
    import unittest

import datetime
import os

from pelican import readers

CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, 'content')


def _filename(*args):
    return os.path.join(CONTENT_PATH, *args)


class RstReaderTest(unittest.TestCase):

    def test_article_with_metadata(self):
        reader = readers.RstReader({})
        content, metadata = reader.read(_filename('article_with_metadata.rst'))
        expected = {
            'category': 'yeah',
            'author': u'Alexis Métaireau',
            'title': 'This is a super article !',
            'summary': 'Multi-line metadata should be supported\nas well as <strong>inline markup</strong>.',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
        }

        for key, value in expected.items():
            self.assertEquals(value, metadata[key], key)

    def test_article_metadata_key_lowercase(self):
        """Keys of metadata should be lowercase."""
        reader = readers.RstReader({})
        content, metadata = reader.read(_filename('article_with_uppercase_metadata.rst'))

        self.assertIn('category', metadata, "Key should be lowercase.")
        self.assertEquals('Yeah', metadata.get('category'), "Value keeps cases.")

    def test_typogrify(self):
        # if nothing is specified in the settings, the content should be
        # unmodified
        content, _ = readers.read_file(_filename('article.rst'))
        expected = "<p>This is some content. With some stuff to "\
                   "&quot;typogrify&quot;.</p>\n"

        self.assertEqual(content, expected)

        # otherwise, typogrify should be applied
        content, _ = readers.read_file(_filename('article.rst'),
                                       settings={'TYPOGRIFY': True})
        expected = "<p>This is some content. With some stuff to&nbsp;"\
                   "&#8220;typogrify&#8221;.</p>\n"

        self.assertEqual(content, expected)
