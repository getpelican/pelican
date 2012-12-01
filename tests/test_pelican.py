try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import os
from filecmp import dircmp
from tempfile import mkdtemp
from shutil import rmtree
import locale
import logging

from mock import patch

from pelican import Pelican
from pelican.settings import read_settings
from .support import LogCountHandler

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PATH = os.path.abspath(os.sep.join((CURRENT_DIR, "..", "samples")))
OUTPUT_PATH = os.path.abspath(os.sep.join((CURRENT_DIR, "output")))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")


def recursiveDiff(dcmp):
    diff = {
            'diff_files': [os.sep.join((dcmp.right, f))
                for f in dcmp.diff_files],
            'left_only': [os.sep.join((dcmp.right, f))
                for f in dcmp.left_only],
            'right_only': [os.sep.join((dcmp.right, f))
                for f in dcmp.right_only],
            }
    for sub_dcmp in dcmp.subdirs.values():
        for k, v in recursiveDiff(sub_dcmp).iteritems():
            diff[k] += v
    return diff


class TestPelican(unittest.TestCase):
    # general functional testing for pelican. Basically, this test case tries
    # to run pelican in different situations and see how it behaves

    def setUp(self):
        self.logcount_handler = LogCountHandler()
        logging.getLogger().addHandler(self.logcount_handler)
        self.temp_path = mkdtemp()
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

    def tearDown(self):
        rmtree(self.temp_path)
        locale.setlocale(locale.LC_ALL, self.old_locale)
        logging.getLogger().removeHandler(self.logcount_handler)

    def assertFilesEqual(self, diff):
        msg = "some generated files differ from the expected functional " \
              "tests output.\n" \
              "This is probably because the HTML generated files " \
              "changed. If these changes are normal, please refer " \
              "to docs/contribute.rst to update the expected " \
              "output of the functional tests."

        self.assertEqual(diff['left_only'], [], msg=msg)
        self.assertEqual(diff['right_only'], [], msg=msg)
        self.assertEqual(diff['diff_files'], [], msg=msg)

    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate correct output without raising any exception
        settings = read_settings(filename=None, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            })
        pelican = Pelican(settings=settings)
        pelican.run()
        dcmp = dircmp(self.temp_path, os.sep.join((OUTPUT_PATH, "basic")))
        self.assertFilesEqual(recursiveDiff(dcmp))
        self.assertEqual(self.logcount_handler.count_logs(
            msg="Unable to find.*skipping url replacement",
            level=logging.WARNING,
            ), 10, msg="bad number of occurences found for this log")

    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(filename=SAMPLE_CONFIG, override={
            'PATH': INPUT_PATH,
            'OUTPUT_PATH': self.temp_path,
            })
        pelican = Pelican(settings=settings)
        pelican.run()
        dcmp = dircmp(self.temp_path, os.sep.join((OUTPUT_PATH, "custom")))
        self.assertFilesEqual(recursiveDiff(dcmp))
