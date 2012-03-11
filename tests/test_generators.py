# -*- coding: utf-8 -*-
from __future__ import with_statement
try:
    from unittest2 import TestCase
except ImportError, e:
    from unittest import TestCase

from pelican.generators import ArticlesGenerator
from pelican.settings import _DEFAULT_CONFIG

class TestArticlesGenerator(TestCase):

    def test_generate_feeds(self):

        class FakeWriter(object):
            def __init__(self):
                self.called = False

            def write_feed(self, *args, **kwargs):
                self.called = True

        generator = ArticlesGenerator(None, {'FEED': _DEFAULT_CONFIG['FEED']},
                                      None, _DEFAULT_CONFIG['THEME'], None,
                                      None)
        writer = FakeWriter()
        generator.generate_feeds(writer)
        assert writer.called, ("The feed should be written, "
                               "if settings['FEED'] is specified.")

        generator = ArticlesGenerator(None, {'FEED': None}, None,
                                      _DEFAULT_CONFIG['THEME'], None, None)
        writer = FakeWriter()
        generator.generate_feeds(writer)
        assert not writer.called, ("If settings['FEED'] is None, "
                                   "the feed should not be generated.")

