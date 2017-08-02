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
from tests.sort_by_hierarchy_tests import *
from tests.get_index_data_tests import *
from tests.get_deadlines_data_tests import *
from tests.create_new_task_tests import *
from tests.task_set_done_tests import *
from tests.task_set_deleted_tests import *
from tests.task_unset_done_tests import *
from tests.task_unset_deleted_tests import *
from tests.do_reset_order_nums_tests import *
from tests.tag_tests import *
from tests.task_tests import *
from tests.task_id_tests import *
from tests.task_css_tests import *
from tests.task_tags_tests import *
from tests.task_duration_text_tests import *
from tests.task_cost_text_tests import *
from tests.search_tests import *
from tests.task_dependencies_tests import *
from tests.ll_task_tags_tests import *
from tests.get_lowest_highest_order_num import *
from tests.task_prioritize_tests import *
from tests.route_tests import *
from tests.persistence_layer_tests import *
from tests.ll_do_import_data_tests import *
from tests.ll_set_task_tests import *
from tests.task_interlinking_tests import *
from tests.interlinking_tests import *
from tests.task_from_dict_tests import *
from tests.task_lazy_tests import *
from tests.tag_from_dict_tests import *
from tests.note_from_dict_tests import *
from tests.note_tests import *
from tests.attachment_tests import *
from tests.attachment_from_dict_tests import *
from tests.user_from_dict_tests import *
from tests.option_from_dict_tests import *


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

    unittest.main(argv=[''], failfast=True)

if __name__ == '__main__':
    run()
