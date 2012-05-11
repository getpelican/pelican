__all__ = [
    'temporary_folder',
    'get_article',
    'unittest',
]

import os
import subprocess
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree

from pelican.contents import Article

try:
    import unittest2 as unittest
except ImportError:
    import unittest


@contextmanager
def temporary_folder():
    """creates a temporary folder, return it and delete it afterwards.

    This allows to do something like this in tests:

        >>> with temporary_folder() as d:
            # do whatever you want
    """
    tempdir = mkdtemp()
    yield tempdir
    rmtree(tempdir)


def get_article(title, slug, content, lang, extra_metadata=None):
    metadata = {'slug': slug, 'title': title, 'lang': lang}
    if extra_metadata is not None:
        metadata.update(extra_metadata)
    return Article(content, metadata=metadata)


def skipIfNoExecutable(executable, valid_exit_code=1):
    """Tries to run an executable to make sure it's in the path, Skips the tests
    if not found.
    """

    # calling with no params the command should exit with 1
    with open(os.devnull, 'w') as fnull:
        try:
            res = subprocess.call(executable, stdout=fnull, stderr=fnull)
        except OSError:
            res = None

    if res != valid_exit_code:
        return unittest.skip('{0} compiler not found'.format(executable))

    return lambda func: func
