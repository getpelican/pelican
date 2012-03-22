try:
    import unittest2
except ImportError, e:
    import unittest as unittest2

from os.path import dirname, abspath, join

from pelican.settings import read_settings, _DEFAULT_CONFIG


class TestSettingsFromFile(unittest2.TestCase):
    """Providing a file, it should read it, replace the default values and
    append new values to the settings, if any
    """
    def setUp(self):
        self.PATH = abspath(dirname(__file__))
        default_conf = join(self.PATH, 'default_conf.py')
        self.settings = read_settings(default_conf)

    def test_overwrite_existing_settings(self):
        self.assertEqual(self.settings.get('SITENAME'), u"Alexis' log")
        self.assertEqual(self.settings.get('SITEURL'),
                'http://blog.notmyidea.org')

    def test_keep_default_settings(self):
        """keep default settings if not defined"""
        self.assertEqual(self.settings.get('DEFAULT_CATEGORY'),
            _DEFAULT_CONFIG['DEFAULT_CATEGORY'])

    def test_dont_copy_small_keys(self):
        """do not copy keys not in caps."""
        self.assertNotIn('foobar', self.settings)

    def test_read_empty_settings(self):
        """providing no file should return the default values."""
        settings = read_settings(None)
        self.assertDictEqual(settings, _DEFAULT_CONFIG)
