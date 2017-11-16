#!/usr/bin/env python

import unittest

from in_memory_persistence_layer import InMemoryPersistenceLayer
from models.task import Task


class TaskIdTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.pl.create_all()

    def test_constructor_default_id_is_none(self):
        # when
        task = Task('summary')
        # then
        self.assertIsNone(task.id)

    def test_db_add_does_not_assign_id(self):
        # given
        task = Task('summary')
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_db_commit_assigns_non_null_id(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)
