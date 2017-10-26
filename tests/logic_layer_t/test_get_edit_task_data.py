#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from models.tag import Tag
from tudor import generate_app
from models.task import Task
from models.user import User


def generate_ll(db_uri='sqlite://'):
    app = generate_app(db_uri=db_uri)
    return app.ll


class EditTaskDataTest(unittest.TestCase):
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
            self.ll.get_edit_task_data,
            None, self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.get_edit_task_data,
            self.task.id + 1, self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_edit_task_data,
            self.task.id, None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_edit_task_data,
            self.task.id, self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.get_edit_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIn('task', result)
        self.assertIs(self.task, result['task'])
        self.assertIn('tag_list', result)
        self.assertEqual('', result['tag_list'])

    def test_single_tag_given_in_list(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.task.tags.add(tag)
        self.pl.commit()
        # when
        result = self.ll.get_edit_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIn('task', result)
        self.assertIs(self.task, result['task'])
        self.assertIn('tag_list', result)
        self.assertEqual('tag', result['tag_list'])

    def test_two_tags_given_in_list(self):
        # given
        tag1 = Tag('tag1')
        self.pl.add(tag1)
        tag2 = Tag('tag2')
        self.pl.add(tag2)
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.task.tags.add(tag1)
        self.task.tags.add(tag2)
        self.pl.commit()
        # when
        result = self.ll.get_edit_task_data(self.task.id, self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(2, len(result))
        self.assertIn('task', result)
        self.assertIs(self.task, result['task'])
        self.assertIn('tag_list', result)
        # order doesn't matter
        self.assertIn(result['tag_list'], ['tag1,tag2', 'tag2,tag1'])
