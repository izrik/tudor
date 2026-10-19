#!/usr/bin/env python

import unittest

from datetime import datetime, UTC
from werkzeug.exceptions import NotFound, Forbidden

from models.object_types import ObjectTypes
from .util import generate_ll


class CreateNewCommentTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1

    def test_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.create_new_comment,
            None, 'content', self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.create_new_comment,
            self.task.id + 1, 'content', self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_comment,
            self.task.id, 'content', None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.create_new_comment,
            self.task.id, 'content', self.user)

    def test_authorized_user_does_not_raise(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_comment(self.task.id, 'content', self.user)
        # then
        self.assertIsNotNone(result)
        self.assertEqual(result.object_type, ObjectTypes.Comment)
        self.assertEqual('content', result.content)
        # the db stores naive datetimes, so compare without tzinfo
        time_delta = (datetime.now(UTC).replace(tzinfo=None) -
                      result.timestamp.replace(tzinfo=None))
        self.assertLessEqual(time_delta.total_seconds(), 1)

    def test_sets_author_to_current_user(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.pl.commit()
        # when
        result = self.ll.create_new_comment(self.task.id, 'content', self.user)
        # then
        self.assertIs(self.user, result.author)
        self.assertEqual(self.user.id, result.author_id)

    def test_admin_becomes_the_author(self):
        # given
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.add(self.task)
        self.pl.commit()
        # when
        result = self.ll.create_new_comment(self.task.id, 'content', admin)
        # then
        self.assertIs(admin, result.author)

    # TODO: content of None?
