try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import os
from filecmp import dircmp
from tempfile import mkdtemp
from shutil import rmtree
import locale

from mock import patch

from pelican import Pelican
from pelican.settings import read_settings

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PATH = os.path.abspath(os.sep.join((CURRENT_DIR, "..", "samples")))
OUTPUT_PATH = os.path.abspath(os.sep.join((CURRENT_DIR, "output")))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")


class TestPelican(unittest.TestCase):
    # general functional testing for pelican. Basically, this test case tries
    # to run pelican in different situations and see how it behaves

    def setUp(self):
        self.temp_path = mkdtemp()
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

    def tearDown(self):
        rmtree(self.temp_path)
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def assertFilesEqual(self, diff):
        msg = "some generated files differ from the expected functional " \
              "tests output.\n" \
              "This is probably because the HTML generated files " \
              "changed. If these changes are normal, please refer " \
              "to docs/contribute.rst to update the expected " \
              "output of the functional tests."

        self.assertEqual(diff.left_only, [], msg=msg)
        self.assertEqual(diff.right_only, [], msg=msg)
        self.assertEqual(diff.diff_files, [], msg=msg)

    @unittest.skip("Test failing")
    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate the output without raising any exception / issuing
        # any warning.
        with patch("pelican.contents.getenv") as mock_getenv:
            # force getenv('USER') to always return the same value
            mock_getenv.return_value = "Dummy Author"
            pelican = Pelican(path=INPUT_PATH, output_path=self.temp_path)
            pelican.run()
            diff = dircmp(
                    self.temp_path, os.sep.join((OUTPUT_PATH, "basic")))
            self.assertFilesEqual(diff)

    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        pelican = Pelican(path=INPUT_PATH, output_path=self.temp_path,
                            settings=read_settings(SAMPLE_CONFIG))
        pelican.run()
        diff = dircmp(self.temp_path, os.sep.join((OUTPUT_PATH, "custom")))
        self.assertFilesEqual(diff)
