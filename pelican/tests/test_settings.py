# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import copy
import os
from os.path import dirname, abspath, join

from pelican.settings import (read_settings, configure_settings,
                              _DEFAULT_CONFIG, DEFAULT_THEME)
from pelican.tests.support import unittest


class TestSettingsConfiguration(unittest.TestCase):
    """Provided a file, it should read it, replace the default values,
    append new values to the settings (if any), and apply basic settings
    optimizations.
    """
    def setUp(self):
        self.PATH = abspath(dirname(__file__))
        default_conf = join(self.PATH, 'default_conf.py')
        self.settings = read_settings(default_conf)

    def test_overwrite_existing_settings(self):
        self.assertEqual(self.settings.get('SITENAME'), "Alexis' log")
        self.assertEqual(self.settings.get('SITEURL'),
                'http://blog.notmyidea.org')

    def test_keep_default_settings(self):
        # Keep default settings if not defined.
        self.assertEqual(self.settings.get('DEFAULT_CATEGORY'),
            _DEFAULT_CONFIG['DEFAULT_CATEGORY'])

    def test_dont_copy_small_keys(self):
        # Do not copy keys not in caps.
        self.assertNotIn('foobar', self.settings)

    def test_read_empty_settings(self):
        # Providing no file should return the default values.
        settings = read_settings(None)
        expected = copy.deepcopy(_DEFAULT_CONFIG)
        expected['FEED_DOMAIN'] = ''  # Added by configure settings
        self.maxDiff = None
        self.assertDictEqual(settings, expected)

    def test_settings_return_independent(self):
        # Make sure that the results from one settings call doesn't
        # effect past or future instances.
        self.PATH = abspath(dirname(__file__))
        default_conf = join(self.PATH, 'default_conf.py')
        settings = read_settings(default_conf)
        settings['SITEURL'] = 'new-value'
        new_settings = read_settings(default_conf)
        self.assertNotEqual(new_settings['SITEURL'], settings['SITEURL'])

    def test_defaults_not_overwritten(self):
        # This assumes 'SITENAME': 'A Pelican Blog'
        settings = read_settings(None)
        settings['SITENAME'] = 'Not a Pelican Blog'
        self.assertNotEqual(settings['SITENAME'], _DEFAULT_CONFIG['SITENAME'])

    def test_path_settings_safety(self):
        """Don't let people setting the static path listings to strs"""
        settings = {'STATIC_PATHS': 'foo/bar',
                'THEME_STATIC_PATHS': 'bar/baz',
                # These 4 settings are required to run configure_settings
                'PATH': '.',
                'THEME': DEFAULT_THEME,
                'SITEURL': 'http://blog.notmyidea.org/',
                'LOCALE': '',
                }
        configure_settings(settings)
        self.assertEqual(settings['STATIC_PATHS'],
                _DEFAULT_CONFIG['STATIC_PATHS'])
        self.assertEqual(settings['THEME_STATIC_PATHS'],
                _DEFAULT_CONFIG['THEME_STATIC_PATHS'])

    def test_configure_settings(self):
        #Manipulations to settings should be applied correctly.

        settings = {
                'SITEURL': 'http://blog.notmyidea.org/',
                'LOCALE': '',
                'PATH': os.curdir,
                'THEME': DEFAULT_THEME,
                }
        configure_settings(settings)
        # SITEURL should not have a trailing slash
        self.assertEqual(settings['SITEURL'], 'http://blog.notmyidea.org')

        # FEED_DOMAIN, if undefined, should default to SITEURL
        self.assertEqual(settings['FEED_DOMAIN'], 'http://blog.notmyidea.org')

        settings['FEED_DOMAIN'] = 'http://feeds.example.com'
        configure_settings(settings)
        self.assertEqual(settings['FEED_DOMAIN'], 'http://feeds.example.com')
