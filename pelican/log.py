# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

__all__ = [
    'init'
]

import os
import sys
import logging
import locale

from collections import defaultdict, Mapping

import six

class BaseFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        FORMAT = '%(customlevelname)s %(message)s'
        super(BaseFormatter, self).__init__(fmt=FORMAT, datefmt=datefmt)

    def format(self, record):
        record.__dict__['customlevelname'] = self._get_levelname(record.levelname)
        # format multiline messages 'nicely' to make it clear they are together
        record.msg = record.msg.replace('\n', '\n  | ')
        return super(BaseFormatter, self).format(record)

    def formatException(self, ei):
        ''' prefix traceback info for better representation '''
        # .formatException returns a bytestring in py2 and unicode in py3
        # since .format will handle unicode conversion,
        # str() calls are used to normalize formatting string
        s = super(BaseFormatter, self).formatException(ei)
        # fancy format traceback
        s = str('\n').join(str('  | ') + line for line in s.splitlines())
        # separate the traceback from the preceding lines
        s = str('  |___\n{}').format(s)
        return s

    def _get_levelname(self, name):
        ''' NOOP: overridden by subclasses '''
        return name


class ANSIFormatter(BaseFormatter):
    ANSI_CODES = {
        'red': '\033[1;31m',
        'yellow': '\033[1;33m',
        'cyan': '\033[1;36m',
        'white': '\033[1;37m',
        'bgred': '\033[1;41m',
        'bggrey': '\033[1;100m',
        'reset': '\033[0;m'}

    LEVEL_COLORS = {
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bgred',
        'DEBUG': 'bggrey'}

    def _get_levelname(self, name):
        color = self.ANSI_CODES[self.LEVEL_COLORS.get(name, 'white')]
        if name == 'INFO':
            fmt = '{0}->{2}'
        else:
            fmt = '{0}{1}{2}:'
        return fmt.format(color, name, self.ANSI_CODES['reset'])


class TextFormatter(BaseFormatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def _get_levelname(self, name):
        if name == 'INFO':
            return '->'
        else:
            return name + ':'


class LimitFilter(logging.Filter):
    """
    Remove duplicates records, and limit the number of records in the same
    group.

    Groups are specified by the message to use when the number of records in
    the same group hit the limit.
    E.g.: log.warning(('43 is not the answer', 'More erroneous answers'))
    """

    _ignore = set()
    _threshold = 5
    _group_count = defaultdict(int)

    def filter(self, record):
        # don't limit log messages for anything above "warning"
        if record.levelno > logging.WARN:
            return True

        # extract group
        group = record.__dict__.get('limit_msg', None)
        group_args = record.__dict__.get('limit_args', ())

        # ignore record if it was already raised
        # use .getMessage() and not .msg for string formatting
        ignore_key = (record.levelno, record.getMessage())
        if ignore_key in self._ignore:
            return False
        else:
            self._ignore.add(ignore_key)

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


class SafeLogger(logging.Logger):
    """
    Base Logger which properly encodes Exceptions in Py2
    """
    _exc_encoding = locale.getpreferredencoding()

    def _log(self, level, msg, args, exc_info=None, extra=None):
        # if the only argument is a Mapping, Logger uses that for formatting
        # format values for that case
        if args and len(args)==1 and isinstance(args[0], Mapping):
            args = ({k: self._decode_arg(v) for k, v in args[0].items()},)
        # otherwise, format each arg
        else:
            args = tuple(self._decode_arg(arg) for arg in args)
        super(SafeLogger, self)._log(level, msg, args,
            exc_info=exc_info, extra=extra)

    def _decode_arg(self, arg):
        '''
        properly decode an arg for Py2 if it's Exception


        localized systems have errors in native language if locale is set
        so convert the message to unicode with the correct encoding
        '''
        if isinstance(arg, Exception):
            text = '%s: %s' % (arg.__class__.__name__, arg)
            if six.PY2:
                text = text.decode(self._exc_encoding)
            return text
        else:
            return arg


class LimitLogger(SafeLogger):
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
