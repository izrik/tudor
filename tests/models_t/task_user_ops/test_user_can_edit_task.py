#!/usr/bin/env python

import unittest

from flask_login import AnonymousUserMixin

from in_memory_persistence_layer import InMemoryPersistenceLayer
from models.task_user_ops import TaskUserOps
from models.task import Task
from models.user import User, GuestUser


class UserCanEditTaskTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_unauthorized_nonadmin_cannot_edit_private_task(self):
        # given
        task = Task('task')
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_edit_private_task(self):
        # given
        task = Task('task')
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_edit_private_task(self):
        # given
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_authorized_admin_can_edit_private_task(self):
        # given
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_guest_user_cannot_edit_private_task(self):
        # given
        task = Task('task')
        guest = GuestUser()
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, guest)
        # then
        self.assertFalse(result)

    def test_anon_user_cannot_edit_private_task(self):
        # given
        task = Task('task')
        anon = AnonymousUserMixin()
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, anon)
        # then
        self.assertFalse(result)

    def test_none_user_cannot_edit_private_task(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, None)
        # then
        self.assertFalse(result)

    def test_unauthorized_nonadmin_cannot_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_authorized_admin_can_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, user)
        # then
        self.assertTrue(result)

    def test_guest_user_cannot_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        guest = GuestUser()
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, guest)
        # then
        self.assertFalse(result)

    def test_anon_user_cannot_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        anon = AnonymousUserMixin()
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, anon)
        # then
        self.assertFalse(result)

    def test_none_user_cannot_edit_public_task(self):
        # given
        task = Task('task', is_public=True)
        self.pl.add(task)
        self.pl.commit()
        # when
        result = TaskUserOps.user_can_edit_task(task, None)
        # then
        self.assertFalse(result)
