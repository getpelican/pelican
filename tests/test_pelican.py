import unittest
import os

from .support import temporary_folder

from pelican import Pelican
from pelican.settings import read_settings

SAMPLES_PATH = os.path.abspath(os.sep.join(
    (os.path.dirname(os.path.abspath(__file__)), "..", "samples")))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")


class TestPelican(unittest.TestCase):
    # general functional testing for pelican. Basically, this test case tries
    # to run pelican in different situations and see how it behaves

    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate the output without raising any exception / issuing
        # any warning.
        with temporary_folder() as temp_path:
            pelican = Pelican(path=INPUT_PATH, output_path=temp_path)
            pelican.run()

        # the same thing with a specified set of settins should work
        with temporary_folder() as temp_path:
            pelican = Pelican(path=INPUT_PATH, output_path=temp_path,
                              settings=read_settings(SAMPLE_CONFIG))
