# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pelican.tests.support import unittest
from pelican.urlwrappers import Author, Category, Tag, URLWrapper


class TestURLWrapper(unittest.TestCase):
    def test_ordering(self):
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

    def test_equality(self):
        tag = Tag('test', settings={})
        cat = Category('test', settings={})
        author = Author('test', settings={})

        # same name, but different class
        self.assertNotEqual(tag, cat)
        self.assertNotEqual(tag, author)

        # should be equal vs text representing the same name
        self.assertEqual(tag, u'test')

        # should not be equal vs binary
        self.assertNotEqual(tag, b'test')

        # Tags describing the same should be equal
        tag_equal = Tag('Test', settings={})
        self.assertEqual(tag, tag_equal)

        # Author describing the same should be equal
        author_equal = Author('Test', settings={})
        self.assertEqual(author, author_equal)

        cat_ascii = Category('指導書', settings={})
        self.assertEqual(cat_ascii, u'zhi-dao-shu')

    def test_slugify_with_substitutions_and_dots(self):
        tag = Tag('Tag Dot',
                  settings={
                        'TAG_SUBSTITUTIONS': [('Tag Dot', 'tag.dot', True)]
                    })
        cat = Category('Category Dot',
                       settings={
                        'CATEGORY_SUBSTITUTIONS': (('Category Dot',
                                                    'cat.dot',
                                                    True),)
                        })

        self.assertEqual(tag.slug, 'tag.dot')
        self.assertEqual(cat.slug, 'cat.dot')

    def test_author_slug_substitutions(self):
        settings = {
            'AUTHOR_SUBSTITUTIONS': [
                                    ('Alexander Todorov', 'atodorov', False),
                                    ('Krasimir Tsonev', 'krasimir', False),
            ]
        }

        author1 = Author('Mr. Senko', settings=settings)
        author2 = Author('Alexander Todorov', settings=settings)
        author3 = Author('Krasimir Tsonev', settings=settings)

        self.assertEqual(author1.slug, 'mr-senko')
        self.assertEqual(author2.slug, 'atodorov')
        self.assertEqual(author3.slug, 'krasimir')
