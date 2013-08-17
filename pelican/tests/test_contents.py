# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from sys import platform

from .support import unittest, get_settings

from pelican.contents import Page, Article, URLWrapper
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import truncate_html_words
from pelican.signals import content_object_init
from jinja2.utils import generate_lorem_ipsum

# generate one paragraph, enclosed with <p>
TEST_CONTENT = str(generate_lorem_ipsum(n=1))
TEST_SUMMARY = generate_lorem_ipsum(n=1, html=False)


class TestPage(unittest.TestCase):

    def setUp(self):
        super(TestPage, self).setUp()
        self.page_kwargs = {
            'content': TEST_CONTENT,
            'context': {
                'localsiteurl': '',
            },
            'metadata': {
                'summary': TEST_SUMMARY,
                'title': 'foo bar',
                'author': 'Blogger',
            },
        }

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
        with self.assertRaises(NameError):
            page.check_properties()

        page = Page('content', metadata={'title': 'foobar'})
        page.check_properties()

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

    def test_slug(self):
        # If a title is given, it should be used to generate the slug.
        page = Page(**self.page_kwargs)
        self.assertEqual(page.slug, 'foo-bar')

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

    def test_metadata_url_format(self):
        # Arbitrary metadata should be passed through url_format()
        page = Page(**self.page_kwargs)
        self.assertIn('summary', page.url_format.keys())
        page.metadata['directory'] = 'test-dir'
        page.settings = get_settings(PAGE_SAVE_AS='{directory}/{slug}')
        self.assertEqual(page.save_as, 'test-dir/foo-bar')

    def test_datetime(self):
        # If DATETIME is set to a tuple, it should be used to override LOCALE
        dt = datetime(2015, 9, 13)

        page_kwargs = self._copy_page_kwargs()

        # set its date to dt
        page_kwargs['metadata']['date'] = dt
        page = Page(**page_kwargs)

        self.assertEqual(page.locale_date,
            dt.strftime(DEFAULT_CONFIG['DEFAULT_DATE_FORMAT']))

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

    def _copy_page_kwargs(self):
        # make a deep copy of page_kwargs
        page_kwargs = dict([(key, self.page_kwargs[key]) for key in
                            self.page_kwargs])
        for key in page_kwargs:
            if not isinstance(page_kwargs[key], dict):
                break
            page_kwargs[key] = dict([(subkey, page_kwargs[key][subkey])
                                     for subkey in page_kwargs[key]])

        return page_kwargs

    def test_signal(self):
        # If a title is given, it should be used to generate the slug.

        def receiver_test_function(sender, instance):
            pass

        content_object_init.connect(receiver_test_function, sender=Page)
        Page(**self.page_kwargs)
        self.assertTrue(content_object_init.has_receivers_for(Page))

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
        self.assertEquals(content, ('A simple test, with a '
                                    '<a href="tag/tagname.html">link</a>'))

        # Category
        args['content'] = ('A simple test, with a '
                           '<a href="|category|category">link</a>')
        page = Page(**args)
        content = page.get_content('http://notmyidea.org')
        self.assertEquals(content,
                          ('A simple test, with a '
                           '<a href="category/category.html">link</a>'))


class TestArticle(TestPage):
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
        settings['SLUG_SUBSTITUTIONS'] = [ ('C#', 'csharp') ]
        settings['ARTICLE_URL'] = '{author}/{category}/{slug}/'
        settings['ARTICLE_SAVE_AS'] = '{author}/{category}/{slug}/index.html'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['author'] = "O'Brien"
        article_kwargs['metadata']['category'] = 'C# & stuff'
        article_kwargs['metadata']['title'] = 'fnord'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'obrien/csharp-stuff/fnord/')
        self.assertEqual(article.save_as, 'obrien/csharp-stuff/fnord/index.html')


class TestURLWrapper(unittest.TestCase):
    def test_comparisons(self):
        # URLWrappers are sorted by name
        wrapper_a = URLWrapper(name='first', settings={})
        wrapper_b = URLWrapper(name='last', settings={})
        self.assertFalse(wrapper_a > wrapper_b)
        self.assertFalse(wrapper_a >= wrapper_b)
        self.assertFalse(wrapper_a == wrapper_b)
        self.assertTrue(wrapper_a != wrapper_b)
        self.assertTrue(wrapper_a <= wrapper_b)
        self.assertTrue(wrapper_a < wrapper_b)
        wrapper_b.name = 'first'
        self.assertFalse(wrapper_a > wrapper_b)
        self.assertTrue(wrapper_a >= wrapper_b)
        self.assertTrue(wrapper_a == wrapper_b)
        self.assertFalse(wrapper_a != wrapper_b)
        self.assertTrue(wrapper_a <= wrapper_b)
        self.assertFalse(wrapper_a < wrapper_b)
        wrapper_a.name = 'last'
        self.assertTrue(wrapper_a > wrapper_b)
        self.assertTrue(wrapper_a >= wrapper_b)
        self.assertFalse(wrapper_a == wrapper_b)
        self.assertTrue(wrapper_a != wrapper_b)
        self.assertFalse(wrapper_a <= wrapper_b)
        self.assertFalse(wrapper_a < wrapper_b)
