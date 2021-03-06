#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class DbLoadNoHierarchyExcludeNonPublicTest(unittest.TestCase):
    def setUp(self):
        # given
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.t1 = self.pl.create_task('t1', is_public=True)
        self.t2 = self.pl.create_task('t2', is_public=False)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.user = self.pl.create_user('name@example.org', None, True)
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
