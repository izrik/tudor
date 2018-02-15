#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from models.tag import Tag
from models.task import Task
from models.user import User
from tests.logic_t.layer.LogicLayer.util import generate_ll


class DeleteTagFromTaskTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_tag_id_none_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            ValueError,
            self.ll.do_delete_tag_from_task,
            task.id, None, admin)

    def test_task_id_none_raises(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_delete_tag_from_task,
            None, tag.id, admin)

    def test_tag_not_in_task_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # when
        result = self.ll.do_delete_tag_from_task(task.id, tag.id, admin)
        # then
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # and
        self.assertIs(tag, result)

    def test_non_authorized_admin_removes_tag(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.tags.add(tag)
        self.pl.commit()
        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        self.assertNotIn(admin, task.users)
        self.assertNotIn(task, admin.tasks)
        # when
        result = self.ll.do_delete_tag_from_task(task.id, tag.id, admin)
        # then
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # and
        self.assertIs(tag, result)

    def test_authorized_admin_removes_tag(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        task.tags.add(tag)
        task.users.add(admin)
        self.pl.commit()
        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        self.assertIn(admin, task.users)
        self.assertIn(task, admin.tasks)
        # when
        result = self.ll.do_delete_tag_from_task(task.id, tag.id, admin)
        # then
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # and
        self.assertIs(tag, result)

    def test_authorized_user_removes_tag(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        user = User('user@example.com')
        self.pl.add(user)
        task.tags.add(tag)
        task.users.add(user)
        self.pl.commit()
        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        result = self.ll.do_delete_tag_from_task(task.id, tag.id, user)
        # then
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # and
        self.assertIs(tag, result)

    def test_non_authorized_user_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        tag = Tag('tag')
        self.pl.add(tag)
        user = User('user@example.com')
        self.pl.add(user)
        task.tags.add(tag)
        self.pl.commit()
        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_delete_tag_from_task,
            task.id, tag.id, user)

    def test_task_not_found_raises(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tasks())
        self.assertIsNone(self.pl.get_task(1))
        # when
        self.assertRaises(
            NotFound,
            self.ll.do_delete_tag_from_task,
            1, tag.id, admin)

    def test_tag_not_found_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        admin = User('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertIsNone(self.pl.get_tag(1))
        self.assertEqual(0, len(task.tags))
        # when
        result = self.ll.do_delete_tag_from_task(task.id, 1, admin)
        # then
        self.assertEqual(0, len(task.tags))
        self.assertIsNone(result)
