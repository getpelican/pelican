# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re

from pelican.tools.pelican_import import wp2fields, fields2pelican, decode_wp_content, build_header
from pelican.tests.support import (unittest, temporary_folder, mute,
                                   skipIfNoExecutable)

CUR_DIR = os.path.dirname(__file__)
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, 'content', 'wordpressexport.xml')
WORDPRESS_ENCODED_CONTENT_SAMPLE = os.path.join(CUR_DIR,
                                                'content',
                                                'wordpress_content_encoded')
WORDPRESS_DECODED_CONTENT_SAMPLE = os.path.join(CUR_DIR,
                                                'content',
                                                'wordpress_content_decoded')

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = False  # NOQA


@skipIfNoExecutable(['pandoc', '--version'])
@unittest.skipUnless(BeautifulSoup, 'Needs BeautifulSoup module')
class TestWordpressXmlImporter(unittest.TestCase):

    def setUp(self):
        self.posts = list(wp2fields(WORDPRESS_XML_SAMPLE))

    def test_ignore_empty_posts(self):
        self.assertTrue(self.posts)
        for title, content, fname, date, author, categ, tags, kind, format in self.posts:
            self.assertTrue(title.strip())

    def test_recognise_page_kind(self):
        """ Check that we recognise pages in wordpress, as opposed to posts """
        self.assertTrue(self.posts)
        # Collect (title, filename, kind) of non-empty posts recognised as page
        pages_data = []
        for title, content, fname, date, author, categ, tags, kind, format in self.posts:
            if kind == 'page':
                pages_data.append((title, fname))
        self.assertEqual(2, len(pages_data))
        self.assertEqual(('Page', 'contact'), pages_data[0])
        self.assertEqual(('Empty Page', 'empty'), pages_data[1])

    def test_dirpage_directive_for_page_kind(self):
        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Empty Page"), self.posts)
        with temporary_folder() as temp:
            fname = list(silent_f2p(test_post, 'markdown', temp, dirpage=True))[0]
            self.assertTrue(fname.endswith('pages%sempty.md' % os.path.sep))

    def test_can_toggle_raw_html_code_parsing(self):
        def r(f):
            with open(f) as infile:
                return infile.read()
        silent_f2p = mute(True)(fields2pelican)

        with temporary_folder() as temp:

            rst_files = (r(f) for f in silent_f2p(self.posts, 'markdown', temp))
            self.assertTrue(any('<iframe' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(self.posts, 'markdown', temp,
                         strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            # no effect in rst
            rst_files = (r(f) for f in silent_f2p(self.posts, 'rst', temp))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(self.posts, 'rst', temp,
                         strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))

    def test_decode_html_entities_in_titles(self):
        test_posts = [post for post in self.posts if post[2] == 'html-entity-test']
        self.assertEqual(len(test_posts), 1)

        post = test_posts[0]
        title = post[0]
        self.assertTrue(title, "A normal post with some <html> entities in the"
                               " title. You can't miss them.")
        self.assertNotIn('&', title)

    def test_decode_wp_content_returns_empty(self):
        """ Check that given an empty string we return an empty string."""
        self.assertEqual(decode_wp_content(""), "")

    def test_decode_wp_content(self):
        """ Check that we can decode a wordpress content string."""
        with open(WORDPRESS_ENCODED_CONTENT_SAMPLE, 'r') as encoded_file:
            encoded_content = encoded_file.read()
            with open(WORDPRESS_DECODED_CONTENT_SAMPLE, 'r') as decoded_file:
                decoded_content = decoded_file.read()
                self.assertEqual(decode_wp_content(encoded_content, br=False), decoded_content)

    def test_preserve_verbatim_formatting(self):
        def r(f):
            with open(f) as infile:
                return infile.read()
        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Code in List"), self.posts)
        with temporary_folder() as temp:
            md = [r(f) for f in silent_f2p(test_post, 'markdown', temp)][0]
            self.assertTrue(re.search(r'\s+a = \[1, 2, 3\]', md))
            self.assertTrue(re.search(r'\s+b = \[4, 5, 6\]', md))

            for_line = re.search(r'\s+for i in zip\(a, b\):', md).group(0)
            print_line = re.search(r'\s+print i', md).group(0)
            self.assertTrue(for_line.rindex('for') < print_line.rindex('print'))

    def test_code_in_list(self):
        def r(f):
            with open(f) as infile:
                return infile.read()
        silent_f2p = mute(True)(fields2pelican)
        test_post = filter(lambda p: p[0].startswith("Code in List"), self.posts)
        with temporary_folder() as temp:
            md = [r(f) for f in silent_f2p(test_post, 'markdown', temp)][0]
            sample_line = re.search(r'-   This is a code sample', md).group(0)
            code_line = re.search(r'\s+a = \[1, 2, 3\]', md).group(0)
            self.assertTrue(sample_line.rindex('This') < code_line.rindex('a'))


class TestBuildHeader(unittest.TestCase):
    def test_build_header(self):
        header = build_header('test', None, None, None, None, None)
        self.assertEqual(header, 'test\n####\n\n')

    def test_build_header_with_east_asian_characters(self):
        header = build_header('これは広い幅の文字だけで構成されたタイトルです',
                None, None, None, None, None)

        self.assertEqual(header,
                'これは広い幅の文字だけで構成されたタイトルです\n' +
                '##############################################\n\n')

