import os
from io import BytesIO
from shutil import rmtree
from tempfile import mkdtemp

from pelican.server import ComplexHTTPRequestHandler
from pelican.tests.support import unittest


class MockRequest:
    def makefile(self, *args, **kwargs):
        return BytesIO(b"")


class MockServer:
    pass


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = MockServer()
        self.temp_output = mkdtemp(prefix="pelicantests.")
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_output)

    def tearDown(self):
        os.chdir(self.old_cwd)
        rmtree(self.temp_output)

    def test_get_path_that_exists(self):
        handler = ComplexHTTPRequestHandler(
            MockRequest(), ("0.0.0.0", 8888), self.server
        )
        handler.base_path = self.temp_output

        open(os.path.join(self.temp_output, "foo.html"), "a").close()
        os.mkdir(os.path.join(self.temp_output, "foo"))
        open(os.path.join(self.temp_output, "foo", "index.html"), "a").close()

        os.mkdir(os.path.join(self.temp_output, "bar"))
        open(os.path.join(self.temp_output, "bar", "index.html"), "a").close()

        os.mkdir(os.path.join(self.temp_output, "baz"))

        for suffix in ["", "/"]:
            # foo.html has precedence over foo/index.html
            path = handler.get_path_that_exists("foo" + suffix)
            self.assertEqual(path, "foo.html")

            # folder with index.html should return folder/index.html
            path = handler.get_path_that_exists("bar" + suffix)
            self.assertEqual(path, "bar/index.html")

            # folder without index.html should return same as input
            path = handler.get_path_that_exists("baz" + suffix)
            self.assertEqual(path, "baz" + suffix)

            # not existing path should return None
            path = handler.get_path_that_exists("quux" + suffix)
            self.assertIsNone(path)
