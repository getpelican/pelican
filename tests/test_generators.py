# -*- coding: utf-8 -*-

from mock import MagicMock
import os
import re
from tempfile import mkdtemp
from shutil import rmtree

from pelican.generators import (ArticlesGenerator, LessCSSGenerator,
                                PagesGenerator)
from .support import unittest, skipIfNoExecutable, get_settings

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
                {'FEED_ATOM': settings['FEED_ATOM']}, None,
                settings['THEME'], None, settings['MARKUP'])
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], settings, 'feeds/all.atom.xml')

        generator = ArticlesGenerator(settings, {'FEED_ATOM': None}, None,
                                      settings['THEME'], None, None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        settings = get_settings()
        settings['ARTICLE_DIR'] = 'content'
        settings['DEFAULT_CATEGORY'] = 'Default'
        generator = ArticlesGenerator(settings.copy(), settings, CUR_DIR,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
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

        categories = [cat.name for cat, _ in generator.categories]
        # assert that the categories are ordered as expected
        self.assertEquals(
                categories, ['Default', 'TestCategory', 'Yeah', 'test',
                             'yeah'])

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
            blog=True, paginated={}, page_name='archives')

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
        settings = get_settings()
        settings['PAGE_DIR'] = 'TestPages'

        generator = PagesGenerator(settings.copy(), settings, CUR_DIR,
                                      settings['THEME'], None,
                                      settings['MARKUP'])
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

        settings = get_settings()
        settings['STATIC_PATHS'] = ['static']
        settings['LESS_GENERATOR'] = True

        generator = LessCSSGenerator(settings, settings, self.temp_content,
                        settings['THEME'], self.temp_output, None)

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
