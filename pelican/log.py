__all__ = [
    'init'
]

import os
import sys
import logging

from logging import Formatter, getLogger, StreamHandler, DEBUG


RESET_TERM = u'\033[0;m'


def start_color(index):
    return u'\033[1;{0}m'.format(index)


def term_color(color):
    code = COLOR_CODES[color]
    return lambda text: start_color(code) + unicode(text) + RESET_TERM


COLOR_CODES = {
    'red': 31,
    'yellow': 33,
    'cyan': 36,
    'white': 37,
    'bgred': 41,
    'bggrey': 100,
}

ANSI = dict((col, term_color(col)) for col in COLOR_CODES)


class ANSIFormatter(Formatter):
    """
    Convert a `logging.LogReport' object into colored text, using ANSI escape sequences.
    """
    ## colors:

    def format(self, record):
        if record.levelname is 'INFO':
            return ANSI['cyan']('-> ') + unicode(record.msg)
        elif record.levelname is 'WARNING':
            return ANSI['yellow'](record.levelname) + ': ' + unicode(record.msg)
        elif record.levelname is 'ERROR':
            return ANSI['red'](record.levelname) + ': ' + unicode(record.msg)
        elif record.levelname is 'CRITICAL':
            return ANSI['bgred'](record.levelname) + ': ' + unicode(record.msg)
        elif record.levelname is 'DEBUG':
            return ANSI['bggrey'](record.levelname) + ': ' + unicode(record.msg)
        else:
            return ANSI['white'](record.levelname) + ': ' + unicode(record.msg)


class TextFormatter(Formatter):
    """
    Convert a `logging.LogReport' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname is 'INFO':
            return record.msg
        else:
            return record.levelname + ': ' + record.msg


class DummyFormatter(object):
    """
    A dummy class.
    Return an instance of the appropriate formatter (ANSIFormatter if
    sys.stdout.isatty() is True, else TextFormatter)
    """

    def __new__(cls, *args, **kwargs):
        if os.isatty(sys.stdout.fileno())\
           and not sys.platform.startswith('win'):
            return ANSIFormatter(*args, **kwargs)
        else:
            return TextFormatter(*args, **kwargs)


def init(level=None, logger=getLogger(), handler=StreamHandler()):
    logger = logging.getLogger()
    fmt = DummyFormatter()
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
