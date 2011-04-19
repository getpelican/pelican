import logging
import sys
import os

global ANSI
ANSI = {
    'gray' : lambda(text) : '\033[1;30m' + unicode(text) + '\033[1;m',
    'red' : lambda(text) : '\033[1;31m' + unicode(text) + '\033[1;m',
    'green' : lambda(text) : '\033[1;32m' + unicode(text) + '\033[1;m',
    'yellow' : lambda(text) : '\033[1;33m' + unicode(text) + '\033[1;m',
    'blue' : lambda(text) : '\033[1;34m' + unicode(text) + '\033[1;m',
    'magenta' : lambda(text) : '\033[1;35m' + unicode(text) + '\033[1;m',
    'cyan' : lambda(text) : '\033[1;36m' + unicode(text) + '\033[1;m',
    'white' : lambda(text) : '\033[1;37m' + unicode(text) + '\033[1;m',
    'crimson' : lambda(text) : '\033[1;38m' + unicode(text) + '\033[1;m',
    'bgred' : lambda(text) : '\033[1;41m' + unicode(text) + '\033[1;m',
    'bggreen' : lambda(text) : '\033[1;42m' + unicode(text) + '\033[1;m',
    'bgbrown' : lambda(text) : '\033[1;43m' + unicode(text) + '\033[1;m',
    'bgblue' : lambda(text) : '\033[1;44m' + unicode(text) + '\033[1;m',
    'bgmagenta' : lambda(text) : '\033[1;45m' + unicode(text) + '\033[1;m',
    'bgcyan' : lambda(text) : '\033[1;46m' + unicode(text) + '\033[1;m',
    'bggray' : lambda(text) : '\033[1;47m' + unicode(text) + '\033[1;m',
    'bgcrimson' : lambda(text) : '\033[1;48m' + unicode(text) + '\033[1;m'
}

class ANSIFormatter(logging.Formatter):
    """
    Convert a `logging.LogReport' object into colored text, using ANSI escape sequences.
    """
    ## colors:

    def format(self, record):
        if not record.levelname or record.levelname is 'INFO':
            return ANSI['white'](record.msg)
        elif record.levelname is 'WARNING':
            return ANSI['yellow'](record.levelname) + ': ' + record.msg
        elif record.levelname is 'ERROR':
            return ANSI['red'](record.levelname) + ': ' + record.msg
        elif record.levelname is 'CRITICAL':
            return ANSI['bgred'](record.levelname) + ': ' + record.msg


class TextFormatter(logging.Formatter):
    """
    Convert a `logging.LogReport' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname is 'INFO':
            return record.msg
        else:
            return record.levelname + ': ' + record.msg


class Formatter(object):
    """
    A dummy class.
    Return an instance of the appropriate formatter (ANSIFormatter if sys.stdout.isatty() is True, else TextFormatter)
    """

    def __new__(cls, *args, **kwargs):
        if os.isatty(sys.stdout.fileno()): # thanks to http://stackoverflow.com/questions/2086961/how-can-i-determine-if-a-python-script-is-executed-from-crontab/2087031#2087031
            return ANSIFormatter(*args, **kwargs)
        else:
            return TextFormatter( *args, **kwargs)



# shortcuts
debug, info, warn, error, critical = (logging.debug,
                                      logging.info,
                                      logging.warn,
                                      logging.error,
                                      logging.critical)
DEBUG, INFO, WARN, ERROR, CRITICAL = (logging.DEBUG,
                                      logging.INFO,
                                      logging.WARN,
                                      logging.ERROR,
                                      logging.CRITICAL)


def init(level=None, logger=logging.getLogger(), handler=logging.StreamHandler()):
    fmt = Formatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    if level:   logger.setLevel(level)


if __name__ == '__main__':
    init()
    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logging.debug('Logging test')
    logging.info('info')
    logging.warning('warning')
    logging.error('error')
    logging.critical('critical')

