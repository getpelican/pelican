import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from pelican import Pelican
from pelican.settings import read_settings
from pelican.tests.support import LoggedTestCase, mute

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(CURRENT_DIR, "simple_content")


class TestTemplateInheritance(LoggedTestCase):
    def setUp(self):
        super().setUp()
        self.temp_output = mkdtemp(prefix="pelican_test_output.")
        self.temp_theme = mkdtemp(prefix="pelican_test_theme.")
        self.temp_cache = mkdtemp(prefix="pelican_test_cache.")

        # Create test theme directory structure
        os.makedirs(os.path.join(self.temp_theme, "templates"), exist_ok=True)

        # Create base.html template that inherits from simple theme
        template_content = """{% extends "!simple/base.html" %}

{% block head %}
{{ super() }}
    <link rel="stylesheet" type="text/css" href="{{ SITEURL }}/theme/css/style.css" />
{% endblock %}

{% block footer %}
    <p>New footer</p>
{% endblock %}
"""

        with open(os.path.join(self.temp_theme, "templates", "base.html"), "w") as f:
            f.write(template_content)

    def tearDown(self):
        """Clean up temporary directories and files"""
        for path in [self.temp_output, self.temp_theme, self.temp_cache]:
            if os.path.exists(path):
                rmtree(path)

        super().tearDown()

    def test_simple_theme(self):
        """Test that when a template is missing from our theme, Pelican falls back
        to using the template from the simple theme."""

        settings = read_settings(
            path=None,
            override={
                "THEME": "simple",
                "PATH": CONTENT_DIR,
                "OUTPUT_PATH": self.temp_output,
                "CACHE_PATH": self.temp_cache,
                "SITEURL": "http://example.com",
                # Disable unnecessary output that might cause failures
                "ARCHIVES_SAVE_AS": "",
                "CATEGORIES_SAVE_AS": "",
                "TAGS_SAVE_AS": "",
                "AUTHOR_SAVE_AS": "",
                "AUTHORS_SAVE_AS": "",
            },
        )

        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()

        output_file = os.path.join(self.temp_output, "test-md-file.html")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            content = f.read()

        # Verify file content is present
        self.assertIn("Test md File", content)

        # Verify simple theme content is present
        self.assertIn('<html lang="en">', content)
        self.assertIn("Proudly powered by", content)

        # Verify our custom theme additions are NOT present
        # (since we should be using the simple theme's template directly)
        self.assertNotIn(
            '<link rel="stylesheet" type="text/css" href="http://example.com/theme/css/style.css"',
            content,
        )

    def test_theme_inheritance(self):
        """Test that theme inheritance works correctly"""
        settings = read_settings(
            path=None,
            override={
                "THEME": self.temp_theme,
                "PATH": CONTENT_DIR,
                "OUTPUT_PATH": self.temp_output,
                "CACHE_PATH": self.temp_cache,
                "SITEURL": "http://example.com",
                # Disable unnecessary output that might cause failures
                "ARCHIVES_SAVE_AS": "",
                "CATEGORIES_SAVE_AS": "",
                "TAGS_SAVE_AS": "",
                "AUTHOR_SAVE_AS": "",
                "AUTHORS_SAVE_AS": "",
            },
        )

        pelican = Pelican(settings=settings)
        # Generate the site with muted output
        mute(True)(pelican.run)()

        # Check the output file
        output_file = os.path.join(self.temp_output, "test-md-file.html")
        self.assertTrue(os.path.exists(output_file))

        with open(output_file) as f:
            content = f.read()

        # Verify inheritance worked
        self.assertIn('<html lang="en">', content)  # From simple theme

        # Verify super() maintained original head content
        self.assertIn('<meta charset="utf-8"', content)

        # Verify our changes were included
        self.assertIn(
            '<link rel="stylesheet" type="text/css" href="http://example.com/theme/css/style.css"',
            content,
        )
        self.assertNotIn("Proudly powered by", content)
        self.assertIn("New footer", content)


if __name__ == "__main__":
    unittest.main()
