#!/usr/bin/env python

import unittest

from tudor import generate_app


class TaskIdTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.db = self.app.pl.db
        self.db.create_all()
        self.Task = self.app.Task

    def test_constructor_default_id_is_none(self):
        # when
        task = self.Task('summary')
        # then
        self.assertIsNone(task.id)

    def test_db_add_does_not_assign_id(self):
        # given
        task = self.Task('summary')
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_db_commit_assigns_non_null_id(self):
        # given
        task = self.Task('summary')
        self.pl.add(task)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)
