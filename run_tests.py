#!/usr/bin/env python

import argparse
import unittest

# TODO: import by name instead of star

from tests.conversions_tests import TypeConversionFunctionTest
from tests.command_line_tests import CommandLineTests

from tests.models_t.attachment_from_dict_tests import AttachmentFromDictTest
from tests.models_t.attachment_tests import AttachmentCleanTimestampTest, \
    AttachmentClearRelationshipsTest
from tests.models_t.interlinking_tests import LazyLoadingTest, \
    InterlinkedSetTest
from tests.models_t.note_from_dict_tests import NoteFromDictTest
from tests.models_t.note_tests import NoteCleanTimestampTest, \
    NoteClearRelationshipsTest
from tests.models_t.option_from_dict_tests import OptionFromDictTest
from tests.models_t.tag_from_dict_tests import TagFromDictTest
from tests.models_t.tag_tests import TagTest
from tests.models_t.task_cost_text_tests import TaskCostTextTest
from tests.models_t.task_css_tests import TaskCssTest
from tests.models_t.task_dependencies_tests import TaskDependenciesTest
from tests.models_t.task_duration_text_tests import TaskDurationTextTest
from tests.models_t.task_from_dict_tests import TaskFromDictTest
from tests.models_t.task_id_tests import TaskIdTest
from tests.models_t.task_interlinking_tests import ChildrenInterlinkingTest, \
    TaskTagsInterlinkingTest, TaskUsersInterlinkingTest, \
    DependeesDependantsInterlinkingTest, \
    PrioritizeBeforeAfterInterlinkingTest, NotesInterlinkingTest, \
    AttachmentsInterlinkingTest
from tests.models_t.task_lazy_tests import TaskLazyParentTest
from tests.models_t.task_prioritize_tests import TaskPrioritizeTest
from tests.models_t.task_tags_tests import TaskTagsTest
from tests.models_t.task_tests import TaskTest
from tests.models_t.user_from_dict_tests import UserFromDictTest
from tests.models_t.user_tests import UserTest, GuestUserTest
from tests.models_t.task_user_ops.is_user_authorized_or_admin_tests import \
    IsUserAuthorizedOrAdminTest
from tests.models_t.task_user_ops.user_can_edit_task_tests import \
    UserCanEditTaskTest
from tests.models_t.task_user_ops.user_can_view_task_tests import \
    UserCanViewTaskTest

from tests.persistence_layer.persistence_layer_tests import *

from tests.logic_layer.convert_task_to_tag_tests import ConvertTaskToTagTest
from tests.logic_layer.create_new_task_tests import CreateNewTaskTest
from tests.logic_layer.db_loader_tests import DbLoaderTest, \
    DbLoaderDoneDeletedTest, DbLoaderDeadlinedTest, DbLoadNoHierarchyTest
from tests.logic_layer.do_import_data_tests import LogicLayerDoImportDataTest
from tests.logic_layer.do_reset_order_nums_tests import ResetOrderNumsTest
from tests.logic_layer.get_deadlines_data_tests import GetDeadlinesDataTest
from tests.logic_layer.get_index_data_tests import GetIndexDataTest
from tests.logic_layer.get_lowest_highest_order_num import \
    GetLowestHighestOrderNumTest
from tests.logic_layer.search_tests import SearchTest
from tests.logic_layer.set_task_tests import LogicLayerSetTaskTest
from tests.logic_layer.sort_by_hierarchy_tests import SortByHierarchyTest
from tests.logic_layer.task_dependencies_tests import \
    TaskDependeesLogicLayerTest, TaskDependantsLogicLayerTest
from tests.logic_layer.task_prioritize_tests import \
    TaskPrioritizeBeforeLogicLayerTest, TaskPrioritizeAfterLogicLayerTest
from tests.logic_layer.task_set_deleted_tests import TaskSetDeletedTest
from tests.logic_layer.task_set_done_tests import TaskSetDoneTest
from tests.logic_layer.task_tags_tests import LogicLayerTaskTagsTest
from tests.logic_layer.task_unset_deleted_tests import TaskUnsetDeletedTest
from tests.logic_layer.task_unset_done_tests import TaskUnsetDoneTest
from tests.logic_layer.get_task_data_tests import GetTaskDataTest
from tests.logic_layer.get_task_hierarchy_data_tests import GetTaskHierarchyDataTest
from tests.logic_layer.create_new_note_tests import CreateNewNoteTest
from tests.logic_layer.get_edit_task_data_tests import EditTaskDataTest
from tests.logic_layer.allowed_file_tests import AllowedFileTest
from tests.logic_layer.create_new_attachment_tests import \
    CreateNewAttachmentTest
from tests.logic_layer.reorder_tasks_tests import ReorderTasksTest
from tests.logic_layer.do_move_task_up_tests import DoMoveTaskUpTest
from tests.logic_layer.do_move_task_down_tests import DoMoveTaskDownTest
from tests.logic_layer.do_move_task_to_top_tests import DoMoveTaskToTopTest
from tests.logic_layer.do_move_task_to_bottom_tests import \
    DoMoveTaskToBottomTest
from tests.logic_layer.load_no_hierarchy_exclude_non_public import \
    DbLoadNoHierarchyExcludeNonPublicTest
from tests.logic_layer.load_is_public_tests import LoadIsPublicTest, \
    LoadIsPublicRegularUserTest

from tests.view_layer.route_tests import RouteTest
from tests.view_layer.task_tests import TaskTest


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
