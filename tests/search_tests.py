#!/usr/bin/env python

import unittest

from tudor import generate_app


class SearchTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.Task = self.app.Task
        self.db = self.app.pl.db
        self.User = self.app.pl.User
        self.admin = self.User('name@example.org', None, True)
        self.pl.create_all()
        self.pl.add(self.admin)
        # self.pl.commit()
        self.ll = self.app.ll

    def test_empty_db_yields_no_results(self):
        # when
        results = self.ll.search('something', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)

    def test_matching_summary_yields_task(self):
        # given
        task = self.Task('one two three')
        self.pl.add(task)
        # when
        results = self.ll.search('two', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([task], results2)

    def test_no_matching_summary_yields_nothing(self):
        # given
        task = self.Task('one two three')
        self.pl.add(task)
        # when
        results = self.ll.search('four', self.admin)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)

    def test_non_admin_may_access_own_tasks(self):
        # given
        user1 = self.User('user1@example.org', None, False)
        self.pl.add(user1)
        task = self.Task('one two three')
        task.users.append(user1)
        self.pl.add(task)
        # when
        results = self.ll.search('two', user1)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([task], results2)

    def test_non_admin_may_not_access_other_tasks(self):
        # given
        user1 = self.User('user1@example.org', None, False)
        self.pl.add(user1)
        user2 = self.User('user2@example.org', None, False)
        self.pl.add(user2)
        task = self.Task('one two three')
        task.users.append(user1)
        self.pl.add(task)
        # when
        results = self.ll.search('two', user2)
        # then
        self.assertIsNotNone(results)
        results2 = list(results)
        self.assertEqual([], results2)
