import logging

gray = lambda(text) : '\033[1;30m' + str(text) + '\033[1;m'
red = lambda(text) : '\033[1;31m' + str(text) + '\033[1;m'
green = lambda(text) : '\033[1;32m' + str(text) + '\033[1;m'
yellow = lambda(text) : '\033[1;33m' + str(text) + '\033[1;m'
blue = lambda(text) : '\033[1;34m' + str(text) + '\033[1;m'
magenta = lambda(text) : '\033[1;35m' + str(text) + '\033[1;m'
cyan = lambda(text) : '\033[1;36m' + str(text) + '\033[1;m'
white = lambda(text) : '\033[1;37m' + str(text) + '\033[1;m'
crimson = lambda(text) : '\033[1;38m' + str(text) + '\033[1;m'
bgred = lambda(text) : '\033[1;41m' + str(text) + '\033[1;m'
bggreen = lambda(text) : '\033[1;42m' + str(text) + '\033[1;m'
bgbrown = lambda(text) : '\033[1;43m' + str(text) + '\033[1;m'
bgblue = lambda(text) : '\033[1;44m' + str(text) + '\033[1;m'
bgmagenta = lambda(text) : '\033[1;45m' + str(text) + '\033[1;m'
bgcyan = lambda(text) : '\033[1;46m' + str(text) + '\033[1;m'
bggray = lambda(text) : '\033[1;47m' + str(text) + '\033[1;m'
bgcrimson = lambda(text) : '\033[1;48m' + str(text) + '\033[1;m'


class Formatter(logging.Formatter):

    def format(self, record):
        if record.levelname is 'INFO':
            return record.msg
        elif record.levelname is 'WARNING':
            return yellow(record.levelname) + ': ' + record.msg
        elif record.levelname is 'ERROR':
            return red(record.levelname) + ': ' + record.msg
        elif record.levelname is 'CRITICAL':
            return bgred(record.levelname) + ': ' + record.msg

def init(logger=logging.getLogger(), handler=logging.StreamHandler()):
    fmt = Formatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

init()


logging.info('info')
logging.warning('warning')
logging.error('error')
logging.critical('critical')

