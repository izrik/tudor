#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import Task
from persistence.in_memory.layer import InMemoryPersistenceLayer


class TaskIdTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_constructor_default_id_is_none(self):
        # when
        task = Task('summary')
        # then
        self.assertIsNone(task.id)

    def test_pl_add_does_not_assign_id(self):
        # given
        task = Task('summary')
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_pl_commit_assigns_non_null_id(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)
