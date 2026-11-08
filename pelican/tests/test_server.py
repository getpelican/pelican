import os
from io import BytesIO
from shutil import rmtree
from tempfile import mkdtemp

from pelican.server import ComplexHTTPRequestHandler
from pelican.tests.support import unittest


class MockRequest:
    def makefile(self, *_args, **_kwargs):
        return BytesIO(b"")


class MockRequestWithResponse:
    """Serves one canned request and captures the response bytes."""

    def __init__(self, request: bytes):
        self.request = BytesIO(request)
        self.response = BytesIO()

    def makefile(self, mode, *_args, **_kwargs):
        return self.request if "r" in mode else self.response

    def sendall(self, data):
        self.response.write(data)


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

    def test_get_missing_file_returns_404(self):
        """A request for a nonexistent file gets an HTTP 404 response,
        not an empty reply."""
        request = MockRequestWithResponse(
            b"GET /quux HTTP/1.1\r\nHost: localhost\r\n\r\n"
        )
        # The request is handled during construction, and the base path is
        # a class attribute (set by `RootedHTTPServer` in production).
        ComplexHTTPRequestHandler.base_path = self.temp_output
        ComplexHTTPRequestHandler(request, ("0.0.0.0", 8888), self.server)

        response = request.response.getvalue()
        self.assertTrue(response.startswith(b"HTTP/1.0 404"), response)
        self.assertIn(b"File not found", response)

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
