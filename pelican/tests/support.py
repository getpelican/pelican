import locale
import logging
import os
import re
import subprocess
import sys
import unittest
from contextlib import contextmanager
from functools import wraps
from io import StringIO
from logging.handlers import BufferingHandler
from shutil import rmtree
from tempfile import mkdtemp
from typing import Optional

from pelican.contents import Article
from pelican.readers import default_metadata
from pelican.settings import DEFAULT_CONFIG

__all__ = ['get_article', 'unittest', 'LogCountHandler']


@contextmanager
def temporary_folder():
    """creates a temporary folder, return it and delete it afterwards.

    This allows to do something like this in tests:

        >>> with temporary_folder() as d:
        ...     pass  # do whatever you want
    """
    tempdir = mkdtemp()
    try:
        yield tempdir
    finally:
        rmtree(tempdir)


def isplit(s, sep=None):
    """Behaves like str.split but returns a generator instead of a list.

    >>> list(isplit('\tUse the force\n')) == '\tUse the force\n'.split()
    True
    >>> list(isplit('\tUse the force\n')) == ['Use', 'the', 'force']
    True
    >>> (list(isplit('\tUse the force\n', "e"))
         == '\tUse the force\n'.split("e"))
    True
    >>> list(isplit('Use the force', "e")) == 'Use the force'.split("e")
    True
    >>> list(isplit('Use the force', "e")) == ['Us', ' th', ' forc', '']
    True

    """
    sep, hardsep = r'\s+' if sep is None else re.escape(sep), sep is not None
    exp, pos, length = re.compile(sep), 0, len(s)
    while True:
        m = exp.search(s, pos)
        if not m:
            if pos < length or hardsep:
                #      ^ mimic "split()": ''.split() returns []
                yield s[pos:]
            break
        start = m.start()
        if pos < start or hardsep:
            #           ^ mimic "split()": includes trailing empty string
            yield s[pos:start]
        pos = m.end()


def mute(returns_output=False):
    """Decorate a function that prints to stdout, intercepting the output.
    If "returns_output" is True, the function will return a generator
    yielding the printed lines instead of the return values.

    The decorator literally hijack sys.stdout during each function
    execution, so be careful with what you apply it to.

    >>> def numbers():
    ...        print("42")
    ...        print("1984")
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
            sys.stdout = StringIO()

            try:
                out = func(*args, **kwargs)
                if returns_output:
                    out = isplit(sys.stdout.getvalue().strip())
            finally:
                sys.stdout = saved_stdout

            return out

        return wrapper

    return decorator


def get_article(title, content, **extra_metadata):
    metadata = default_metadata(settings=DEFAULT_CONFIG)
    metadata['title'] = title
    if extra_metadata:
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
        return unittest.skip('{} executable not found'.format(executable))

    return lambda func: func


def module_exists(module_name):
    """Test if a module is importable."""

    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def locale_available(locale_):
    old_locale = locale.setlocale(locale.LC_TIME)

    try:
        locale.setlocale(locale.LC_TIME, str(locale_))
    except locale.Error:
        return False
    else:
        locale.setlocale(locale.LC_TIME, old_locale)
        return True


def can_symlink():
    res = True
    try:
        with temporary_folder() as f:
            os.symlink(
                f,
                os.path.join(f, 'symlink')
            )
    except OSError:
        res = False
    return res


def get_settings(**kwargs):
    """Provide tweaked setting dictionaries for testing

    Set keyword arguments to override specific settings.
    """
    settings = DEFAULT_CONFIG.copy()
    for key, value in kwargs.items():
        settings[key] = value
    return settings


def get_context(settings=None, **kwargs):
    context = settings.copy() if settings else {}
    context['generated_content'] = {}
    context['static_links'] = set()
    context['static_content'] = {}
    context.update(kwargs)
    return context


def diff_subproc(first, second):
    """
    Return a subprocess that runs a diff on the two paths.

    Check results with::
        >>> proc = diff_subproc("first.txt","second.txt")
        >>> out_stream, err_stream = proc.communicate()
        >>> didCheckFail = proc.returnCode != 0
    """
    return subprocess.Popen(
        ['git', '--no-pager', 'diff', '--no-ext-diff', '--exit-code',
         '-w', first, second],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class LogCountHandler(BufferingHandler):
    """Capturing and counting logged messages."""

    def __init__(self, capacity=1000):
        super().__init__(capacity)

    @classmethod
    @contextmanager
    def examine(cls, loggerObj):
        """
        Context in which a logger's propagated messages can be examined.

        Yields
        ======
        A handle to ``LogCountHandler.assert_count`` that has been added to the
        specified logger for the duration of the context.

        The yielded caller can be used to assert whether a certain number of
        log messages have occurred within the context.
        """
        hnd = cls()
        try:
            loggerObj.addHandler(hnd)
            yield hnd.assert_count
        finally:
            loggerObj.removeHandler(hnd)

    def assert_count(
        self,
        count: int,
        msg: Optional[str] = None,
        level: Optional[int] = None,
        as_regex: bool = False
    ):
        """
        Assert how often the specified messages have been handled.

        Raises
        -------
        AssertionError
        """
        occurances = self.count_logs(msg, level, as_regex)
        if count != occurances:
            report = 'Logged occurrence'
            if msg is not None:
                report += ' of {!r}'.format(msg)

            if level is not None:
                raise AssertionError(
                    ' at {}'.format(logging.getLevelName(level))
                )
            raise AssertionError(
                report + ': expected/found {}/{}'.format(count, occurances)
            )

    def match_record(
        self,
        pattern: re.Pattern,
        record: logging.LogRecord,
        level: Optional[int]
    ) -> Optional[re.Match]:
        """
        Return regex object if pattern found in message at specified severity.
        """
        if level is not None and level != record.levelno:
            return None

        # prefix pattern with "^" for re.match behavior
        return pattern.search(record.getMessage())

    def count_logs(
        self,
        msg: Optional[str],
        level: Optional[int],
        as_regex: bool = False
    ) -> int:
        """
        Returns the number of times a message has been logged.
        """
        if not msg:
            if not level:
                matched = self.buffer  # all logged messages
            else:
                # all logged messages of matching severity level
                matched = [rec for rec in self.buffer if rec.levelno == level]
        else:
            # all logged messages matching the regex and level
            if not as_regex:
                msg = re.escape(msg)

            pattern = re.compile(msg)
            matched = [
                record for record in self.buffer
                if self.match_record(pattern, record, level)
            ]

        return len(matched)


class TestCaseWithCLocale(unittest.TestCase):
    """Set locale to C for each test case, then restore afterward.

    Use utils.temporary_locale if you want a context manager ("with" statement).
    """
    def setUp(self):
        self.old_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.old_locale)
