import os
import sys
from logging import CRITICAL, ERROR,  WARN, INFO, DEBUG
from logging import critical, error, info, warning, warn, debug
from logging import Formatter, getLogger, StreamHandler


RESET_TERM = u'\033[0;m'


def term_color(code):
    return lambda text: code + unicode(text) + RESET_TERM


COLOR_CODES = {
    'gray': u'\033[1;30m',
    'red': u'\033[1;31m',
    'green': u'\033[1;32m',
    'yellow': u'\033[1;33m',
    'blue': u'\033[1;34m',
    'magenta': u'\033[1;35m',
    'cyan': u'\033[1;36m',
    'white': u'\033[1;37m',
    'bgred': u'\033[1;41m',
    'bggreen': u'\033[1;42m',
    'bgbrown': u'\033[1;43m',
    'bgblue': u'\033[1;44m',
    'bgmagenta': u'\033[1;45m',
    'bgcyan': u'\033[1;46m',
    'bggray': u'\033[1;47m',
    'bgyellow': u'\033[1;43m',
    'bggrey': u'\033[1;100m',
}

ANSI = dict((col, term_color(code)) for col, code in COLOR_CODES.items())


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
            return TextFormatter( *args, **kwargs)


def init(level=None, logger=getLogger(), handler=StreamHandler()):
    fmt = DummyFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    if level:
        logger.setLevel(level)


if __name__ == '__main__':
    init(level=DEBUG)
    debug('debug')
    info('info')
    warning('warning')
    error('error')
    critical('critical')


__all__ = [
    "debug",
    "info",
    "warn",
    "warning",
    "error",
    "critical",
    "DEBUG",
    "INFO",
    "WARN",
    "ERROR",
    "CRITICAL"
]
