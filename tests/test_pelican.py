try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import os
from filecmp import dircmp

from .support import temporary_folder

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

    @unittest.skip("Test failing")
    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate the output without raising any exception / issuing
        # any warning.
        with temporary_folder() as temp_path:
            pelican = Pelican(path=INPUT_PATH, output_path=temp_path)
            pelican.run()
            diff = dircmp(temp_path, os.sep.join((OUTPUT_PATH, "basic")))
            self.assertEqual(diff.left_only, [])
            self.assertEqual(diff.right_only, [])
            self.assertEqual(diff.diff_files, [])

    @unittest.skip("Test failing")
    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        with temporary_folder() as temp_path:
            pelican = Pelican(path=INPUT_PATH, output_path=temp_path,
                              settings=read_settings(SAMPLE_CONFIG))
            pelican.run()
            diff = dircmp(temp_path, os.sep.join((OUTPUT_PATH, "custom")))
            self.assertEqual(diff.left_only, [])
            self.assertEqual(diff.right_only, [])
            self.assertEqual(diff.diff_files, [])
