#!/usr/bin/env python

import unittest

import werkzeug.exceptions

from tudor import generate_app


class CreateNewTaskTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.app = app
        self.ll = app.ll
        self.Task = app.ds.Task
        self.admin = app.ds.User('name@example.org', None, True)
        self.db.session.add(self.admin)
        self.user = app.ds.User('name2@example.org', None, False)
        self.db.session.add(self.user)

    def test_admin_adds_first_task(self):
        # when
        result = self.ll.create_new_task(self.admin, 't1', parent_id=None)

        # then
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        task = result[0]
        tul = result[1]
        self.assertIsInstance(task, self.Task)
        self.assertEqual('t1', task.summary)
        self.assertIsNone(task.parent)
        self.assertIsInstance(tul, self.app.ds.TaskUserLink)

    def test_admin_adds_second_task(self):
        # given
        t1 = self.Task('t1')
        t1.order_num = 1

        self.db.session.add(t1)

        # when
        result = self.ll.create_new_task(self.admin, 't2', parent_id=None)

        # then
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        task = result[0]
        tul = result[1]
        self.assertIsInstance(task, self.Task)
        self.assertEqual('t2', task.summary)
        self.assertIsNone(task.parent)
        self.assertIsInstance(tul, self.app.ds.TaskUserLink)

    def test_admin_adds_child_task_to_parent(self):
        # given
        p = self.Task('p')
        p.order_num = 1

        self.db.session.add(p)
        self.db.session.commit()

        # when
        result = self.ll.create_new_task(self.admin, 'c', parent_id=p.id)

        # then
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        task = result[0]
        tul = result[1]
        self.assertIsInstance(task, self.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)
        self.assertIsInstance(tul, self.app.ds.TaskUserLink)

    def test_user_adds_task_to_authorized_parent_succeeds(self):
        # given
        p = self.Task('p')
        p.order_num = 1

        self.db.session.add(p)
        self.db.session.commit()

        tul = self.app.ds.TaskUserLink(None, None)
        tul.task = p
        tul.user = self.user

        self.db.session.add(tul)

        # when
        result = self.ll.create_new_task(self.user, 'c', parent_id=p.id)

        # then
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        task = result[0]
        tul = result[1]
        self.assertIsInstance(task, self.Task)
        self.assertEqual('c', task.summary)
        self.assertIs(p, task.parent)
        self.assertIsInstance(tul, self.app.ds.TaskUserLink)

    def test_user_adds_task_to_non_authorized_parent_raises_403(self):
        # given
        p = self.Task('p')
        p.order_num = 1

        self.db.session.add(p)
        self.db.session.commit()

        # expect
        self.assertRaises(werkzeug.exceptions.Forbidden,
                          self.ll.create_new_task, self.user, 'c',
                          parent_id=p.id)
