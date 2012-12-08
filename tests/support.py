__all__ = [
    'get_article',
    'unittest',
]

import cStringIO
import os
import re
import subprocess
import sys
import logging
from logging.handlers import BufferingHandler

from functools import wraps
from contextlib import contextmanager
from tempfile import mkdtemp
from shutil import rmtree

from pelican.contents import Article
from pelican.settings import _DEFAULT_CONFIG

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
    try:
        yield tempdir
    finally:
        rmtree(tempdir)


def isplit(s, sep=None):
    """
        Behave like str.split but returns a generator instead of a list.

        >>> list(isplit('\tUse the force\n')) == '\tUse the force\n'.split()
        True
        >>> list(isplit('\tUse the force\n')) == ['Use', 'the', 'force']
        True
        >>> list(isplit('\tUse the force\n', "e")) == '\tUse the force\n'.split("e")
        True
        >>> list(isplit('Use the force', "e")) == 'Use the force'.split("e")
        True
        >>> list(isplit('Use the force', "e")) == ['Us', ' th', ' forc', '']
        True

    """
    sep, hardsep = r'\s+' if sep is None else re.escape(sep), sep is not None
    exp, pos, l = re.compile(sep), 0, len(s)
    while True:
        m = exp.search(s, pos)
        if not m:
            if pos < l or hardsep:
                #      ^ mimic "split()": ''.split() returns []
                yield s[pos:]
            break
        start = m.start()
        if pos < start or hardsep:
            #           ^ mimic "split()": includes trailing empty string
            yield s[pos:start]
        pos = m.end()


def mute(returns_output=False):
    """
        Decorate a function that prints to stdout, intercepting the output.
        If "returns_output" is True, the function will return a generator
        yielding the printed lines instead of the return values.

        The decorator litterally hijack sys.stdout during each function
        execution, so be careful with what you apply it to.

        >>> def numbers():
            print "42"
            print "1984"
        ...
        >>> numbers()
        42
        1984
        >>> mute()(numbers)()
        >>> list(mute(True)(numbers)())
        ['42', '1984']

    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            saved_stdout = sys.stdout
            sys.stdout = cStringIO.StringIO()

            try:
                out = func(*args, **kwargs)
                if returns_output:
                    out = isplit(sys.stdout.getvalue().strip())
            finally:
                sys.stdout = saved_stdout

            return out

        return wrapper

    return decorator


def get_article(title, slug, content, lang, extra_metadata=None):
    metadata = {'slug': slug, 'title': title, 'lang': lang}
    if extra_metadata is not None:
        metadata.update(extra_metadata)
    return Article(content, metadata=metadata)


def skipIfNoExecutable(executable):
    """Skip test if `executable` is not found

    Tries to run `executable` with subprocess to make sure it's in the path,
    and skips the tests if not found (if subprocess raises a `OSError`).
    """

    with open(os.devnull, 'w') as fnull:
        try:
            res = subprocess.call(executable, stdout=fnull, stderr=fnull)
        except OSError:
            res = None

    if res is None:
        return unittest.skip('{0} executable not found'.format(executable))

    return lambda func: func


def module_exists(module_name):
    """Test if a module is importable."""

    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def get_settings():
    settings = _DEFAULT_CONFIG.copy()
    settings['DIRECT_TEMPLATES'] = ['archives']
    settings['filenames'] = {}
    return settings


class LogCountHandler(BufferingHandler):
    """
    Capturing and counting logged messages.
    """

    def __init__(self, capacity=1000):
        logging.handlers.BufferingHandler.__init__(self, capacity)

    def count_logs(self, msg=None, level=None):
        return len([l for l in self.buffer
            if (msg is None or re.match(msg, l.getMessage()))
            and (level is None or l.levelno == level)
            ])
