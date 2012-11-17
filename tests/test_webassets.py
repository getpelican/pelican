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


@unittest.skipUnless(module_exists('webassets'), "webassets isn't installed")
@skipIfNoExecutable(['scss', '-v'])
@skipIfNoExecutable(['cssmin', '--version'])
class TestWebAssets(unittest.TestCase):

    def setUp(self):
        """Run pelican with two settings (absolute and relative urls)."""

        self.theme_dir = os.path.join(CUR_DIR, 'themes', 'assets')

        self.temp_path = mkdtemp()
        self.settings = read_settings(override={
            'PATH': os.path.join(CUR_DIR, 'content', 'TestCategory'),
            'OUTPUT_PATH': self.temp_path,
            'PLUGINS': ['pelican.plugins.assets', ],
            'THEME': self.theme_dir,
        })
        pelican = Pelican(settings=self.settings)
        pelican.run()

        # run Pelican a second time with absolute urls
        self.temp_path2 = mkdtemp()
        self.settings2 = read_settings(override={
            'PATH': os.path.join(CUR_DIR, 'content', 'TestCategory'),
            'OUTPUT_PATH': self.temp_path2,
            'PLUGINS': ['pelican.plugins.assets', ],
            'THEME': self.theme_dir,
            'RELATIVE_URLS': False,
            'SITEURL': 'http://localhost'
        })
        pelican2 = Pelican(settings=self.settings2)
        pelican2.run()

        self.css_ref = open(os.path.join(self.theme_dir, 'static', 'css',
                                         'style.min.css')).read()
        self.version = hashlib.md5(self.css_ref).hexdigest()[0:8]

    def tearDown(self):
        rmtree(self.temp_path)
        rmtree(self.temp_path2)

    def test_jinja2_ext(self):
        """Test that the Jinja2 extension was correctly added."""

        from webassets.ext.jinja2 import AssetsExtension
        self.assertIn(AssetsExtension, self.settings['JINJA_EXTENSIONS'])

    def test_compilation(self):
        """Compare the compiled css with the reference."""

        gen_file = os.path.join(self.temp_path, 'theme', 'gen',
                                'style.{0}.min.css'.format(self.version))

        self.assertTrue(os.path.isfile(gen_file))
        css_new = open(gen_file).read()
        self.assertEqual(css_new, self.css_ref)

    def check_link_tag(self, css_file, html_file):
        """Check the presence of `css_file` in `html_file`."""

        link_tag = '<link rel="stylesheet" href="{css_file}">'.\
                   format(css_file=css_file)
        html = open(html_file).read()
        self.assertRegexpMatches(html, link_tag)

    def test_template(self):
        """Look in the output index.html file for the link tag."""

        css_file = 'theme/gen/style.{0}.min.css'.format(self.version)
        html_files = ['index.html', 'archives.html',
                      'this-is-an-article-with-category.html']
        for f in html_files:
            self.check_link_tag(css_file, os.path.join(self.temp_path, f))

    def test_absolute_url(self):
        """Look in the output index.html file for the link tag with abs url."""

        css_file = 'http://localhost/theme/gen/style.{0}.min.css'.\
                   format(self.version)
        html_files = ['index.html', 'archives.html',
                      'this-is-an-article-with-category.html']
        for f in html_files:
            self.check_link_tag(css_file, os.path.join(self.temp_path2, f))
