# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import locale
import os

from codecs import open
from shutil import rmtree
from tempfile import mkdtemp

from pelican.generators import (ArticlesGenerator, Generator, PagesGenerator,
                                StaticGenerator, TemplatePagesGenerator)
from pelican.tests.support import get_settings, unittest
from pelican.writers import Writer

try:
    from unittest.mock import MagicMock
except ImportError:
    try:
        from mock import MagicMock
    except ImportError:
        MagicMock = False


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
        self.settings['IGNORE_FILES'] = {'ignored1.rst', 'ignored2.rst'}

        filename = os.path.join(CUR_DIR, 'content', 'article.rst')
        include_path = self.generator._include_path
        self.assertTrue(include_path(filename))
        self.assertTrue(include_path(filename, extensions=('rst',)))
        self.assertFalse(include_path(filename, extensions=('md',)))

        ignored_file = os.path.join(CUR_DIR, 'content', 'ignored1.rst')
        self.assertFalse(include_path(ignored_file))

    def test_get_files_exclude(self):
        """Test that Generator.get_files() properly excludes directories.
        """
        # We use our own Generator so we can give it our own content path
        generator = Generator(
            context=self.settings.copy(),
            settings=self.settings,
            path=os.path.join(CUR_DIR, 'nested_content'),
            theme=self.settings['THEME'], output_path=None)

        filepaths = generator.get_files(paths=['maindir'])
        found_files = {os.path.basename(f) for f in filepaths}
        expected_files = {'maindir.md', 'subdir.md'}
        self.assertFalse(
            expected_files - found_files,
            "get_files() failed to find one or more files")

        # Test string as `paths` argument rather than list
        filepaths = generator.get_files(paths='maindir')
        found_files = {os.path.basename(f) for f in filepaths}
        expected_files = {'maindir.md', 'subdir.md'}
        self.assertFalse(
            expected_files - found_files,
            "get_files() failed to find one or more files")

        filepaths = generator.get_files(paths=[''], exclude=['maindir'])
        found_files = {os.path.basename(f) for f in filepaths}
        self.assertNotIn(
            'maindir.md', found_files,
            "get_files() failed to exclude a top-level directory")
        self.assertNotIn(
            'subdir.md', found_files,
            "get_files() failed to exclude a subdir of an excluded directory")

        filepaths = generator.get_files(
            paths=[''],
            exclude=[os.path.join('maindir', 'subdir')])
        found_files = {os.path.basename(f) for f in filepaths}
        self.assertNotIn(
            'subdir.md', found_files,
            "get_files() failed to exclude a subdirectory")

        filepaths = generator.get_files(paths=[''], exclude=['subdir'])
        found_files = {os.path.basename(f) for f in filepaths}
        self.assertIn(
            'subdir.md', found_files,
            "get_files() excluded a subdirectory by name, ignoring its path")

    def test_custom_jinja_environment(self):
        """
            Test that setting the JINJA_ENVIRONMENT
            properly gets set from the settings config
        """
        settings = get_settings()
        comment_start_string = 'abc'
        comment_end_string = '/abc'
        settings['JINJA_ENVIRONMENT'] = {
            'comment_start_string': comment_start_string,
            'comment_end_string': comment_end_string
        }
        generator = Generator(settings.copy(), settings,
                              CUR_DIR, settings['THEME'], None)
        self.assertEqual(comment_start_string,
                         generator.env.comment_start_string)
        self.assertEqual(comment_end_string,
                         generator.env.comment_end_string)


class TestArticlesGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        settings['CACHE_CONTENT'] = False

        cls.generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        cls.generator.generate_context()
        cls.articles = cls.distill_articles(cls.generator.articles)

    def setUp(self):
        self.temp_cache = mkdtemp(prefix='pelican_cache.')

    def tearDown(self):
        rmtree(self.temp_cache)

    @staticmethod
    def distill_articles(articles):
        return [[article.title, article.status, article.category.name,
                 article.template] for article in articles]

    @unittest.skipUnless(MagicMock, 'Needs Mock module')
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
            ['Test metadata duplicates', 'published', 'test', 'article'],
            ['Test mkd File', 'published', 'test', 'article'],
            ['This is a super article !', 'published', 'Yeah', 'article'],
            ['This is a super article !', 'published', 'Yeah', 'article'],
            ['Article with Nonconformant HTML meta tags', 'published',
                'Default', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'Default', 'article'],
            ['This is an article with category !', 'published', 'yeah',
             'article'],
            ['This is an article with multiple authors!', 'published',
                'Default', 'article'],
            ['This is an article with multiple authors!', 'published',
                'Default', 'article'],
            ['This is an article with multiple authors in list format!',
                'published', 'Default', 'article'],
            ['This is an article with multiple authors in lastname, '
             'firstname format!', 'published', 'Default', 'article'],
            ['This is an article without category !', 'published', 'Default',
                'article'],
            ['This is an article without category !', 'published',
             'TestCategory', 'article'],
            ['An Article With Code Block To Test Typogrify Ignore',
                'published', 'Default', 'article'],
            ['マックOS X 10.8でパイソンとVirtualenvをインストールと設定',
                'published', '指導書', 'article'],
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

    @unittest.skipUnless(MagicMock, 'Needs Mock module')
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

    @unittest.skipUnless(MagicMock, 'Needs Mock module')
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

    @unittest.skipUnless(MagicMock, 'Needs Mock module')
    def test_direct_templates_save_as_false(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = False
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        self.assertEqual(write.call_count, 0)

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

    @unittest.skipUnless(MagicMock, 'Needs Mock module')
    def test_period_in_timeperiod_archive(self):
        """
        Test that the context of a generated period_archive is passed
        'period' : a tuple of year, month, day according to the time period
        """
        old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))
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
        # among other things it must have at least been called with this
        settings["period"] = (1970,)
        write.assert_called_with("posts/1970/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)

        del settings["period"]
        settings['MONTH_ARCHIVE_SAVE_AS'] = \
            'posts/{date:%Y}/{date:%b}/index.html'
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates
                 if d.date.year == 1970 and d.date.month == 1]
        self.assertEqual(len(dates), 1)
        settings["period"] = (1970, "January")
        # among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)

        del settings["period"]
        settings['DAY_ARCHIVE_SAVE_AS'] = \
            'posts/{date:%Y}/{date:%b}/{date:%d}/index.html'
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [
            d for d in generator.dates if
            d.date.year == 1970 and
            d.date.month == 1 and
            d.date.day == 1
        ]
        self.assertEqual(len(dates), 1)
        settings["period"] = (1970, "January", 1)
        # among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/01/index.html",
                                 generator.get_template("period_archives"),
                                 settings,
                                 blog=True, dates=dates)
        locale.setlocale(locale.LC_ALL, old_locale)

    def test_nonexistent_template(self):
        """Attempt to load a non-existent template"""
        settings = get_settings(filenames={})
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        self.assertRaises(Exception, generator.get_template, "not_a_template")

    def test_generate_authors(self):
        """Check authors generation."""
        authors = [author.name for author, _ in self.generator.authors]
        authors_expected = sorted(
            ['Alexis Métaireau', 'Author, First', 'Author, Second',
             'First Author', 'Second Author'])
        self.assertEqual(sorted(authors), authors_expected)
        # test for slug
        authors = [author.slug for author, _ in self.generator.authors]
        authors_expected = ['alexis-metaireau', 'author-first',
                            'author-second', 'first-author', 'second-author']
        self.assertEqual(sorted(authors), sorted(authors_expected))

    def test_standard_metadata_in_default_metadata(self):
        settings = get_settings(filenames={})
        settings['CACHE_CONTENT'] = False
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['DEFAULT_METADATA'] = (('author', 'Blogger'),
                                        # category will be ignored in favor of
                                        # DEFAULT_CATEGORY
                                        ('category', 'Random'),
                                        ('tags', 'general, untagged'))
        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()

        authors = sorted([author.name for author, _ in generator.authors])
        authors_expected = sorted(['Alexis Métaireau', 'Blogger',
                                   'Author, First', 'Author, Second',
                                   'First Author', 'Second Author'])
        self.assertEqual(authors, authors_expected)

        categories = sorted([category.name
                             for category, _ in generator.categories])
        categories_expected = [
            sorted(['Default', 'TestCategory', 'yeah', 'test', '指導書']),
            sorted(['Default', 'TestCategory', 'Yeah', 'test', '指導書'])]
        self.assertIn(categories, categories_expected)

        tags = sorted([tag.name for tag in generator.tags])
        tags_expected = sorted(['bar', 'foo', 'foobar', 'general', 'untagged',
                                'パイソン', 'マック'])
        self.assertEqual(tags, tags_expected)

    def test_article_order_by(self):
        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['ARTICLE_ORDER_BY'] = 'title'

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()

        expected = [
            'An Article With Code Block To Test Typogrify Ignore',
            'Article title',
            'Article with Nonconformant HTML meta tags',
            'Article with markdown and summary metadata multi',
            'Article with markdown and summary metadata single',
            'Article with markdown containing footnotes',
            'Article with template',
            'Rst with filename metadata',
            'Test Markdown extensions',
            'Test markdown File',
            'Test md File',
            'Test mdown File',
            'Test metadata duplicates',
            'Test mkd File',
            'This is a super article !',
            'This is a super article !',
            'This is a super article !',
            'This is a super article !',
            'This is a super article !',
            'This is a super article !',
            'This is an article with category !',
            ('This is an article with multiple authors in lastname, '
             'firstname format!'),
            'This is an article with multiple authors in list format!',
            'This is an article with multiple authors!',
            'This is an article with multiple authors!',
            'This is an article without category !',
            'This is an article without category !',
            'マックOS X 10.8でパイソンとVirtualenvをインストールと設定']

        articles = [article.title for article in generator.articles]
        self.assertEqual(articles, expected)

        # reversed title
        settings = get_settings(filenames={})
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['ARTICLE_ORDER_BY'] = 'reversed-title'

        generator = ArticlesGenerator(
            context=settings.copy(), settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()

        articles = [article.title for article in generator.articles]
        self.assertEqual(articles, list(reversed(expected)))


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
             'custom'],
            ['Page with a bunch of links', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
        ]
        hidden_pages_expected = [
            ['This is a test hidden page', 'hidden', 'page'],
            ['This is a markdown test hidden page', 'hidden', 'page'],
            ['This is a test hidden page with a custom template', 'hidden',
             'custom']
        ]

        self.assertEqual(sorted(pages_expected), sorted(pages))
        self.assertEqual(
            sorted(pages_expected),
            sorted(self.distill_pages(generator.context['pages'])))
        self.assertEqual(sorted(hidden_pages_expected), sorted(hidden_pages))
        self.assertEqual(
            sorted(hidden_pages_expected),
            sorted(self.distill_pages(generator.context['hidden_pages'])))

    def test_generate_sorted(self):
        settings = get_settings(filenames={})
        settings['PAGE_PATHS'] = ['TestPages']  # relative to CUR_DIR
        settings['CACHE_PATH'] = self.temp_cache
        settings['DEFAULT_DATE'] = (1970, 1, 1)

        # default sort (filename)
        pages_expected_sorted_by_filename = [
            ['This is a test page', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom'],
        ]
        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        self.assertEqual(pages_expected_sorted_by_filename, pages)

        # sort by title
        pages_expected_sorted_by_title = [
            ['A Page (Test) for sorting', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['This is a test page', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom'],
        ]
        settings['PAGE_ORDER_BY'] = 'title'
        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        self.assertEqual(pages_expected_sorted_by_title, pages)

        # sort by title reversed
        pages_expected_sorted_by_title = [
            ['This is a test page with a preset template', 'published',
             'custom'],
            ['This is a test page', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
        ]
        settings['PAGE_ORDER_BY'] = 'reversed-title'
        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        self.assertEqual(pages_expected_sorted_by_title, pages)

    def test_tag_and_category_links_on_generated_pages(self):
        """
        Test to ensure links of the form {tag}tagname and {category}catname
        are generated correctly on pages
        """
        settings = get_settings(filenames={})
        settings['PAGE_PATHS'] = ['TestPages']    # relative to CUR_DIR
        settings['CACHE_PATH'] = self.temp_cache
        settings['DEFAULT_DATE'] = (1970, 1, 1)

        generator = PagesGenerator(
            context=settings.copy(), settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages_by_title = {p.title: p.content for p in generator.pages}

        test_content = pages_by_title['Page with a bunch of links']
        self.assertIn('<a href="/category/yeah.html">', test_content)
        self.assertIn('<a href="/tag/matsuku.html">', test_content)


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


class TestStaticGenerator(unittest.TestCase):

    def setUp(self):
        self.content_path = os.path.join(CUR_DIR, 'mixed_content')

    def test_static_excludes(self):
        """Test that StaticGenerator respects STATIC_EXCLUDES.
        """
        settings = get_settings(
            STATIC_EXCLUDES=['subdir'],
            PATH=self.content_path,
            STATIC_PATHS=[''],
            filenames={})
        context = settings.copy()

        StaticGenerator(
            context=context, settings=settings,
            path=settings['PATH'], output_path=None,
            theme=settings['THEME']).generate_context()

        staticnames = [os.path.basename(c.source_path)
                       for c in context['staticfiles']]

        self.assertNotIn(
            'subdir_fake_image.jpg', staticnames,
            "StaticGenerator processed a file in a STATIC_EXCLUDES directory")
        self.assertIn(
            'fake_image.jpg', staticnames,
            "StaticGenerator skipped a file that it should have included")

    def test_static_exclude_sources(self):
        """Test that StaticGenerator respects STATIC_EXCLUDE_SOURCES.
        """

        settings = get_settings(
            STATIC_EXCLUDE_SOURCES=True,
            PATH=self.content_path,
            PAGE_PATHS=[''],
            STATIC_PATHS=[''],
            CACHE_CONTENT=False,
            filenames={})
        context = settings.copy()

        for generator_class in (PagesGenerator, StaticGenerator):
            generator_class(
                context=context, settings=settings,
                path=settings['PATH'], output_path=None,
                theme=settings['THEME']).generate_context()

        staticnames = [os.path.basename(c.source_path)
                       for c in context['staticfiles']]

        self.assertFalse(
            any(name.endswith(".md") for name in staticnames),
            "STATIC_EXCLUDE_SOURCES=True failed to exclude a markdown file")

        settings.update(STATIC_EXCLUDE_SOURCES=False)
        context = settings.copy()
        context['filenames'] = {}

        for generator_class in (PagesGenerator, StaticGenerator):
            generator_class(
                context=context, settings=settings,
                path=settings['PATH'], output_path=None,
                theme=settings['THEME']).generate_context()

        staticnames = [os.path.basename(c.source_path)
                       for c in context['staticfiles']]

        self.assertTrue(
            any(name.endswith(".md") for name in staticnames),
            "STATIC_EXCLUDE_SOURCES=False failed to include a markdown file")
