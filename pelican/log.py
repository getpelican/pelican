# -*- encoding=utf-8 -*-
from __future__ import unicode_literals, print_function

__all__ = [
    'init'
]

import os
import sys
import logging

from logging import Formatter, getLogger, StreamHandler, DEBUG


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


class ANSIFormatter(Formatter):
    """
    Convert a `logging.LogReport' object into colored text, using ANSI escape sequences.
    """
    ## colors:

    def format(self, record):
        if record.levelname is 'INFO':
            return ansi('cyan', '-> ') + record.msg
        elif record.levelname is 'WARNING':
            return ansi('yellow', record.levelname) + ': ' + record.msg
        elif record.levelname is 'ERROR':
            return ansi('red', record.levelname) + ': ' + record.msg
        elif record.levelname is 'CRITICAL':
            return ansi('bgred', record.levelname) + ': ' + record.msg
        elif record.levelname is 'DEBUG':
            return ansi('bggrey', record.levelname) + ': ' + record.msg
        else:
            return ansi('white', record.levelname) + ': ' + record.msg


class TextFormatter(Formatter):
    """
    Convert a `logging.LogReport' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname is 'INFO':
            return record.msg
        else:
            return record.levelname + ': ' + record.msg


def init(level=None, logger=getLogger(), handler=StreamHandler()):
    logger = logging.getLogger()

    if os.isatty(sys.stdout.fileno()) \
       and not sys.platform.startswith('win'):
        fmt = ANSIFormatter()
    else:
        fmt = TextFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)


if __name__ == '__main__':
    init(level=DEBUG)

    root_logger = logging.getLogger()
    root_logger.debug('debug')
    root_logger.info('info')
    root_logger.warning('warning')
    root_logger.error('error')
    root_logger.critical('critical')
