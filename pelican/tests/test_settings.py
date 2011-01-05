from unittest2 import TestCase

from pelican.settings import read_settings, DEFAULT_CONFIG

class SettingsTest(TestCase):

    def test_read_settings(self):
        # providing no file should return the default values
        settings = read_settings(None)
        self.assertDictEqual(settings, DEFAULT_CONFIG)

        # providing a file should read it, replace the default values and append 
        # new values to the settings, if any
        settings = read_settings(mock)
        self.assertIn('key', settings)
        self.assertEqual(settings['KEY'
