# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

# Standard lib
import os
import sys
import shutil
from io import StringIO
from tempfile import mkdtemp
import contextlib

# Pelican
from pelican.tools import pelican_quickstart
from .support import unittest

# python2 doesn't have mock in the standard lib
try:
    mock = unittest.mock
except AttributeError:
    mock = None

if mock is None:
    try:
        import mock
    except ImportError:
        mock = None


# Helper classes
class FileSystemTest(unittest.TestCase):
    """ Make a temporary dir to test file I/O """

    def setUp(self):
        prev_self = super(FileSystemTest, self)
        if hasattr(prev_self, 'setUp'):
            prev_self.setUp()

        self.tempdir = mkdtemp()

    def tearDown(self):
        try:
            if os.path.isdir(self.tempdir):
                shutil.rmtree(self.tempdir)
        except Exception:
            pass

        prev_self = super(FileSystemTest, self)
        if hasattr(prev_self, 'tearDown'):
            prev_self.tearDown()

    def assertIsFile(self, path):

        msg = 'File not found: {}'.format(path)
        self.assertTrue(os.path.isfile(path), msg=msg)

    def assertIsDir(self, path):

        msg = 'Directory not found: {}'.format(path)
        self.assertTrue(os.path.isdir(path), msg=msg)

    def assertPathDoesntExist(self, path):

        msg = 'Path found unexpectedly: {}'.format(path)
        self.assertFalse(os.path.exists(path), msg=msg)


@contextlib.contextmanager
def record_output():
    """ Record the standard output of a command

    Usage::

        >>> with record_output() as out:
        >>>    print('hiiiiiii')
        >>> out.getvalue()
        'hiiiiiii\n'
    """

    old_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = old_stdout


# Tests
class TestMakeDirs(FileSystemTest):

    dirnames = ['content', 'output']

    def test_make_dir_okay(self):

        for dirname in self.dirnames:

            dirpath = os.path.join(self.tempdir, dirname)

            self.assertPathDoesntExist(dirpath)

            pelican_quickstart.makedirs(dirpath)

            self.assertIsDir(dirpath)

    @unittest.skipIf(mock is None, "need to install mock")
    def test_make_dir_error(self):

        dirpath = os.path.join(self.tempdir, 'evil')

        with mock.patch('os.makedirs') as makedirs:
            makedirs.side_effect = OSError
            with record_output() as out:

                pelican_quickstart.makedirs(dirpath)

        self.assertTrue(out.getvalue().startswith('Error:'))


class TestChmod(FileSystemTest):

    def test_make_dir_okay(self):

        filepath = os.path.join(self.tempdir, 'foo.txt')

        with open(filepath, 'wt') as fp:
            fp.write('')

        pelican_quickstart.chmod(filepath, 493)  # 0o755

        self.assertTrue(os.access(filepath, os.R_OK))
        self.assertTrue(os.access(filepath, os.W_OK))
        self.assertTrue(os.access(filepath, os.X_OK))

    @unittest.skipIf(mock is None, "need to install mock")
    def test_make_dir_error(self):

        with mock.patch('os.chmod') as chmod:
            chmod.side_effect = OSError
            with record_output() as out:
                pelican_quickstart.chmod('bad.txt', 493)

        self.assertTrue(out.getvalue().startswith('Error:'))


class TestMakeTemplate(FileSystemTest):

    template_files = [
        'pelicanconf.py', 'publishconf.py', 'fabfile.py',
        'Makefile', 'develop_server.sh',
    ]

    def test_make_template(self):

        for filename in self.template_files:

            filepath = os.path.join(self.tempdir, filename)

            self.assertPathDoesntExist(filepath)

            pelican_quickstart.make_template(filepath, {})

            self.assertIsFile(filepath)

    @unittest.skipIf(mock is None, "need to install mock")
    def test_make_template_fails(self):

        filepath = os.path.join(self.tempdir, 'pelicanconf.py')

        with mock.patch('codecs.open') as codecs_open:
            codecs_open.side_effect = OSError
            with record_output() as out:

                pelican_quickstart.make_template(filepath, {})

        self.assertTrue(out.getvalue().startswith('Error:'))


class TestShellEscape(unittest.TestCase):
    """ Shell escape things """

    def test_escapes_boring_strings(self):

        conf = {'foo': 'something',
                'bar': '"something"'}

        res = pelican_quickstart.escape_shell(conf)

        self.assertEqual(res, {'foo': 'something', 'bar': '"something"'})
        self.assertIsNot(res, conf)

    def test_escapes_important_strings(self):

        conf = {'foo': 'something with spaces'}

        res = pelican_quickstart.escape_shell(conf)

        self.assertEqual(res, {'foo': '"something with spaces"'})
        self.assertIsNot(res, conf)

    def test_escapes_double_quotes(self):

        conf = {'foo': 'something with "quotes"'}

        res = pelican_quickstart.escape_shell(conf)

        self.assertEqual(res, {'foo': r'"something with \"quotes\""'})
        self.assertIsNot(res, conf)
