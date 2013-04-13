# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from mock import MagicMock
import os

from codecs import open
from tempfile import mkdtemp
from shutil import rmtree

from pelican.generators import (ArticlesGenerator, PagesGenerator,
                                TemplatePagesGenerator)
from pelican.writers import Writer
from pelican.settings import _DEFAULT_CONFIG
from pelican.tests.support import unittest, get_settings

CUR_DIR = os.path.dirname(__file__)


class TestArticlesGenerator(unittest.TestCase):

    def setUp(self):
        super(TestArticlesGenerator, self).setUp()
        self.generator = None

    def get_populated_generator(self):
        """
        We only need to pull all the test articles once, but read from it
        for each test.
        """
        if self.generator is None:
            settings = get_settings()
            settings['ARTICLE_DIR'] = 'content'
            settings['DEFAULT_CATEGORY'] = 'Default'
            settings['DEFAULT_DATE'] = (1970, 1, 1)
            self.generator = ArticlesGenerator(settings.copy(), settings,
                                CUR_DIR, settings['THEME'], None,
                                settings['MARKUP'])
            self.generator.generate_context()
        return self.generator

    def distill_articles(self, articles):
        distilled = []
        for page in articles:
            distilled.append([
                    page.title,
                    page.status,
                    page.category.name,
                    page.template
                ]
           )
        return distilled

    def test_generate_feeds(self):
        settings = get_settings()
        generator = ArticlesGenerator(settings,
                {'FEED_ALL_ATOM': settings['FEED_ALL_ATOM']}, None,
                settings['THEME'], None, settings['MARKUP'])
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], settings,
                                             'feeds/all.atom.xml')

        generator = ArticlesGenerator(settings, {'FEED_ALL_ATOM': None}, None,
                                      settings['THEME'], None, None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        generator = self.get_populated_generator()
        articles = self.distill_articles(generator.articles)
        articles_expected = [
            ['Article title', 'published', 'Default', 'article'],
            ['Article with markdown and summary metadata single', 'published',
             'Default', 'article'],
            ['Article with markdown and summary metadata multi', 'published',
             'Default', 'article'],
            ['Article with template', 'published', 'Default', 'custom'],
            ['Test md File', 'published', 'test', 'article'],
            ['Rst with filename metadata', 'published', 'yeah', 'article'],
            ['Test Markdown extensions', 'published', 'Default', 'article'],
            ['This is a super article !', 'published', 'Yeah', 'article'],
            ['This is an article with category !', 'published', 'yeah',
              'article'],
            ['This is an article without category !', 'published', 'Default',
             'article'],
            ['This is an article without category !', 'published',
             'TestCategory', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['マックOS X 10.8でパイソンとVirtualenvをインストールと設定', 'published', '指導書', 'article']
        ]
        self.assertEqual(sorted(articles_expected), sorted(articles))

    def test_generate_categories(self):

        generator = self.get_populated_generator()
        categories = [cat.name for cat, _ in generator.categories]
        categories_expected = ['Default', 'TestCategory', 'Yeah', 'test',
                               'yeah', '指導書']
        self.assertEqual(categories, categories_expected)

    def test_do_not_use_folder_as_category(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['ARTICLE_DIR'] = 'content'
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['USE_FOLDER_AS_CATEGORY'] = False
        settings['filenames'] = {}
        generator = ArticlesGenerator(settings.copy(), settings,
                            CUR_DIR, _DEFAULT_CONFIG['THEME'], None,
                            _DEFAULT_CONFIG['MARKUP'])
        generator.generate_context()

        categories = [cat.name for cat, _ in generator.categories]
        self.assertEqual(categories, ['Default', 'Yeah', 'test', 'yeah', '指導書'])

    def test_direct_templates_save_as_default(self):

        settings = get_settings()
        generator = ArticlesGenerator(settings, settings, None,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_modified(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives/index.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives/index')

    def test_direct_templates_save_as_false(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_count == 0

    def test_per_article_template(self):
        """
        Custom template articles get the field but standard/unset are None
        """
        generator = self.get_populated_generator()
        articles = self.distill_articles(generator.articles)
        custom_template = ['Article with template', 'published', 'Default',
                           'custom']
        standard_template = ['This is a super article !', 'published', 'Yeah',
                             'article']
        self.assertIn(custom_template, articles)
        self.assertIn(standard_template, articles)


class TestPageGenerator(unittest.TestCase):
    # Note: Every time you want to test for a new field; Make sure the test
    # pages in "TestPages" have all the fields Add it to distilled in
    # distill_pages Then update the assertEqual in test_generate_context
    # to match expected

    def distill_pages(self, pages):
        distilled = []
        for page in pages:
            distilled.append([
                    page.title,
                    page.status,
                    page.template
                ]
           )
        return distilled

    def test_generate_context(self):
        settings = get_settings()
        settings['PAGE_DIR'] = 'TestPages'
        settings['DEFAULT_DATE'] = (1970, 1, 1)

        generator = PagesGenerator(settings.copy(), settings, CUR_DIR,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        hidden_pages = self.distill_pages(generator.hidden_pages)

        pages_expected = [
            ['This is a test page', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom']
        ]
        hidden_pages_expected = [
            ['This is a test hidden page', 'hidden', 'page'],
            ['This is a markdown test hidden page', 'hidden', 'page'],
            ['This is a test hidden page with a custom template', 'hidden',
             'custom']
        ]

        self.assertEqual(sorted(pages_expected), sorted(pages))
        self.assertEqual(sorted(hidden_pages_expected), sorted(hidden_pages))


class TestTemplatePagesGenerator(unittest.TestCase):

    TEMPLATE_CONTENT = "foo: {{ foo }}"

    def setUp(self):
        self.temp_content = mkdtemp(prefix='pelicantests.')
        self.temp_output = mkdtemp(prefix='pelicantests.')

    def tearDown(self):
        rmtree(self.temp_content)
        rmtree(self.temp_output)

    def test_generate_output(self):

        settings = get_settings()
        settings['STATIC_PATHS'] = ['static']
        settings['TEMPLATE_PAGES'] = {
                'template/source.html': 'generated/file.html'
                }

        generator = TemplatePagesGenerator({'foo': 'bar'}, settings,
                self.temp_content, '', self.temp_output, None)

        # create a dummy template file
        template_dir = os.path.join(self.temp_content, 'template')
        template_path = os.path.join(template_dir, 'source.html')
        os.makedirs(template_dir)
        with open(template_path, 'w') as template_file:
            template_file.write(self.TEMPLATE_CONTENT)

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(
                self.temp_output, 'generated', 'file.html')

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with open(output_path, 'r') as output_file:
            self.assertEqual(output_file.read(), 'foo: bar')
