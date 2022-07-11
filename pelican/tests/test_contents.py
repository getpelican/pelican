import datetime
import locale
import logging
import os.path
from posixpath import join as posix_join
from sys import platform

from jinja2.utils import generate_lorem_ipsum

from pelican.contents import Article, Author, Category, Page, Static
from pelican.plugins.signals import content_object_init
from pelican.settings import DEFAULT_CONFIG
from pelican.tests.support import (LoggedTestCase, get_context, get_settings,
                                   unittest)
from pelican.utils import (path_to_url, posixize_path, truncate_html_words)


# generate one paragraph, enclosed with <p>
TEST_CONTENT = str(generate_lorem_ipsum(n=1))
TEST_SUMMARY = generate_lorem_ipsum(n=1, html=False)


class TestBase(LoggedTestCase):

    def setUp(self):
        super().setUp()
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
        self.page_kwargs = {
            'content': TEST_CONTENT,
            'context': {
                'localsiteurl': '',
                'generated_content': {},
                'static_content': {},
                'static_links': set()
            },
            'metadata': {
                'summary': TEST_SUMMARY,
                'title': 'foo bar',
                'author': Author('Blogger', DEFAULT_CONFIG),
            },
            'source_path': '/path/to/file/foo.ext'
        }
        self._disable_limit_filter()

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)
        self._enable_limit_filter()

    def _disable_limit_filter(self):
        from pelican.contents import logger
        logger.disable_filter()

    def _enable_limit_filter(self):
        from pelican.contents import logger
        logger.enable_filter()

    def _copy_page_kwargs(self):
        # make a deep copy of page_kwargs
        page_kwargs = {key: self.page_kwargs[key] for key in self.page_kwargs}
        for key in page_kwargs:
            if not isinstance(page_kwargs[key], dict):
                break
            page_kwargs[key] = {
                subkey: page_kwargs[key][subkey] for subkey in page_kwargs[key]
            }

        return page_kwargs


class TestPage(TestBase):
    def test_use_args(self):
        # Creating a page with arguments passed to the constructor should use
        # them to initialise object's attributes.
        metadata = {'foo': 'bar', 'foobar': 'baz', 'title': 'foobar', }
        page = Page(TEST_CONTENT, metadata=metadata,
                    context={'localsiteurl': ''})
        for key, value in metadata.items():
            self.assertTrue(hasattr(page, key))
            self.assertEqual(value, getattr(page, key))
        self.assertEqual(page.content, TEST_CONTENT)

    def test_mandatory_properties(self):
        # If the title is not set, must throw an exception.
        page = Page('content')
        self.assertFalse(page._has_valid_mandatory_properties())
        self.assertLogCountEqual(
                count=1,
                msg="Skipping .*: could not find information about 'title'",
                level=logging.ERROR)
        page = Page('content', metadata={'title': 'foobar'})
        self.assertTrue(page._has_valid_mandatory_properties())

    def test_summary_from_metadata(self):
        # If a :summary: metadata is given, it should be used
        page = Page(**self.page_kwargs)
        self.assertEqual(page.summary, TEST_SUMMARY)

    def test_summary_max_length(self):
        # If a :SUMMARY_MAX_LENGTH: is set, and there is no other summary,
        # generated summary should not exceed the given length.
        page_kwargs = self._copy_page_kwargs()
        settings = get_settings()
        page_kwargs['settings'] = settings
        del page_kwargs['metadata']['summary']
        settings['SUMMARY_MAX_LENGTH'] = None
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, TEST_CONTENT)
        settings['SUMMARY_MAX_LENGTH'] = 10
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, truncate_html_words(TEST_CONTENT, 10))
        settings['SUMMARY_MAX_LENGTH'] = 0
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, '')

    def test_summary_end_suffix(self):
        # If a :SUMMARY_END_SUFFIX: is set, and there is no other summary,
        # generated summary should contain the specified marker at the end.
        page_kwargs = self._copy_page_kwargs()
        settings = get_settings()
        page_kwargs['settings'] = settings
        del page_kwargs['metadata']['summary']
        settings['SUMMARY_END_SUFFIX'] = 'test_marker'
        settings['SUMMARY_MAX_LENGTH'] = 10
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, truncate_html_words(TEST_CONTENT, 10,
                                                           'test_marker'))
        self.assertIn('test_marker', page.summary)

    def test_summary_get_summary_warning(self):
        """calling ._get_summary() should issue a warning"""
        page_kwargs = self._copy_page_kwargs()
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, TEST_SUMMARY)
        self.assertEqual(page._get_summary(), TEST_SUMMARY)
        self.assertLogCountEqual(
                count=1,
                msg=r"_get_summary\(\) has been deprecated since 3\.6\.4\. "
                    "Use the summary decorator instead",
                level=logging.WARNING)

    def test_slug(self):
        page_kwargs = self._copy_page_kwargs()
        settings = get_settings()
        page_kwargs['settings'] = settings
        settings['SLUGIFY_SOURCE'] = "title"
        page = Page(**page_kwargs)
        self.assertEqual(page.slug, 'foo-bar')
        settings['SLUGIFY_SOURCE'] = "basename"
        page = Page(**page_kwargs)
        self.assertEqual(page.slug, 'foo')

        # test slug from title with unicode and case

        inputs = (
            # (title, expected, preserve_case, use_unicode)
            ('指導書', 'zhi-dao-shu', False, False),
            ('指導書', 'Zhi-Dao-Shu', True, False),
            ('指導書', '指導書', False, True),
            ('指導書', '指導書', True, True),
            ('Çığ', 'cig', False, False),
            ('Çığ', 'Cig', True, False),
            ('Çığ', 'çığ', False, True),
            ('Çığ', 'Çığ', True, True),
        )

        settings = get_settings()
        page_kwargs = self._copy_page_kwargs()
        page_kwargs['settings'] = settings

        for title, expected, preserve_case, use_unicode in inputs:
            settings['SLUGIFY_PRESERVE_CASE'] = preserve_case
            settings['SLUGIFY_USE_UNICODE'] = use_unicode
            page_kwargs['metadata']['title'] = title
            page = Page(**page_kwargs)
            self.assertEqual(page.slug, expected,
                             (title, preserve_case, use_unicode))

    def test_defaultlang(self):
        # If no lang is given, default to the default one.
        page = Page(**self.page_kwargs)
        self.assertEqual(page.lang, DEFAULT_CONFIG['DEFAULT_LANG'])

        # it is possible to specify the lang in the metadata infos
        self.page_kwargs['metadata'].update({'lang': 'fr', })
        page = Page(**self.page_kwargs)
        self.assertEqual(page.lang, 'fr')

    def test_save_as(self):
        # If a lang is not the default lang, save_as should be set
        # accordingly.

        # if a title is defined, save_as should be set
        page = Page(**self.page_kwargs)
        self.assertEqual(page.save_as, "pages/foo-bar.html")

        # if a language is defined, save_as should include it accordingly
        self.page_kwargs['metadata'].update({'lang': 'fr', })
        page = Page(**self.page_kwargs)
        self.assertEqual(page.save_as, "pages/foo-bar-fr.html")

    def test_relative_source_path(self):
        # 'relative_source_path' should be the relative path
        # from 'PATH' to 'source_path'
        page_kwargs = self._copy_page_kwargs()

        # If 'source_path' is None, 'relative_source_path' should
        # also return None
        page_kwargs['source_path'] = None
        page = Page(**page_kwargs)
        self.assertIsNone(page.relative_source_path)

        page_kwargs = self._copy_page_kwargs()
        settings = get_settings()
        full_path = page_kwargs['source_path']

        settings['PATH'] = os.path.dirname(full_path)
        page_kwargs['settings'] = settings
        page = Page(**page_kwargs)

        # if 'source_path' is set, 'relative_source_path' should
        # return the relative path from 'PATH' to 'source_path'
        self.assertEqual(
            page.relative_source_path,
            os.path.relpath(
                full_path,
                os.path.dirname(full_path)
            ))

    def test_metadata_url_format(self):
        # Arbitrary metadata should be passed through url_format()
        page = Page(**self.page_kwargs)
        self.assertIn('summary', page.url_format.keys())
        page.metadata['directory'] = 'test-dir'
        page.settings = get_settings(PAGE_SAVE_AS='{directory}/{slug}')
        self.assertEqual(page.save_as, 'test-dir/foo-bar')

    def test_datetime(self):
        # If DATETIME is set to a tuple, it should be used to override LOCALE
        dt = datetime.datetime(2015, 9, 13)

        page_kwargs = self._copy_page_kwargs()

        # set its date to dt
        page_kwargs['metadata']['date'] = dt
        page = Page(**page_kwargs)

        # page.locale_date is a unicode string in both python2 and python3
        dt_date = dt.strftime(DEFAULT_CONFIG['DEFAULT_DATE_FORMAT'])

        self.assertEqual(page.locale_date, dt_date)
        page_kwargs['settings'] = get_settings()

        # I doubt this can work on all platforms ...
        if platform == "win32":
            locale = 'jpn'
        else:
            locale = 'ja_JP.utf8'
        page_kwargs['settings']['DATE_FORMATS'] = {'jp': (locale,
                                                          '%Y-%m-%d(%a)')}
        page_kwargs['metadata']['lang'] = 'jp'

        import locale as locale_module
        try:
            page = Page(**page_kwargs)
            self.assertEqual(page.locale_date, '2015-09-13(\u65e5)')
        except locale_module.Error:
            # The constructor of ``Page`` will try to set the locale to
            # ``ja_JP.utf8``. But this attempt will failed when there is no
            # such locale in the system. You can see which locales there are
            # in your system with ``locale -a`` command.
            #
            # Until we find some other method to test this functionality, we
            # will simply skip this test.
            unittest.skip("There is no locale %s in this system." % locale)

    def test_template(self):
        # Pages default to page, metadata overwrites
        default_page = Page(**self.page_kwargs)
        self.assertEqual('page', default_page.template)
        page_kwargs = self._copy_page_kwargs()
        page_kwargs['metadata']['template'] = 'custom'
        custom_page = Page(**page_kwargs)
        self.assertEqual('custom', custom_page.template)

    def test_signal(self):
        def receiver_test_function(sender):
            receiver_test_function.has_been_called = True
            pass
        receiver_test_function.has_been_called = False

        content_object_init.connect(receiver_test_function)
        self.assertIn(
            receiver_test_function,
            content_object_init.receivers_for(Page))

        self.assertFalse(receiver_test_function.has_been_called)
        Page(**self.page_kwargs)
        self.assertTrue(receiver_test_function.has_been_called)

    def test_get_content(self):
        # Test that the content is updated with the relative links to
        # filenames, tags and categories.
        settings = get_settings()
        args = self.page_kwargs.copy()
        args['settings'] = settings

        # Tag
        args['content'] = ('A simple test, with a '
                           '<a href="|tag|tagname">link</a>')
        page = Page(**args)
        content = page.get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            ('A simple test, with a '
             '<a href="http://notmyidea.org/tag/tagname.html">link</a>'))

        # Category
        args['content'] = ('A simple test, with a '
                           '<a href="|category|category">link</a>')
        page = Page(**args)
        content = page.get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            ('A simple test, with a '
             '<a href="http://notmyidea.org/category/category.html">link</a>'))

    def test_intrasite_link(self):
        cls_name = '_DummyArticle'
        article = type(cls_name, (object,), {'url': 'article.html'})

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['generated_content'] = {'article.rst': article}

        # Classic intrasite link via filename
        args['content'] = (
            'A simple test, with a '
            '<a href="|filename|article.rst">link</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a '
            '<a href="http://notmyidea.org/article.html">link</a>'
        )

        # fragment
        args['content'] = (
            'A simple test, with a '
            '<a href="|filename|article.rst#section-2">link</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a '
            '<a href="http://notmyidea.org/article.html#section-2">link</a>'
        )

        # query
        args['content'] = (
            'A simple test, with a '
            '<a href="|filename|article.rst'
            '?utm_whatever=234&highlight=word">link</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a '
            '<a href="http://notmyidea.org/article.html'
            '?utm_whatever=234&highlight=word">link</a>'
        )

        # combination
        args['content'] = (
            'A simple test, with a '
            '<a href="|filename|article.rst'
            '?utm_whatever=234&highlight=word#section-2">link</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a '
            '<a href="http://notmyidea.org/article.html'
            '?utm_whatever=234&highlight=word#section-2">link</a>'
        )

        # also test for summary in metadata
        parsed = (
            'A simple summary test, with a '
            '<a href="|filename|article.rst">link</a>'
        )
        linked = (
            'A simple summary test, with a '
            '<a href="http://notmyidea.org/article.html">link</a>'
        )
        args['settings']['FORMATTED_FIELDS'] = ['summary', 'custom']
        args['metadata']['summary'] = parsed
        args['metadata']['custom'] = parsed
        args['context']['localsiteurl'] = 'http://notmyidea.org'
        p = Page(**args)
        # This is called implicitly from all generators and Pelican.run() once
        # all files are processed. Here we process just one page so it needs
        # to be called explicitly.
        p.refresh_metadata_intersite_links()
        self.assertEqual(p.summary, linked)
        self.assertEqual(p.custom, linked)

    def test_intrasite_link_more(self):
        cls_name = '_DummyAsset'

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['static_content'] = {
            'images/poster.jpg':
                type(cls_name, (object,), {'url': 'images/poster.jpg'}),
            'assets/video.mp4':
                type(cls_name, (object,), {'url': 'assets/video.mp4'}),
            'images/graph.svg':
                type(cls_name, (object,), {'url': 'images/graph.svg'}),
        }
        args['context']['generated_content'] = {
            'reference.rst':
                type(cls_name, (object,), {'url': 'reference.html'}),
        }

        # video.poster
        args['content'] = (
            'There is a video with poster '
            '<video controls poster="{static}/images/poster.jpg">'
            '<source src="|static|/assets/video.mp4" type="video/mp4">'
            '</video>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'There is a video with poster '
            '<video controls poster="http://notmyidea.org/images/poster.jpg">'
            '<source src="http://notmyidea.org/assets/video.mp4"'
            ' type="video/mp4">'
            '</video>'
        )

        # object.data
        args['content'] = (
            'There is a svg object '
            '<object data="{static}/images/graph.svg"'
            ' type="image/svg+xml">'
            '</object>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'There is a svg object '
            '<object data="http://notmyidea.org/images/graph.svg"'
            ' type="image/svg+xml">'
            '</object>'
        )

        # blockquote.cite
        args['content'] = (
            'There is a blockquote with cite attribute '
            '<blockquote cite="{filename}reference.rst">blah blah</blockquote>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'There is a blockquote with cite attribute '
            '<blockquote cite="http://notmyidea.org/reference.html">'
            'blah blah'
            '</blockquote>'
        )

    def test_intrasite_link_absolute(self):
        """Test that absolute URLs are merged properly."""

        args = self.page_kwargs.copy()
        args['settings'] = get_settings(
            STATIC_URL='http://static.cool.site/{path}',
            ARTICLE_URL='http://blog.cool.site/{slug}.html')
        args['source_path'] = 'content'
        args['context']['static_content'] = {
            'images/poster.jpg':
                Static('', settings=args['settings'],
                       source_path='images/poster.jpg'),
        }
        args['context']['generated_content'] = {
            'article.rst':
                Article('', settings=args['settings'], metadata={
                    'slug': 'article', 'title': 'Article'})
        }

        # Article link will go to blog
        args['content'] = (
            '<a href="{filename}article.rst">Article</a>'
        )
        content = Page(**args).get_content('http://cool.site')
        self.assertEqual(
            content,
            '<a href="http://blog.cool.site/article.html">Article</a>'
        )

        # Page link will go to the main site
        args['content'] = (
            '<a href="{index}">Index</a>'
        )
        content = Page(**args).get_content('http://cool.site')
        self.assertEqual(
            content,
            '<a href="http://cool.site/index.html">Index</a>'
        )

        # Image link will go to static
        args['content'] = (
            '<img src="{static}/images/poster.jpg"/>'
        )
        content = Page(**args).get_content('http://cool.site')
        self.assertEqual(
            content,
            '<img src="http://static.cool.site/images/poster.jpg"/>'
        )

        # Image link will go to static
        args['content'] = (
            '<meta content="{static}/images/poster.jpg"/>'
        )
        content = Page(**args).get_content('http://cool.site')
        self.assertEqual(
            content,
            '<meta content="http://static.cool.site/images/poster.jpg"/>'
        )

    def test_intrasite_link_escape(self):
        article = type(
            '_DummyArticle', (object,), {'url': 'article-spaces.html'})
        asset = type(
            '_DummyAsset', (object,), {'url': 'name@example.com'})

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['generated_content'] = {'article spaces.rst': article}
        args['context']['static_content'] = {'name@example.com': asset}

        expected_output = (
            'A simple test with a '
            '<a href="http://notmyidea.org/article-spaces.html#anchor">link</a> '
            '<a href="http://notmyidea.org/name@example.com#anchor">file</a>'
        )

        # not escaped
        args['content'] = (
            'A simple test with a '
            '<a href="{filename}article spaces.rst#anchor">link</a> '
            '<a href="{static}name@example.com#anchor">file</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(content, expected_output)

        # html escaped
        args['content'] = (
            'A simple test with a '
            '<a href="{filename}article spaces.rst#anchor">link</a> '
            '<a href="{static}name&#64;example.com#anchor">file</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(content, expected_output)

        # url escaped
        args['content'] = (
            'A simple test with a '
            '<a href="{filename}article%20spaces.rst#anchor">link</a> '
            '<a href="{static}name%40example.com#anchor">file</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(content, expected_output)

        # html and url escaped
        args['content'] = (
            'A simple test with a '
            '<a href="{filename}article%20spaces.rst#anchor">link</a> '
            '<a href="{static}name&#64;example.com#anchor">file</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(content, expected_output)

    def test_intrasite_link_markdown_spaces(self):
        cls_name = '_DummyArticle'
        article = type(cls_name, (object,), {'url': 'article-spaces.html'})

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['generated_content'] = {'article spaces.rst': article}

        # An intrasite link via filename with %20 as a space
        args['content'] = (
            'A simple test, with a '
            '<a href="|filename|article%20spaces.rst">link</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a '
            '<a href="http://notmyidea.org/article-spaces.html">link</a>'
        )

    def test_intrasite_link_source_and_generated(self):
        """Test linking both to the source and the generated article
        """
        cls_name = '_DummyAsset'

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['generated_content'] = {
            'article.rst': type(cls_name, (object,), {'url': 'article.html'})}
        args['context']['static_content'] = {
            'article.rst': type(cls_name, (object,), {'url': 'article.rst'})}

        args['content'] = (
            'A simple test, with a link to an'
            '<a href="{filename}article.rst">article</a> and its'
            '<a href="{static}article.rst">source</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a link to an'
            '<a href="http://notmyidea.org/article.html">article</a> and its'
            '<a href="http://notmyidea.org/article.rst">source</a>'
        )

    def test_intrasite_link_to_static_content_with_filename(self):
        """Test linking to a static resource with deprecated {filename}
        """
        cls_name = '_DummyAsset'

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['static_content'] = {
            'poster.jpg':
                type(cls_name, (object,), {'url': 'images/poster.jpg'})}

        args['content'] = (
            'A simple test, with a link to a'
            '<a href="{filename}poster.jpg">poster</a>'
        )
        content = Page(**args).get_content('http://notmyidea.org')
        self.assertEqual(
            content,
            'A simple test, with a link to a'
            '<a href="http://notmyidea.org/images/poster.jpg">poster</a>'
        )

    def test_multiple_authors(self):
        """Test article with multiple authors."""
        args = self.page_kwargs.copy()
        content = Page(**args)
        assert content.authors == [content.author]
        args['metadata'].pop('author')
        args['metadata']['authors'] = [Author('First Author', DEFAULT_CONFIG),
                                       Author('Second Author', DEFAULT_CONFIG)]
        content = Page(**args)
        assert content.authors
        assert content.author == content.authors[0]


class TestArticle(TestBase):
    def test_template(self):
        # Articles default to article, metadata overwrites
        default_article = Article(**self.page_kwargs)
        self.assertEqual('article', default_article.template)
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['template'] = 'custom'
        custom_article = Article(**article_kwargs)
        self.assertEqual('custom', custom_article.template)

    def test_slugify_category_author(self):
        settings = get_settings()
        settings['SLUG_REGEX_SUBSTITUTIONS'] = [
            (r'C#', 'csharp'),
            (r'[^\w\s-]', ''),
            (r'(?u)\A\s*', ''),
            (r'(?u)\s*\Z', ''),
            (r'[-\s]+', '-'),
        ]
        settings['ARTICLE_URL'] = '{author}/{category}/{slug}/'
        settings['ARTICLE_SAVE_AS'] = '{author}/{category}/{slug}/index.html'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['author'] = Author("O'Brien", settings)
        article_kwargs['metadata']['category'] = Category(
            'C# & stuff', settings)
        article_kwargs['metadata']['title'] = 'fnord'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'obrien/csharp-stuff/fnord/')
        self.assertEqual(
            article.save_as, 'obrien/csharp-stuff/fnord/index.html')

    def test_slugify_with_author_substitutions(self):
        settings = get_settings()
        settings['AUTHOR_REGEX_SUBSTITUTIONS'] = [
            ('Alexander Todorov', 'atodorov'),
            ('Krasimir Tsonev', 'krasimir'),
            (r'[^\w\s-]', ''),
            (r'(?u)\A\s*', ''),
            (r'(?u)\s*\Z', ''),
            (r'[-\s]+', '-'),
        ]
        settings['ARTICLE_URL'] = 'blog/{author}/{slug}/'
        settings['ARTICLE_SAVE_AS'] = 'blog/{author}/{slug}/index.html'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['author'] = Author('Alexander Todorov',
                                                      settings)
        article_kwargs['metadata']['title'] = 'fnord'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'blog/atodorov/fnord/')
        self.assertEqual(article.save_as, 'blog/atodorov/fnord/index.html')

    def test_slugify_category_with_dots(self):
        settings = get_settings()
        settings['CATEGORY_REGEX_SUBSTITUTIONS'] = [
            ('Fedora QA', 'fedora.qa'),
        ]
        settings['ARTICLE_URL'] = '{category}/{slug}/'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['category'] = Category('Fedora QA',
                                                          settings)
        article_kwargs['metadata']['title'] = 'This Week in Fedora QA'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'fedora.qa/this-week-in-fedora-qa/')

    def test_valid_save_as_detects_breakout(self):
        settings = get_settings()
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['slug'] = '../foo'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertFalse(article._has_valid_save_as())

    def test_valid_save_as_detects_breakout_to_root(self):
        settings = get_settings()
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['slug'] = '/foo'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertFalse(article._has_valid_save_as())

    def test_valid_save_as_passes_valid(self):
        settings = get_settings()
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['slug'] = 'foo'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertTrue(article._has_valid_save_as())


class TestStatic(LoggedTestCase):

    def setUp(self):
        super().setUp()
        self.settings = get_settings(
            STATIC_SAVE_AS='{path}',
            STATIC_URL='{path}',
            PAGE_SAVE_AS=os.path.join('outpages', '{slug}.html'),
            PAGE_URL='outpages/{slug}.html')
        self.context = get_context(self.settings)

        self.static = Static(content=None, metadata={}, settings=self.settings,
                             source_path=posix_join('dir', 'foo.jpg'),
                             context=self.context)

        self.context['static_content'][self.static.source_path] = self.static

    def tearDown(self):
        pass

    def test_attach_to_same_dir(self):
        """attach_to() overrides a static file's save_as and url.
        """
        page = Page(
            content="fake page",
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'fakepage.md'))
        self.static.attach_to(page)

        expected_save_as = os.path.join('outpages', 'foo.jpg')
        self.assertEqual(self.static.save_as, expected_save_as)
        self.assertEqual(self.static.url, path_to_url(expected_save_as))

    def test_attach_to_parent_dir(self):
        """attach_to() preserves dirs inside the linking document dir.
        """
        page = Page(content="fake page", metadata={'title': 'fakepage'},
                    settings=self.settings, source_path='fakepage.md')
        self.static.attach_to(page)

        expected_save_as = os.path.join('outpages', 'dir', 'foo.jpg')
        self.assertEqual(self.static.save_as, expected_save_as)
        self.assertEqual(self.static.url, path_to_url(expected_save_as))

    def test_attach_to_other_dir(self):
        """attach_to() ignores dirs outside the linking document dir.
        """
        page = Page(content="fake page",
                    metadata={'title': 'fakepage'}, settings=self.settings,
                    source_path=os.path.join('dir', 'otherdir', 'fakepage.md'))
        self.static.attach_to(page)

        expected_save_as = os.path.join('outpages', 'foo.jpg')
        self.assertEqual(self.static.save_as, expected_save_as)
        self.assertEqual(self.static.url, path_to_url(expected_save_as))

    def test_attach_to_ignores_subsequent_calls(self):
        """attach_to() does nothing when called a second time.
        """
        page = Page(content="fake page",
                    metadata={'title': 'fakepage'}, settings=self.settings,
                    source_path=os.path.join('dir', 'fakepage.md'))

        self.static.attach_to(page)

        otherdir_settings = self.settings.copy()
        otherdir_settings.update(dict(
            PAGE_SAVE_AS=os.path.join('otherpages', '{slug}.html'),
            PAGE_URL='otherpages/{slug}.html'))
        otherdir_page = Page(
            content="other page",
            metadata={'title': 'otherpage'},
            settings=otherdir_settings,
            source_path=os.path.join('dir', 'otherpage.md'))

        self.static.attach_to(otherdir_page)

        otherdir_save_as = os.path.join('otherpages', 'foo.jpg')
        self.assertNotEqual(self.static.save_as, otherdir_save_as)
        self.assertNotEqual(self.static.url, path_to_url(otherdir_save_as))

    def test_attach_to_does_nothing_after_save_as_referenced(self):
        """attach_to() does nothing if the save_as was already referenced.
        (For example, by a {static} link an a document processed earlier.)
        """
        original_save_as = self.static.save_as

        page = Page(
            content="fake page",
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'fakepage.md'))
        self.static.attach_to(page)

        self.assertEqual(self.static.save_as, original_save_as)
        self.assertEqual(self.static.url, path_to_url(original_save_as))

    def test_attach_to_does_nothing_after_url_referenced(self):
        """attach_to() does nothing if the url was already referenced.
        (For example, by a {static} link an a document processed earlier.)
        """
        original_url = self.static.url

        page = Page(
            content="fake page",
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'fakepage.md'))
        self.static.attach_to(page)

        self.assertEqual(self.static.save_as, self.static.source_path)
        self.assertEqual(self.static.url, original_url)

    def test_attach_to_does_not_override_an_override(self):
        """attach_to() does not override paths that were overridden elsewhere.
        (For example, by the user with EXTRA_PATH_METADATA)
        """
        customstatic = Static(
            content=None,
            metadata=dict(save_as='customfoo.jpg', url='customfoo.jpg'),
            settings=self.settings,
            source_path=os.path.join('dir', 'foo.jpg'),
            context=self.settings.copy())

        page = Page(
            content="fake page",
            metadata={'title': 'fakepage'}, settings=self.settings,
            source_path=os.path.join('dir', 'fakepage.md'))

        customstatic.attach_to(page)

        self.assertEqual(customstatic.save_as, 'customfoo.jpg')
        self.assertEqual(customstatic.url, 'customfoo.jpg')

    def test_attach_link_syntax(self):
        """{attach} link syntax triggers output path override & url replacement.
        """
        html = '<a href="{attach}../foo.jpg">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(
            content, html,
            "{attach} link syntax did not trigger URL replacement.")

        expected_save_as = os.path.join('outpages', 'foo.jpg')
        self.assertEqual(self.static.save_as, expected_save_as)
        self.assertEqual(self.static.url, path_to_url(expected_save_as))

    def test_tag_link_syntax(self):
        "{tag} link syntax triggers url replacement."

        html = '<a href="{tag}foo">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(content, html)

    def test_category_link_syntax(self):
        "{category} link syntax triggers url replacement."

        html = '<a href="{category}foo">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(content, html)

    def test_author_link_syntax(self):
        "{author} link syntax triggers url replacement."

        html = '<a href="{author}foo">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(content, html)

    def test_index_link_syntax(self):
        "{index} link syntax triggers url replacement."

        html = '<a href="{index}">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(content, html)

        expected_html = ('<a href="' +
                         '/'.join((self.settings['SITEURL'],
                                   self.settings['INDEX_SAVE_AS'])) +
                         '">link</a>')
        self.assertEqual(content, expected_html)

    def test_unknown_link_syntax(self):
        "{unknown} link syntax should trigger warning."

        html = '<a href="{unknown}foo">link</a>'
        page = Page(content=html,
                    metadata={'title': 'fakepage'}, settings=self.settings,
                    source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
                    context=self.context)
        content = page.get_content('')

        self.assertEqual(content, html)
        self.assertLogCountEqual(
            count=1,
            msg="Replacement Indicator 'unknown' not recognized, "
                "skipping replacement",
            level=logging.WARNING)

    def test_link_to_unknown_file(self):
        "{filename} link to unknown file should trigger warning."

        html = '<a href="{filename}foo">link</a>'
        page = Page(content=html,
                    metadata={'title': 'fakepage'}, settings=self.settings,
                    source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
                    context=self.context)
        content = page.get_content('')

        self.assertEqual(content, html)
        self.assertLogCountEqual(
            count=1,
            msg="Unable to find 'foo', skipping url replacement.",
            level=logging.WARNING)

    def test_index_link_syntax_with_spaces(self):
        """{index} link syntax triggers url replacement
        with spaces around the equal sign."""

        html = '<a href = "{index}">link</a>'
        page = Page(
            content=html,
            metadata={'title': 'fakepage'},
            settings=self.settings,
            source_path=os.path.join('dir', 'otherdir', 'fakepage.md'),
            context=self.context)
        content = page.get_content('')

        self.assertNotEqual(content, html)

        expected_html = ('<a href = "' +
                         '/'.join((self.settings['SITEURL'],
                                   self.settings['INDEX_SAVE_AS'])) +
                         '">link</a>')
        self.assertEqual(content, expected_html)

    def test_not_save_as_draft(self):
        """Static.save_as is not affected by draft status."""

        static = Static(
            content=None,
            metadata=dict(status='draft',),
            settings=self.settings,
            source_path=os.path.join('dir', 'foo.jpg'),
            context=self.settings.copy())

        expected_save_as = posixize_path(os.path.join('dir', 'foo.jpg'))
        self.assertEqual(static.status, 'draft')
        self.assertEqual(static.save_as, expected_save_as)
        self.assertEqual(static.url, path_to_url(expected_save_as))
