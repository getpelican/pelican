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
# cd ~/pelican/pelican/tests && python -m unittest discover . 'test_importeds*' && cd -
class TestImportLib(unittest.TestCase):
    def setUp(self):
        self.path = path = os.path.join(os.path.dirname(__file__), '../..')
        sys.path.append(os.path.abspath(path))


    def test_importedsettings(self):
        self.settings = read_settings(path=None, override={
            'LOCALE': locale.normalize('en_US'),
            'THEME': '/'.join([self.path, 'pelican/themes/simple'])
            })
        from pelican.settings import conf
        for key in _DEFAULT_CONFIG.keys():
            assert hasattr(conf, key)

