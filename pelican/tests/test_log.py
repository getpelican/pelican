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
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self._reset_limit_filter()
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
