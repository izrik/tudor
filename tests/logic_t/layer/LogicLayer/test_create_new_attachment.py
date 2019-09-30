#!/usr/bin/env python

import unittest

from datetime import datetime
from werkzeug.exceptions import NotFound, Forbidden

from models.object_types import ObjectTypes
from tests.util import MockFileObject
from .util import generate_ll


class CreateNewAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1
        self.f = MockFileObject('/filename.txt')

    def test_authorized_user_creates_new_attachment(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f,
                                               'test attachment', self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(result.object_type, ObjectTypes.Attachment)
        self.assertIsNotNone(result.id)
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
        self.task.users.append(self.user)
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
        self.task.users.append(self.user)
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

    def test_timestamp_sets_timestamp(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.pl.commit()
        timestamp = datetime(2018, 1, 1)
        # when
        result = self.ll.create_new_attachment(self.task.id, self.f,
                                               'test attachment', self.user,
                                               timestamp=timestamp)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(result.object_type, ObjectTypes.Attachment)
        self.assertEqual(timestamp, result.timestamp)
