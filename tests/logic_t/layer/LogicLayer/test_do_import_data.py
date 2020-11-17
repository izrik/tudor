#!/usr/bin/env python

import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from flask import json
from werkzeug.exceptions import Conflict, BadRequest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class LogicLayerDoImportDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_do_import_data_empty(self):
        # given
        src = '{"format_version":1}'

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
        src = '{"tasks":[],"format_version":1}'

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
        src = '''{"format_version":1,
        "tasks":[{
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
        src = '''{"format_version":1,
        "tasks":[{
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
        src = '''{"format_version":1,
        "tasks":[{
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
        t0 = self.pl.create_task('pre-existing')
        self.pl.add(t0)
        self.pl.commit()
        src = '{"format_version":1,"tasks":[{"id": ' + str(t0.id) + \
              ',"summary":"summary"}]}'

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
        self.assertRaisesRegex(
            Conflict,
            r"^409 Conflict: Some specified task id's already exist in the "
            r"database$",
            self.ll.do_import_data,
            json.loads(src))

    def test_imports_task_with_a_tag(self):
        # given
        src = '''{"format_version":1,
        "tasks":[{
            "id": 1,
            "summary":"summary",
            "tag_ids": [2]
        }],
        "tags":[{
            "id": 2,
            "value": "tag",
            "description": "a tag"
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

        self.assertEqual(1, self.pl.count_tags())
        tag = self.pl.get_tag(2)
        self.assertIsNotNone(tag)

        self.assertEqual(1, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual([tag], list(task.tags))

        self.assertEqual('tag', tag.value)
        self.assertEqual([task], list(tag.tasks))

        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_tag_of_task_not_found_raises(self):
        # given
        src = '''{"format_version":1,
        "tasks":[{
            "id": 1,
            "summary":"summary",
            "tag_ids": [2]
        }]}'''

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        # expect
        self.assertRaisesRegex(
            BadRequest,
            r"^400 Bad Request: The data was incorrect",
            self.ll.do_import_data,
            json.loads(src))

        # and
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_tags(self):
        # given
        src = '{"tags":[],"format_version":1}'

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

    def test_imports_single_tag(self):
        # given
        src = '{"format_version":1,' \
              '"tags":[{' \
              '"id":123,' \
              '"value":"tag",' \
              '"description":"description"}]}'

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
        self.assertEqual(1, self.pl.count_tags())
        tags = list(self.pl.get_tags())
        self.assertEqual(1, len(tags))
        tag = tags[0]
        self.assertEqual(123, tag.id)
        self.assertEqual('tag', tag.value)
        self.assertEqual('description', tag.description)
        self.assertEqual(set(), set(tag.tasks))
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_notes(self):
        # given
        src = '{"format_version":1,"notes":[]}'

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

    def test_imports_single_note(self):
        # given
        src = '''{"format_version":1,
        "tasks":[{
            "id": 1,
            "summary":"summary"
        }],
        "notes":[{
            "id":2,
            "content":"note",
            "timestamp": "2018-01-01",
            "task_id": 1
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
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(1, self.pl.count_notes())
        note = self.pl.get_note(2)
        self.assertIsNotNone(note)
        self.assertEqual('note', note.content)
        self.assertEqual(datetime(2018, 1, 1), note.timestamp)
        self.assertIs(task, note.task)
        self.assertEqual([note], list(task.notes))
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_attachments(self):
        # given
        src = '{"format_version":1,"attachments":[]}'

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

    def test_do_import_data_single_attachment(self):
        # given
        src = {
            "format_version": 1,
            "tasks": [{
                "id": 1,
                "summary": "summary"
            }],
            "attachments": [{
                "id": 2,
                "timestamp": "2020-01-01",
                "path": "path",
                "filename": "filename",
                "description": "description",
                "task_id": 1
            }]}

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(src)

        # then
        self.assertEqual(1, self.pl.count_tasks())
        task = self.pl.get_task(1)
        self.assertIsNotNone(task)
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(1, self.pl.count_attachments())
        attachment = self.pl.get_attachment(2)
        self.assertIsNotNone(attachment)
        self.assertEqual(datetime(2020, 1, 1), attachment.timestamp)
        self.assertEqual('path', attachment.path)
        self.assertEqual('filename', attachment.filename)
        self.assertEqual('description', attachment.description)
        self.assertEqual([attachment], list(task.attachments))
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_users(self):
        # given
        src = '{"format_version":1,"users":[]}'

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

    def test_do_import_data_single_user(self):
        # given
        src = {
            "format_version": 1,
            "users": [{
                "id": 1,
                "email": "name@example.com",
                "hashed_password": "hashed_password",
                "is_admin": False
            }]}

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(src)

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(1, self.pl.count_users())
        user = self.pl.get_user(1)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'name@example.com')
        self.assertEqual(user.hashed_password, 'hashed_password')
        self.assertFalse(user.is_admin)
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_empty_options(self):
        # given
        src = '{"format_version":1,"options":[]}'

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

    def test_imports_task_with_a_user(self):
        # given
        src = {
            "format_version": 1,
            "tasks": [{
                "id": 1,
                "summary": "summary",
                "user_ids": [2]
            }],
            "users": [{
                "id": 2,
                "email": "email",
                "hashed_password": "hashed_password",
                "is_admin": False}]}

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(src)
        self.pl.commit()

        # then
        self.assertEqual(1, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(1, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())
        # and
        task = self.pl.get_task(1)
        self.assertIsNotNone(task)
        user = self.pl.get_user(2)
        self.assertIsNotNone(user)
        self.assertEqual(1, task.id)
        self.assertEqual('summary', task.summary)
        self.assertEqual([user], list(task.users))
        self.assertEqual('email', user.email)
        self.assertEqual('hashed_password', user.hashed_password)
        self.assertFalse(user.is_admin)
        self.assertEqual([task], list(user.tasks))

    def test_do_import_data_single_option(self):
        # given
        src = {
            "format_version": 1,
            "options": [{
                "key": "key",
                "value": "value"}]}

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # when
        self.ll.do_import_data(src)

        # then
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(1, self.pl.count_options())
        option = self.pl.get_option('key')
        self.assertIsNotNone(option)
        self.assertEqual(option.key, 'key')
        self.assertEqual(option.value, 'value')

    def test_do_import_data_no_format_version_raises(self):
        # given
        src = '{"options":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # expect
        self.assertRaisesRegex(
            BadRequest,
            r"^400 Bad Request: Missing format_version",
            self.ll.do_import_data,
            json.loads(src))

        # and
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_wrong_format_version_raises(self):
        # given
        src = '{"format_version":2}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # expect
        self.assertRaisesRegex(
            BadRequest,
            r"^400 Bad Request: Bad format_version",
            self.ll.do_import_data,
            json.loads(src))

        # and
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_invalid_format_version_raises(self):
        # given
        src = '{"format_version":"one"}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # expect
        self.assertRaisesRegex(
            BadRequest,
            r"^400 Bad Request: Bad format_version",
            self.ll.do_import_data,
            json.loads(src))

        # and
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_do_import_data_invalid_format_version_raises_2(self):
        # given
        src = '{"format_version":[]}'

        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

        # expect
        self.assertRaisesRegex(
            BadRequest,
            r"^400 Bad Request: Bad format_version",
            self.ll.do_import_data,
            json.loads(src))

        # and
        self.assertEqual(0, self.pl.count_tasks())
        self.assertEqual(0, self.pl.count_tags())
        self.assertEqual(0, self.pl.count_notes())
        self.assertEqual(0, self.pl.count_attachments())
        self.assertEqual(0, self.pl.count_users())
        self.assertEqual(0, self.pl.count_options())

    def test_task_missing_id_raises(self):
        # given
        src = {
            "format_version": 1,
            'tasks': [
                {'summary': 'this is a task'}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error collecting tasks: \'id\'')

    def test_tag_missing_id_raises(self):
        # given
        src = {
            "format_version": 1,
            'tags': [
                {'value': 'this is a tag'}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error collecting tags: \'id\'')

    def test_user_missing_id_raises(self):
        # given
        src = {
            "format_version": 1,
            'users': [
                {'email': 'name@example.com'}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error collecting users: \'id\'')

    def test_task_missing_summary_raises(self):
        # given
        src = {
            "format_version": 1,
            'tasks': [
                {'id': 123}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading task: '
            '{\'id\': 123}: \'summary\'')

    def test_tag_missing_value_raises(self):
        # given
        src = {
            "format_version": 1,
            'tags': [
                {'id': 123,
                 'description': 'desc'}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading tag: '
            '{\'id\': 123, \'description\': \'desc\'}: \'value\'')

    def test_note_missing_content_raises(self):
        # given
        src = {
            "format_version": 1,
            'notes': [
                {'id': 123}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading note: '
            '{\'id\': 123}: \'content\'')

    def test_attachment_missing_timestamp_raises(self):
        # given
        src = {
            "format_version": 1,
            'attachments': [
                {'id': 123}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading attachment: '
            '{\'id\': 123}: \'timestamp\'')

    def test_user_missing_email_raises(self):
        # given
        src = {
            "format_version": 1,
            'users': [
                {'id': 123}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading user: '
            '{\'id\': 123}: \'email\'')

    def test_option_missing_key_raises(self):
        # given
        src = {
            "format_version": 1,
            'options': [
                {'value': 'abc'}]}
        self.ll._logger = Mock()
        # expect
        with self.assertRaises(BadRequest) as e:
            self.ll.do_import_data(src)
        # and
        self.assertEqual(e.exception.description, 'The data was incorrect')
        # and
        self.ll._logger.error.assert_called_once_with(
            'Exception while importing data: Error loading option: '
            '{\'value\': \'abc\'}: \'key\'')
