# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import collections
import locale
import logging
import os
import subprocess
import sys

from shutil import rmtree
from tempfile import mkdtemp

from pelican import Pelican
from pelican.generators import StaticGenerator
from pelican.settings import read_settings
from pelican.tests.support import (LoggedTestCase, locale_available,
                                   mute, unittest)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PATH = os.path.abspath(os.path.join(
    CURRENT_DIR, os.pardir, os.pardir, 'samples'))
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_DIR, 'output'))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")
SAMPLE_FR_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf_FR.py")


def recursiveDiff(dcmp):
    diff = {
        'diff_files': [os.path.join(dcmp.right, f) for f in dcmp.diff_files],
        'left_only': [os.path.join(dcmp.right, f) for f in dcmp.left_only],
        'right_only': [os.path.join(dcmp.right, f) for f in dcmp.right_only],
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

    def assertDirsEqual(self, left_path, right_path):
        out, err = subprocess.Popen(
            ['git', 'diff', '--no-ext-diff', '--exit-code',
             '-w', left_path, right_path],
            env={str('PAGER'): str('')},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        def ignorable_git_crlf_errors(line):
            # Work around for running tests on Windows
            for msg in [
                    "LF will be replaced by CRLF",
                    "The file will have its original line endings"]:
                if msg in line:
                    return True
            return False
        if err:
            err = '\n'.join([l for l in err.decode('utf8').splitlines()
                             if not ignorable_git_crlf_errors(l)])
        assert not out, out
        assert not err, err

    def test_order_of_generators(self):
        # StaticGenerator must run last, so it can identify files that
        # were skipped by the other generators, and so static files can
        # have their output paths overridden by the {attach} link syntax.

        pelican = Pelican(settings=read_settings(path=None))
        generator_classes = pelican.get_generator_classes()

        self.assertTrue(
            generator_classes[-1] is StaticGenerator,
            "StaticGenerator must be the last generator, but it isn't!")
        self.assertIsInstance(
            generator_classes, collections.Sequence,
            "get_generator_classes() must return a Sequence to preserve order")

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
        self.assertDirsEqual(
            self.temp_path, os.path.join(OUTPUT_PATH, 'basic'))
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
        self.assertDirsEqual(
            self.temp_path, os.path.join(OUTPUT_PATH, 'custom'))

    @unittest.skipUnless(locale_available('fr_FR.UTF-8') or
                         locale_available('French'), 'French locale needed')
    def test_custom_locale_generation_works(self):
        '''Test that generation with fr_FR.UTF-8 locale works'''
        if sys.platform == 'win32':
            our_locale = str('French')
        else:
            our_locale = str('fr_FR.UTF-8')

        settings = read_settings(path=SAMPLE_FR_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'LOCALE': our_locale,
        })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(
            self.temp_path, os.path.join(OUTPUT_PATH, 'custom_locale'))

    def test_theme_static_paths_copy(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(path=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'THEME_STATIC_PATHS': [os.path.join(SAMPLES_PATH, 'very'),
                                   os.path.join(SAMPLES_PATH, 'kinda'),
                                   os.path.join(SAMPLES_PATH,
                                                'theme_standard')]
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
            'THEME_STATIC_PATHS': [os.path.join(SAMPLES_PATH,
                                                'theme_standard')]
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
            msg="Writing .*",
            level=logging.INFO)

    def test_md_extensions_deprecation(self):
        """Test that a warning is issued if MD_EXTENSIONS is used"""
        settings = read_settings(path=None, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'CACHE_PATH': self.temp_cache,
            'MD_EXTENSIONS': {},
        })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertLogCountEqual(
            count=1,
            msg="MD_EXTENSIONS is deprecated use MARKDOWN instead.",
            level=logging.WARNING)
