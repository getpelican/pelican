# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from pelican.generators import ArticlesGenerator
from pelican.writers import Writer
from pelican.tests.support import unittest, get_settings
from pelican.paginator import Paginator

CUR_DIR = os.path.dirname(__file__)
CONTENT_DIR = os.path.join(CUR_DIR, 'content')


class TestPaginator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)

        cls.generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        cls.generator.generate_context()
        cls.articles = [[page.title, page.status, page.category.name,
                         page.template] for page in cls.generator.articles]    

    def test_default_pagination_default(self):

        settings = get_settings()
        paginator = Paginator('index', 'index', self.articles, settings)

        self.assertEqual(paginator._get_num_pages(), 1)

    def test_default_pagination_value(self):

        settings = get_settings()
        settings['DEFAULT_PAGINATION'] = 5
        paginator = Paginator('articles', 'articles', self.articles, settings)

        self.assertTrue(paginator._get_num_pages() > 1)

    def test_per_template_pagination_unaffected(self):

        settings = get_settings()
        settings['TEMPLATE_PAGINATION'] = { 'articles' : 5 }
        paginator = Paginator('index', 'index', self.articles, settings)

        self.assertEqual(paginator._get_num_pages(), 1)

    def test_per_template_pagination_affected(self):

        settings = get_settings()
        settings['TEMPLATE_PAGINATION'] = { 'articles' : 5 }
        paginator = Paginator('articles', 'articles', self.articles, settings)

        self.assertTrue(paginator._get_num_pages() > 1)
