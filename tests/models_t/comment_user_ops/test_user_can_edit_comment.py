#!/usr/bin/env python

import unittest

from tests.util import generate_test_app

from flask_login import AnonymousUserMixin

from models.comment_user_ops import CommentUserOps


class UserCanEditCommentTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_test_app().pl
        self.task = self.pl.DbTask('task')
        self.author = self.pl.DbUser('author@example.org')
        self.pl.add(self.task)
        self.pl.add(self.author)
        self.task.users.append(self.author)
        self.comment = self.pl.DbComment('comment')
        self.comment.task = self.task
        self.comment.author = self.author
        self.pl.add(self.comment)
        self.pl.commit()

    def test_author_can_edit_own_comment(self):
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, self.author)
        # then
        self.assertTrue(result)

    def test_other_authorized_user_cannot_edit_comment(self):
        # given
        other = self.pl.DbUser('other@example.org')
        self.pl.add(other)
        self.task.users.append(other)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, other)
        # then
        self.assertFalse(result)

    def test_unauthorized_user_cannot_edit_comment(self):
        # given
        other = self.pl.DbUser('other@example.org')
        self.pl.add(other)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, other)
        # then
        self.assertFalse(result)

    def test_author_cannot_edit_comment_on_task_they_lost_access_to(self):
        # given
        self.task.users.remove(self.author)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, self.author)
        # then
        self.assertFalse(result)

    def test_admin_can_edit_someone_elses_comment(self):
        # given
        admin = self.pl.DbUser('admin@example.org', None, True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, admin)
        # then
        self.assertTrue(result)

    def test_authorless_comment_cannot_be_edited_by_regular_user(self):
        # given
        self.comment.author = None
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, self.author)
        # then
        self.assertFalse(result)

    def test_authorless_comment_can_be_edited_by_admin(self):
        # given
        self.comment.author = None
        admin = self.pl.DbUser('admin@example.org', None, True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, admin)
        # then
        self.assertTrue(result)

    def test_guest_user_cannot_edit_comment(self):
        # given
        guest = self.pl.get_guest_user()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, guest)
        # then
        self.assertFalse(result)

    def test_anon_user_cannot_edit_comment(self):
        # given
        anon = AnonymousUserMixin()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, anon)
        # then
        self.assertFalse(result)

    def test_none_user_cannot_edit_comment(self):
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, None)
        # then
        self.assertFalse(result)

    def test_none_comment_cannot_be_edited(self):
        # when
        result = CommentUserOps.user_can_edit_comment(
            None, self.task, self.author)
        # then
        self.assertFalse(result)

    def test_public_task_does_not_let_a_stranger_edit_comments(self):
        # given
        self.task.is_public = True
        other = self.pl.DbUser('other@example.org')
        self.pl.add(other)
        self.pl.commit()
        # when
        result = CommentUserOps.user_can_edit_comment(
            self.comment, self.task, other)
        # then
        self.assertFalse(result)
