import copy
import locale
import os
from os.path import abspath, dirname, join

from pelican.settings import (
    DEFAULT_CONFIG,
    DEFAULT_THEME,
    _printf_s_to_format_field,
    configure_settings,
    handle_deprecated_settings,
    read_settings,
)
from pelican.tests.support import unittest


class TestSettingsConfiguration(unittest.TestCase):
    """Provided a file, it should read it, replace the default values,
    append new values to the settings (if any), and apply basic settings
    optimizations.
    """

    def setUp(self):
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")
        self.PATH = abspath(dirname(__file__))
        default_conf = join(self.PATH, "default_conf.py")
        self.settings = read_settings(default_conf)

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)

    def test_overwrite_existing_settings(self):
        self.assertEqual(self.settings.get("SITENAME"), "Alexis' log")
        self.assertEqual(self.settings.get("SITEURL"), "http://blog.notmyidea.org")

    def test_keep_default_settings(self):
        # Keep default settings if not defined.
        self.assertEqual(
            self.settings.get("DEFAULT_CATEGORY"), DEFAULT_CONFIG["DEFAULT_CATEGORY"]
        )

    def test_dont_copy_small_keys(self):
        # Do not copy keys not in caps.
        self.assertNotIn("foobar", self.settings)

    def test_read_empty_settings(self):
        # Ensure an empty settings file results in default settings.
        settings = read_settings(None)
        expected = copy.deepcopy(DEFAULT_CONFIG)
        # Added by configure settings
        expected["FEED_DOMAIN"] = ""
        expected["ARTICLE_EXCLUDES"] = ["pages"]
        expected["PAGE_EXCLUDES"] = [""]
        self.maxDiff = None
        self.assertDictEqual(settings, expected)

    def test_settings_return_independent(self):
        # Make sure that the results from one settings call doesn't
        # effect past or future instances.
        self.PATH = abspath(dirname(__file__))
        default_conf = join(self.PATH, "default_conf.py")
        settings = read_settings(default_conf)
        settings["SITEURL"] = "new-value"
        new_settings = read_settings(default_conf)
        self.assertNotEqual(new_settings["SITEURL"], settings["SITEURL"])

    def test_defaults_not_overwritten(self):
        # This assumes 'SITENAME': 'A Pelican Blog'
        settings = read_settings(None)
        settings["SITENAME"] = "Not a Pelican Blog"
        self.assertNotEqual(settings["SITENAME"], DEFAULT_CONFIG["SITENAME"])

    def test_static_path_settings_safety(self):
        # Disallow static paths from being strings
        settings = {
            "STATIC_PATHS": "foo/bar",
            "THEME_STATIC_PATHS": "bar/baz",
            # These 4 settings are required to run configure_settings
            "PATH": ".",
            "THEME": DEFAULT_THEME,
            "SITEURL": "http://blog.notmyidea.org/",
            "LOCALE": "",
        }
        configure_settings(settings)
        self.assertEqual(settings["STATIC_PATHS"], DEFAULT_CONFIG["STATIC_PATHS"])
        self.assertEqual(
            settings["THEME_STATIC_PATHS"], DEFAULT_CONFIG["THEME_STATIC_PATHS"]
        )

    def test_configure_settings(self):
        # Manipulations to settings should be applied correctly.
        settings = {
            "SITEURL": "http://blog.notmyidea.org/",
            "LOCALE": "",
            "PATH": os.curdir,
            "THEME": DEFAULT_THEME,
        }
        configure_settings(settings)

        # SITEURL should not have a trailing slash
        self.assertEqual(settings["SITEURL"], "http://blog.notmyidea.org")

        # FEED_DOMAIN, if undefined, should default to SITEURL
        self.assertEqual(settings["FEED_DOMAIN"], "http://blog.notmyidea.org")

        settings["FEED_DOMAIN"] = "http://feeds.example.com"
        configure_settings(settings)
        self.assertEqual(settings["FEED_DOMAIN"], "http://feeds.example.com")

    def test_theme_settings_exceptions(self):
        settings = self.settings

        # Check that theme lookup in "pelican/themes" functions as expected
        settings["THEME"] = os.path.split(settings["THEME"])[1]
        configure_settings(settings)
        self.assertEqual(settings["THEME"], DEFAULT_THEME)

        # Check that non-existent theme raises exception
        settings["THEME"] = "foo"
        self.assertRaises(Exception, configure_settings, settings)

    def test_deprecated_dir_setting(self):
        settings = self.settings

        settings["ARTICLE_DIR"] = "foo"
        settings["PAGE_DIR"] = "bar"

        settings = handle_deprecated_settings(settings)

        self.assertEqual(settings["ARTICLE_PATHS"], ["foo"])
        self.assertEqual(settings["PAGE_PATHS"], ["bar"])

        with self.assertRaises(KeyError):
            settings["ARTICLE_DIR"]
            settings["PAGE_DIR"]

    def test_default_encoding(self):
        # Test that the user locale is set if not specified in settings

        locale.setlocale(locale.LC_ALL, "C")
        # empty string = user system locale
        self.assertEqual(self.settings["LOCALE"], [""])

        configure_settings(self.settings)
        lc_time = locale.getlocale(locale.LC_TIME)  # should be set to user locale

        # explicitly set locale to user pref and test
        locale.setlocale(locale.LC_TIME, "")
        self.assertEqual(lc_time, locale.getlocale(locale.LC_TIME))

    def test_invalid_settings_throw_exception(self):
        # Test that the path name is valid

        # test that 'PATH' is set
        settings = {}

        self.assertRaises(Exception, configure_settings, settings)

        # Test that 'PATH' is valid
        settings["PATH"] = ""
        self.assertRaises(Exception, configure_settings, settings)

        # Test nonexistent THEME
        settings["PATH"] = os.curdir
        settings["THEME"] = "foo"

        self.assertRaises(Exception, configure_settings, settings)

    def test__printf_s_to_format_field(self):
        for s in ("%s", "{%s}", "{%s"):
            option = f"foo/{s}/bar.baz"
            result = _printf_s_to_format_field(option, "slug")
            expected = option % "qux"
            found = result.format(slug="qux")
            self.assertEqual(expected, found)

    def test_deprecated_extra_templates_paths(self):
        settings = self.settings
        settings["EXTRA_TEMPLATES_PATHS"] = ["/foo/bar", "/ha"]

        settings = handle_deprecated_settings(settings)

        self.assertEqual(settings["THEME_TEMPLATES_OVERRIDES"], ["/foo/bar", "/ha"])
        self.assertNotIn("EXTRA_TEMPLATES_PATHS", settings)

    def test_deprecated_paginated_direct_templates(self):
        settings = self.settings
        settings["PAGINATED_DIRECT_TEMPLATES"] = ["index", "archives"]
        settings["PAGINATED_TEMPLATES"] = {"index": 10, "category": None}
        settings = handle_deprecated_settings(settings)
        self.assertEqual(
            settings["PAGINATED_TEMPLATES"],
            {"index": 10, "category": None, "archives": None},
        )
        self.assertNotIn("PAGINATED_DIRECT_TEMPLATES", settings)

    def test_deprecated_paginated_direct_templates_from_file(self):
        # This is equivalent to reading a settings file that has
        # PAGINATED_DIRECT_TEMPLATES defined but no PAGINATED_TEMPLATES.
        settings = read_settings(
            None, override={"PAGINATED_DIRECT_TEMPLATES": ["index", "archives"]}
        )
        self.assertEqual(
            settings["PAGINATED_TEMPLATES"],
            {
                "archives": None,
                "author": None,
                "index": None,
                "category": None,
                "tag": None,
            },
        )
        self.assertNotIn("PAGINATED_DIRECT_TEMPLATES", settings)

    def test_theme_and_extra_templates_exception(self):
        settings = self.settings
        settings["EXTRA_TEMPLATES_PATHS"] = ["/ha"]
        settings["THEME_TEMPLATES_OVERRIDES"] = ["/foo/bar"]

        self.assertRaises(Exception, handle_deprecated_settings, settings)

    def test_slug_and_slug_regex_substitutions_exception(self):
        settings = {}
        settings["SLUG_REGEX_SUBSTITUTIONS"] = [("C++", "cpp")]
        settings["TAG_SUBSTITUTIONS"] = [("C#", "csharp")]

        self.assertRaises(Exception, handle_deprecated_settings, settings)

    def test_deprecated_slug_substitutions(self):
        default_slug_regex_subs = self.settings["SLUG_REGEX_SUBSTITUTIONS"]

        # If no deprecated setting is set, don't set new ones
        settings = {}
        settings = handle_deprecated_settings(settings)
        self.assertNotIn("SLUG_REGEX_SUBSTITUTIONS", settings)
        self.assertNotIn("TAG_REGEX_SUBSTITUTIONS", settings)
        self.assertNotIn("CATEGORY_REGEX_SUBSTITUTIONS", settings)
        self.assertNotIn("AUTHOR_REGEX_SUBSTITUTIONS", settings)

        # If SLUG_SUBSTITUTIONS is set, set {SLUG, AUTHOR}_REGEX_SUBSTITUTIONS
        # correctly, don't set {CATEGORY, TAG}_REGEX_SUBSTITUTIONS
        settings = {}
        settings["SLUG_SUBSTITUTIONS"] = [("C++", "cpp")]
        settings = handle_deprecated_settings(settings)
        self.assertEqual(
            settings.get("SLUG_REGEX_SUBSTITUTIONS"),
            [(r"C\+\+", "cpp")] + default_slug_regex_subs,
        )
        self.assertNotIn("TAG_REGEX_SUBSTITUTIONS", settings)
        self.assertNotIn("CATEGORY_REGEX_SUBSTITUTIONS", settings)
        self.assertEqual(
            settings.get("AUTHOR_REGEX_SUBSTITUTIONS"), default_slug_regex_subs
        )

        # If {CATEGORY, TAG, AUTHOR}_SUBSTITUTIONS are set, set
        # {CATEGORY, TAG, AUTHOR}_REGEX_SUBSTITUTIONS correctly, don't set
        # SLUG_REGEX_SUBSTITUTIONS
        settings = {}
        settings["TAG_SUBSTITUTIONS"] = [("C#", "csharp")]
        settings["CATEGORY_SUBSTITUTIONS"] = [("C#", "csharp")]
        settings["AUTHOR_SUBSTITUTIONS"] = [("Alexander Todorov", "atodorov")]
        settings = handle_deprecated_settings(settings)
        self.assertNotIn("SLUG_REGEX_SUBSTITUTIONS", settings)
        self.assertEqual(
            settings["TAG_REGEX_SUBSTITUTIONS"],
            [(r"C\#", "csharp")] + default_slug_regex_subs,
        )
        self.assertEqual(
            settings["CATEGORY_REGEX_SUBSTITUTIONS"],
            [(r"C\#", "csharp")] + default_slug_regex_subs,
        )
        self.assertEqual(
            settings["AUTHOR_REGEX_SUBSTITUTIONS"],
            [(r"Alexander\ Todorov", "atodorov")] + default_slug_regex_subs,
        )

        # If {SLUG, CATEGORY, TAG, AUTHOR}_SUBSTITUTIONS are set, set
        # {SLUG, CATEGORY, TAG, AUTHOR}_REGEX_SUBSTITUTIONS correctly
        settings = {}
        settings["SLUG_SUBSTITUTIONS"] = [("C++", "cpp")]
        settings["TAG_SUBSTITUTIONS"] = [("C#", "csharp")]
        settings["CATEGORY_SUBSTITUTIONS"] = [("C#", "csharp")]
        settings["AUTHOR_SUBSTITUTIONS"] = [("Alexander Todorov", "atodorov")]
        settings = handle_deprecated_settings(settings)
        self.assertEqual(
            settings["TAG_REGEX_SUBSTITUTIONS"],
            [(r"C\+\+", "cpp")] + [(r"C\#", "csharp")] + default_slug_regex_subs,
        )
        self.assertEqual(
            settings["CATEGORY_REGEX_SUBSTITUTIONS"],
            [(r"C\+\+", "cpp")] + [(r"C\#", "csharp")] + default_slug_regex_subs,
        )
        self.assertEqual(
            settings["AUTHOR_REGEX_SUBSTITUTIONS"],
            [(r"Alexander\ Todorov", "atodorov")] + default_slug_regex_subs,
        )

        # Handle old 'skip' flags correctly
        settings = {}
        settings["SLUG_SUBSTITUTIONS"] = [("C++", "cpp", True)]
        settings["AUTHOR_SUBSTITUTIONS"] = [("Alexander Todorov", "atodorov", False)]
        settings = handle_deprecated_settings(settings)
        self.assertEqual(
            settings.get("SLUG_REGEX_SUBSTITUTIONS"),
            [(r"C\+\+", "cpp")] + [(r"(?u)\A\s*", ""), (r"(?u)\s*\Z", "")],
        )
        self.assertEqual(
            settings["AUTHOR_REGEX_SUBSTITUTIONS"],
            [(r"Alexander\ Todorov", "atodorov")] + default_slug_regex_subs,
        )

    def test_deprecated_slug_substitutions_from_file(self):
        # This is equivalent to reading a settings file that has
        # SLUG_SUBSTITUTIONS defined but no SLUG_REGEX_SUBSTITUTIONS.
        settings = read_settings(
            None, override={"SLUG_SUBSTITUTIONS": [("C++", "cpp")]}
        )
        self.assertEqual(
            settings["SLUG_REGEX_SUBSTITUTIONS"],
            [(r"C\+\+", "cpp")] + self.settings["SLUG_REGEX_SUBSTITUTIONS"],
        )
        self.assertNotIn("SLUG_SUBSTITUTIONS", settings)
