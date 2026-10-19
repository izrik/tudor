#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from .util import generate_ll


class GetEditCommentDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.task.users.append(self.user)
        self.comment = self.pl.create_comment('content')
        self.comment.task = self.task
        self.comment.author = self.user
        self.pl.add(self.comment)
        self.pl.commit()

    def test_non_existent_comment_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.get_edit_comment_data,
            self.comment.id + 1, self.user)

    def test_user_none_raises(self):
        self.assertRaises(
            Forbidden,
            self.ll.get_edit_comment_data,
            self.comment.id, None)

    def test_non_author_raises(self):
        # given
        other_user = self.pl.create_user('other@example.com')
        self.pl.add(other_user)
        self.task.users.append(other_user)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.get_edit_comment_data,
            self.comment.id, other_user)

    def test_author_gets_the_comment(self):
        # when
        result = self.ll.get_edit_comment_data(self.comment.id, self.user)
        # then
        self.assertIs(self.comment, result['comment'])

    def test_admin_gets_the_comment(self):
        # given
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        result = self.ll.get_edit_comment_data(self.comment.id, admin)
        # then
        self.assertIs(self.comment, result['comment'])
