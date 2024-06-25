import contextlib
import io
import locale
import logging
import os
import subprocess
import sys
import unittest
from collections.abc import Sequence
from shutil import rmtree
from tempfile import TemporaryDirectory, mkdtemp
from unittest.mock import PropertyMock, patch

from rich.console import Console

import pelican.readers
from pelican import Pelican, __version__, main
from pelican.generators import StaticGenerator
from pelican.settings import read_settings
from pelican.tests.support import (
    LoggedTestCase,
    diff_subproc,
    locale_available,
    mute,
    skipIfNoExecutable,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, os.pardir, os.pardir, "samples")
)
OUTPUT_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "output"))

INPUT_PATH = os.path.join(SAMPLES_PATH, "content")
SAMPLE_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf.py")
SAMPLE_FR_CONFIG = os.path.join(SAMPLES_PATH, "pelican.conf_FR.py")


def recursiveDiff(dcmp):
    diff = {
        "diff_files": [os.path.join(dcmp.right, f) for f in dcmp.diff_files],
        "left_only": [os.path.join(dcmp.right, f) for f in dcmp.left_only],
        "right_only": [os.path.join(dcmp.right, f) for f in dcmp.right_only],
    }
    for sub_dcmp in dcmp.subdirs.values():
        for k, v in recursiveDiff(sub_dcmp).items():
            diff[k] += v
    return diff


class TestPelican(LoggedTestCase):
    # general functional testing for pelican. Basically, this test case tries
    # to run pelican in different situations and see how it behaves

    def setUp(self):
        super().setUp()
        self.temp_path = mkdtemp(prefix="pelicantests.")
        self.temp_cache = mkdtemp(prefix="pelican_cache.")
        self.maxDiff = None
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")

    def tearDown(self):
        read_settings()  # cleanup PYGMENTS_RST_OPTIONS
        rmtree(self.temp_path)
        rmtree(self.temp_cache)
        locale.setlocale(locale.LC_ALL, self.old_locale)
        super().tearDown()

    def assertDirsEqual(self, left_path, right_path, msg=None):
        """
        Check if the files are the same (ignoring whitespace) below both paths.
        """
        proc = diff_subproc(left_path, right_path)

        out, err = proc.communicate()
        if proc.returncode != 0:
            msg = self._formatMessage(
                msg,
                f"{left_path} and {right_path} differ:\nstdout:\n{out}\nstderr\n{err}",
            )
            raise self.failureException(msg)

    def test_order_of_generators(self):
        # StaticGenerator must run last, so it can identify files that
        # were skipped by the other generators, and so static files can
        # have their output paths overridden by the {attach} link syntax.

        pelican = Pelican(settings=read_settings(path=None))
        generator_classes = pelican._get_generator_classes()

        self.assertTrue(
            generator_classes[-1] is StaticGenerator,
            "StaticGenerator must be the last generator, but it isn't!",
        )
        self.assertIsInstance(
            generator_classes,
            Sequence,
            "_get_generator_classes() must return a Sequence to preserve order",
        )

    @skipIfNoExecutable(["git", "--version"])
    def test_basic_generation_works(self):
        # when running pelican without settings, it should pick up the default
        # ones and generate correct output without raising any exception
        settings = read_settings(
            path=None,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "LOCALE": locale.normalize("en_US"),
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(self.temp_path, os.path.join(OUTPUT_PATH, "basic"))
        self.assertLogCountEqual(
            count=1,
            msg="Unable to find.*skipping url replacement",
            level=logging.WARNING,
        )

    @skipIfNoExecutable(["git", "--version"])
    def test_custom_generation_works(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(
            path=SAMPLE_CONFIG,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "LOCALE": locale.normalize("en_US.UTF-8"),
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(self.temp_path, os.path.join(OUTPUT_PATH, "custom"))

    @skipIfNoExecutable(["git", "--version"])
    @unittest.skipUnless(
        locale_available("fr_FR.UTF-8") or locale_available("French"),
        "French locale needed",
    )
    def test_custom_locale_generation_works(self):
        """Test that generation with fr_FR.UTF-8 locale works"""
        if sys.platform == "win32":
            our_locale = "French"
        else:
            our_locale = "fr_FR.UTF-8"

        settings = read_settings(
            path=SAMPLE_FR_CONFIG,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "LOCALE": our_locale,
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertDirsEqual(self.temp_path, os.path.join(OUTPUT_PATH, "custom_locale"))

    def test_theme_static_paths_copy(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(
            path=SAMPLE_CONFIG,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "THEME_STATIC_PATHS": [
                    os.path.join(SAMPLES_PATH, "very"),
                    os.path.join(SAMPLES_PATH, "kinda"),
                    os.path.join(SAMPLES_PATH, "theme_standard"),
                ],
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        theme_output = os.path.join(self.temp_path, "theme")
        extra_path = os.path.join(theme_output, "exciting", "new", "files")

        for file in ["a_stylesheet", "a_template"]:
            self.assertTrue(os.path.exists(os.path.join(theme_output, file)))

        for file in ["wow!", "boom!", "bap!", "zap!"]:
            self.assertTrue(os.path.exists(os.path.join(extra_path, file)))

    def test_theme_static_paths_copy_single_file(self):
        # the same thing with a specified set of settings should work
        settings = read_settings(
            path=SAMPLE_CONFIG,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "THEME_STATIC_PATHS": [os.path.join(SAMPLES_PATH, "theme_standard")],
            },
        )

        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        theme_output = os.path.join(self.temp_path, "theme")

        for file in ["a_stylesheet", "a_template"]:
            self.assertTrue(os.path.exists(os.path.join(theme_output, file)))

    def test_cyclic_intersite_links_no_warnings(self):
        settings = read_settings(
            path=None,
            override={
                "PATH": os.path.join(CURRENT_DIR, "cyclic_intersite_links"),
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        # There are four different intersite links:
        # - one pointing to the second article from first and third
        # - one pointing to the first article from second and third
        # - one pointing to the third article from first and second
        # - one pointing to a nonexistent from each
        # If everything goes well, only the warning about the nonexistent
        # article should be printed. Only two articles are not sufficient,
        # since the first will always have _context['generated_content'] empty
        # (thus skipping the link resolving) and the second will always have it
        # non-empty, containing the first, thus always succeeding.
        self.assertLogCountEqual(
            count=1,
            msg="Unable to find '.*\\.rst', skipping url replacement.",
            level=logging.WARNING,
        )

    def test_md_extensions_deprecation(self):
        """Test that a warning is issued if MD_EXTENSIONS is used"""
        settings = read_settings(
            path=None,
            override={
                "PATH": INPUT_PATH,
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
                "MD_EXTENSIONS": {},
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertLogCountEqual(
            count=1,
            msg="MD_EXTENSIONS is deprecated use MARKDOWN instead.",
            level=logging.WARNING,
        )

    def test_parse_errors(self):
        # Verify that just an error is printed and the application doesn't
        # abort, exit or something.
        settings = read_settings(
            path=None,
            override={
                "PATH": os.path.abspath(os.path.join(CURRENT_DIR, "parse_error")),
                "OUTPUT_PATH": self.temp_path,
                "CACHE_PATH": self.temp_cache,
            },
        )
        pelican = Pelican(settings=settings)
        mute(True)(pelican.run)()
        self.assertLogCountEqual(
            count=1, msg="Could not process .*parse_error.rst", level=logging.ERROR
        )

    def test_module_load(self):
        """Test loading via python -m pelican --help displays the help"""
        output = subprocess.check_output(
            [sys.executable, "-m", "pelican", "--help"]
        ).decode("ascii", "replace")
        assert "usage:" in output

    def test_main_version(self):
        """Run main --version."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit):
                main(["--version"])
            self.assertEqual(f"{__version__}\n", out.getvalue())

    def test_main_help(self):
        """Run main --help."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit):
                main(["--help"])
            self.assertIn("A tool to generate a static blog", out.getvalue())

    def test_main_on_content(self):
        """Invoke main on simple_content directory."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with TemporaryDirectory() as temp_dir:
                # Don't highlight anything.
                # See https://rich.readthedocs.io/en/stable/highlighting.html
                with patch("pelican.console", new=Console(highlight=False)):
                    main(["-o", temp_dir, "pelican/tests/simple_content"])
            self.assertIn("Processed 1 article", out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_main_on_content_markdown_disabled(self):
        """Invoke main on simple_content directory."""
        with patch.object(
            pelican.readers.MarkdownReader, "enabled", new_callable=PropertyMock
        ) as attr_mock:
            attr_mock.return_value = False
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                with TemporaryDirectory() as temp_dir:
                    # Don't highlight anything.
                    # See https://rich.readthedocs.io/en/stable/highlighting.html
                    with patch("pelican.console", new=Console(highlight=False)):
                        main(["-o", temp_dir, "pelican/tests/simple_content"])
                self.assertIn("Processed 0 articles", out.getvalue())
                self.assertLogCountEqual(
                    1,
                    ".*article_with_md_extension.md: "
                    "Could not import 'markdown.Markdown'. "
                    "Have you installed the 'markdown' package?",
                )
