#!/usr/bin/env python

import unittest
import argparse
import logging

from tudor import generate_app

import tests
from tests.conversions_tests import *
from tests.convert_task_to_tag_tests import *
from tests.db_loader_tests import *
from tests.user_tests import *
from tests.is_user_authorized_or_admin_tests import *
from tests.task_hierarchy_tests import *
from tests.sort_by_hierarchy_tests import *
from tests.get_index_data_tests import *
from tests.get_deadlines_data_tests import *


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-log', action='store_true',
                        help='Print the log.')
    args = parser.parse_args()

    if args.print_log:
        logging.basicConfig(level=logging.DEBUG,
                            format=('%(asctime)s %(levelname)s:%(name)s:'
                                    '%(funcName)s:'
                                    '%(filename)s(%(lineno)d):'
                                    '%(threadName)s(%(thread)d):%(message)s'))

    unittest.main(argv=[''])

if __name__ == '__main__':
    run()
