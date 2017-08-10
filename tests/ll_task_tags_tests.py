#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from tudor import generate_app
from models.task import Task
from models.user import User
from models.tag import Tag


class LogicLayerTaskTagsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl
        self.pl.create_all()
        self.ll = app.ll
        self.admin = User('name@example.org', None, True)
        self.pl.add(self.admin)
        self.user = User('name2@example.org', None, False)
        self.pl.add(self.user)

    def test_get_or_create_tag_nonexistent_creates_tag(self):
        # precondition
        self.assertEqual(0, self.pl.count_tags())

        # when
        tag = self.ll.get_or_create_tag('abc')

        # then
        self.assertEqual(1, self.pl.count_tags())
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('abc', tag.value)

    def test_get_or_create_tag_existent_gets_tag(self):
        # given
        tag1 = Tag('def')
        self.pl.add(tag1)

        # precondition
        self.assertEqual(1, self.pl.count_tags())

        # when
        tag2 = self.ll.get_or_create_tag('def')

        # then
        self.assertEqual(1, self.pl.count_tags())
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('def', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_admin_nonexistent_adds_tag(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task.id, 'ghi', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('ghi', tag.value)

    def test_add_tag_to_task_admin_existent_adds_tag(self):
        # given
        task = Task('task')
        tag1 = Tag('jkl')
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task.id, 'jkl', self.admin)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('jkl', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_user_nonexistent_adds_tag(self):
        # given
        task = Task('task')
        task.users.append(self.user)
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag = self.ll.do_add_tag_to_task(task.id, 'mno', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)
        self.assertEqual('mno', tag.value)

    def test_add_tag_to_task_user_existent_adds_tag(self):
        # given
        task = Task('task')
        tag1 = Tag('pqr')
        task.users.append(self.user)
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # when
        tag2 = self.ll.do_add_tag_to_task(task.id, 'pqr', self.user)

        # then
        self.assertEqual(1, len(task.tags))
        self.assertIsNotNone(tag2)
        self.assertIsInstance(tag2, Tag)
        self.assertEqual('pqr', tag2.value)
        self.assertIs(tag1, tag2)

    def test_add_tag_to_task_missing_tasks_raises_not_found(self):
        # precondition
        self.assertEqual(0, self.pl.count_tasks())

        # expect
        self.assertRaises(NotFound,
                          self.ll.do_add_tag_to_task,
                          1, 'abc', self.admin)

    def test_add_tag_to_task_user_not_authorized_raises_forbidden(self):
        # given
        other_user = User('name3@example.org', None, False)
        self.pl.add(other_user)
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()

        # precondition
        self.assertIsNotNone(task.id)
        self.assertEqual(0, len(task.tags))

        # expect
        self.assertRaises(Forbidden,
                          self.ll.do_add_tag_to_task,
                          1, 'abc', other_user)
