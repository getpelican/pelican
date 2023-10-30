import logging
import unittest
from contextlib import contextmanager

from pelican import log
from pelican.tests.support import LogCountHandler


LOG_LVLS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL
]
# Set this module's logging level to DEBUG to prevent
# tests' loggers effectiveLevels from reaching **root logger**,
# which we *don't* want to play with here.
logging.getLogger(__name__).setLevel(logging.DEBUG)


class _LoggingTestCase(unittest.TestCase):
    """Test Case w/ test-specific loggers, and contexts for temp filters."""

    def setUp(self):
        "Each test should use a unique logger and handle all levels."
        self.logger = logging.getLogger(self.id())
        self.logger.setLevel(logging.NOTSET)  # log all levels

    @contextmanager
    def temp_filter(self, flt):
        """
        Context in which a filter is temporarily applied to test's logger.
        """
        with log.temp_filter(self.logger, flt):
            yield flt


class TestLogLevel(unittest.TestCase):

    def test_severity_name(self):
        self.assertEqual(log.severity_from_name('errors'), logging.ERROR)
        self.assertEqual(log.severity_from_name('error'), logging.ERROR)
        self.assertEqual(log.severity_from_name('WARNINGS'), logging.WARNING)
        self.assertEqual(log.severity_from_name('info'), logging.INFO)
        self.assertEqual(log.severity_from_name('INFO'), logging.INFO)
        self.assertEqual(log.severity_from_name(''), logging.NOTSET)
        self.assertEqual(log.severity_from_name('error'), logging.ERROR)

        # add a custom level:
        logging.addLevelName(5, "TRACE")
        self.assertEqual(log.severity_from_name('trace'), 5)

        with self.assertRaises(KeyError):
            self.assertEqual(log.severity_from_name("wrong"), logging.NOTSET)


class TestFatal(_LoggingTestCase):

    def test_levels(self):
        logger = self.logger
        with log.temp_handler(self.logger, log.AbortHandler(logging.ERROR)):
            logger.debug("Calculating airspeed velocity of an unladen swallow...")
            logger.info("Tis but a scratch.")
            logger.warning("And now for something completely different.")
            with self.assertRaises(log.AbortException):
                logger.error("This is a late parrot!")
            with self.assertRaises(log.AbortException):
                logger.critical("Unexpected: Spanish Inquisition.")


class TestLogInit(_LoggingTestCase):

    def test_alt_logger(self):
        self.assertEqual(log.set_filters(self.logger), self.logger)

    def test_default(self):
        null_settings = dict(
            LOG_LIMIT_THRESHOLD=None,
            LOG_ONCE_LEVEL=None,
        )
        # assert returned logger is "pelican".
        pkg_logger = logging.getLogger('pelican')
        self.assertEqual(pkg_logger.filters, [])
        self.assertEqual(pkg_logger, log.configure(null_settings))
        # because no filtering settings supplied,
        # no filters should have been added:
        self.assertEqual(pkg_logger.filters, [])

        # assert no pre-existing filters on test's logger:
        self.assertEqual(log.LimitFilter.get_filters(self.logger), [])

        logger = log.configure(dict(LOG_LOGGER=self.logger.name))

        # assert returned logger has been set up with a LimitFilter
        self.assertNotEqual(log.LimitFilter.get_filters(self.logger), [])

        with LogCountHandler.examine(logger) as count_msgs:
            msg = 'init with alt logger: %s' % logger
            for level in LOG_LVLS:
                logger.log(level, msg)
                logger.log(level, msg)  # suppressed for WARNINGS and worse
            count_msgs(
                sum([1 if lvl >= logging.WARNING  # dedupe warnings & above
                     else 2  # lvls below should not be deduped
                     for lvl in LOG_LVLS]),
                msg
            )

    def test_dedupe_all(self):
        logger = log.set_filters(self.logger, once_lvl=logging.NOTSET)  # dedup all
        with LogCountHandler.examine(logger) as count_msgs:
            msg = 'init with alt logger: %s' % logger
            for level in LOG_LVLS:
                logger.log(level, msg)
                logger.log(level, msg)  # poss. suppressed
            count_msgs(len(LOG_LVLS), msg)

    def test_dedupe_none(self):
        logger = log.set_filters(self.logger, once_lvl=None)
        with LogCountHandler.examine(logger) as count_msgs:
            msg = 'init with alt logger: %s' % logger
            for level in LOG_LVLS:
                logger.log(level, msg)
                logger.log(level, msg)  # do not suppress
            count_msgs(len(LOG_LVLS * 2), msg)


class classTestOnceFilter(_LoggingTestCase):

    def test_levels(self):
        """
        Don't de-duplicate messages for levels below filter's value.
        """
        logger = self.logger
        msg = "levels_test"
        with LogCountHandler.examine(logger) as count_msgs:
            with self.temp_filter(log.OnceFilter()):  # default=NOTSET: dedup all
                for level in LOG_LVLS:
                    logger.log(level, msg)
                    logger.log(level, msg)  # copy should be suppressed
                count_msgs(len(LOG_LVLS), msg)

        with LogCountHandler.examine(logger) as count_msgs:
            with self.temp_filter(log.OnceFilter(logging.WARNING)):
                for level in LOG_LVLS:
                    logger.log(level, msg)
                    logger.log(level, msg)  # copy should be suppressed
                count_msgs(
                    sum([1 if lvl >= logging.WARNING  # dedupe warnings & above
                         else 2  # lvls below should not be deduped
                         for lvl in LOG_LVLS]),
                    msg
                )

    def test_deduplication(self):
        """Confirm that duplicate messages are ignored."""
        logger = self.logger

        # ensure counting is correct before adding filters
        msg = "without filter"
        with LogCountHandler.examine(logger) as count_msgs:
            for level in LOG_LVLS:
                logger.log(level, msg)
            # count w/ level requirements
            count_msgs(1, msg, level=logging.DEBUG)
            count_msgs(1, msg, level=logging.INFO)
            # count w/ no level requirqement
            count_msgs(len(LOG_LVLS), msg)

        # add filter, check count
        with self.temp_filter(log.OnceFilter()):
            msg = "with filter"
            with LogCountHandler.examine(logger) as count_msgs:
                for level in LOG_LVLS:
                    logger.log(level, msg)
                    logger.log(level, msg)
                    logger.log(level, msg)

                # counting w/ level requirements
                for level in LOG_LVLS:
                    count_msgs(1, msg, level=level)

                # counting w/ no level requirement
                count_msgs(len(LOG_LVLS), msg)

        # check counting again after filter removed
        msg = "removed filter"
        with LogCountHandler.examine(logger) as count_msgs:
            for level in LOG_LVLS:
                logger.log(level, msg)
            count_msgs(5, msg)


class TestLimitFilter(_LoggingTestCase):

    def setUp(self):
        super().setUp()
        self.logger.setLevel(logging.DEBUG)

    def test_get_filters(self):
        """Assert LimitFilters on a logger are collected."""
        fltrs = [log.LimitFilter() for x in range(5)]

        assert not self.logger.filters

        for each in fltrs:
            self.logger.addFilter(each)

        self.assertEqual(fltrs, log.LimitFilter.get_filters(self.logger))

        for each in fltrs:
            self.logger.removeFilter(each)

        assert not self.logger.filters

    def test_threshold(self):
        """
        Assert that the `limit_msg` activates after the threshold is reached.
        """
        threshold = 4
        with self.temp_filter(log.LimitFilter(threshold)):
            msg = "Threshold: %s"
            limits = {'limit_msg': "Threshold exceeded"}
            with LogCountHandler.examine(self.logger) as count_msgs:
                for i in range(1, threshold + 3):
                    self.logger.warning(msg, i, extra=limits)
                # up to threshold
                count_msgs(threshold - 1, "Threshold: [1-9+]", as_regex=True)
                # exactly one "limit_msg"
                count_msgs(1, limits['limit_msg'])
                # total count should be == threshold, all in all.
                count_msgs(threshold)

    def test_limit_args(self):
        """
        `limit_args` should be used in the `limit_msg`.
        """
        threshold = 3
        with self.temp_filter(log.LimitFilter(threshold)):
            limits = {'limit_msg': "Threshold exceeded @ %s %s",
                      'limit_args': ('count of', threshold)}
            with LogCountHandler.examine(self.logger) as count_msgs:
                for i in range(threshold + 1):
                    self.logger.warning("Threshold: %s", i, extra=limits)
                count_msgs(1, limits['limit_msg'] % limits['limit_args'])

    def test_ignore(self):
        """Confirm blacklisted messages (eg. from config) are not emitted."""
        blacklist = [
            "SPAM SPAM SPAM",
            "I'll have your spam. I love it."
        ]

        with self.temp_filter(log.BlacklistFilter()) as flt:
            for template in blacklist:
                flt.ignore(logging.WARNING, template)

            with LogCountHandler.examine(self.logger) as count_msgs:
                count_msgs(0)
                self.logger.warning(blacklist[0])  # ignored
                self.logger.warning(blacklist[0])  # ignored
                self.logger.warning("I don't like spam!")  # 1
                self.logger.warning("Sshh, dear, don't cause a fuss.")  # 2
                self.logger.warning(blacklist[1])  # ignored
                self.logger.info(blacklist[1])  # 3 : diff. level (below)
                self.logger.error(blacklist[1])  # 4 : diff. level (above)
                count_msgs(4)
