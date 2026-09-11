#!/usr/bin/env python

import unittest

from models.comment_base import CommentBase
from tests.util import generate_test_app
from datetime import datetime


class CommentCleanTimestampTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_none_yields_none(self):
        # expect
        self.assertIsNone(CommentBase._clean_timestamp(None))

    def test_string_gets_parsed(self):
        # when
        result = CommentBase._clean_timestamp('2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_unicode_gets_parsed(self):
        # when
        result = CommentBase._clean_timestamp('2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_datetime_gets_set(self):
        # when
        result = CommentBase._clean_timestamp(datetime(2017, 1, 1))
        # then
        self.assertEqual(datetime(2017, 1, 1), result)


class CommentClearRelationshipsTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_clearing_nullifies_task(self):
        # given
        task = self.pl.DbTask('task')
        comment = self.pl.DbComment('comment')
        comment.task = task
        # precondition
        self.assertIs(task, comment.task)
        # when
        comment.clear_relationships()
        # then
        self.assertIsNone(comment.task)
