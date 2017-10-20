#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden, Unauthorized

from tudor import generate_app
from models.task import Task
from models.user import User, GuestUser
from persistence_layer import Pager


def generate_ll(db_uri='sqlite://'):
    app = generate_app(db_uri=db_uri)
    return app.ll


class GetTaskDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.pl.create_all()
        self.user = User('name@example.com')
        self.guest = GuestUser()
        self.task = Task('task')
        self.task.id = 1
        self.pl.add(self.task)
        self.pl.commit()

    def test_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.get_task_data,
            None, self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_task_data,
            self.task.id + 1, self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Unauthorized,
            self.ll.get_task_data,
            self.task.id, None)

    def test_user_guest_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Unauthorized,
            self.ll.get_task_data,
            self.task.id,
            self.guest)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_task_data,
            self.task.id, self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertIn('task', result)
        self.assertIsNotNone(result['task'])
        self.assertIs(self.task, result['task'])
        self.assertIn('descendants', result)
        self.assertEqual([self.task], result['descendants'])
        self.assertIn('pager', result)
        self.assertIsNotNone(result['pager'])
        self.assertIsInstance(result['pager'], Pager)

    def test_guest_user_can_see_public_tasks(self):
        # given
        self.task.is_public = True
        self.pl.commit()
        # when
        result = self.ll.get_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))

    def test_not_authorized_admin_can_see_tasks(self):
        # given
        admin = User('admin@example.com', '', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertNotIn(admin, self.task.users)
        self.assertNotIn(self.task, admin.tasks)
        # when
        result = self.ll.get_task_data(self.task.id, admin)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))

    # TODO: is_done and is_deleted
