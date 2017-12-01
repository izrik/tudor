#!/usr/bin/env python

import unittest

from models.task import Task
from models.user import User
from tests.logic_layer_t.util import generate_ll


class DbLoadNoHierarchyExcludeNonPublicTest(unittest.TestCase):
    def setUp(self):
        # given
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl
        self.t1 = Task('t1', is_public=True)
        self.t2 = Task('t2', is_public=False)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.user = User('name@example.org', None, True)
        self.pl.add(self.user)
        self.pl.commit()

    def test_exclude_non_public_false_returns_all_tasks(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, exclude_non_public=False)
        # then
        self.assertEqual({self.t1, self.t2}, set(tasks))

    def test_exclude_non_public_true_only_returns_public_tasks(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, exclude_non_public=True)
        # then
        self.assertEqual({self.t1}, set(tasks))


