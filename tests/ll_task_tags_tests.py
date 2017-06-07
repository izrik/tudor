#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from tudor import generate_app


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.db = app.ds.db
        self.db.create_all()
        self.Task = app.ds.Task
        self.Tag = app.ds.Tag
        self.ll = app.ll
        self.User = app.ds.User
        self.admin = self.User('name@example.org', None, True)
        self.db.session.add(self.admin)
        self.user = self.User('name2@example.org', None, False)
        self.db.session.add(self.user)

    def test_get_or_create_tag_nonexistent_creates_tag(self):
        # precondition
        self.assertEqual(0, self.Tag.query.count())

        # when
        tag = self.ll.get_or_create_tag('abc')

        # then
        self.assertEqual(1, self.Tag.query.count())
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, self.Tag)
        self.assertEqual('abc', tag.value)

    def test_get_or_create_tag_existent_gets_tag(self):
        # given
        tag1 = self.Tag('def')
        self.db.session.add(tag1)

        # precondition
        self.assertEqual(1, self.Tag.query.count())

        # when
        tag2 = self.ll.get_or_create_tag('def')

        # then
        self.assertEqual(1, self.Tag.query.count())
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, self.Tag)
        self.assertEqual('def', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_admin_nonexistent_adds_tag(self):
        # given
        task = self.Task('task')
        self.db.session.add(task)
        self.db.session.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task.id, 'ghi', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, self.Tag)
        self.assertEqual('ghi', tag.value)

    def test_add_tag_to_task_admin_existent_adds_tag(self):
        # given
        task = self.Task('task')
        tag1 = self.Tag('jkl')
        self.db.session.add(task)
        self.db.session.add(tag1)
        self.db.session.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task.id, 'jkl', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, self.Tag)
        self.assertEqual('jkl', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_user_nonexistent_adds_tag(self):
        # given
        task = self.Task('task')
        task.users.append(self.user)
        self.db.session.add(task)
        self.db.session.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task.id, 'mno', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, self.Tag)
        self.assertEqual('mno', tag.value)

    def test_add_tag_to_task_user_existent_adds_tag(self):
        # given
        task = self.Task('task')
        tag1 = self.Tag('pqr')
        task.users.append(self.user)
        self.db.session.add(task)
        self.db.session.add(tag1)
        self.db.session.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task.id, 'pqr', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, self.Tag)
        self.assertEqual('pqr', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_missing_tasks_raises_not_found(self):
        # precondition
        self.assertEqual(0, self.Task.query.count())

        # expect
        self.assertRaises(NotFound,
                          self.ll.do_add_tag_to_task,
                          1, 'abc', self.admin)

    def test_add_tag_to_task_user_not_authorized_raises_forbidden(self):
        # given
        other_user = self.User('name3@example.org', None, False)
        self.db.session.add(other_user)
        task = self.Task('task')
        self.db.session.add(task)
        self.db.session.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # expect
        self.assertRaises(Forbidden,
                          self.ll.do_add_tag_to_task,
                          1, 'abc', other_user)