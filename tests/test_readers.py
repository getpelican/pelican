# coding: utf-8

import datetime
import os

from pelican import readers
from .support import unittest

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
            'summary': u'<p class="first last">Multi-line metadata should be'\
                       u' supported\nas well as <strong>inline'\
                       u' markup</strong>.</p>\n',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
            'custom_field': 'http://notmyidea.org',
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
                   "&quot;typogrify&quot;.</p>\n<p>Now with added "\
                   'support for <abbr title="three letter acronym">'\
                   'TLA</abbr>.</p>\n'

        self.assertEqual(content, expected)

        try:
            # otherwise, typogrify should be applied
            content, _ = readers.read_file(_filename('article.rst'),
                                           settings={'TYPOGRIFY': True})
            expected = u"<p>This is some content. With some stuff to&nbsp;"\
                       "&#8220;typogrify&#8221;.</p>\n<p>Now with added "\
                       'support for <abbr title="three letter acronym">'\
                       '<span class="caps">TLA</span></abbr>.</p>\n'

            self.assertEqual(content, expected)
        except ImportError:
            return unittest.skip('need the typogrify distribution')


class MdReaderTest(unittest.TestCase):

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_md_extention(self):
        # test to ensure the md extension is being processed by the correct reader
        reader = readers.MarkdownReader({})
        content, metadata = reader.read(_filename('article_with_md_extension.md'))
        expected = "<h1>Test Markdown File Header</h1>\n"\
                "<h2>Used for pelican test</h2>\n"\
                "<p>The quick brown fox jumped over the lazy dog's back.</p>"
        
        self.assertEqual(content, expected)

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_mkd_extension(self):
        # test to ensure the mkd extension is being processed by the correct reader
        reader = readers.MarkdownReader({})
        content, metadata = reader.read(_filename('article_with_mkd_extension.mkd'))
        expected = "<h1>Test Markdown File Header</h1>\n"\
                "<h2>Used for pelican test</h2>\n"\
                "<p>This is another markdown test file.  Uses the mkd extension.</p>"
        
        self.assertEqual(content, expected)

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_markdown_markup_extension(self):
        # test to ensure the markdown markup extension is being processed as expected
        reader = readers.MarkdownReader({})
        reader.settings.update(dict(MARKDOWN_EXTENTIONS=['toc']))
        content, metadata = reader.read(_filename('article_with_markdown_markup_extentions.md'))
        expected = '<div class="toc">\n'\
            '<ul>\n'\
            '<li><a href="#level1">Level1</a><ul>\n'\
            '<li><a href="#level2">Level2</a></li>\n'\
            '</ul>\n'\
            '</li>\n'\
            '</ul>\n'\
            '</div>\n'\
            '<h2 id="level1">Level1</h2>\n'\
            '<h3 id="level2">Level2</h3>'

        self.assertEqual(content, expected)
