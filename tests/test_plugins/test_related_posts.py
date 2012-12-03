import os

from pelican import signals
from pelican.settings import _DEFAULT_CONFIG
from pelican.plugins.related_posts import add_related_posts
from pelican.generators import ArticlesGenerator

from ..support import unittest

TESTS_DIR = os.path.dirname(os.path.dirname(__file__))


class TestRelatedPosts(unittest.TestCase):

    def setUp(self):
        signals.article_generate_context.connect(add_related_posts)

    def tearDown(self):
        signals.article_generate_context.disconnect(add_related_posts)

    def get_generator(self, *posts):
        settings = _DEFAULT_CONFIG.copy()
        settings['ARTICLE_DIR'] = 'content'
        settings['DEFAULT_CATEGORY'] = 'Default'
        generator = ArticlesGenerator(settings.copy(), settings, TESTS_DIR,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        return generator

    def test_related_posts_is_set(self):
        """The related posts plugin adds related_posts
           to article metadata."""
        generator = self.get_generator()
        generator.generate_context()

        self.assertIn('foo', generator.tags)
        self.assertEquals(len(generator.tags['foo']), 2)

        # both articles should have related_posts defined.
        # (this was broken under Pelican 3.1)
        for article in generator.tags['foo']:
            self.assertIn('related_posts', article.metadata)

    def test_exclude_self(self):
        """A post is not relatated to itself."""

        generator = self.get_generator()
        generator.generate_context()

        self.assertIn('foo', generator.tags)
        for article in generator.tags['foo']:
            self.assertIn('related_posts', article.metadata)
            self.assertNotIn(article, article.metadata['related_posts'])

    def test_ordering(self):
        """Related posts are ordered by most closely related first."""

        generator = self.get_generator()
        generator.generate_context()

        self.assertIn('foo', generator.tags)
        # TODO is there a better way to get a single article?
        by_title = dict((a.title, a) for a in generator.tags['foo'])

        self.assertIn(u'This is a super article !', by_title)
        article = by_title[u'This is a super article !']

        self.assertIn('related_posts', article.metadata)

        # the first of these articles shares two tags (foo & bar),
        # the second shares just one tag (bar).
        related = [a.title for a in article.metadata['related_posts']]
        self.assertEquals(related, [u'This is an article tagged foo, bar',
                                    u'This is an article tagged bar'])
