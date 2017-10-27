#!/usr/bin/env python

import unittest

from tudor import generate_app
from models.task import Task
from models.tag import Tag


class TaskTagsTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.pl = app.pl

    def test_no_tags_yields_no_tags(self):
        # given
        t1 = Task('t1')

        # when
        result = set(t1.get_tag_values())

        # then
        self.assertEqual(set(), result)

    def test_tasks_with_tags_return_those_tags_values(self):
        # given
        t1 = Task('t1')
        tag1 = Tag('tag1')
        t1.tags.append(tag1)
        t2 = Task('t2')
        tag2 = Tag('tag2')
        t2.tags.append(tag1)
        t2.tags.append(tag2)

        self.pl.create_all()
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