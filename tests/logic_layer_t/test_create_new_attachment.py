#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from models.attachment import Attachment
from models.task import Task
from models.user import User
from tests.util import MockFileObject
from util import generate_ll


class CreateNewAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = User('name@example.com')
        self.task = Task('task')
        self.task.id = 1
        self.f = MockFileObject('/filename.txt')

    def test_authorized_user_creates_new_attachment(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f,
                                               'test attachment', self.user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Attachment)
        self.assertIsNone(result.id)
        self.assertIsNone(result.timestamp)
        self.assertEqual('filename.txt', result.path)
        # self.assertEqual('filename.txt', result.filename)
        self.assertEqual('test attachment', result.description)
        self.assertIs(self.task, result.task)
        self.assertIn(result, self.task.attachments)

    def test_task_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.create_new_attachment,
            None, self.f, 'test attachment', self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.create_new_attachment,
            self.task.id + 1, self.f, 'test attachment', self.user)

    def test_file_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.create_new_attachment,
            self.task.id, None, 'test attachment', self.user)

    def test_description_sets_description(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f, 'abc',
                                               self.user)
        # then
        self.assertEqual('abc', result.description)
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f, 'xyz',
                                               self.user)
        # then
        self.assertEqual('xyz', result.description)

    def test_description_none_sets_none(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f, None,
                                               self.user)
        # then
        self.assertIsNone(result.description)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_attachment,
            self.task.id, self.f, 'test attachment', None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_attachment,
            self.task.id, self.f, 'test attachment', self.user)
