import logging
from collections import defaultdict
from contextlib import contextmanager

from rich.console import Console
from rich.logging import RichHandler


console = Console()

# handles messages logged from anywhere within the pelican namespace.
PKG_LOGGER = logging.getLogger('pelican')


def severity_from_name(string_val):
    """Convert string value to appropriate severity (AKA log level)."""
    if not string_val:
        return logging.NOTSET
    level_name = string_val.upper().rstrip('S')
    try:
        return logging.getLevelNamesMapping()[level_name]
    except AttributeError:  # Python < 3.11
        return logging._nameToLevel.copy()[level_name]


@contextmanager
def temp_filter(logger, flt):
    """
    Context in which a custom filter is temporarily applied to logger.
    """
    try:
        logger.addFilter(flt)
        yield flt
    finally:
        logger.removeFilter(flt)


@contextmanager
def temp_handler(logger, hnd):
    """
    Context in which a custom handler is temporarily applied to logger.
    """
    try:
        logger.addHandler(hnd)
        yield hnd
    finally:
        logger.removeHandler(hnd)


class AbortException(Exception):
    def __init__(self, *args, record=None):
        self.record = record
        super().__init__(*args)


class AbortHandler(logging.Handler):
    """
    Set severity level to trigger an AbortException (eg. to exit application).

    Example::

        # add a handler to raise an exception on logs of warning level or higher
        root = logging.getLogger()
        root.addHandler(AbortHandler(logging.WARNING))
        root.info("Safe")
        try:
            root.warning("Critical!")
        except AbortHandler.EXCEPTION_CLS as e:
            print(e)
            print('exiting...')
            raise
    """
    EXCEPTION_CLS = AbortException
    _HANDLER_DEPTH = 3

    @classmethod
    def trim_traceback(cls, e):
        # only trim if exception came from this handler...
        if isinstance(e, cls.EXCEPTION_CLS):
            # find bottom of tb ...
            next_tb = e.__traceback__.tb_next
            record = e.record
            while next_tb:
                # Seek traceback for logging call that triggered the handler
                if (
                    next_tb.tb_frame.f_code.co_filename == record.pathname
                    and
                    next_tb.tb_lineno == record.lineno
                ):
                    next_tb.tb_next = None  # remaining traceback is irrelevant
                    break
                else:
                    next_tb = next_tb.tb_next

    def emit(self, record):
        # Fail on set severity level (or higher)
        if (record.levelno >= self.level):
            exc = AbortException(
                'Aborting on log severity of {lvl!r} or greater.'.format(
                    lvl=logging.getLevelName(self.level)
                ),
                record=record
            )
            raise exc


class LimitFilter(logging.Filter):
    """
    Modify logs using a generic message (`limit_msg`) after reaching threshold.

    Messages logged with the `limit_msg` keyword in `extra` are tracked as a
    group; once the group has reached the threshold, the record is modified to
    use the limit_msg instead.  All subsequent log messages in the group are
    ignored.

    EG.::

        inputs = list(range(43, 55))
        for i in inputs:
            logger.warning(
                '%s is not the answer', i,
                extra={
                    'limit_msg': 'Many erroneous answers: %s',
                    'limit_args': inputs
                }
            )
    """

    @classmethod
    def get_filters(cls, logger):
        """Return a list of LimitFilters currently on logger."""
        found = []
        for x in logger.filters:
            if isinstance(x, cls):
                found.append(x)
        return found

    def __init__(self, threshold=5):
        """
        :int threshold:
            For messages logged with the `limit_msg` in extra, the limit_msg
            will be used after the threshold is met.

            Example::

                if resource.is_missing:
                    logger.warning(
                        'The resource %s is missing', resource.name,
                        extra={'limit_msg': 'Other resources were missing'}
                    )

                # if threshold=5, logs:
                # WARNING: The resource prettiest_cat.jpg is missing
                # WARNING: The resource best_cat_ever.jpg is missing
                # WARNING: The resource cutest_cat.jpg is missing
                # WARNING: The resource lolcat.jpg is missing
                # WARNING: Other resources were missing

        """
        super().__init__()
        self.limit_threshold = None
        if threshold is not None:
            # react at, not after, threshold
            self.limit_threshold = threshold - 1
        self.group_count = defaultdict(int)

    def filter(self, record):
        # ``limit_msg`` handling
        limit_template = record.__dict__.get('limit_msg', None)
        if limit_template:
            key = (record.levelno, limit_template)
            counter = self.group_count[key]
            if counter > self.limit_threshold:
                return False  # reject: threshold exceeded
            elif counter == self.limit_threshold:
                # change message to the "limit_msg"
                record.msg = limit_template
                record.args = record.__dict__.get('limit_args', ())

            self.group_count[key] += 1

        return True  # accept


class OnceFilter(logging.Filter):
    """
    Allow only the first occurance of matching log messages.

    Similar to the "once" behavior in the ``warnings`` module.

    Parameters
    ----------
    level: int
        Only enable log de-duplication for levels equal to or above this
        value.
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__()
        self.level = level
        self._ignored = set()

    def ignore(self, level, message):
        self._ignored.add((level, message))

    def filter(self, record):
        if record.levelno < self.level:
            # Do not dedeuplicate messages of lower severity
            return True

        # ignore duplicates of resolved/formatted messages:
        message_key = (record.levelno, record.getMessage())  # resolved msg
        ignored = self._ignored

        if message_key in ignored:
            return False  # skip messages already encountered
        else:
            ignored.add(message_key)  # continue, but mark to ignore next time

        return True


class BlacklistFilter(logging.Filter):
    """Use to prevent messages of specific level & content from emitting."""

    def __init__(self, item_pairs=()):
        super().__init__()
        self._ignored = set()
        for lvl, msg in item_pairs:
            self.ignore(lvl, msg)

    @classmethod
    def get_filters(cls, logger):
        """Return a list of BlacklistFilters currently on logger."""
        found = []
        for x in logger.filters:
            if isinstance(x, cls):
                found.append(x)
        return found

    def ignore(self, level, message):
        self._ignored.add((level, message))

    def filter(self, record):
        if not self._ignored:
            return True
        if (
            ((record.levelno, record.msg) in self._ignored)
            or
            ((record.levelno, record.getMessage()) in self._ignored)
        ):
            return False  # do not emit msg
        return True


def init(
    level=None,  # init root log level
    handlers=None,  # root log handler
):
    """
    Wrapper for logging.basicConfig, but with a rich.console default handler.

    If the root logger has *not already been configured* (eg. has no handlers),
    then the specified handler (default:rich.ConsoleHandler) will be added, and
    the logging level will be set (Python defaults to WARNING level).
    """
    if handlers is None:  # default handler:
        handlers = [RichHandler(console=console)]
    logging.basicConfig(
        level=level,
        format="%(message)s",  # default format
        datefmt="[%H:%M:%S]",  # default date format
        handlers=handlers
    )


def configure(settings):
    """
    Apply logging settings, and return the configured logger.

    Applicable settings
    --------------------

    LOG_LOGGER:
        Default: ``"pelican"`` (PKG_LOGGER.name).

        The name of the logger to apply filtering to.

    LOG_LIMIT_THRESHOLD:
        Default: ``5``.

        The nth occurance at which a log message will be substituted with its
        ``limit_msg`` value.

    LOG_ONCE_LEVEL:
        Default: ``logging.WARNING``

        The lowest severity at which log messages will be deduplicated.

    LOG_FILTER:
        An iterable of (severity, msg) tuples which will be silenced by the
        logger.

    LOG_FATAL:
        The minimum severity at which logs should raise an ``AbortException``.

        NOTE: this appends a (filtered) handler to the root logger; this
        handler will *only* act on messages the LOG_LOGGER would propogate --
        effectively still targeting *only* logs from the specified logger (and
        its sub-loggers), despite being at the root level.  This allows all
        handlers to complete *before* triggering the ``AbortException``.

    """
    cfg = dict(  # config values that have defaults:
        LOG_LOGGER=PKG_LOGGER.name,
        LOG_LIMIT_THRESHOLD=5,
        LOG_ONCE_LEVEL="WARNING"
    )
    cfg.update(settings.copy())

    # validate & transform types/values: treat ``None`` as logging.NOTSET
    if not isinstance(cfg.get('LOG_ONCE_LEVEL') or logging.NOTSET, int):
        cfg['LOG_ONCE_LEVEL'] = severity_from_name(cfg['LOG_ONCE_LEVEL'])

    if not isinstance(cfg.get('LOG_LOGGER'), logging.Logger):
        cfg['LOG_LOGGER'] = logging.getLogger(cfg.get('LOG_LOGGER'))

    # == FILTERING:
    logger = set_filters(
        logger=cfg.get('LOG_LOGGER'),
        limit_threshold=cfg.get('LOG_LIMIT_THRESHOLD'),
        once_lvl=cfg.get('LOG_ONCE_LEVEL'),
        blacklist=cfg.get('LOG_FILTER')
    )

    # == HANDLING:
    if cfg.get('LOG_FATAL'):
        hnd = AbortHandler(cfg['LOG_FATAL'])

        # Add to root logger so all other handlers can write/emit first.
        root = logging.getLogger()
        if logger is not root:
            # handler only acts on records from specified logger (& children).
            hnd.addFilter(logging.Filter(logger.name))
        root.addHandler(hnd)

    return logger


def set_filters(
    logger=None,  # logger of interest
    limit_threshold=None,  # LimitFilter: when to start using limit_msg
    once_lvl=None,  # OnceFilter: which severity to dedupe msgs at
    blacklist=None  # BlacklistFilter:
):
    """
    Apply filtering on the logger (Default: ``PKG_LOGGER``).

    Up to three filters are (optionally) applied:
        ``LimitFilter``:
            Modifies log records using `limit_msg` in the `extras` dict. The
            `limit_threshold` specifies how many records using the same
            limit_msg are emitted before converting the message.  See
            ``LimitFilter`` for an example.
        ``OnceFilter``:
            De-duplicates messages of identical severity & content. Only
            affects messages of once_lvl and higher.
        ``BlacklistFilter``:
            Prevents log records of (severity, msg) from being emitted.

    Returns
    -------
    The logger object the filters were applied to.
    """
    if logger is None:
        logger = PKG_LOGGER

    if blacklist:
        try:
            flt = BlacklistFilter.get_filters(logger)[0]
        except IndexError:
            flt = BlacklistFilter()
            logger.addFilter(flt)

        for lvl, msg in blacklist:
            flt.ignore(lvl, msg)

    if once_lvl is not None:
        # deduplicate this severity and above:
        logger.addFilter(OnceFilter(once_lvl))

    if limit_threshold is not None:
        try:
            flt = LimitFilter.get_filters(logger)[0].threshold = limit_threshold
        except IndexError:
            logger.addFilter(LimitFilter(limit_threshold))

    logger.debug("{!r} : log filtering configured.".format(logger))
    return logger


if __name__ == "__main__":
    init(level=logging.INFO)
    segue = "And now for something completely different: %s"
    ignored_records = [
        (logging.WARNING, "I'd like to have an argument, please."),
        (logging.INFO, segue)
    ]
    configure(
        dict(
            LOG_FATAL=logging.ERROR,
            LOG_FILTER=ignored_records
        )
    )
    logger = PKG_LOGGER
    logger.info("hey")
    logger.info("hey")  # INFO < WARNING, not deduplicated
    logger.log(*ignored_records[0])  # blacklisted
    logger.log(*ignored_records[1])  # blacklisted
    logger.info(segue, "a man with 3 buttocks.")  # blacklisted
    logger.warning("oof")
    logger.warning("oof")  # deduplicated
    logger.warning("oof")  # deduplicated

    # on 5th occurance, limit_msg is used.
    for i in range(1, 11):
        logger.warning("watch out x%s!", i,
                       extra={"limit_msg": "[more watches were outed]"})

    # on 5th occurance, limit_msg is used, formatting msg w/ limit_args
    inputs = list(range(43, 55))
    for i in inputs:
        logger.warning(
            '%s is not the answer', i,
            extra={
                'limit_msg': 'Many erroneous answers: %s',
                'limit_args': inputs
            }
        )

    # logger not from pkg, will not trip the AbortHandler
    logging.getLogger("notpelican").error("that's not good...")

    # logger from pkg: *will* trip the AbortHandler
    logging.getLogger("pelican.log.example").error("x_x")
    logger.critical("This line should not run.")
