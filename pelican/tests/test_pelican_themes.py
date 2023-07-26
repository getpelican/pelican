# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from pelican.tools.pelican_themes import symlink, _THEMES_PATH
from pelican.tests.support import LoggedTestCase

CURRENT_DIR_REL = os.path.dirname(__file__)
THEME_TARGET_PATH = os.path.join(_THEMES_PATH, "theme")

class TestPelicanThemes(LoggedTestCase):
    # testing for pelican-themes commands. 

    def setUp(self):
        super(TestPelicanThemes, self).setUp()

    def tearDown(self):
        super(TestPelicanThemes, self).tearDown()
        os.remove(THEME_TARGET_PATH)

    def test_symlink_relative(self):
        symlink(os.path.join(CURRENT_DIR_REL, "TestTheme/theme/"))
        self.assertTrue(os.path.exists(THEME_TARGET_PATH))
