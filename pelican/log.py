# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

__all__ = [
    'init'
]

import os
import sys
import logging

from collections import defaultdict


RESET_TERM = '\033[0;m'

COLOR_CODES = {
    'red': 31,
    'yellow': 33,
    'cyan': 36,
    'white': 37,
    'bgred': 41,
    'bggrey': 100,
}


def ansi(color, text):
    """Wrap text in an ansi escape sequence"""
    code = COLOR_CODES[color]
    return '\033[1;{0}m{1}{2}'.format(code, text, RESET_TERM)


class ANSIFormatter(logging.Formatter):
    """Convert a `logging.LogRecord' object into colored text, using ANSI
       escape sequences.

    """
    def format(self, record):
        msg = record.getMessage()
        if record.levelname == 'INFO':
            return ansi('cyan', '-> ') + msg
        elif record.levelname == 'WARNING':
            return ansi('yellow', record.levelname) + ': ' + msg
        elif record.levelname == 'ERROR':
            return ansi('red', record.levelname) + ': ' + msg
        elif record.levelname == 'CRITICAL':
            return ansi('bgred', record.levelname) + ': ' + msg
        elif record.levelname == 'DEBUG':
            return ansi('bggrey', record.levelname) + ': ' + msg
        else:
            return ansi('white', record.levelname) + ': ' + msg


class TextFormatter(logging.Formatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname == 'INFO':
            return record.getMessage()
        else:
            return record.levelname + ': ' + record.getMessage()


class LimitFilter(logging.Filter):
    """
    Remove duplicates records, and limit the number of records in the same
    group.

    Groups are specified by the message to use when the number of records in
    the same group hit the limit.
    E.g.: log.warning(('43 is not the answer', 'More erroneous answers'))
    """

    ignore = set()
    threshold = 5
    group_count = defaultdict(int)

    def filter(self, record):
        # don't limit log messages for anything above "warning"
        if record.levelno > logging.WARN:
            return record
        # extract group
        group = None
        if len(record.msg) == 2:
            record.msg, group = record.msg
        # ignore record if it was already raised
        # use .getMessage() and not .msg for string formatting
        ignore_key = (record.levelno, record.getMessage())
        to_ignore = ignore_key in LimitFilter.ignore
        LimitFilter.ignore.add(ignore_key)
        if to_ignore:
            return False
        # check if we went over threshold
        if group:
            key = (record.levelno, group)
            LimitFilter.group_count[key] += 1
            if LimitFilter.group_count[key] == LimitFilter.threshold:
                record.msg = group
            if LimitFilter.group_count[key] > LimitFilter.threshold:
                return False
        return record


class LimitLogger(logging.Logger):
    """
    A logger which adds LimitFilter automatically
    """

    limit_filter = LimitFilter()

    def __init__(self, *args, **kwargs):
        super(LimitLogger, self).__init__(*args, **kwargs)
        self.addFilter(LimitLogger.limit_filter)

logging.setLoggerClass(LimitLogger)


def init(level=None, handler=logging.StreamHandler()):

    logger = logging.getLogger()

    if (os.isatty(sys.stdout.fileno())
            and not sys.platform.startswith('win')):
        fmt = ANSIFormatter()
    else:
        fmt = TextFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)


if __name__ == '__main__':
    init(level=logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.debug('debug')
    root_logger.info('info')
    root_logger.warning('warning')
    root_logger.error('error')
    root_logger.critical('critical')
