# -*- coding: utf-8 -*-

import hashlib
import os
from codecs import open
from tempfile import mkdtemp
from shutil import rmtree

from pelican import Pelican
from pelican.settings import read_settings
from .support import unittest, skipIfNoExecutable, module_exists

CUR_DIR = os.path.dirname(__file__)
THEME_DIR = os.path.join(CUR_DIR, 'themes', 'assets')
CSS_REF = open(os.path.join(THEME_DIR, 'static', 'css',
                            'style.min.css')).read()
CSS_HASH = hashlib.md5(CSS_REF).hexdigest()[0:8]


@unittest.skipUnless(module_exists('webassets'), "webassets isn't installed")
@skipIfNoExecutable(['scss', '-v'])
@skipIfNoExecutable(['cssmin', '--version'])
class TestWebAssets(unittest.TestCase):
    """Base class for testing webassets."""

    def setUp(self, override=None):
        self.temp_path = mkdtemp()
        settings = {
            'PATH': os.path.join(CUR_DIR, 'content', 'TestCategory'),
            'OUTPUT_PATH': self.temp_path,
            'PLUGINS': ['pelican.plugins.assets', ],
            'THEME': THEME_DIR,
        }
        if override:
            settings.update(override)

        self.settings = read_settings(override=settings)
        pelican = Pelican(settings=self.settings)
        pelican.run()

    def tearDown(self):
        rmtree(self.temp_path)

    def check_link_tag(self, css_file, html_file):
        """Check the presence of `css_file` in `html_file`."""

        link_tag = '<link rel="stylesheet" href="{css_file}">'.\
                   format(css_file=css_file)
        html = open(html_file).read()
        self.assertRegexpMatches(html, link_tag)


class TestWebAssetsRelativeURLS(TestWebAssets):
    """Test pelican with relative urls."""

    def test_jinja2_ext(self):
        """Test that the Jinja2 extension was correctly added."""

        from webassets.ext.jinja2 import AssetsExtension
        self.assertIn(AssetsExtension, self.settings['JINJA_EXTENSIONS'])

    def test_compilation(self):
        """Compare the compiled css with the reference."""

        gen_file = os.path.join(self.temp_path, 'theme', 'gen',
                                'style.{0}.min.css'.format(CSS_HASH))
        self.assertTrue(os.path.isfile(gen_file))

        css_new = open(gen_file).read()
        self.assertEqual(css_new, CSS_REF)

    def test_template(self):
        """Look in the output files for the link tag."""

        css_file = './theme/gen/style.{0}.min.css'.format(CSS_HASH)
        html_files = ['index.html', 'archives.html',
                      'this-is-an-article-with-category.html']
        for f in html_files:
            self.check_link_tag(css_file, os.path.join(self.temp_path, f))

        self.check_link_tag(
            '../theme/gen/style.{0}.min.css'.format(CSS_HASH),
            os.path.join(self.temp_path, 'category/yeah.html'))


class TestWebAssetsAbsoluteURLS(TestWebAssets):
    """Test pelican with absolute urls."""

    def setUp(self):
        TestWebAssets.setUp(self, override={'RELATIVE_URLS': False,
                                            'SITEURL': 'http://localhost'})

    def test_absolute_url(self):
        """Look in the output files for the link tag with absolute url."""

        css_file = 'http://localhost/theme/gen/style.{0}.min.css'.\
                   format(CSS_HASH)
        html_files = ['index.html', 'archives.html',
                      'this-is-an-article-with-category.html']
        for f in html_files:
            self.check_link_tag(css_file, os.path.join(self.temp_path, f))
