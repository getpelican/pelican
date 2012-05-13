# -*- coding: utf-8 -*-

import os

from pelican.tools.pelican_import import wp2fields
from .support import unittest

CUR_DIR = os.path.dirname(__file__)
WORDPRESS_XML_SAMPLE = os.path.join(CUR_DIR, 'content', 'wordpressexport.xml')


class TestArticlesImporter(unittest.TestCase):

    def test_import_wordpress_xml_with_emtpy_posts_ignore_them(self):

        posts = list(wp2fields(WORDPRESS_XML_SAMPLE))
        self.assertTrue(posts)
        for title, content, fname, date, author, categ, tags, format in posts:
            self.assertTrue(title.strip())
