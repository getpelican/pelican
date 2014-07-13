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
        super().setUp()
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
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
        paginator = Paginator('foobar.foo', 'foobar/foo', object_list,
                              settings)
        page = paginator.page(1)
        self.assertEqual(page.save_as, 'foobar.foo')

    def test_custom_pagination_pattern(self):
        from pelican.paginator import PaginationRule
        settings = get_settings()
        settings['PAGINATION_PATTERNS'] = [PaginationRule(*r) for r in [
            (1, '/{url}', '{base_name}/index.html'),
            (2, '/{url}{number}/', '{base_name}/{number}/index.html')
        ]]

        self.page_kwargs['metadata']['author'] = Author('Blogger', settings)
        object_list = [Article(**self.page_kwargs),
                       Article(**self.page_kwargs)]
        paginator = Paginator('blog/index.html', '//blog.my.site/',
                              object_list, settings, 1)
        # The URL *has to* stay absolute (with // in the front), so verify that
        page1 = paginator.page(1)
        self.assertEqual(page1.save_as, 'blog/index.html')
        self.assertEqual(page1.url, '//blog.my.site/')
        page2 = paginator.page(2)
        self.assertEqual(page2.save_as, 'blog/2/index.html')
        self.assertEqual(page2.url, '//blog.my.site/2/')

    def test_custom_pagination_pattern_last_page(self):
        from pelican.paginator import PaginationRule
        settings = get_settings()
        settings['PAGINATION_PATTERNS'] = [PaginationRule(*r) for r in [
            (1, '/{url}1/', '{base_name}/1/index.html'),
            (2, '/{url}{number}/', '{base_name}/{number}/index.html'),
            (-1, '/{url}', '{base_name}/index.html'),
        ]]

        self.page_kwargs['metadata']['author'] = Author('Blogger', settings)
        object_list = [Article(**self.page_kwargs),
                       Article(**self.page_kwargs),
                       Article(**self.page_kwargs)]
        paginator = Paginator('blog/index.html', '//blog.my.site/',
                              object_list, settings, 1)
        # The URL *has to* stay absolute (with // in the front), so verify that
        page1 = paginator.page(1)
        self.assertEqual(page1.save_as, 'blog/1/index.html')
        self.assertEqual(page1.url, '//blog.my.site/1/')
        page2 = paginator.page(2)
        self.assertEqual(page2.save_as, 'blog/2/index.html')
        self.assertEqual(page2.url, '//blog.my.site/2/')
        page3 = paginator.page(3)
        self.assertEqual(page3.save_as, 'blog/index.html')
        self.assertEqual(page3.url, '//blog.my.site/')
