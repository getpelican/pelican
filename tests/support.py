from contextlib import contextmanager

from tempfile import mkdtemp
from shutil import rmtree


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
