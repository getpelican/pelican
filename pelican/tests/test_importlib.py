# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import codecs
import logging
import shutil
import os
import datetime
import time
import unittest
import sys
import shutil

from pelican.utils.importlib import import_module

# runtest with:
# cd ~/pelican/pelican/tests && python -m unittest discover . 'test_importlib*' && cd -
class TestImportLib(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('/tmp/pytest'):
            os.makedirs('/tmp/pytest')
        with codecs.open('/tmp/pytest/__init__.py','wb+', 'utf-8') as stream:
            stream.write('# -*- coding: utf-8 -*-')

        with codecs.open('/tmp/pytest/injected_module.py', 'wb+', 'utf-8') as stream:
            stream.write('''# -*- coding: utf-8 -*-
class Awesome(object):
    """
    This is pretty awesome.
    """
    def cute(self):
        return True
        
sauce = Awesome()
''')
        sys.path.append('/tmp')

    def tearDown(self):
        shutil.rmtree('/tmp/pytest')

    def test_import_lib(self):
        assert os.path.exists('/tmp/pytest/injected_module.py')
        assert '/tmp' in sys.path

        module = import_module('pytest.injected_module')
        assert hasattr(module, 'Awesome')
        assert hasattr(module, 'sauce')
        assert module.sauce.cute()

