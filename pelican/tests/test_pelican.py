# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
from tempfile import mkdtemp
from shutil import rmtree
import locale
import logging
import subprocess

from pelican import Pelican
from pelican.settings import read_settings
from pelican.tests.support import LoggedTestCase, mute

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PATH = os.path.abspath(os.path.join(
        CURRENT_DIR, os.pardir, os.pardir, 'samples'))
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'output'))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")


def recursiveDiff(dcmp):
    diff = {
            'diff_files': [os.path.join(dcmp.right, f)
                for f in dcmp.diff_files],
            'left_only': [os.path.join(dcmp.right, f)
                for f in dcmp.left_only],
            'right_only': [os.path.join(dcmp.right, f)
                for f in dcmp.right_only],
            }
    for sub_dcmp in dcmp.subdirs.values():
        for k, v in recursiveDiff(sub_dcmp).items():
            diff[k] += v
    return diff


class TestPelican(LoggedTestCase):
    # general functional testing for pelican. Basically, this test case tries
    # to run pelican in different situations and see how it behaves

    def setUp(self):
        super(TestPelican, self).setUp()
        self.temp_path = mkdtemp(prefix='pelicantests.')
        self.temp_cache = mkdtemp(prefix='pelican_cache.')
        self.maxDiff = None
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, str('C'))

    def tearDown(self):
        rmtree(self.temp_path)
        rmtree(self.temp_cache)
        locale.setlocale(locale.LC_ALL, self.old_locale)
        super(TestPelican, self).tearDown()

    def assertFilesEqual(self, diff):
        msg = ("some generated files differ from the expected functional "
               "tests output.\n"
               "This is probably because the HTML generated files "
               "changed. If these changes are normal, please refer "
               "to docs/contribute.rst to update the expected "
               "output of the functional tests.")

        self.assertEqual(diff['left_only'], [], msg=msg)
        self.assertEqual(diff['right_only'], [], msg=msg)
        self.assertEqual(diff['diff_files'], [], msg=msg)

    def assertDirsEqual(self, left_path, right_path):
        out, err = subprocess.Popen(
            ['git', 'diff', '--no-ext-diff', '--exit-code', '-w', left_path, right_path], env={'PAGER': ''},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        assert not out, out
        assert not err, err

    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate correct output without raising any exception
        settings = read_settings(path=None, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'LOCALE': locale.normalize('en_US'),
            })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(self.temp_path, os.path.join(OUTPUT_PATH, 'basic'))
        self.assertLogCountEqual(
            count=3,
            msg="Unable to find.*skipping url replacement",
            level=logging.WARNING)

    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(path=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'LOCALE': locale.normalize('en_US'),
            })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(self.temp_path, os.path.join(OUTPUT_PATH, 'custom'))

    def test_theme_static_paths_copy(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(path=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'THEME_STATIC_PATHS': [os.path.join(SAMPLES_PATH, 'very'),
                                   os.path.join(SAMPLES_PATH, 'kinda'),
                                   os.path.join(SAMPLES_PATH, 'theme_standard')]
            })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        theme_output = os.path.join(self.temp_path, 'theme')
        extra_path = os.path.join(theme_output, 'exciting', 'new', 'files')

        for file in ['a_stylesheet', 'a_template']:
            self.assertTrue(os.path.exists(os.path.join(theme_output, file)))

        for file in ['wow!', 'boom!', 'bap!', 'zap!']:
            self.assertTrue(os.path.exists(os.path.join(extra_path, file)))

    def test_theme_static_paths_copy_single_file(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(path=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'THEME_STATIC_PATHS': [os.path.join(SAMPLES_PATH, 'theme_standard')]
            })

        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        theme_output = os.path.join(self.temp_path, 'theme')

        for file in ['a_stylesheet', 'a_template']:
            self.assertTrue(os.path.exists(os.path.join(theme_output, file)))

    def test_write_only_selected(self):
        """Test that only the selected files are written"""
        settings = read_settings(path=None, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'WRITE_SELECTED': [
                os.path.join(self.temp_path, 'oh-yeah.html'),
                os.path.join(self.temp_path, 'categories.html'),
                ],
            'LOCALE': locale.normalize('en_US'),
            })
        pelican = Pelican(settings=settings)
        logger = logging.getLogger()
        orig_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        mute(True)(pelican.run)()
        logger.setLevel(orig_level)
        self.assertLogCountEqual(
            count=2,
            msg="writing .*",
            level=logging.INFO)
