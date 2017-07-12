
import logging

config_was_set = False

logging.basicConfig(
    level=logging.WARN,
    format='%(relativeCreated)d:%(levelname)s:%(name)s:%(funcName)s:'
           # '%(pathname)s,%(lineno)d:'
           ' %(message)s')


def get_logger(module, obj):
    return logging.getLogger('{}.{}'.format(module, type(obj).__name__))
