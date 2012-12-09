# -*- coding: utf-8 -*-
'''Core plugins unit tests'''

import os
import tempfile

from pelican.plugins import gzip_cache

from support import unittest, temporary_folder

class TestGzipCache(unittest.TestCase):
    '''Unit tests for the gzip cache plugin'''

    def test_should_compress(self):
        '''Test that some filetypes should compress and others shouldn't.'''
        self.assertTrue(gzip_cache.should_compress('foo.html'))
        self.assertTrue(gzip_cache.should_compress('bar.css'))
        self.assertTrue(gzip_cache.should_compress('baz.js'))
        self.assertTrue(gzip_cache.should_compress('foo.txt'))

        self.assertFalse(gzip_cache.should_compress('foo.gz'))
        self.assertFalse(gzip_cache.should_compress('bar.png'))
        self.assertFalse(gzip_cache.should_compress('baz.mp3'))
        self.assertFalse(gzip_cache.should_compress('foo.mov'))

    def test_creates_gzip_file(self):
        '''Test that a file matching the input filename with a .gz extension is
        created.'''
        # The plugin walks over the output content after the finalized signal
        # so it is safe to assume that the file exists (otherwise walk would
        # not report it). Therefore, create a dummy file to use.
        with temporary_folder() as tempdir:
            (_, a_html_filename) = tempfile.mkstemp(suffix='.html', dir=tempdir)
            gzip_cache.create_gzip_file(a_html_filename)
            self.assertTrue(os.path.exists(a_html_filename + '.gz'))

