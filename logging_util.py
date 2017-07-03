
import logging

config_was_set = False

logging.basicConfig(
    level=logging.DEBUG,
    format='%(relativeCreated)d:%(levelname)s:%(name)s:%(funcName)s:'
           # '%(pathname)s,%(lineno)d:'
           ' %(message)s')
