#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden, Unauthorized

from models.task import Task
from models.user import User
from util import generate_ll


class GetTaskHierarchyDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.pl.create_all()
        self.user = User('name@example.com')
        self.task = Task('task')
        self.task.id = 1

    def test_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.get_task_hierarchy_data,
            None, self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_task_hierarchy_data,
            self.task.id + 1, self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Unauthorized,
            self.ll.get_task_hierarchy_data,
            self.task.id, None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_task_hierarchy_data,
            self.task.id, self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_hierarchy_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIn('task', result)
        self.assertIsNotNone(result['task'])
        self.assertIs(self.task, result['task'])
        self.assertIn('descendants', result)
        self.assertEqual([self.task], result['descendants'])

    # TODO: is_done and is_deleted
