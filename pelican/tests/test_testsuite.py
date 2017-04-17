# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import warnings

import six

from pelican.tests.support import unittest


class TestSuiteTest(unittest.TestCase):
    def test_error_on_warning(self):
        if six.PY2:
            asserter = self.assertRaises
        else:
            asserter = self.assertWarns

        with asserter(UserWarning):
            warnings.warn('test warning')
