# -*- coding: utf-8 -*-

from mock import MagicMock
import os

from pelican.generators import ArticlesGenerator
from pelican.settings import _DEFAULT_CONFIG
from .support import unittest

CUR_DIR = os.path.dirname(__file__)


class TestArticlesGenerator(unittest.TestCase):

    def test_generate_feeds(self):

        generator = ArticlesGenerator(None, {'FEED': _DEFAULT_CONFIG['FEED']},
                                      None, _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], None, 'feeds/all.atom.xml')

        generator = ArticlesGenerator(None, {'FEED': None}, None,
                                      _DEFAULT_CONFIG['THEME'], None, None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['ARTICLE_DIR'] = 'content'
        settings['DEFAULT_CATEGORY'] = 'Default'
        generator = ArticlesGenerator(settings.copy(), settings, CUR_DIR,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        generator.generate_context()
        for article in generator.articles:
            relfilepath = os.path.relpath(article.filename, CUR_DIR)
            if relfilepath == os.path.join("TestCategory",
                                           "article_with_category.rst"):
                self.assertEquals(article.category.name, 'yeah')
            elif relfilepath == os.path.join("TestCategory",
                                             "article_without_category.rst"):
                self.assertEquals(article.category.name, 'TestCategory')
            elif relfilepath == "article_without_category.rst":
                self.assertEquals(article.category.name, 'Default')

    def test_direct_templates_save_as_default(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        generator = ArticlesGenerator(settings.copy(), settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_modified(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives/index.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_false(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_count == 0
