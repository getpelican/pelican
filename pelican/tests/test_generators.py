import locale
import os
import sys
from shutil import copy, rmtree
from tempfile import mkdtemp
from unittest.mock import MagicMock

from pelican.generators import (ArticlesGenerator, Generator, PagesGenerator,
                                PelicanTemplateNotFound, StaticGenerator,
                                TemplatePagesGenerator)
from pelican.tests.support import (can_symlink, get_context, get_settings,
                                   unittest)
from pelican.writers import Writer


CUR_DIR = os.path.dirname(__file__)
CONTENT_DIR = os.path.join(CUR_DIR, 'content')


class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
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

    def test_theme_overrides(self):
        """
            Test that the THEME_TEMPLATES_OVERRIDES configuration setting is
            utilized correctly in the Generator.
        """
        override_dirs = (os.path.join(CUR_DIR, 'theme_overrides', 'level1'),
                         os.path.join(CUR_DIR, 'theme_overrides', 'level2'))
        self.settings['THEME_TEMPLATES_OVERRIDES'] = override_dirs
        generator = Generator(
            context=self.settings.copy(),
            settings=self.settings,
            path=CUR_DIR,
            theme=self.settings['THEME'],
            output_path=None)

        filename = generator.get_template('article').filename
        self.assertEqual(override_dirs[0], os.path.dirname(filename))
        self.assertEqual('article.html', os.path.basename(filename))

        filename = generator.get_template('authors').filename
        self.assertEqual(override_dirs[1], os.path.dirname(filename))
        self.assertEqual('authors.html', os.path.basename(filename))

        filename = generator.get_template('taglist').filename
        self.assertEqual(os.path.join(self.settings['THEME'], 'templates'),
                         os.path.dirname(filename))
        self.assertNotIn(os.path.dirname(filename), override_dirs)
        self.assertEqual('taglist.html', os.path.basename(filename))

    def test_simple_prefix(self):
        """
            Test `!simple` theme prefix.
        """
        filename = self.generator.get_template('!simple/authors').filename
        expected_path = os.path.join(
            os.path.dirname(CUR_DIR), 'themes', 'simple', 'templates')
        self.assertEqual(expected_path, os.path.dirname(filename))
        self.assertEqual('authors.html', os.path.basename(filename))

    def test_theme_prefix(self):
        """
            Test `!theme` theme prefix.
        """
        filename = self.generator.get_template('!theme/authors').filename
        expected_path = os.path.join(
            os.path.dirname(CUR_DIR), 'themes', 'notmyidea', 'templates')
        self.assertEqual(expected_path, os.path.dirname(filename))
        self.assertEqual('authors.html', os.path.basename(filename))

    def test_bad_prefix(self):
        """
            Test unknown/bad theme prefix throws exception.
        """
        self.assertRaises(PelicanTemplateNotFound, self.generator.get_template,
                          '!UNKNOWN/authors')


class TestArticlesGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        settings = get_settings()
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['READERS'] = {'asc': None}
        settings['CACHE_CONTENT'] = False
        context = get_context(settings)

        cls.generator = ArticlesGenerator(
            context=context, settings=settings,
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

    def test_generate_feeds(self):
        settings = get_settings()
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], settings,
                                             'feeds/all.atom.xml',
                                             'feeds/all.atom.xml')

        generator = ArticlesGenerator(
            context=settings, settings=get_settings(FEED_ALL_ATOM=None),
            path=None, theme=settings['THEME'], output_path=None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_feeds_override_url(self):
        settings = get_settings()
        settings['CACHE_PATH'] = self.temp_cache
        settings['FEED_ALL_ATOM_URL'] = 'feeds/atom/all/'
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], settings,
                                             'feeds/all.atom.xml',
                                             'feeds/atom/all/')

    def test_generate_context(self):
        articles_expected = [
            ['Article title', 'published', 'Default', 'article'],
            ['Article with markdown and summary metadata multi', 'published',
             'Default', 'article'],
            ['Article with markdown and nested summary metadata', 'published',
             'Default', 'article'],
            ['Article with markdown and summary metadata single', 'published',
             'Default', 'article'],
            ['Article with markdown containing footnotes', 'published',
             'Default', 'article'],
            ['Article with template', 'published', 'Default', 'custom'],
            ['Metadata tags as list!', 'published', 'Default', 'article'],
            ['Rst with filename metadata', 'published', 'yeah', 'article'],
            ['One -, two --, three --- dashes!', 'published', 'Default',
             'article'],
            ['One -, two --, three --- dashes!', 'published', 'Default',
             'article'],
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
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'yeah', 'article'],
            ['This is a super article !', 'published', 'Default', 'article'],
            ['Article with an inline SVG', 'published', 'Default', 'article'],
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
        settings = get_settings()
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['USE_FOLDER_AS_CATEGORY'] = False
        settings['CACHE_PATH'] = self.temp_cache
        settings['READERS'] = {'asc': None}
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
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

    def test_direct_templates_save_as_url_default(self):

        settings = get_settings()
        settings['CACHE_PATH'] = self.temp_cache
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives.html",
                                 generator.get_template("archives"), context,
                                 articles=generator.articles,
                                 dates=generator.dates, blog=True,
                                 template_name='archives',
                                 page_name='archives', url="archives.html")

    def test_direct_templates_save_as_url_modified(self):

        settings = get_settings()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        settings['ARCHIVES_URL'] = 'archives/'
        settings['CACHE_PATH'] = self.temp_cache
        generator = ArticlesGenerator(
            context=settings, settings=settings,
            path=None, theme=settings['THEME'], output_path=None)
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives/index.html",
                                 generator.get_template("archives"), settings,
                                 articles=generator.articles,
                                 dates=generator.dates, blog=True,
                                 template_name='archives',
                                 page_name='archives/index',
                                 url="archives/")

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

    def test_period_in_timeperiod_archive(self):
        """
        Test that the context of a generated period_archive is passed
        'period' : a tuple of year, month, day according to the time period
        """
        old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
        settings = get_settings()

        settings['YEAR_ARCHIVE_SAVE_AS'] = 'posts/{date:%Y}/index.html'
        settings['YEAR_ARCHIVE_URL'] = 'posts/{date:%Y}/'
        settings['CACHE_PATH'] = self.temp_cache
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates if d.date.year == 1970]
        articles = [d for d in generator.articles if d.date.year == 1970]
        self.assertEqual(len(dates), 1)
        # among other things it must have at least been called with this
        context["period"] = (1970,)
        write.assert_called_with("posts/1970/index.html",
                                 generator.get_template("period_archives"),
                                 context, blog=True, articles=articles,
                                 dates=dates, template_name='period_archives',
                                 url="posts/1970/",
                                 all_articles=generator.articles)

        settings['MONTH_ARCHIVE_SAVE_AS'] = \
            'posts/{date:%Y}/{date:%b}/index.html'
        settings['MONTH_ARCHIVE_URL'] = \
            'posts/{date:%Y}/{date:%b}/'
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        write = MagicMock()
        generator.generate_period_archives(write)
        dates = [d for d in generator.dates
                 if d.date.year == 1970 and d.date.month == 1]
        articles = [d for d in generator.articles
                    if d.date.year == 1970 and d.date.month == 1]
        self.assertEqual(len(dates), 1)
        context["period"] = (1970, "January")
        # among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/index.html",
                                 generator.get_template("period_archives"),
                                 context, blog=True, articles=articles,
                                 dates=dates, template_name='period_archives',
                                 url="posts/1970/Jan/",
                                 all_articles=generator.articles)

        settings['DAY_ARCHIVE_SAVE_AS'] = \
            'posts/{date:%Y}/{date:%b}/{date:%d}/index.html'
        settings['DAY_ARCHIVE_URL'] = \
            'posts/{date:%Y}/{date:%b}/{date:%d}/'
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
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
        articles = [
            d for d in generator.articles if
            d.date.year == 1970 and
            d.date.month == 1 and
            d.date.day == 1
        ]
        self.assertEqual(len(dates), 1)
        context["period"] = (1970, "January", 1)
        # among other things it must have at least been called with this
        write.assert_called_with("posts/1970/Jan/01/index.html",
                                 generator.get_template("period_archives"),
                                 context, blog=True, articles=articles,
                                 dates=dates, template_name='period_archives',
                                 url="posts/1970/Jan/01/",
                                 all_articles=generator.articles)
        locale.setlocale(locale.LC_ALL, old_locale)

    def test_nonexistent_template(self):
        """Attempt to load a non-existent template"""
        settings = get_settings()
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
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
        settings = get_settings()
        settings['CACHE_CONTENT'] = False
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['DEFAULT_METADATA'] = (('author', 'Blogger'),
                                        # category will be ignored in favor of
                                        # DEFAULT_CATEGORY
                                        ('category', 'Random'),
                                        ('tags', 'general, untagged'))
        context = get_context(settings)
        generator = ArticlesGenerator(
            context=context, settings=settings,
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
        settings = get_settings()
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['ARTICLE_ORDER_BY'] = 'title'
        context = get_context(settings)

        generator = ArticlesGenerator(
            context=context, settings=settings,
            path=CONTENT_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()

        expected = [
            'An Article With Code Block To Test Typogrify Ignore',
            'Article title',
            'Article with Nonconformant HTML meta tags',
            'Article with an inline SVG',
            'Article with markdown and nested summary metadata',
            'Article with markdown and summary metadata multi',
            'Article with markdown and summary metadata single',
            'Article with markdown containing footnotes',
            'Article with template',
            'Metadata tags as list!',
            'One -, two --, three --- dashes!',
            'One -, two --, three --- dashes!',
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
        settings = get_settings()
        settings['DEFAULT_CATEGORY'] = 'Default'
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        settings['ARTICLE_ORDER_BY'] = 'reversed-title'
        context = get_context(settings)

        generator = ArticlesGenerator(
            context=context, settings=settings,
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
        settings = get_settings()
        settings['CACHE_PATH'] = self.temp_cache
        settings['PAGE_PATHS'] = ['TestPages']  # relative to CUR_DIR
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        context = get_context(settings)

        generator = PagesGenerator(
            context=context, settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        hidden_pages = self.distill_pages(generator.hidden_pages)
        draft_pages = self.distill_pages(generator.draft_pages)

        pages_expected = [
            ['This is a test page', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom'],
            ['Page with a bunch of links', 'published', 'page'],
            ['Page with static links', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
        ]
        hidden_pages_expected = [
            ['This is a test hidden page', 'hidden', 'page'],
            ['This is a markdown test hidden page', 'hidden', 'page'],
            ['This is a test hidden page with a custom template', 'hidden',
             'custom'],
        ]
        draft_pages_expected = [
            ['This is a test draft page', 'draft', 'page'],
            ['This is a markdown test draft page', 'draft', 'page'],
            ['This is a test draft page with a custom template', 'draft',
             'custom'],
        ]

        self.assertEqual(sorted(pages_expected), sorted(pages))
        self.assertEqual(
            sorted(pages_expected),
            sorted(self.distill_pages(generator.context['pages'])))
        self.assertEqual(sorted(hidden_pages_expected), sorted(hidden_pages))
        self.assertEqual(sorted(draft_pages_expected), sorted(draft_pages))
        self.assertEqual(
            sorted(hidden_pages_expected),
            sorted(self.distill_pages(generator.context['hidden_pages'])))
        self.assertEqual(
            sorted(draft_pages_expected),
            sorted(self.distill_pages(generator.context['draft_pages'])))

    def test_generate_sorted(self):
        settings = get_settings()
        settings['PAGE_PATHS'] = ['TestPages']  # relative to CUR_DIR
        settings['CACHE_PATH'] = self.temp_cache
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        context = get_context(settings)

        # default sort (filename)
        pages_expected_sorted_by_filename = [
            ['This is a test page', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['Page with static links', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom'],
        ]
        generator = PagesGenerator(
            context=context, settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        self.assertEqual(pages_expected_sorted_by_filename, pages)

        # sort by title
        pages_expected_sorted_by_title = [
            ['A Page (Test) for sorting', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['Page with static links', 'published', 'page'],
            ['This is a markdown test page', 'published', 'page'],
            ['This is a test page', 'published', 'page'],
            ['This is a test page with a preset template', 'published',
             'custom'],
        ]
        settings['PAGE_ORDER_BY'] = 'title'
        context = get_context(settings)
        generator = PagesGenerator(
            context=context.copy(), settings=settings,
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
            ['Page with static links', 'published', 'page'],
            ['Page with a bunch of links', 'published', 'page'],
            ['A Page (Test) for sorting', 'published', 'page'],
        ]
        settings['PAGE_ORDER_BY'] = 'reversed-title'
        context = get_context(settings)
        generator = PagesGenerator(
            context=context, settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        self.assertEqual(pages_expected_sorted_by_title, pages)

    def test_tag_and_category_links_on_generated_pages(self):
        """
        Test to ensure links of the form {tag}tagname and {category}catname
        are generated correctly on pages
        """
        settings = get_settings()
        settings['PAGE_PATHS'] = ['TestPages']    # relative to CUR_DIR
        settings['CACHE_PATH'] = self.temp_cache
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        context = get_context(settings)

        generator = PagesGenerator(
            context=context, settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()
        pages_by_title = {p.title: p for p in generator.pages}

        test_content = pages_by_title['Page with a bunch of links'].content
        self.assertIn('<a href="/category/yeah.html">', test_content)
        self.assertIn('<a href="/tag/matsuku.html">', test_content)

    def test_static_and_attach_links_on_generated_pages(self):
        """
        Test to ensure links of the form {static}filename and {attach}filename
        are included in context['static_links']
        """
        settings = get_settings()
        settings['PAGE_PATHS'] = ['TestPages/page_with_static_links.md']
        settings['CACHE_PATH'] = self.temp_cache
        settings['DEFAULT_DATE'] = (1970, 1, 1)
        context = get_context(settings)

        generator = PagesGenerator(
            context=context, settings=settings,
            path=CUR_DIR, theme=settings['THEME'], output_path=None)
        generator.generate_context()

        self.assertIn('pelican/tests/TestPages/image0.jpg',
                      context['static_links'])
        self.assertIn('pelican/tests/TestPages/image1.jpg',
                      context['static_links'])


class TestTemplatePagesGenerator(unittest.TestCase):

    TEMPLATE_CONTENT = "foo: {{ foo }}"

    def setUp(self):
        self.temp_content = mkdtemp(prefix='pelicantests.')
        self.temp_output = mkdtemp(prefix='pelicantests.')
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

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
        with open(output_path) as output_file:
            self.assertEqual(output_file.read(), 'foo: bar')


class TestStaticGenerator(unittest.TestCase):

    def setUp(self):
        self.content_path = os.path.join(CUR_DIR, 'mixed_content')
        self.temp_content = mkdtemp(prefix='testcontent.')
        self.temp_output = mkdtemp(prefix='testoutput.')
        self.settings = get_settings()
        self.settings['PATH'] = self.temp_content
        self.settings['STATIC_PATHS'] = ["static"]
        self.settings['OUTPUT_PATH'] = self.temp_output
        os.mkdir(os.path.join(self.temp_content, "static"))
        self.startfile = os.path.join(self.temp_content,
                                      "static", "staticfile")
        self.endfile = os.path.join(self.temp_output, "static", "staticfile")
        self.generator = StaticGenerator(
            context=get_context(),
            settings=self.settings,
            path=self.temp_content,
            theme="",
            output_path=self.temp_output,
            )

    def tearDown(self):
        rmtree(self.temp_content)
        rmtree(self.temp_output)

    def set_ancient_mtime(self, path, timestamp=1):
        os.utime(path, (timestamp, timestamp))

    def test_theme_static_paths_dirs(self):
        """Test that StaticGenerator properly copies also files mentioned in
           TEMPLATE_STATIC_PATHS, not just directories."""
        settings = get_settings(PATH=self.content_path)
        context = get_context(settings, staticfiles=[])

        StaticGenerator(
            context=context, settings=settings,
            path=settings['PATH'], output_path=self.temp_output,
            theme=settings['THEME']).generate_output(None)

        # The content of dirs listed in THEME_STATIC_PATHS (defaulting to
        # "static") is put into the output
        self.assertTrue(os.path.isdir(os.path.join(self.temp_output,
                                                   "theme/css/")))
        self.assertTrue(os.path.isdir(os.path.join(self.temp_output,
                                                   "theme/fonts/")))

    def test_theme_static_paths_files(self):
        """Test that StaticGenerator properly copies also files mentioned in
           TEMPLATE_STATIC_PATHS, not just directories."""
        settings = get_settings(
            PATH=self.content_path,
            THEME_STATIC_PATHS=['static/css/fonts.css', 'static/fonts/'],)
        context = get_context(settings, staticfiles=[])

        StaticGenerator(
            context=context, settings=settings,
            path=settings['PATH'], output_path=self.temp_output,
            theme=settings['THEME']).generate_output(None)

        # Only the content of dirs and files listed in THEME_STATIC_PATHS are
        # put into the output, not everything from static/
        self.assertFalse(os.path.isdir(os.path.join(self.temp_output,
                                                    "theme/css/")))
        self.assertFalse(os.path.isdir(os.path.join(self.temp_output,
                                                    "theme/fonts/")))

        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_output, "theme/Yanone_Kaffeesatz_400.eot")))
        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_output, "theme/Yanone_Kaffeesatz_400.svg")))
        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_output, "theme/Yanone_Kaffeesatz_400.ttf")))
        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_output, "theme/Yanone_Kaffeesatz_400.woff")))
        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_output, "theme/Yanone_Kaffeesatz_400.woff2")))
        self.assertTrue(os.path.isfile(os.path.join(self.temp_output,
                                                    "theme/font.css")))
        self.assertTrue(os.path.isfile(os.path.join(self.temp_output,
                                                    "theme/fonts.css")))

    def test_static_excludes(self):
        """Test that StaticGenerator respects STATIC_EXCLUDES.
        """
        settings = get_settings(
            STATIC_EXCLUDES=['subdir'],
            PATH=self.content_path,
            STATIC_PATHS=[''],)
        context = get_context(settings)

        StaticGenerator(
            context=context, settings=settings,
            path=settings['PATH'], output_path=self.temp_output,
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
            CACHE_CONTENT=False,)
        context = get_context(settings)

        for generator_class in (PagesGenerator, StaticGenerator):
            generator_class(
                context=context, settings=settings,
                path=settings['PATH'], output_path=self.temp_output,
                theme=settings['THEME']).generate_context()

        staticnames = [os.path.basename(c.source_path)
                       for c in context['staticfiles']]

        self.assertFalse(
            any(name.endswith(".md") for name in staticnames),
            "STATIC_EXCLUDE_SOURCES=True failed to exclude a markdown file")

        settings.update(STATIC_EXCLUDE_SOURCES=False)
        context = get_context(settings)

        for generator_class in (PagesGenerator, StaticGenerator):
            generator_class(
                context=context, settings=settings,
                path=settings['PATH'], output_path=self.temp_output,
                theme=settings['THEME']).generate_context()

        staticnames = [os.path.basename(c.source_path)
                       for c in context['staticfiles']]

        self.assertTrue(
            any(name.endswith(".md") for name in staticnames),
            "STATIC_EXCLUDE_SOURCES=False failed to include a markdown file")

    def test_static_links(self):
        """Test that StaticGenerator uses files in static_links
        """
        settings = get_settings(
            STATIC_EXCLUDES=['subdir'],
            PATH=self.content_path,
            STATIC_PATHS=[],)
        context = get_context(settings)
        context['static_links'] |= {'short_page.md', 'subdir_fake_image.jpg'}

        StaticGenerator(
            context=context, settings=settings,
            path=settings['PATH'], output_path=self.temp_output,
            theme=settings['THEME']).generate_context()

        staticfiles_names = [
            os.path.basename(c.source_path) for c in context['staticfiles']]

        static_content_names = [
            os.path.basename(c) for c in context['static_content']]

        self.assertIn(
            'short_page.md', staticfiles_names,
            "StaticGenerator skipped a file that it should have included")
        self.assertIn(
            'short_page.md', static_content_names,
            "StaticGenerator skipped a file that it should have included")
        self.assertIn(
            'subdir_fake_image.jpg', staticfiles_names,
            "StaticGenerator skipped a file that it should have included")
        self.assertIn(
            'subdir_fake_image.jpg', static_content_names,
            "StaticGenerator skipped a file that it should have included")

    def test_copy_one_file(self):
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        self.generator.generate_context()
        self.generator.generate_output(None)
        with open(self.endfile) as f:
            self.assertEqual(f.read(), "staticcontent")

    def test_file_update_required_when_dest_does_not_exist(self):
        staticfile = MagicMock()
        staticfile.source_path = self.startfile
        staticfile.save_as = self.endfile
        with open(staticfile.source_path, "w") as f:
            f.write("a")
        update_required = self.generator._file_update_required(staticfile)
        self.assertTrue(update_required)

    def test_dest_and_source_mtimes_are_equal(self):
        staticfile = MagicMock()
        staticfile.source_path = self.startfile
        staticfile.save_as = self.endfile
        self.settings['STATIC_CHECK_IF_MODIFIED'] = True
        with open(staticfile.source_path, "w") as f:
            f.write("a")
        os.mkdir(os.path.join(self.temp_output, "static"))
        copy(staticfile.source_path, staticfile.save_as)
        isnewer = self.generator._source_is_newer(staticfile)
        self.assertFalse(isnewer)

    def test_source_is_newer(self):
        staticfile = MagicMock()
        staticfile.source_path = self.startfile
        staticfile.save_as = self.endfile
        with open(staticfile.source_path, "w") as f:
            f.write("a")
        os.mkdir(os.path.join(self.temp_output, "static"))
        copy(staticfile.source_path, staticfile.save_as)
        self.set_ancient_mtime(staticfile.save_as)
        isnewer = self.generator._source_is_newer(staticfile)
        self.assertTrue(isnewer)

    def test_skip_file_when_source_is_not_newer(self):
        self.settings['STATIC_CHECK_IF_MODIFIED'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        os.mkdir(os.path.join(self.temp_output, "static"))
        with open(self.endfile, "w") as f:
            f.write("staticcontent")
        expected = os.path.getmtime(self.endfile)
        self.set_ancient_mtime(self.startfile)
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertEqual(os.path.getmtime(self.endfile), expected)

    def test_dont_link_by_default(self):
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertFalse(os.path.samefile(self.startfile, self.endfile))

    def test_output_file_is_linked_to_source(self):
        self.settings['STATIC_CREATE_LINKS'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertTrue(os.path.samefile(self.startfile, self.endfile))

    def test_output_file_exists_and_is_newer(self):
        self.settings['STATIC_CREATE_LINKS'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        os.mkdir(os.path.join(self.temp_output, "static"))
        with open(self.endfile, "w") as f:
            f.write("othercontent")
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertTrue(os.path.samefile(self.startfile, self.endfile))

    @unittest.skipUnless(can_symlink(), 'No symlink privilege')
    def test_can_symlink_when_hardlink_not_possible(self):
        self.settings['STATIC_CREATE_LINKS'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        os.mkdir(os.path.join(self.temp_output, "static"))
        self.generator.fallback_to_symlinks = True
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertTrue(os.path.islink(self.endfile))

    @unittest.skipUnless(can_symlink(), 'No symlink privilege')
    def test_existing_symlink_is_considered_up_to_date(self):
        self.settings['STATIC_CREATE_LINKS'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        os.mkdir(os.path.join(self.temp_output, "static"))
        os.symlink(self.startfile, self.endfile)
        staticfile = MagicMock()
        staticfile.source_path = self.startfile
        staticfile.save_as = self.endfile
        requires_update = self.generator._file_update_required(staticfile)
        self.assertFalse(requires_update)

    @unittest.skipUnless(can_symlink(), 'No symlink privilege')
    def test_invalid_symlink_is_overwritten(self):
        self.settings['STATIC_CREATE_LINKS'] = True
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        os.mkdir(os.path.join(self.temp_output, "static"))
        os.symlink("invalid", self.endfile)
        staticfile = MagicMock()
        staticfile.source_path = self.startfile
        staticfile.save_as = self.endfile
        requires_update = self.generator._file_update_required(staticfile)
        self.assertTrue(requires_update)
        self.generator.fallback_to_symlinks = True
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertTrue(os.path.islink(self.endfile))

        # os.path.realpath is broken on Windows before python3.8 for symlinks.
        # This is a (ugly) workaround.
        # see: https://bugs.python.org/issue9949
        if os.name == 'nt' and sys.version_info < (3, 8):
            def get_real_path(path):
                return os.readlink(path) if os.path.islink(path) else path
        else:
            get_real_path = os.path.realpath

        self.assertEqual(get_real_path(self.endfile),
                         get_real_path(self.startfile))

    def test_delete_existing_file_before_mkdir(self):
        with open(self.startfile, "w") as f:
            f.write("staticcontent")
        with open(os.path.join(self.temp_output, "static"), "w") as f:
            f.write("This file should be a directory")
        self.generator.generate_context()
        self.generator.generate_output(None)
        self.assertTrue(
            os.path.isdir(os.path.join(self.temp_output, "static")))
        self.assertTrue(os.path.isfile(self.endfile))


class TestJinja2Environment(unittest.TestCase):

    def setUp(self):
        self.temp_content = mkdtemp(prefix='pelicantests.')
        self.temp_output = mkdtemp(prefix='pelicantests.')
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

    def tearDown(self):
        rmtree(self.temp_content)
        rmtree(self.temp_output)
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def _test_jinja2_helper(self, additional_settings, content, expected):
        settings = get_settings()
        settings['STATIC_PATHS'] = ['static']
        settings['TEMPLATE_PAGES'] = {
            'template/source.html': 'generated/file.html'
        }
        settings.update(additional_settings)

        generator = TemplatePagesGenerator(
            context={'foo': 'foo', 'bar': 'bar'}, settings=settings,
            path=self.temp_content, theme='', output_path=self.temp_output)

        # create a dummy template file
        template_dir = os.path.join(self.temp_content, 'template')
        template_path = os.path.join(template_dir, 'source.html')
        os.makedirs(template_dir)
        with open(template_path, 'w') as template_file:
            template_file.write(content)

        writer = Writer(self.temp_output, settings=settings)
        generator.generate_output(writer)

        output_path = os.path.join(self.temp_output, 'generated', 'file.html')

        # output file has been generated
        self.assertTrue(os.path.exists(output_path))

        # output content is correct
        with open(output_path) as output_file:
            self.assertEqual(output_file.read(), expected)

    def test_jinja2_filter(self):
        """JINJA_FILTERS adds custom filters to Jinja2 environment"""
        content = 'foo: {{ foo|custom_filter }}, bar: {{ bar|custom_filter }}'
        settings = {'JINJA_FILTERS': {'custom_filter': lambda x: x.upper()}}
        expected = 'foo: FOO, bar: BAR'

        self._test_jinja2_helper(settings, content, expected)

    def test_jinja2_test(self):
        """JINJA_TESTS adds custom tests to Jinja2 environment"""
        content = 'foo {{ foo is custom_test }}, bar {{ bar is custom_test }}'
        settings = {'JINJA_TESTS': {'custom_test': lambda x: x == 'bar'}}
        expected = 'foo False, bar True'

        self._test_jinja2_helper(settings, content, expected)

    def test_jinja2_global(self):
        """JINJA_GLOBALS adds custom globals to Jinja2 environment"""
        content = '{{ custom_global }}'
        settings = {'JINJA_GLOBALS': {'custom_global': 'foobar'}}
        expected = 'foobar'

        self._test_jinja2_helper(settings, content, expected)

    def test_jinja2_extension(self):
        """JINJA_ENVIRONMENT adds extensions to Jinja2 environment"""
        content = '{% set stuff = [] %}{% do stuff.append(1) %}{{ stuff }}'
        settings = {'JINJA_ENVIRONMENT': {'extensions': ['jinja2.ext.do']}}
        expected = '[1]'

        self._test_jinja2_helper(settings, content, expected)
