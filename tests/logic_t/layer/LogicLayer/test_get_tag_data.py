#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTagDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_ordinary_user_gets_single_tag(self):
        # given a tag
        tag = self.pl.create_tag('tag')
        self.pl.add(tag)
        # and a user to attempt the retrieval
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(1, self.pl.count_tags())
        # when
        results = self.ll.get_tag_data(tag.id, user)
        # then
        self.assertIsInstance(results, dict)
        self.assertEqual(2, len(results.items()))
        self.assertIn('tag', results)
        self.assertIs(tag, results['tag'])
        self.assertIn('tasks', results)
        self.assertEqual([], results['tasks'])

    def test_tag_not_found_raises(self):
        # given a user to attempt the retrieval
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertEqual(0, self.pl.count_tags())
        self.assertIsNone(self.pl.get_tag(123))
        # expect
        self.assertRaises(NotFound, self.ll.get_tag_data, 123, user)
