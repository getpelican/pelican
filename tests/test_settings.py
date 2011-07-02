from unittest2 import TestCase
import os

from pelican.settings import read_settings, _DEFAULT_CONFIG

SETTINGS = os.sep.join([os.path.dirname(os.path.abspath(__file__)),
        "../../samples/pelican.conf.py"])

class SettingsTest(TestCase):


    def test_read_settings(self):
        # providing a file, it should read it, replace the default values and append 
        # new values to the settings, if any
        settings = read_settings(SETTINGS)

        # overwrite existing settings
        self.assertEqual(settings.get('SITENAME'), u"Alexis' log")
        
        # add new settings
        self.assertEqual(settings.get('SITEURL'), 'http://blog.notmyidea.org')

        # keep default settings if not defined
        self.assertEqual(settings.get('DEFAULT_CATEGORY'), 
            _DEFAULT_CONFIG['DEFAULT_CATEGORY'])

        # do not copy keys not in caps
        self.assertNotIn('foobar', settings)


    def test_empty_read_settings(self):
        # providing no file should return the default values
        settings = read_settings(None)
        self.assertDictEqual(settings, _DEFAULT_CONFIG)
