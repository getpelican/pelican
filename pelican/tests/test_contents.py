# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import locale
import logging
import os.path
from posixpath import join as posix_join
from sys import platform

from jinja2.utils import generate_lorem_ipsum

import six

from pelican.contents import Article, Author, Category, Page, Static, Tag
from pelican.settings import DEFAULT_CONFIG
from pelican.signals import content_object_init
from pelican.tests.support import LoggedTestCase, get_settings, unittest
from pelican.utils import SafeDatetime, path_to_url, truncate_html_words


# generate one paragraph, enclosed with <p>
TEST_CONTENT = str(generate_lorem_ipsum(n=1))
TEST_SUMMARY = generate_lorem_ipsum(n=1, html=False)


class TestPage(LoggedTestCase):

    def setUp(self):
        super(TestPage, self).setUp()
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))
        self.page_kwargs = {
            'content': TEST_CONTENT,
            'context': {
                'localsiteurl': '',
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

    def test_summary_get_summary_warning(self):
        """calling ._get_summary() should issue a warning"""
        page_kwargs = self._copy_page_kwargs()
        page = Page(**page_kwargs)
        self.assertEqual(page.summary, TEST_SUMMARY)
        self.assertEqual(page._get_summary(), TEST_SUMMARY)
        self.assertLogCountEqual(
                count=1,
                msg="_get_summary\(\) has been deprecated since 3\.6\.4\. "
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
        dt = SafeDatetime(2015, 9, 13)

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
        # type does not take unicode in PY2 and bytes in PY3, which in
        # combination with unicode literals leads to following insane line:
        cls_name = '_DummyArticle' if six.PY3 else b'_DummyArticle'
        article = type(cls_name, (object,), {'url': 'article.html'})

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['filenames'] = {'article.rst': article}

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
        args['metadata']['summary'] = (
            'A simple summary test, with a '
            '<a href="|filename|article.rst">link</a>'
        )
        args['context']['localsiteurl'] = 'http://notmyidea.org'
        p = Page(**args)
        self.assertEqual(
            p.summary,
            'A simple summary test, with a '
            '<a href="http://notmyidea.org/article.html">link</a>'
        )

    def test_intrasite_link_more(self):
        # type does not take unicode in PY2 and bytes in PY3, which in
        # combination with unicode literals leads to following insane line:
        cls_name = '_DummyAsset' if six.PY3 else b'_DummyAsset'

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['filenames'] = {
            'images/poster.jpg': type(
                cls_name, (object,), {'url': 'images/poster.jpg'}),
            'assets/video.mp4': type(
                cls_name, (object,), {'url': 'assets/video.mp4'}),
            'images/graph.svg': type(
                cls_name, (object,), {'url': 'images/graph.svg'}),
            'reference.rst': type(
                cls_name, (object,), {'url': 'reference.html'}),
        }

        # video.poster
        args['content'] = (
            'There is a video with poster '
            '<video controls poster="{filename}/images/poster.jpg">'
            '<source src="|filename|/assets/video.mp4" type="video/mp4">'
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
            '<object data="{filename}/images/graph.svg"'
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

    def test_intrasite_link_markdown_spaces(self):
        # Markdown introduces %20 instead of spaces, this tests that
        # we support markdown doing this.
        cls_name = '_DummyArticle' if six.PY3 else b'_DummyArticle'
        article = type(cls_name, (object,), {'url': 'article-spaces.html'})

        args = self.page_kwargs.copy()
        args['settings'] = get_settings()
        args['source_path'] = 'content'
        args['context']['filenames'] = {'article spaces.rst': article}

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
        settings['SLUG_SUBSTITUTIONS'] = [('C#', 'csharp')]
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
        settings['AUTHOR_SUBSTITUTIONS'] = [
                                    ('Alexander Todorov', 'atodorov', False),
                                    ('Krasimir Tsonev', 'krasimir', False),
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
        settings['CATEGORY_SUBSTITUTIONS'] = [('Fedora QA', 'fedora.qa', True)]
        settings['ARTICLE_URL'] = '{category}/{slug}/'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['category'] = Category('Fedora QA',
                                                          settings)
        article_kwargs['metadata']['title'] = 'This Week in Fedora QA'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'fedora.qa/this-week-in-fedora-qa/')

    def test_slugify_tags_with_dots(self):
        settings = get_settings()
        settings['TAG_SUBSTITUTIONS'] = [('Fedora QA', 'fedora.qa', True)]
        settings['ARTICLE_URL'] = '{tag}/{slug}/'
        article_kwargs = self._copy_page_kwargs()
        article_kwargs['metadata']['tag'] = Tag('Fedora QA', settings)
        article_kwargs['metadata']['title'] = 'This Week in Fedora QA'
        article_kwargs['settings'] = settings
        article = Article(**article_kwargs)
        self.assertEqual(article.url, 'fedora.qa/this-week-in-fedora-qa/')


class TestStatic(LoggedTestCase):

    def setUp(self):
        super(TestStatic, self).setUp()
        self.settings = get_settings(
            STATIC_SAVE_AS='{path}',
            STATIC_URL='{path}',
            PAGE_SAVE_AS=os.path.join('outpages', '{slug}.html'),
            PAGE_URL='outpages/{slug}.html')
        self.context = self.settings.copy()

        self.static = Static(content=None, metadata={}, settings=self.settings,
                             source_path=posix_join('dir', 'foo.jpg'),
                             context=self.context)

        self.context['filenames'] = {self.static.source_path: self.static}

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
        (For example, by a {filename} link an a document processed earlier.)
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
        (For example, by a {filename} link an a document processed earlier.)
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
