#!/usr/bin/env python

import argparse

from tests.conversions_tests import *

from tests.models_t.attachment_from_dict_tests import *
from tests.models_t.attachment_tests import *
from tests.models_t.interlinking_tests import *
from tests.models_t.note_from_dict_tests import *
from tests.models_t.note_tests import *
from tests.models_t.option_from_dict_tests import *
from tests.models_t.tag_from_dict_tests import *
from tests.models_t.tag_tests import *
from tests.models_t.task_cost_text_tests import *
from tests.models_t.task_css_tests import *
from tests.models_t.task_dependencies_tests import *
from tests.models_t.task_duration_text_tests import *
from tests.models_t.task_from_dict_tests import *
from tests.models_t.task_id_tests import *
from tests.models_t.task_interlinking_tests import *
from tests.models_t.task_lazy_tests import *
from tests.models_t.task_prioritize_tests import *
from tests.models_t.task_tags_tests import *
from tests.models_t.task_tests import *
from tests.models_t.user_from_dict_tests import *
from tests.models_t.user_tests import *

from tests.persistence_layer.persistence_layer_tests import *

from tests.logic_layer.convert_task_to_tag_tests import *
from tests.logic_layer.create_new_task_tests import *
from tests.logic_layer.db_loader_tests import *
from tests.logic_layer.do_import_data_tests import *
from tests.logic_layer.do_reset_order_nums_tests import *
from tests.logic_layer.get_deadlines_data_tests import *
from tests.logic_layer.get_index_data_tests import *
from tests.logic_layer.get_lowest_highest_order_num import *
from tests.logic_layer.is_user_authorized_or_admin_tests import *
from tests.logic_layer.search_tests import *
from tests.logic_layer.set_task_tests import *
from tests.logic_layer.sort_by_hierarchy_tests import *
from tests.logic_layer.task_dependencies_tests import *
from tests.logic_layer.task_prioritize_tests import *
from tests.logic_layer.task_set_deleted_tests import *
from tests.logic_layer.task_set_done_tests import *
from tests.logic_layer.task_tags_tests import *
from tests.logic_layer.task_unset_deleted_tests import *
from tests.logic_layer.task_unset_done_tests import *

from tests.view_layer.route_tests import *


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
