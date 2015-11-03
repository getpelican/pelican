# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys
import warnings

from pelican.tests.support import unittest


class TestSuiteTest(unittest.TestCase):

    @unittest.skipIf(sys.version_info[:2] == (3, 3),
                     "does not throw an exception on python 3.3")
    def test_error_on_warning(self):
        with self.assertRaises(UserWarning):
            warnings.warn('test warning')
