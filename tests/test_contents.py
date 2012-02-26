from __future__ import with_statement
from unittest2 import TestCase

from pelican.contents import Page
from pelican.settings import _DEFAULT_CONFIG

class TestPage(TestCase):

    def setUp(self):
        super(TestPage, self).setUp()
        self.page_kwargs = {
            'content': 'content',
            'metadata':{
                'title': 'foo bar',
                'author': 'Blogger',
            },
        }

    def test_use_args(self):
        """Creating a page with arguments passed to the constructor should use
        them to initialise object's attributes.

        """
        metadata = {'foo': 'bar', 'foobar': 'baz', 'title': 'foobar', }
        page = Page('content', metadata=metadata)
        for key, value in metadata.items():
            self.assertTrue(hasattr(page, key))
            self.assertEqual(value, getattr(page, key))
        self.assertEqual(page.content, 'content')

    def test_mandatory_properties(self):
        """If the title is not set, must throw an exception."""
        self.assertRaises(AttributeError, Page, 'content')
        page = Page(**self.page_kwargs)
        page.check_properties()

    def test_slug(self):
        """If a title is given, it should be used to generate the slug."""
        page = Page(**self.page_kwargs)
        self.assertEqual(page.slug, 'foo-bar')

    def test_defaultlang(self):
        """If no lang is given, default to the default one."""
        page = Page(**self.page_kwargs)
        self.assertEqual(page.lang, _DEFAULT_CONFIG['DEFAULT_LANG'])

        # it is possible to specify the lang in the metadata infos
        self.page_kwargs['metadata'].update({'lang': 'fr', })
        page = Page(**self.page_kwargs)
        self.assertEqual(page.lang, 'fr')

    def test_save_as(self):
        """If a lang is not the default lang, save_as should be set
        accordingly.

        """
        # if a title is defined, save_as should be set
        page = Page(**self.page_kwargs)
        page.save_as = 'foo-bar.html'

        # if a language is defined, save_as should include it accordingly
        self.page_kwargs['metadata'].update({'lang': 'fr', })
        page = Page(**self.page_kwargs)
        self.assertEqual(page.save_as, "foo-bar-fr.html")
