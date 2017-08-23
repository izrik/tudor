#!/usr/bin/env python

import unittest
from datetime import datetime

from decimal import Decimal
from flask import json
from werkzeug.exceptions import Conflict

from tudor import generate_app
from models.task import Task


class LogicLayerDoImportDataTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.ll = self.app.ll
        self.pl = self.app.pl
        self.pl.create_all()

    def test_do_import_data_empty(self):
        # given
        src = '{}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_tasks(self):
        # given
        src = '{"tasks":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_single_task(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary"
        }]}'''

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))
        self.pl.commit()

        # then
        self.assertEqual(1, self.pl.count_tasks())
        task = self.pl.get_task(1)
        self.assertIsNotNone(task)
        self.assertEqual(1, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('', task.description)
        self.assertEqual(False, task.is_done)
        self.assertEqual(False, task.is_deleted)
        self.assertEqual(0, task.order_num)
        self.assertIsNone(task.deadline)
        self.assertIsNone(task.expected_duration_minutes)
        self.assertIsNone(task.expected_cost)
        self.assertIsNone(task.parent_id)
        self.assertIsNone(task.parent)
        self.assertEqual([], list(task.children))
        self.assertEqual([], list(task.tags))
        self.assertEqual([], list(task.users))
        self.assertEqual([], list(task.dependees))
        self.assertEqual([], list(task.dependants))
        self.assertEqual([], list(task.prioritize_before))
        self.assertEqual([], list(task.prioritize_after))
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_single_task_set_all_fields(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary":"summary",
            "description":"desc",
            "deadline": "2017-01-01",
            "is_done": true,
            "is_deleted": true,
            "order_num": 12345,
            "expected_duration_minutes": 6789,
            "expected_cost": 123.45
        }]}'''

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(1, self.pl.count_tasks())
        task = self.pl.get_task(1)
        self.assertIsNotNone(task)
        self.assertEqual(1, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual('desc', task.description)
        self.assertEqual(True, task.is_done)
        self.assertEqual(True, task.is_deleted)
        self.assertEqual(12345, task.order_num)
        self.assertEqual(datetime(2017, 1, 1), task.deadline)
        self.assertEqual(6789, task.expected_duration_minutes)
        self.assertEqual(Decimal('123.45'), task.expected_cost)
        self.assertIsNone(task.parent_id)
        self.assertIsNone(task.parent)
        self.assertEqual([], list(task.children))
        self.assertEqual([], list(task.tags))
        self.assertEqual([], list(task.users))
        self.assertEqual([], list(task.dependees))
        self.assertEqual([], list(task.dependants))
        self.assertEqual([], list(task.prioritize_before))
        self.assertEqual([], list(task.prioritize_after))
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_tasks_child_and_parent(self):
        # given
        src = '''{"tasks":[{
            "id": 1,
            "summary": "summary"
        },
        {
            "id": 2,
            "summary": "summary2",
            "parent_id": 1
        }]}'''

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))
        self.pl.commit()

        # then
        self.assertEqual(2, self.pl.count_tasks())

        t1 = self.pl.get_task(1)
        self.assertIsNotNone(t1)

        t2 = self.pl.get_task(2)
        self.assertIsNotNone(t2)

        self.assertEqual(1, t1.id)
        self.assertEqual('summary', t1.summary)
        self.assertEqual('', t1.description)
        self.assertEqual(False, t1.is_done)
        self.assertEqual(False, t1.is_deleted)
        self.assertEqual(0, t1.order_num)
        self.assertIsNone(t1.deadline)
        self.assertIsNone(t1.expected_duration_minutes)
        self.assertIsNone(t1.expected_cost)
        self.assertIsNone(t1.parent_id)
        self.assertIsNone(t1.parent)
        self.assertEqual([t2], list(t1.children))
        self.assertEqual([], list(t1.tags))
        self.assertEqual([], list(t1.users))
        self.assertEqual([], list(t1.dependees))
        self.assertEqual([], list(t1.dependants))
        self.assertEqual([], list(t1.prioritize_before))
        self.assertEqual([], list(t1.prioritize_after))

        self.assertEqual(2, t2.id)
        self.assertEqual('summary2', t2.summary)
        self.assertEqual('', t2.description)
        self.assertEqual(False, t2.is_done)
        self.assertEqual(False, t2.is_deleted)
        self.assertEqual(0, t2.order_num)
        self.assertIsNone(t2.deadline)
        self.assertIsNone(t2.expected_duration_minutes)
        self.assertIsNone(t2.expected_cost)
        self.assertEqual(1, t2.parent_id)
        self.assertIs(t1, t2.parent)
        self.assertEqual([], list(t2.children))
        self.assertEqual([], list(t2.tags))
        self.assertEqual([], list(t2.users))
        self.assertEqual([], list(t2.dependees))
        self.assertEqual([], list(t2.dependants))
        self.assertEqual([], list(t2.prioritize_before))
        self.assertEqual([], list(t2.prioritize_after))

    def test_do_import_data_task_conflict_id_already_exists(self):
        # given
        t0 = Task('pre-existing')
        self.pl.add(t0)
        self.pl.commit()
        src = '{"tasks":[{"id": ' + str(t0.id) + ',"summary":"summary"}]}'

        # precondition
        self.assertEqual(1, self.pl.count_tasks())
        t0_ = self.pl.get_task(t0.id)
        self.assertIsNotNone(t0_)
        self.assertIs(t0, t0_)
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # expect
        self.assertRaisesRegexp(
            Conflict,
            r"^409 Conflict: Some specified task id's already exist in the "
            r"database$",
            self.ll.do_import_data,
            json.loads(src))

    def test_do_import_data_empty_tags(self):
        # given
        src = '{"tags":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_notes(self):
        # given
        src = '{"notes":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_attachments(self):
        # given
        src = '{"attachments":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_users(self):
        # given
        src = '{"users":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_options(self):
        # given
        src = '{"options":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())
