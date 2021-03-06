#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class SearchTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.admin = self.pl.create_user('name@example.org', None, True)
        self.pl.add(self.admin)
        self.pl.commit()

    def test_empty_db_yields_no_results(self):
        # when
        results = self.ll.search('something', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)

    def test_matching_summary_yields_task(self):
        # given
        task = self.pl.create_task('one two three')
        self.pl.add(task)
        self.pl.commit()
        # when
        results = self.ll.search('two', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([task], results2)

    def test_no_matching_summary_yields_nothing(self):
        # given
        task = self.pl.create_task('one two three')
        self.pl.add(task)
        self.pl.commit()
        # when
        results = self.ll.search('four', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)

    def test_non_admin_may_access_own_tasks(self):
        # given
        user1 = self.pl.create_user('user1@example.org', None, False)
        self.pl.add(user1)
        task = self.pl.create_task('one two three')
        task.users.append(user1)
        self.pl.add(task)
        self.pl.commit()
        # when
        results = self.ll.search('two', user1)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([task], results2)

    def test_non_admin_may_not_access_other_tasks(self):
        # given
        user1 = self.pl.create_user('user1@example.org', None, False)
        self.pl.add(user1)
        user2 = self.pl.create_user('user2@example.org', None, False)
        self.pl.add(user2)
        task = self.pl.create_task('one two three')
        task.users.append(user1)
        self.pl.add(task)
        self.pl.commit()
        # when
        results = self.ll.search('two', user2)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)
