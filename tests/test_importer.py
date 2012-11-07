# -*- coding: utf-8 -*-

import os

from pelican.tools.pelican_import import wp2fields, fields2pelican
from .support import unittest, temporary_folder, mute, skipIfNoExecutable

CUR_DIR = os.path.dirname(__file__)
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, 'content', 'wordpressexport.xml')

try:
    import BeautifulSoup
except ImportError:
    BeautifulSoup = False  # NOQA


@skipIfNoExecutable(['pandoc', '--version'])
@unittest.skipUnless(BeautifulSoup, 'Needs BeautifulSoup module')
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
            rst_files = (r(f) for f in silent_f2p(posts, 'markdown', temp,
                         strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            # no effect in rst
            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp,
                         strip_raw=True))
            self.assertFalse(any('<iframe' in rst for rst in rst_files))

    def test_can_toggle_slug_storage(self):

        posts = list(self.posts)
        r = lambda f: open(f).read()
        silent_f2p = mute(True)(fields2pelican)

        with temporary_folder() as temp:

            rst_files = (r(f) for f in silent_f2p(posts, 'markdown', temp))
            self.assertTrue(all('Slug:' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(posts, 'markdown', temp,
                         disable_slugs=True))
            self.assertFalse(any('Slug:' in rst for rst in rst_files))

            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp))
            self.assertTrue(all(':slug:' in rst for rst in rst_files))
            rst_files = (r(f) for f in silent_f2p(posts, 'rst', temp,
                         disable_slugs=True))
            self.assertFalse(any(':slug:' in rst for rst in rst_files))

    def test_decode_html_entities_in_titles(self):
        posts = list(self.posts)
        test_posts = [post for post in posts if post[2] == 'html-entity-test']
        self.assertTrue(len(test_posts) == 1)
        
        post = test_posts[0]
        title = post[0]
        self.assertTrue(title, "A normal post with some <html> entities in the title. You can't miss them.")
        self.assertTrue('&' not in title)
