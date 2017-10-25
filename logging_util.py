
import logging

config_was_set = False

logging.basicConfig(
    level=logging.INFO,
    format=u'%(relativeCreated)d:%(levelname)s:%(name)s:%(funcName)s:'
           # u'%(pathname)s,%(lineno)d:'
           u' %(message)s')


def get_logger_by_object(module, obj):
    return get_logger_by_class(module, type(obj))


def get_logger_by_class(module, cls):
    return get_logger_by_name(module, cls.__name__)


def get_logger_by_name(module, name):
    return logging.getLogger('{}.{}'.format(module, name))
