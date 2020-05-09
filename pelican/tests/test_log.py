import logging
import unittest
from collections import defaultdict
from contextlib import contextmanager

from pelican import log
from pelican.tests.support import LogCountHandler


class TestLog(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.logger = logging.getLogger(__name__)
        self.handler = LogCountHandler()
        self.handler.setFormatter(log.get_formatter())
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self._reset_limit_filter()
        self.logger.removeHandler(self.handler)
        super().tearDown()

    def _reset_limit_filter(self):
        log.LimitFilter._ignore = set()
        log.LimitFilter._raised_messages = set()
        log.LimitFilter._threshold = 5
        log.LimitFilter._group_count = defaultdict(int)

    @contextmanager
    def reset_logger(self):
        try:
            yield None
        finally:
            self._reset_limit_filter()
            self.handler.flush()

    def test_log_formatter(self):
        counter = self.handler.count_formatted_logs
        with self.reset_logger():
            # log simple case
            self.logger.warning('Log %s', 'test')
            self.assertEqual(
                counter('Log test', logging.WARNING),
                1)

        with self.reset_logger():
            # log multiline message
            self.logger.warning('Log\n%s', 'test')
            # Log
            # | test
            self.assertEqual(
                counter('Log', logging.WARNING),
                1)
            self.assertEqual(
                counter(' | test', logging.WARNING),
                1)

        with self.reset_logger():
            # log multiline argument
            self.logger.warning('Log %s', 'test1\ntest2')
            # Log test1
            # | test2
            self.assertEqual(
                counter('Log test1', logging.WARNING),
                1)
            self.assertEqual(
                counter(' | test2', logging.WARNING),
                1)

        with self.reset_logger():
            # log single list
            self.logger.warning('Log %s', ['foo', 'bar'])
            self.assertEqual(
                counter(r"Log \['foo', 'bar'\]", logging.WARNING),
                1)

        with self.reset_logger():
            # log single dict
            self.logger.warning('Log %s', {'foo': 1, 'bar': 2})
            self.assertEqual(
                # dict order is not guaranteed
                counter(r"Log {'.*': \d, '.*': \d}", logging.WARNING),
                1)

    def test_log_filter(self):
        def do_logging():
            for i in range(5):
                self.logger.warning('Log %s', i)
                self.logger.warning('Another log %s', i)
        # no filter
        with self.reset_logger():
            do_logging()
            self.assertEqual(
                self.handler.count_logs('Log \\d', logging.WARNING),
                5)
            self.assertEqual(
                self.handler.count_logs('Another log \\d', logging.WARNING),
                5)

        # filter by template
        with self.reset_logger():
            log.LimitFilter._ignore.add((logging.WARNING, 'Log %s'))
            do_logging()
            self.assertEqual(
                self.handler.count_logs('Log \\d', logging.WARNING),
                0)
            self.assertEqual(
                self.handler.count_logs('Another log \\d', logging.WARNING),
                5)

        # filter by exact message
        with self.reset_logger():
            log.LimitFilter._ignore.add((logging.WARNING, 'Log 3'))
            do_logging()
            self.assertEqual(
                self.handler.count_logs('Log \\d', logging.WARNING),
                4)
            self.assertEqual(
                self.handler.count_logs('Another log \\d', logging.WARNING),
                5)

        # filter by both
        with self.reset_logger():
            log.LimitFilter._ignore.add((logging.WARNING, 'Log 3'))
            log.LimitFilter._ignore.add((logging.WARNING, 'Another log %s'))
            do_logging()
            self.assertEqual(
                self.handler.count_logs('Log \\d', logging.WARNING),
                4)
            self.assertEqual(
                self.handler.count_logs('Another log \\d', logging.WARNING),
                0)
