# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import datetime
import os

from pelican import readers
from pelican.tests.support import unittest

CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, 'content')


def _path(*args):
    return os.path.join(CONTENT_PATH, *args)


class RstReaderTest(unittest.TestCase):

    def test_article_with_metadata(self):
        reader = readers.RstReader({})
        content, metadata = reader.read(_path('article_with_metadata.rst'))
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'title': 'This is a super article !',
            'summary': '<p class="first last">Multi-line metadata should be'
                       ' supported\nas well as <strong>inline'
                       ' markup</strong>.</p>\n',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
            'custom_field': 'http://notmyidea.org',
        }

        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

    def test_article_with_filename_metadata(self):
        content, metadata = readers.read_file(
                _path('2012-11-29_rst_w_filename_meta#foo-bar.rst'),
                settings={})
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'title': 'Rst with filename metadata',
        }
        for key, value in metadata.items():
            self.assertEqual(value, expected[key], key)

        content, metadata = readers.read_file(
                _path('2012-11-29_rst_w_filename_meta#foo-bar.rst'),
                settings={
                    'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2}).*'
                    })
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'title': 'Rst with filename metadata',
            'date': datetime.datetime(2012, 11, 29),
        }
        for key, value in metadata.items():
            self.assertEqual(value, expected[key], key)

        content, metadata = readers.read_file(
                _path('2012-11-29_rst_w_filename_meta#foo-bar.rst'),
                settings={
                    'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2})_'
                                         '_(?P<Slug>.*)'
                                         '#(?P<MyMeta>.*)-(?P<author>.*)'
                    })
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'title': 'Rst with filename metadata',
            'date': datetime.datetime(2012, 11, 29),
            'slug': 'article_with_filename_metadata',
            'mymeta': 'foo',
        }
        for key, value in metadata.items():
            self.assertEqual(value, expected[key], key)

    def test_article_metadata_key_lowercase(self):
        # Keys of metadata should be lowercase.
        reader = readers.RstReader({})
        content, metadata = reader.read(
                _path('article_with_uppercase_metadata.rst'))

        self.assertIn('category', metadata, 'Key should be lowercase.')
        self.assertEqual('Yeah', metadata.get('category'),
                          'Value keeps case.')

    def test_typogrify(self):
        # if nothing is specified in the settings, the content should be
        # unmodified
        content, _ = readers.read_file(_path('article.rst'))
        expected = ('<p>This is some content. With some stuff to '
                    '&quot;typogrify&quot;.</p>\n<p>Now with added '
                    'support for <abbr title="three letter acronym">'
                    'TLA</abbr>.</p>\n')

        self.assertEqual(content, expected)

        try:
            # otherwise, typogrify should be applied
            content, _ = readers.read_file(_path('article.rst'),
                                           settings={'TYPOGRIFY': True})
            expected = ('<p>This is some content. With some stuff to&nbsp;'
                        '&#8220;typogrify&#8221;.</p>\n<p>Now with added '
                        'support for <abbr title="three letter acronym">'
                        '<span class="caps">TLA</span></abbr>.</p>\n')

            self.assertEqual(content, expected)
        except ImportError:
            return unittest.skip('need the typogrify distribution')


class MdReaderTest(unittest.TestCase):

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_metadata(self):
        reader = readers.MarkdownReader({})
        content, metadata = reader.read(
            _path('article_with_md_extension.md'))
        expected = {
            'category': 'test',
            'title': 'Test md File',
            'summary': '<p>I have a lot to test</p>',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
        }
        for key, value in metadata.items():
            self.assertEqual(value, expected[key], key)

        content, metadata = reader.read(
            _path('article_with_markdown_and_nonascii_summary.md'))
        expected = {
            'title': 'マックOS X 10.8でパイソンとVirtualenvをインストールと設定',
            'summary': '<p>パイソンとVirtualenvをまっくでインストールする方法について明確に説明します。</p>',
            'category': '指導書',
            'date': datetime.datetime(2012, 12, 20),
            'tags': ['パイソン', 'マック'],
            'slug': 'python-virtualenv-on-mac-osx-mountain-lion-10.8',
        }
        for key, value in metadata.items():
            self.assertEqual(value, expected[key], key)

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_file_extensions(self):
        reader = readers.MarkdownReader({})
        # test to ensure the md file extension is being processed by the
        # correct reader
        content, metadata = reader.read(
            _path('article_with_md_extension.md'))
        expected = (
                "<h1>Test Markdown File Header</h1>\n"
                "<h2>Used for pelican test</h2>\n"
                "<p>The quick brown fox jumped over the lazy dog's back.</p>")
        self.assertEqual(content, expected)
        # test to ensure the mkd file extension is being processed by the
        # correct reader
        content, metadata = reader.read(
            _path('article_with_mkd_extension.mkd'))
        expected = ("<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
                    " test</h2>\n<p>This is another markdown test file.  Uses"
                    " the mkd extension.</p>")
        self.assertEqual(content, expected)
        # test to ensure the markdown file extension is being processed by the
        # correct reader
        content, metadata = reader.read(
            _path('article_with_markdown_extension.markdown'))
        expected = ("<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
                    " test</h2>\n<p>This is another markdown test file.  Uses"
                    " the markdown extension.</p>")
        self.assertEqual(content, expected)
        # test to ensure the mdown file extension is being processed by the
        # correct reader
        content, metadata = reader.read(
            _path('article_with_mdown_extension.mdown'))
        expected = ("<h1>Test Markdown File Header</h1>\n<h2>Used for pelican"
                    " test</h2>\n<p>This is another markdown test file.  Uses"
                    " the mdown extension.</p>")
        self.assertEqual(content, expected)

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_markdown_markup_extension(self):
        # test to ensure the markdown markup extension is being processed as
        # expected
        content, metadata = readers.read_file(
                _path('article_with_markdown_markup_extensions.md'),
                settings={'MD_EXTENSIONS': ['toc', 'codehilite', 'extra']})
        expected = ('<div class="toc">\n'
                    '<ul>\n'
                    '<li><a href="#level1">Level1</a><ul>\n'
                    '<li><a href="#level2">Level2</a></li>\n'
                    '</ul>\n'
                    '</li>\n'
                    '</ul>\n'
                    '</div>\n'
                    '<h2 id="level1">Level1</h2>\n'
                    '<h3 id="level2">Level2</h3>')

        self.assertEqual(content, expected)

    @unittest.skipUnless(readers.Markdown, "markdown isn't installed")
    def test_article_with_filename_metadata(self):
        content, metadata = readers.read_file(
                _path('2012-11-30_md_w_filename_meta#foo-bar.md'),
                settings={})
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
        }
        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

        content, metadata = readers.read_file(
                _path('2012-11-30_md_w_filename_meta#foo-bar.md'),
                settings={
                    'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2}).*'
                    })
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'date': datetime.datetime(2012, 11, 30),
        }
        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

        content, metadata = readers.read_file(
                _path('2012-11-30_md_w_filename_meta#foo-bar.md'),
                settings={
                    'FILENAME_METADATA': '(?P<date>\d{4}-\d{2}-\d{2})'
                                         '_(?P<Slug>.*)'
                                         '#(?P<MyMeta>.*)-(?P<author>.*)'
                    })
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'date': datetime.datetime(2012, 11, 30),
            'slug': 'md_w_filename_meta',
            'mymeta': 'foo',
        }
        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)


class AdReaderTest(unittest.TestCase):

    @unittest.skipUnless(readers.asciidoc, "asciidoc isn't installed")
    def test_article_with_asc_extension(self):
        # Ensure the asc extension is being processed by the correct reader
        reader = readers.AsciiDocReader({})
        content, metadata = reader.read(
                                _path('article_with_asc_extension.asc'))
        expected = ('<hr>\n<h2><a name="_used_for_pelican_test">'
                    '</a>Used for pelican test</h2>\n'
                    '<p>The quick brown fox jumped over'
                    ' the lazy dog&#8217;s back.</p>\n')
        self.assertEqual(content, expected)
        expected = {
            'category': 'Blog',
            'author': 'Author O. Article',
            'title': 'Test AsciiDoc File Header',
            'date': datetime.datetime(2011, 9, 15, 9, 5),
            'tags': ['Linux', 'Python', 'Pelican'],
        }

        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

        expected = {
            'category': 'Blog',
            'author': 'Author O. Article',
            'title': 'Test AsciiDoc File Header',
            'date': datetime.datetime(2011, 9, 15, 9, 5),
            'tags': ['Linux', 'Python', 'Pelican'],
        }

        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

    @unittest.skipUnless(readers.asciidoc, "asciidoc isn't installed")
    def test_article_with_asc_options(self):
        # test to ensure the ASCIIDOC_OPTIONS is being used
        reader = readers.AsciiDocReader(
                dict(ASCIIDOC_OPTIONS=["-a revision=1.0.42"]))
        content, metadata = reader.read(_path('article_with_asc_options.asc'))
        expected = ('<hr>\n<h2><a name="_used_for_pelican_test"></a>Used for'
                    ' pelican test</h2>\n<p>version 1.0.42</p>\n'
                    '<p>The quick brown fox jumped over the lazy'
                    ' dog&#8217;s back.</p>\n')
        self.assertEqual(content, expected)


class HTMLReaderTest(unittest.TestCase):
    def test_article_with_comments(self):
        reader = readers.HTMLReader({})
        content, metadata = reader.read(_path('article_with_comments.html'))

        self.assertEqual('''
        Body content
        <!--  This comment is included (including extra whitespace)   -->
    ''', content)

    def test_article_with_keywords(self):
        reader = readers.HTMLReader({})
        content, metadata = reader.read(_path('article_with_keywords.html'))
        expected = {
            'tags': ['foo', 'bar', 'foobar'],
        }

        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

    def test_article_with_metadata(self):
        reader = readers.HTMLReader({})
        content, metadata = reader.read(_path('article_with_metadata.html'))
        expected = {
            'category': 'yeah',
            'author': 'Alexis Métaireau',
            'title': 'This is a super article !',
            'summary': 'Summary and stuff',
            'date': datetime.datetime(2010, 12, 2, 10, 14),
            'tags': ['foo', 'bar', 'foobar'],
            'custom_field': 'http://notmyidea.org',
        }

        for key, value in expected.items():
            self.assertEqual(value, metadata[key], key)

    def test_article_with_null_attributes(self):
        reader = readers.HTMLReader({})
        content, metadata = reader.read(
                _path('article_with_null_attributes.html'))

        self.assertEqual('''
        Ensure that empty attributes are copied properly.
        <input name="test" disabled style="" />
    ''', content)

    def test_article_metadata_key_lowercase(self):
        # Keys of metadata should be lowercase.
        reader = readers.HTMLReader({})
        content, metadata = reader.read(
                _path('article_with_uppercase_metadata.html'))
        self.assertIn('category', metadata, 'Key should be lowercase.')
        self.assertEqual('Yeah', metadata.get('category'),
                          'Value keeps cases.')
