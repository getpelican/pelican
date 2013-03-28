# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import unittest
import sys
import locale

from pelican.utils.importlib import import_module
from pelican.settings import read_settings
from pelican.settings.base import _DEFAULT_CONFIG

# runtest with:
# cd ~/pelican/pelican/tests && python -m unittest discover . 'test_pygments*' && cd -
class TestPygments(unittest.TestCase):

    def test_formatter(self):
        pass