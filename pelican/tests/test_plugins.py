# -*- coding: utf-8 -*-
'''Core plugins unit tests'''

import os
import tempfile

from pelican.contents import Page
from pelican.plugins import gzip_cache

from pelican.tests.test_contents import TEST_CONTENT, TEST_SUMMARY
from pelican.tests.support import unittest, temporary_folder


class TestGzipCache(unittest.TestCase):

    def test_should_compress(self):
        # Some filetypes should compress and others shouldn't.
        self.assertTrue(gzip_cache.should_compress('foo.html'))
        self.assertTrue(gzip_cache.should_compress('bar.css'))
        self.assertTrue(gzip_cache.should_compress('baz.js'))
        self.assertTrue(gzip_cache.should_compress('foo.txt'))

        self.assertFalse(gzip_cache.should_compress('foo.gz'))
        self.assertFalse(gzip_cache.should_compress('bar.png'))
        self.assertFalse(gzip_cache.should_compress('baz.mp3'))
        self.assertFalse(gzip_cache.should_compress('foo.mov'))

    def test_creates_gzip_file(self):
        # A file matching the input filename with a .gz extension is created.

        # The plugin walks over the output content after the finalized signal
        # so it is safe to assume that the file exists (otherwise walk would
        # not report it). Therefore, create a dummy file to use.
        with temporary_folder() as tempdir:
            _, a_html_filename = tempfile.mkstemp(suffix='.html', dir=tempdir)
            gzip_cache.create_gzip_file(a_html_filename)
            self.assertTrue(os.path.exists(a_html_filename + '.gz'))


class TestSummary(unittest.TestCase):
    def setUp(self):
        super(TestSummary, self).setUp()

        from pelican.plugins import summary

        summary.register()
        summary.initialized(None)
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

    def test_end_summary(self):
        page_kwargs = self._copy_page_kwargs()
        del page_kwargs['metadata']['summary']
        page_kwargs['content'] = (
            TEST_SUMMARY + '<!-- PELICAN_END_SUMMARY -->' + TEST_CONTENT)
        page = Page(**page_kwargs)
        # test both the summary and the marker removal
        self.assertEqual(page.summary, TEST_SUMMARY)
        self.assertEqual(page.content, TEST_SUMMARY + TEST_CONTENT)

    def test_begin_summary(self):
        page_kwargs = self._copy_page_kwargs()
        del page_kwargs['metadata']['summary']
        page_kwargs['content'] = (
            'FOOBAR<!-- PELICAN_BEGIN_SUMMARY -->' + TEST_CONTENT)
        page = Page(**page_kwargs)
        # test both the summary and the marker removal
        self.assertEqual(page.summary, TEST_CONTENT)
        self.assertEqual(page.content, 'FOOBAR' + TEST_CONTENT)

    def test_begin_end_summary(self):
        page_kwargs = self._copy_page_kwargs()
        del page_kwargs['metadata']['summary']
        page_kwargs['content'] = (
                'FOOBAR<!-- PELICAN_BEGIN_SUMMARY -->' + TEST_SUMMARY +
                '<!-- PELICAN_END_SUMMARY -->' + TEST_CONTENT)
        page = Page(**page_kwargs)
        # test both the summary and the marker removal
        self.assertEqual(page.summary, TEST_SUMMARY)
        self.assertEqual(page.content, 'FOOBAR' + TEST_SUMMARY + TEST_CONTENT)
