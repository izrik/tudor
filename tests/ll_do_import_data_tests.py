#!/usr/bin/env python

import unittest

from flask import json

from tudor import generate_app


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
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_tasks(self):
        # given
        src = '{"tasks":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_tags(self):
        # given
        src = '{"tags":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_notes(self):
        # given
        src = '{"notes":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_attachments(self):
        # given
        src = '{"attachments":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_users(self):
        # given
        src = '{"users":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

    def test_do_import_data_empty_options(self):
        # given
        src = '{"options":[]}'

        # precondition
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())

        # when
        self.ll.do_import_data(json.loads(src))

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())
