# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import re

from pelican.tools.pelican_import import wp2fields, fields2pelican, decode_wp_content
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
        for title, content, fname, date, author, categ, tags, format in self.posts:
            self.assertTrue(title.strip())

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
        self.assertTrue(len(test_posts) == 1)

        post = test_posts[0]
        title = post[0]
        self.assertTrue(title, "A normal post with some <html> entities in the"
                               " title. You can't miss them.")
        self.assertTrue('&' not in title)

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
