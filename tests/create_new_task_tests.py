#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tudor import generate_app


class CreateNewTaskTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.pl.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.pl.Task
        self.admin = app.pl.User('name@example.org', None, True)
        self.db.session.add(self.admin)
        self.user = app.pl.User('name2@example.org', None, False)
        self.db.session.add(self.user)

    def test_admin_adds_first_task(self):
        # when
        task = self.ll.create_new_task(summary='t1', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, self.Task)
        self.assertEqual('t1', task.summary)
        self.assertIsNone(task.parent)

    def test_admin_adds_second_task(self):
        # given
        t1 = self.Task('t1')
        t1.order_num = 1

        self.db.session.add(t1)

        # when
        task = self.ll.create_new_task(summary='t2', current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, self.Task)
        self.assertEqual('t2', task.summary)
        self.assertIsNone(task.parent)

    def test_admin_adds_child_task_to_parent(self):
        # given
        p = self.Task('p')
        p.order_num = 1

        self.db.session.add(p)
        self.db.session.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.admin)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, self.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_authorized_parent_succeeds(self):
        # given
        p = self.Task('p')
        p.order_num = 1
        p.users.append(self.user)

        self.db.session.add(p)
        self.db.session.commit()

        # when
        task = self.ll.create_new_task(summary='c', parent_id=p.id,
                                       current_user=self.user)

        # then
        self.assertIsNotNone(task)
        self.assertIsInstance(task, self.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)

    def test_user_adds_task_to_non_authorized_parent_raises_403(self):
        # given
        p = self.Task('p')
        p.order_num = 1

        self.db.session.add(p)
        self.db.session.commit()

        # expect
        self.assertRaises(werkzeug.exceptions.Forbidden,
                          self.ll.create_new_task,
                          summary='c', parent_id=p.id, current_user=self.user)
