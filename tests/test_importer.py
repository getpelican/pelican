# -*- coding: utf-8 -*-

import os

from pelican.tools.pelican_import import wp2fields, fields2pelican
from .support import unittest, temporary_folder, mute

CUR_DIR = os.path.dirname(__file__)
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, 'content', 'wordpressexport.xml')


class TestWordpressXmlImporter(unittest.TestCase):


    def setUp(self):
        self.posts = wp2fields(WORDPRESS_XML_SAMPLE)


    def test_ignore_empty_posts(self):

        posts = list(self.posts)
        self.assertTrue(posts)
        for title, content, fname, date, author, categ, tags, format in posts:
            self.assertTrue(title.strip())


    def test_can_toggle_raw_html_code_parsing(self):

        posts = list(self.posts)
        r = lambda f: open(f).read()
        silent_f2p = mute(True)(fields2pelican)

        with temporary_folder() as temp:

            rst_files = (r(f) for f in silent_f2p(posts, 'markdown', temp))
            self.assertTrue(any('<iframe' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(posts, 'markdown', temp, strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            # no effect in rst
            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp, strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
