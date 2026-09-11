#!/usr/bin/env python

import unittest

from tests.util import generate_test_app


class TaskTagsTest(unittest.TestCase):

    def setUp(self):
        self.pl = generate_test_app().pl

    def test_no_tags_yields_no_tags(self):
        # given
        t1 = self.pl.DbTask('t1')

        # when
        result = set(t1.get_tag_values())

        # then
        self.assertEqual(set(), result)

    def test_tasks_with_tags_return_those_tags_values(self):
        # given
        t1 = self.pl.DbTask('t1')
        tag1 = self.pl.DbTag('tag1')
        t1.tags.append(tag1)
        t2 = self.pl.DbTask('t2')
        tag2 = self.pl.DbTag('tag2')
        t2.tags.append(tag1)
        t2.tags.append(tag2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(tag1)
        self.pl.add(tag2)
        self.pl.commit()

        # when
        result = set(t1.get_tag_values())

        # then
        self.assertEqual({tag1.value}, result)

        # when
        result = set(t2.get_tag_values())

        # then
        self.assertEqual({tag1.value, tag2.value}, result)
