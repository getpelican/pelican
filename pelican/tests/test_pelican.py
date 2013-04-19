# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
from filecmp import dircmp
from tempfile import mkdtemp
from shutil import rmtree
import locale
import logging

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
        self.old_locale = locale.setlocale(locale.LC_ALL)
        self.maxDiff = None
        locale.setlocale(locale.LC_ALL, str('C'))

    def tearDown(self):
        rmtree(self.temp_path)
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

    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate correct output without raising any exception
        settings = read_settings(path=None, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'LOCALE': locale.normalize('en_US'),
            })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        dcmp = dircmp(self.temp_path, os.path.join(OUTPUT_PATH, 'basic'))
        self.assertFilesEqual(recursiveDiff(dcmp))
        self.assertLogCountEqual(
            count=4,
            msg="Unable to find.*skipping url replacement",
            level=logging.WARNING)

    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(path=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            'LOCALE': locale.normalize('en_US'),
            })
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        dcmp = dircmp(self.temp_path, os.path.join(OUTPUT_PATH, 'custom'))
        self.assertFilesEqual(recursiveDiff(dcmp))
