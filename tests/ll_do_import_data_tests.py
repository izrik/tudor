#!/usr/bin/env python

import unittest

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
        self.ll.do_import_data(src)

        # then
        self.assertEqual(0, self.pl.task_query.count())
        self.assertEqual(0, self.pl.tag_query.count())
        self.assertEqual(0, self.pl.note_query.count())
        self.assertEqual(0, self.pl.attachment_query.count())
        self.assertEqual(0, self.pl.user_query.count())
        self.assertEqual(0, self.pl.option_query.count())
