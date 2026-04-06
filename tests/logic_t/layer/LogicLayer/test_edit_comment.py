#!/usr/bin/env python

import unittest

from datetime import datetime, UTC
from werkzeug.exceptions import NotFound, Forbidden

from .util import generate_ll


class EditCommentTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.comment = self.pl.create_comment('original content')
        self.comment.task = self.task
        self.pl.add(self.comment)
        self.pl.commit()

    def test_non_existent_comment_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.edit_comment,
            self.comment.id + 1, 'new content', self.user)

    def test_user_none_raises(self):
        self.assertRaises(
            Forbidden,
            self.ll.edit_comment,
            self.comment.id, 'new content', None)

    def test_not_authorized_user_raises(self):
        # given
        other_user = self.pl.create_user('other@example.com')
        self.pl.add(other_user)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.edit_comment,
            self.comment.id, 'new content', other_user)

    def test_updates_content(self):
        # when
        result = self.ll.edit_comment(self.comment.id, 'new content', self.user)
        # then
        self.assertEqual('new content', result.content)

    def test_sets_date_last_updated(self):
        # precondition
        self.assertIsNone(self.comment.date_last_updated)
        # when
        result = self.ll.edit_comment(self.comment.id, 'new content', self.user)
        # then
        self.assertIsNotNone(result.date_last_updated)
        time_delta = datetime.now(UTC) - result.date_last_updated
        self.assertLessEqual(time_delta.total_seconds(), 1)

    def test_does_not_change_timestamp(self):
        # given
        original_timestamp = self.comment.timestamp
        # when
        self.ll.edit_comment(self.comment.id, 'new content', self.user)
        # then
        self.assertEqual(original_timestamp, self.comment.timestamp)
