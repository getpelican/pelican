# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from codecs import open
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
from shutil import rmtree
from tempfile import mkdtemp

from pelican.generators import (Generator, ArticlesGenerator, PagesGenerator,
                                TemplatePagesGenerator)
from pelican.writers import Writer
from pelican.tests.support import unittest, get_settings
import locale

CUR_DIR = os.path.dirname(__file__)
CONTENT_DIR = os.path.join(CUR_DIR, 'content')


class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))
        self.settings = get_settings()
        self.settings['READERS'] = {'asc': None}
        self.generator = Generator(self.settings.copy(), self.settings,
                                   CUR_DIR, self.settings['THEME'], None)

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)


    def test_include_path(self):
        filename = os.path.join(CUR_DIR, 'content', 'article.rst')
        include_path = self.generator._include_path
        self.assertTrue(include_path(filename))
        self.assertTrue(include_path(filename, extensions=('rst',)))
        self.assertFalse(include_path(filename, extensions=('md',)))


class TestArticlesGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        settings['CACHE_CONTENT'] = False   # cache not needed for this logic tests

        cls.generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        cls.generator.generate_context()
        cls.articles = [[page.title, page.status, page.category.name,
                         page.template] for page in cls.generator.articles]

    def setUp(self):
        self.temp_cache = mkdtemp(prefix='pelican_cache.')

    def tearDown(self):
        rmtree(self.temp_cache)

    def test_generate_feeds(self):
        settings = get_settings()
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], settings,
                                             'feeds/all.atom.xml')

        generator = ArticlesGenerator(
            context=settings, settings=get_settings(FEED_ALL_ATOM=None),
            path=None, theme=settings['THEME'], output_path=None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        articles_expected = [
            ['Article title', 'published', 'Default', 'article'],
            ['Article with markdown and summary metadata multi', 'published',
             'Default', 'article'],
            ['Article with markdown and summary metadata single', 'published',
             'Default', 'article'],
            ['Article with markdown containing footnotes', 'published',
             'Default', 'article'],
            ['Article with template', 'published', 'Default', 'custom'],
            ['Rst with filename metadata', 'published', 'yeah', 'article'],
            ['Test Markdown extensions', 'published', 'Default', 'article'],
            ['Test markdown File', 'published', 'test', 'article'],
            ['Test md File', 'published', 'test', 'article'],
            ['Test mdown File', 'published', 'test', 'article'],
            ['Test mkd File', 'published', 'test', 'article'],
            ['This is a super article !', 'published', 'Yeah', 'article'],
            ['This is a super article !', 'published', 'Yeah', 'article'],
            ['Article with Nonconformant HTML meta tags', 'published', 'Default', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'Default', 'article'],
            ['This is an article with category !', 'published', 'yeah',
             'article'],
            ['This is an article with multiple authors!', 'published', 'Default', 'article'],
            ['This is an article with multiple authors!', 'published', 'Default', 'article'],
            ['This is an article without category !', 'published', 'Default',
             'article'],
            ['This is an article without category !', 'published',
             'TestCategory', 'article'],
            ['マックOS X 10.8でパイソンとVirtualenvをインストールと設定', 'published',
             '指導書', 'article'],
        ]
        self.assertEqual(sorted(articles_expected), sorted(self.articles))

    def test_generate_categories(self):

        # test for name
        # categories are grouped by slug; if two categories have the same slug
        # but different names they will be grouped together, the first one in
        # terms of process order will define the name for that category
        categories = [cat.name for cat, _ in self.generator.categories]
        categories_alternatives = (
            sorted(['Default', 'TestCategory', 'Yeah', 'test', '指導書']),
            sorted(['Default', 'TestCategory', 'yeah', 'test', '指導書']),
        )
        self.assertIn(sorted(categories), categories_alternatives)
        # test for slug
        categories = [cat.slug for cat, _ in self.generator.categories]
        categories_expected = ['default', 'testcategory', 'yeah', 'test',
                               'zhi-dao-shu']
        self.assertEqual(sorted(categories), sorted(categories_expected))

    def test_do_not_use_folder_as_category(self):

        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['USE_FOLDER_AS_CATEGORY'] = False
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}
        settings['filenames'] = {}
        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        # test for name
        # categories are grouped by slug; if two categories have the same slug
        # but different names they will be grouped together, the first one in
        # terms of process order will define the name for that category
        categories = [cat.name for cat, _ in generator.categories]
        categories_alternatives = (
            sorted(['Default', 'Yeah', 'test', '指導書']),
            sorted(['Default', 'yeah', 'test', '指導書']),
        )
        self.assertIn(sorted(categories), categories_alternatives)
        # test for slug
        categories = [cat.slug for cat, _ in generator.categories]
        categories_expected = ['default', 'yeah', 'test', 'zhi-dao-shu']
        self.assertEqual(sorted(categories), sorted(categories_expected))

    def test_direct_templates_save_as_default(self):

        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives.html",
                                 generator.get_template("archives"), settings,
                                 blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_modified(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives/index.html",
                                 generator.get_template("archives"), settings,
                                 blog=True, paginated={},
                                 page_name='archives/index')

    def test_direct_templates_save_as_false(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_count == 0

    def test_per_article_template(self):
        """
        Custom template articles get the field but standard/unset are None
        """
        custom_template = ['Article with template', 'published', 'Default',
                           'custom']
        standard_template = ['This is a super article !', 'published', 'Yeah',
                             'article']
        self.assertIn(custom_template, self.articles)
        self.assertIn(standard_template, self.articles)

    def test_period_in_timeperiod_archive(self):
        """
        Test that the context of a generated period_archive is passed
        'period' : a tuple of year, month, day according to the time period
        """
        settings = get_settings(filenames={})

        settings['YEAR_ARCHIVE_SAVE_AS'] = 'posts/{date:%Y}/index.html'
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates if d.date.year == 1970]
        self.assertEqual(len(dates), 1)
        #among other things it must have at least been called with this
        settings["period"] = (1970,)
        write.assert_called_with("posts/1970/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)

        del settings["period"]
        settings['MONTH_ARCHIVE_SAVE_AS'] = 'posts/{date:%Y}/{date:%b}/index.html'
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates if d.date.year == 1970
                                            and d.date.month == 1]
        self.assertEqual(len(dates), 1)
        settings["period"] = (1970, "January")
        #among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)

        del settings["period"]
        settings['DAY_ARCHIVE_SAVE_AS'] = 'posts/{date:%Y}/{date:%b}/{date:%d}/index.html'
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates if d.date.year == 1970
                                            and d.date.month == 1
                                            and d.date.day == 1]
        self.assertEqual(len(dates), 1)
        settings["period"] = (1970, "January", 1)
        #among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/01/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)

    def test_generate_authors(self):
        """Check authors generation."""
        authors = [author.name for author, _ in self.generator.authors]
        authors_expected = sorted(['Alexis Métaireau', 'First Author', 'Second Author'])
        self.assertEqual(sorted(authors), authors_expected)
        # test for slug
        authors = [author.slug for author, _ in self.generator.authors]
        authors_expected = ['alexis-metaireau', 'first-author', 'second-author']
        self.assertEqual(sorted(authors), sorted(authors_expected))

    def test_article_object_caching(self):
        """Test Article objects caching at the generator level"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['CONTENT_CACHING_LAYER'] = 'generator'
        settings['READERS'] = {'asc': None}

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache'))

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        generator.readers.read_file.assert_called_count == 0

    def test_reader_content_caching(self):
        """Test raw content caching at the reader level"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator.readers, '_cache'))

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        readers = generator.readers.readers
        for reader in readers.values():
            reader.read = MagicMock()
        generator.generate_context()
        for reader in readers.values():
            reader.read.assert_called_count == 0

    def test_ignore_cache(self):
        """Test that all the articles are read again when not loading cache

        used in --ignore-cache or autoreload mode"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache_open'))
        orig_call_count = generator.readers.read_file.call_count

        settings['LOAD_CONTENT_CACHE'] = False
        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        generator.readers.read_file.assert_called_count == orig_call_count


class TestPageGenerator(unittest.TestCase):
    # Note: Every time you want to test for a new field; Make sure the test
    # pages in "TestPages" have all the fields Add it to distilled in
    # distill_pages Then update the assertEqual in test_generate_context
    # to match expected

    def setUp(self):
        self.temp_cache = mkdtemp(prefix='pelican_cache.')

    def tearDown(self):
        rmtree(self.temp_cache)

    def distill_pages(self, pages):
        return [[page.title, page.status, page.template] for page in pages]

    def test_generate_context(self):
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['PAGE_PATHS'] = ['TestPages']  # relative to CUR_DIR
        settings['DEFAULT_DATE'] = (1970, 1, 1)

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
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

    def test_page_object_caching(self):
        """Test Page objects caching at the generator level"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['CONTENT_CACHING_LAYER'] = 'generator'
        settings['READERS'] = {'asc': None}

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache'))

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        generator.readers.read_file.assert_called_count == 0

    def test_reader_content_caching(self):
        """Test raw content caching at the reader level"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator.readers, '_cache'))

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        readers = generator.readers.readers
        for reader in readers.values():
            reader.read = MagicMock()
        generator.generate_context()
        for reader in readers.values():
            reader.read.assert_called_count == 0

    def test_ignore_cache(self):
        """Test that all the pages are read again when not loading cache

        used in --ignore_cache or autoreload mode"""
        settings = get_settings(filenames={})
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache_open'))
        orig_call_count = generator.readers.read_file.call_count

        settings['LOAD_CONTENT_CACHE'] = False
        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        generator.readers.read_file.assert_called_count == orig_call_count


class TestTemplatePagesGenerator(unittest.TestCase):

    TEMPLATE_CONTENT = "foo: {{ foo }}"

    def setUp(self):
        self.temp_content = mkdtemp(prefix='pelicantests.')
        self.temp_output = mkdtemp(prefix='pelicantests.')
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))


    def tearDown(self):
        rmtree(self.temp_content)
        rmtree(self.temp_output)
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def test_generate_output(self):

        settings = get_settings()
        settings['STATIC_PATHS'] = ['static']
        settings['TEMPLATE_PAGES'] = {
            'template/source.html': 'generated/file.html'
        }

        generator = TemplatePagesGenerator(
            context={'foo': 'bar'}, settings=settings,
            path=self.temp_content, theme='', output_path=self.temp_output)

        # create a dummy template file
        template_dir = os.path.join(self.temp_content, 'template')
        template_path = os.path.join(template_dir, 'source.html')
        os.makedirs(template_dir)
        with open(template_path, 'w') as template_file:
            template_file.write(self.TEMPLATE_CONTENT)

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(self.temp_output, 'generated', 'file.html')

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with open(output_path, 'r') as output_file:
            self.assertEqual(output_file.read(), 'foo: bar')
