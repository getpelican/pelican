import os
from io import BytesIO
from shutil import rmtree
from tempfile import mkdtemp

from pelican.server import ComplexHTTPRequestHandler
from pelican.tests.support import unittest
from http.server import SimpleHTTPRequestHandler
from unittest.mock import patch

class MockRequest:
    def makefile(self, *_args, **_kwargs):
        return BytesIO(b"")


class MockServer:
    pass


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = MockServer()
        self.temp_output = mkdtemp(prefix="pelicantests.")
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_output)
        self.handler = ComplexHTTPRequestHandler(
            MockRequest(), ("0.0.0.0", 8888), self.server
        )
        self.handler.base_path = self.temp_output

    def tearDown(self):
        os.chdir(self.old_cwd)
        rmtree(self.temp_output)

    def test_get_path_that_exists(self):
        open(os.path.join(self.temp_output, "foo.html"), "a").close()
        os.mkdir(os.path.join(self.temp_output, "foo"))
        open(os.path.join(self.temp_output, "foo", "index.html"), "a").close()

        os.mkdir(os.path.join(self.temp_output, "bar"))
        open(os.path.join(self.temp_output, "bar", "index.html"), "a").close()

        os.mkdir(os.path.join(self.temp_output, "baz"))

        for suffix in ["", "/"]:
            # foo.html has precedence over foo/index.html
            path = self.handler.get_path_that_exists("foo" + suffix)
            self.assertEqual(path, "foo.html")

            # folder with index.html should return folder/index.html
            path = self.handler.get_path_that_exists("bar" + suffix)
            self.assertEqual(path, "bar/index.html")

            # folder without index.html should return same as input
            path = self.handler.get_path_that_exists("baz" + suffix)
            self.assertEqual(path, "baz" + suffix)

            # not existing path should return None
            path = self.handler.get_path_that_exists("quux" + suffix)
            self.assertIsNone(path)

    def test_guess_type_method_returns_javascript_for_js_files(self):
        js_file = os.path.join(self.temp_output, "script.js")
        with open(js_file, "w") as f:
            f.write("console.log('hello');")

        mimetype = self.handler.guess_type(js_file)
        self.assertIn(
            mimetype,
            ("text/javascript", "application/javascript"),
            f"Expected .js MIME type to be 'text/javascript' or 'application/javascript', got '{mimetype}'",
        )
    def test_get_missing_path_sends_404(self):
        self.handler.path = "/missing"

        with patch.object(self.handler, "send_error") as send_error:
            self.handler.do_GET()

        send_error.assert_called_once_with(404, "File not found")

    def test_head_resolves_html_suffix(self):
        with open(os.path.join(self.temp_output, "page.html"), "w") as f:
            f.write("Pelican test page")

        self.handler.path = "/page"

        with patch.object(SimpleHTTPRequestHandler, "do_HEAD") as parent_do_head:
            self.handler.do_HEAD()

        self.assertEqual(self.handler.path, "/page.html")
        parent_do_head.assert_called_once_with(self.handler)

    def test_head_missing_path_sends_404(self):
        self.handler.path = "/missing"

        with patch.object(self.handler, "send_error") as send_error:
            self.handler.do_HEAD()

        send_error.assert_called_once_with(404, "File not found")
