from __future__ import with_statement
try:
    from unittest2 import TestCase
except ImportError, e:
    from unittest import TestCase

from pelican.contents import Page
from pelican.settings import _DEFAULT_CONFIG

class TestPage(TestCase):

    def test_use_args(self):
        # creating a page with arguments passed to the connstructor should use
        # them to initialise object's attributes
        metadata = {'foo': 'bar', 'foobar': 'baz'}
        page = Page('content', metadata=metadata)
        for key, value in metadata.items():
            self.assertTrue(hasattr(page, key))
            self.assertEqual(value, getattr(page, key))
        self.assertEqual(page.content, "content")

    def test_mandatory_properties(self):
        # if the title is not set, must throw an exception
        page = Page('content')
        with self.assertRaises(NameError) as cm:
            page.check_properties()

        page = Page('content', metadata={'title': 'foobar'})
        page.check_properties()

    def test_slug(self):
        # if a title is given, it should be used to generate the slug
        page = Page('content', {'title': 'foobar is foo'})
        self.assertEqual(page.slug, 'foobar-is-foo')

    def test_defaultlang(self):
        # if no lang is given, default to the default one
        page = Page('content')
        self.assertEqual(page.lang, _DEFAULT_CONFIG['DEFAULT_LANG'])

        # it is possible to specify the lang in the metadata infos
        page = Page('content', {'lang': 'fr'})
        self.assertEqual(page.lang, 'fr')

    def test_save_as(self):
        # if a lang is not the default lang, save_as should be set accordingly
        page = Page('content', {'title': 'foobar', 'lang': 'fr'}) #default lang is en
        self.assertEqual(page.save_as, "foobar-fr.html")

        # otherwise, if a title is defined, save_as should be set
        page = Page('content', {'title': 'foobar'})
        page.save_as = 'foobar.html'

        # if no title is given, there is no save_as
        page = Page('content')
        self.assertFalse(hasattr(page, 'save_as'))
