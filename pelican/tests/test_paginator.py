# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import locale

from jinja2.utils import generate_lorem_ipsum

from pelican.contents import Article, Author
from pelican.paginator import Paginator
from pelican.settings import DEFAULT_CONFIG
from pelican.tests.support import get_settings, unittest


# generate one paragraph, enclosed with <p>
TEST_CONTENT = str(generate_lorem_ipsum(n=1))
TEST_SUMMARY = generate_lorem_ipsum(n=1, html=False)


class TestPage(unittest.TestCase):
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
            },
            'source_path': '/path/to/file/foo.ext'
        }

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def test_save_as_preservation(self):
        settings = get_settings()
        # fix up pagination rules
        from pelican.paginator import PaginationRule
        pagination_rules = [
            PaginationRule(*r) for r in settings.get(
                'PAGINATION_PATTERNS',
                DEFAULT_CONFIG['PAGINATION_PATTERNS'],
            )
        ]
        settings['PAGINATION_PATTERNS'] = sorted(
            pagination_rules,
            key=lambda r: r[0],
        )

        self.page_kwargs['metadata']['author'] = Author('Blogger', settings)
        object_list = [Article(**self.page_kwargs),
                       Article(**self.page_kwargs)]
        paginator = Paginator('foobar.foo', object_list, settings)
        page = paginator.page(1)
        self.assertEqual(page.save_as, 'foobar.foo')
