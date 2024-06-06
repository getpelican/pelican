import logging
from collections import defaultdict

from rich.console import Console
from rich.logging import RichHandler

__all__ = ["init"]

console = Console()


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
    warnings_fatal = False
    errors_fatal = False

    def warning(self, *args, stacklevel=1, **kwargs):
        """
        Displays a logging warning.

        Wrapping it here allows Pelican to filter warnings, and conditionally
        make warnings fatal.

        Args:
            stacklevel (int): the stacklevel that would be used to display the
            calling location, except for this function. Adjusting the
            stacklevel allows you to see the "true" calling location of the
            warning, rather than this wrapper location.
        """
        stacklevel += 1
        super().warning(*args, stacklevel=stacklevel, **kwargs)
        if FatalLogger.warnings_fatal:
            raise RuntimeError("Warning encountered")

    def error(self, *args, stacklevel=1, **kwargs):
        """
        Displays a logging error.

        Wrapping it here allows Pelican to filter errors, and conditionally
        make errors non-fatal.

        Args:
            stacklevel (int): the stacklevel that would be used to display the
            calling location, except for this function. Adjusting the
            stacklevel allows you to see the "true" calling location of the
            error, rather than this wrapper location.
        """
        stacklevel += 1
        super().error(*args, stacklevel=stacklevel, **kwargs)
        if FatalLogger.errors_fatal:
            raise RuntimeError("Error encountered")


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
    FatalLogger.warnings_fatal = fatal.startswith("warning")
    FatalLogger.errors_fatal = bool(fatal)

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
    import warnings

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
