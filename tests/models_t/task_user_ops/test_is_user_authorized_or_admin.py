#!/usr/bin/env python

import unittest

from in_memory_persistence_layer import InMemoryPersistenceLayer
from models.task_user_ops import TaskUserOps
from models.task import Task
from models.user import User


class IsUserAuthorizedOrAdminTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_unauthorized_nonadmin_cannot_access_task(self):
        # given
        task = Task('task')
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertFalse(result)

    def test_authorized_nonadmin_can_access_task(self):
        # given
        task = Task('task')
        user = User('name@example.org')
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)

    def test_unauthorized_admin_can_access_task(self):
        # given
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)

    def test_authorized_admin_can_access_task(self):
        # given
        task = Task('task')
        user = User('name@example.org', None, True)
        self.pl.add(task)
        self.pl.add(user)
        task.users.append(user)
        self.pl.commit()
        # when
        result = TaskUserOps.is_user_authorized_or_admin(task, user)
        # then
        self.assertTrue(result)
