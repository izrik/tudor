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

    def test_clearing_nullifies_author(self):
        # given
        user = self.pl.DbUser('name@example.org')
        comment = self.pl.DbComment('comment')
        comment.author = user
        # precondition
        self.assertIs(user, comment.author)
        # when
        comment.clear_relationships()
        # then
        self.assertIsNone(comment.author)


class CommentAuthorDeletionTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_deleting_the_author_keeps_the_comment(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('name@example.org')
        comment = self.pl.DbComment('comment')
        comment.task = task
        comment.author = user
        self.pl.add(task)
        self.pl.add(user)
        self.pl.add(comment)
        self.pl.commit()
        comment_id = comment.id
        # when
        self.pl.delete(user)
        # then
        result = self.pl.get_comment(comment_id)
        self.assertIsNotNone(result)
        self.assertEqual('comment', result.content)
        self.assertIsNone(result.author)
        self.assertIsNone(result.author_id)


class CommentToFlatDictTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl

    def test_author_becomes_author_id(self):
        # given
        user = self.pl.DbUser('name@example.org')
        comment = self.pl.DbComment('comment')
        comment.author = user
        self.pl.add(user)
        self.pl.add(comment)
        self.pl.commit()
        # when
        d = comment.to_flat_dict()
        # then
        self.assertNotIn('author', d)
        self.assertEqual(user.id, d['author_id'])

    def test_no_author_yields_none(self):
        # given
        comment = self.pl.DbComment('comment')
        self.pl.add(comment)
        self.pl.commit()
        # when
        d = comment.to_flat_dict()
        # then
        self.assertNotIn('author', d)
        self.assertIsNone(d['author_id'])
