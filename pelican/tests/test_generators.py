# -*- coding: utf-8 -*-

from mock import MagicMock
import os
import re
from tempfile import mkdtemp
from shutil import rmtree

from pelican.generators import ArticlesGenerator, LessCSSGenerator, PagesGenerator
from pelican.settings import _DEFAULT_CONFIG
from .support import unittest, skipIfNoExecutable

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
            settings = _DEFAULT_CONFIG.copy()
            settings['ARTICLE_DIR'] = 'content'
            settings['DEFAULT_CATEGORY'] = 'Default'
            self.generator = ArticlesGenerator(settings.copy(), settings,
                                CUR_DIR, _DEFAULT_CONFIG['THEME'], None,
                                _DEFAULT_CONFIG['MARKUP'])
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

        generator = ArticlesGenerator(None, {'FEED_ATOM': _DEFAULT_CONFIG['FEED_ATOM']},
                                      None, _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], None, 'feeds/all.atom.xml')

        generator = ArticlesGenerator(None, {'FEED_ATOM': None}, None,
                                      _DEFAULT_CONFIG['THEME'], None, None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        generator = self.get_populated_generator()
        articles = self.distill_articles(generator.articles)
        articles_expected = [
            [u'Article title', 'published', 'Default', 'article'],
            [u'Article with template', 'published', 'Default', 'custom'],
            [u'Test md File', 'published', 'test', 'article'],
            [u'This is a super article !', 'published', 'Yeah', 'article'],
            [u'This is an article with category !', 'published', 'yeah', 'article'],
            [u'This is an article without category !', 'published', 'Default', 'article'],
            [u'This is an article without category !', 'published', 'TestCategory', 'article'],
            [u'This is a super article !', 'published', 'yeah', 'article']
        ]
        self.assertItemsEqual(articles_expected, articles)

    def test_generate_categories(self):

        generator = self.get_populated_generator()
        categories = [cat.name for cat, _ in generator.categories]
        categories_expected = ['Default', 'TestCategory', 'Yeah', 'test', 'yeah']
        self.assertEquals(categories, categories_expected)

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

    def test_per_article_template(self):
        """
        Custom template articles get the field but standard/unset are None
        """
        generator = self.get_populated_generator()
        articles = self.distill_articles(generator.articles)
        custom_template = ['Article with template', 'published', 'Default', 'custom']
        standard_template = ['This is a super article !', 'published', 'Yeah', 'article']
        self.assertIn(custom_template, articles)
        self.assertIn(standard_template, articles)

class TestPageGenerator(unittest.TestCase):
    """
    Every time you want to test for a new field;
    Make sure the test pages in "TestPages" have all the fields
    Add it to distilled in distill_pages
    Then update the assertItemsEqual in test_generate_context to match expected
    """

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
        settings = _DEFAULT_CONFIG.copy()

        settings['PAGE_DIR'] = 'TestPages'
        generator = PagesGenerator(settings.copy(), settings, CUR_DIR,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        hidden_pages = self.distill_pages(generator.hidden_pages)

        pages_expected = [
            [u'This is a test page', 'published', 'page'],
            [u'This is a markdown test page', 'published', 'page'],
            [u'This is a test page with a preset template', 'published', 'custom']
        ]
        hidden_pages_expected = [
            [u'This is a test hidden page', 'hidden', 'page'],
            [u'This is a markdown test hidden page', 'hidden', 'page'],
            [u'This is a test hidden page with a custom template', 'hidden', 'custom']
        ]

        self.assertItemsEqual(pages_expected,pages)
        self.assertItemsEqual(hidden_pages_expected,hidden_pages)


class TestLessCSSGenerator(unittest.TestCase):

    LESS_CONTENT = """
        @color: #4D926F;

        #header {
          color: @color;
        }
        h2 {
          color: @color;
        }
    """

    def setUp(self):
        self.temp_content = mkdtemp()
        self.temp_output = mkdtemp()

    def tearDown(self):
        rmtree(self.temp_content)
        rmtree(self.temp_output)

    @skipIfNoExecutable('lessc')
    def test_less_compiler(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['STATIC_PATHS'] = ['static']
        settings['LESS_GENERATOR'] = True

        generator = LessCSSGenerator(None, settings, self.temp_content,
                        _DEFAULT_CONFIG['THEME'], self.temp_output, None)

        # create a dummy less file
        less_dir = os.path.join(self.temp_content, 'static', 'css')
        less_filename = os.path.join(less_dir, 'test.less')

        less_output = os.path.join(self.temp_output, 'static', 'css',
                            'test.css')

        os.makedirs(less_dir)
        with open(less_filename, 'w') as less_file:
            less_file.write(self.LESS_CONTENT)

        generator.generate_output()

        # we have the file ?
        self.assertTrue(os.path.exists(less_output))

        # was it compiled ?
        self.assertIsNotNone(re.search(r'^\s+color:\s*#4D926F;$',
            open(less_output).read(), re.MULTILINE | re.IGNORECASE))
