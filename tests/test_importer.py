# -*- coding: utf-8 -*-

import os

from pelican.tools.pelican_import import wp2fields, fields2pelican
from .support import unittest, temporary_folder, mute

CUR_DIR = os.path.dirname(__file__)
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, 'content', 'wordpressexport.xml')


class TestWordpressXmlImporter(unittest.TestCase):


    def setUp(self):
        self.posts = wp2fields(WORDPRESS_XML_SAMPLE)


    def test_ignore_empty_published_posts(self):

        posts = list(self.posts)
        self.assertTrue(posts)
        self.assertTrue(all(p[0].strip() for p in posts if p[8] == 'publish'))


    def test_parse_drafts_and_published_posts(self):

        posts = list(self.posts)
        self.assertTrue(any(p for p in posts if p[8] == 'draft'))
        self.assertTrue(any(p for p in posts if p[8] == 'publish'))
        forbidden = any(p for p in posts if p[8] not in ('publish', 'draft'))
        self.assertTrue(not forbidden)


    def test_accept_empty_drafts(self):

        drafts = (p for p in self.posts if p[8] == 'draft')
        self.assertTrue(any((not p[0].strip()) for p in drafts))


    def test_drafts_are_saved_with_proper_metadata(self):

        posts = list(self.posts)
        r = lambda f: open(f).read()
        silent_f2p = mute(True)(fields2pelican)

        with temporary_folder() as temp:

            rst_files = list(r(f) for f in silent_f2p(posts, 'rst', temp))
            self.assertTrue(any(':status: draft' in rst for rst in rst_files))
            self.assertTrue(any(':status: draft' not in rst for rst in rst_files))

            md_files = list(r(f) for f in silent_f2p(posts, 'markdown', temp))
            self.assertTrue(any('Status: draft' in md for md in md_files))
            self.assertTrue(any('Status: draft' not in md for md in md_files))
