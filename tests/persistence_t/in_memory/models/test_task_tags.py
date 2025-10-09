#!/usr/bin/env python

import unittest

from persistence.in_memory.models.tag import IMTag
from persistence.in_memory.models.task import IMTask
from persistence.in_memory.layer import InMemoryPersistenceLayer


class TaskTagsTest(unittest.TestCase):

    def setUp(self):
        self.pl = InMemoryPersistenceLayer()

    def test_no_tags_yields_no_tags(self):
        # given
        t1 = self.pl.create_task('t1')
        self.pl.save(t1)

        # when
        result = set(tag.value for tag in self.pl.get_task_tags(t1.id))

        # then
        self.assertEqual(set(), result)

    def test_tasks_with_tags_return_those_tags_values(self):
        # given
        t1 = self.pl.create_task('t1')
        tag1 = self.pl.create_tag('tag1')
        t2 = self.pl.create_task('t2')
        tag2 = self.pl.create_tag('tag2')

        self.pl.save(t1)
        self.pl.save(t2)
        self.pl.save(tag1)
        self.pl.save(tag2)

        self.pl.associate_tag_with_task(t1.id, tag1.id)
        self.pl.associate_tag_with_task(t2.id, tag1.id)
        self.pl.associate_tag_with_task(t2.id, tag2.id)

        # when
        result = set(tag.value for tag in self.pl.get_task_tags(t1.id))

        # then
        self.assertEqual({tag1.value}, result)

        # when
        result = set(tag.value for tag in self.pl.get_task_tags(t2.id))

        # then
        self.assertEqual({tag1.value, tag2.value}, result)
