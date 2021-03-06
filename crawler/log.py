import logging
from functools import reduce


class SimpleLog(object):
    msg_format = '{} - {} -> {} | {} : {}'
    msg_l = []

    def __init__(self, file_name):
        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(20)
        fmt = '[%(asctime)s] - %(levelname)s : %(message)s'
        formatter = logging.Formatter(fmt)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        log_file = '../' + file_name + '.log'
        file_handler = logging.FileHandler(log_file, encoding='utf8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, *msg, unpacking=True):
        if unpacking:
            SimpleLog.msg_l.extend(list(msg))
            message = SimpleLog.msg_format.format(*SimpleLog.msg_l)
        else:
            message = reduce((lambda a, b: a + b), [str(i) for i in msg])
        self.logger.info(message)
        SimpleLog.msg_l.clear()

    def warning(self, *msg, unpacking=True):
        if unpacking:
            SimpleLog.msg_l.extend(list(msg))
            message = SimpleLog.msg_format.format(*SimpleLog.msg_l)
        else:
            message = reduce((lambda a, b: a + b), [str(i) for i in msg])
        self.logger.warning(message)
        SimpleLog.msg_l.clear()

    def error(self, *msg):
        message = reduce((lambda a, b: a + b), [str(i) for i in msg])
        self.logger.error(message)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, level, msg):
        self.logger.log(level, msg)

    def set_level(self, level):
        self.logger.setLevel(level)

    @staticmethod
    def set_msg(*args):
        SimpleLog.msg_l.extend(list(args))

    @staticmethod
    def disable():
        logging.disable(50)


log = SimpleLog('info')
err_log = SimpleLog('warning')
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)