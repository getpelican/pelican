import logging
import warnings
from collections import defaultdict

from rich.console import Console
from rich.logging import RichHandler

__all__ = ["init"]

console = Console()


class FilteredMessage(Exception):
    """An exception to signal whether a message was filtered or not."""


class LimitFilter(logging.Filter):
    """
    Remove duplicates records, and limit the number of records in the same
    group.

    Groups are specified by the message to use when the number of records in
    the same group hit the limit.
    E.g.: log.warning(('43 is not the answer', 'More erroneous answers'))
    """

    LOGS_DEDUP_MIN_LEVEL = logging.WARNING

    _ignore = set()
    _raised_messages = set()
    _threshold = 5
    _group_count = defaultdict(int)

    def filter(self, record):
        # don't limit log messages for anything above "warning"
        if record.levelno > self.LOGS_DEDUP_MIN_LEVEL:
            return True

        # extract group
        group = record.__dict__.get("limit_msg", None)
        group_args = record.__dict__.get("limit_args", ())

        # ignore record if it was already raised
        message_key = (record.levelno, record.getMessage())
        if message_key in self._raised_messages:
            return False
        else:
            self._raised_messages.add(message_key)

        # ignore LOG_FILTER records by templates or messages
        # when "debug" isn't enabled
        logger_level = logging.getLogger().getEffectiveLevel()
        if logger_level > logging.DEBUG:
            template_key = (record.levelno, record.msg)
            message_key = (record.levelno, record.getMessage())
            if template_key in self._ignore or message_key in self._ignore:
                return False

        # check if we went over threshold
        if group:
            key = (record.levelno, group)
            self._group_count[key] += 1
            if self._group_count[key] == self._threshold:
                record.msg = group
                record.args = group_args
            elif self._group_count[key] > self._threshold:
                return False
        return True


class LimitLogger(logging.Logger):
    """
    A logger which adds LimitFilter automatically
    """

    limit_filter = LimitFilter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_filter()

    def disable_filter(self):
        self.removeFilter(LimitLogger.limit_filter)

    def enable_filter(self):
        self.addFilter(LimitLogger.limit_filter)


class FatalLogger(LimitLogger):
    fatal_lvl = logging.CRITICAL + 1  # i.e. No levels by default

    def filter(self, record):
        """A hack to let _log() know whether a message was logged or not."""
        result = super().filter(record)
        if not result:
            raise FilteredMessage()
        return result

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        try:
            super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1)
        except FilteredMessage:
            # Avoid raising RuntimeError below if no log was emitted.
            return

        # __init__.py:main() catches this exception then does it's own critical log.
        # We need to avoid throwing the exception a second time here.
        if level >= FatalLogger.fatal_lvl and level != logging.CRITICAL:
            raise RuntimeError("Warning or error encountered")


logging.setLoggerClass(FatalLogger)
# force root logger to be of our preferred class
logging.getLogger().__class__ = FatalLogger

DEFAULT_LOG_HANDLER = RichHandler(console=console)


def init(
    level=None,
    fatal="",
    handler=DEFAULT_LOG_HANDLER,
    name=None,
    logs_dedup_min_level=None,
):
    if fatal:
        FatalLogger.fatal_lvl = logging.WARNING if fatal.startswith("warning") else logging.ERROR

    LOG_FORMAT = "%(message)s"
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt="[%H:%M:%S]",
        handlers=[handler] if handler else [],
    )

    logger = logging.getLogger(name)

    if level:
        logger.setLevel(level)
    if logs_dedup_min_level:
        LimitFilter.LOGS_DEDUP_MIN_LEVEL = logs_dedup_min_level


def log_warnings():
    logging.captureWarnings(True)
    warnings.simplefilter("default", DeprecationWarning)
    init(logging.DEBUG, name="py.warnings")


if __name__ == "__main__":
    init(level=logging.DEBUG, name=__name__)

    root_logger = logging.getLogger(__name__)
    root_logger.debug("debug")
    root_logger.info("info")
    root_logger.warning("warning")
    root_logger.error("error")
    root_logger.critical("critical")
