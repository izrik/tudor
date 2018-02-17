#!/usr/bin/env python

import unittest

from datetime import datetime
from werkzeug.exceptions import NotFound, Forbidden

from persistence.in_memory.models.note import Note
from persistence.in_memory.models.user import User
from util import generate_ll


class CreateNewNoteTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = User('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1

    def test_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.create_new_note,
            None, 'content', self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.create_new_note,
            self.task.id + 1, 'content', self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_note,
            self.task.id, 'content', None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_note,
            self.task.id, 'content', self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.add(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_note(self.task.id, 'content', self.user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)
        self.assertEqual('content', result.content)
        time_delta = (datetime.utcnow() - result.timestamp)
        self.assertLessEqual(time_delta.total_seconds(), 1)

    # TODO: content of None?
