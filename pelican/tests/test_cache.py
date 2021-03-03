import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from pelican.generators import ArticlesGenerator, PagesGenerator
from pelican.tests.support import get_context, get_settings, unittest


CUR_DIR = os.path.dirname(__file__)
CONTENT_DIR = os.path.join(CUR_DIR, 'content')


class TestCache(unittest.TestCase):

    def setUp(self):
        self.temp_cache = mkdtemp(prefix='pelican_cache.')

    def tearDown(self):
        rmtree(self.temp_cache)

    def _get_cache_enabled_settings(self):
        settings = get_settings()
        settings['CACHE_CONTENT'] = True
        settings['LOAD_CONTENT_CACHE'] = True
        settings['CACHE_PATH'] = self.temp_cache
        return settings

    def test_generator_caching(self):
        """Test that cached and uncached content is same in generator level"""
        settings = self._get_cache_enabled_settings()
        settings['CONTENT_CACHING_LAYER'] = 'generator'
        settings['PAGE_PATHS'] = ['TestPages']
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        def sorted_titles(items):
            return sorted(item.title for item in items)

        # Articles
        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        uncached_articles = sorted_titles(generator.articles)
        uncached_drafts = sorted_titles(generator.drafts)

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        cached_articles = sorted_titles(generator.articles)
        cached_drafts = sorted_titles(generator.drafts)

        self.assertEqual(uncached_articles, cached_articles)
        self.assertEqual(uncached_drafts, cached_drafts)

        # Pages
        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        uncached_pages = sorted_titles(generator.pages)
        uncached_hidden_pages = sorted_titles(generator.hidden_pages)
        uncached_draft_pages = sorted_titles(generator.draft_pages)

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        cached_pages = sorted_titles(generator.pages)
        cached_hidden_pages = sorted_titles(generator.hidden_pages)
        cached_draft_pages = sorted_titles(generator.draft_pages)

        self.assertEqual(uncached_pages, cached_pages)
        self.assertEqual(uncached_hidden_pages, cached_hidden_pages)
        self.assertEqual(uncached_draft_pages, cached_draft_pages)

    def test_reader_caching(self):
        """Test that cached and uncached content is same in reader level"""
        settings = self._get_cache_enabled_settings()
        settings['CONTENT_CACHING_LAYER'] = 'reader'
        settings['PAGE_PATHS'] = ['TestPages']
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        def sorted_titles(items):
            return sorted(item.title for item in items)

        # Articles
        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        uncached_articles = sorted_titles(generator.articles)
        uncached_drafts = sorted_titles(generator.drafts)

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        cached_articles = sorted_titles(generator.articles)
        cached_drafts = sorted_titles(generator.drafts)

        self.assertEqual(uncached_articles, cached_articles)
        self.assertEqual(uncached_drafts, cached_drafts)

        # Pages
        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        uncached_pages = sorted_titles(generator.pages)
        uncached_hidden_pages = sorted_titles(generator.hidden_pages)

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        cached_pages = sorted_titles(generator.pages)
        cached_hidden_pages = sorted_titles(generator.hidden_pages)

        self.assertEqual(uncached_pages, cached_pages)
        self.assertEqual(uncached_hidden_pages, cached_hidden_pages)

    def test_article_object_caching(self):
        """Test Article objects caching at the generator level"""
        settings = self._get_cache_enabled_settings()
        settings['CONTENT_CACHING_LAYER'] = 'generator'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache'))

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        """
        6 files don't get cached because they were not valid
        - article_with_attributes_containing_double_quotes.html
        - article_with_comments.html
        - article_with_null_attributes.html
        - 2012-11-30_md_w_filename_meta#foo-bar.md
        - empty.md
        - empty_with_bom.md
        """
        self.assertEqual(generator.readers.read_file.call_count, 6)

    def test_article_reader_content_caching(self):
        """Test raw article content caching at the reader level"""
        settings = self._get_cache_enabled_settings()
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator.readers, '_cache'))

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        readers = generator.readers.readers
        for reader in readers.values():
            reader.read = MagicMock()
        generator.generate_context()
        for reader in readers.values():
            self.assertEqual(reader.read.call_count, 0)

    def test_article_ignore_cache(self):
        """Test that all the articles are read again when not loading cache

        used in --ignore-cache or autoreload mode"""
        settings = self._get_cache_enabled_settings()
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache_open'))
        orig_call_count = generator.readers.read_file.call_count

        settings['LOAD_CONTENT_CACHE'] = False
        generator = ArticlesGenerator(
            context=context.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertEqual(
            generator.readers.read_file.call_count,
            orig_call_count)

    def test_page_object_caching(self):
        """Test Page objects caching at the generator level"""
        settings = self._get_cache_enabled_settings()
        settings['CONTENT_CACHING_LAYER'] = 'generator'
        settings['PAGE_PATHS'] = ['TestPages']
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache'))

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        """
        1 File doesn't get cached because it was not valid
        - bad_page.rst
        """
        self.assertEqual(generator.readers.read_file.call_count, 1)

    def test_page_reader_content_caching(self):
        """Test raw page content caching at the reader level"""
        settings = self._get_cache_enabled_settings()
        settings['PAGE_PATHS'] = ['TestPages']
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        self.assertTrue(hasattr(generator.readers, '_cache'))

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        readers = generator.readers.readers
        for reader in readers.values():
            reader.read = MagicMock()
        generator.generate_context()
        for reader in readers.values():
            self.assertEqual(reader.read.call_count, 0)

    def test_page_ignore_cache(self):
        """Test that all the pages are read again when not loading cache

        used in --ignore_cache or autoreload mode"""
        settings = self._get_cache_enabled_settings()
        settings['PAGE_PATHS'] = ['TestPages']
        settings['READERS'] = {'asc': None}
        context = get_context(settings)

        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertTrue(hasattr(generator, '_cache_open'))
        orig_call_count = generator.readers.read_file.call_count

        settings['LOAD_CONTENT_CACHE'] = False
        generator = PagesGenerator(
            context=context.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.readers.read_file = MagicMock()
        generator.generate_context()
        self.assertEqual(
            generator.readers.read_file.call_count,
            orig_call_count)
