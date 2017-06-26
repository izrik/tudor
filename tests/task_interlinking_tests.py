#!/usr/bin/env python

import unittest

from models.task import Task, InterlinkedChildren


class ChildrenInterlinkingTest(unittest.TestCase):
    def setUp(self):
        self.parent = Task('parent')
        self.c1 = Task('c1')
        self.c2 = Task('c2')

    def test_in(self):
        # precondition
        self.assertEqual(0, len(self.parent.children))
        self.assertIsNone(self.c1.parent)
        self.assertIsNone(self.c2.parent)
        self.assertNotIn(self.c1, self.parent.children)
        self.assertNotIn(self.c2, self.parent.children)
        # when
        self.parent.children.list.append(self.c1)
        self.c1._parent = self.parent
        # then
        self.assertIn(self.c1, self.parent.children)
        self.assertNotIn(self.c2, self.parent.children)

    def test_append(self):
        # precondition
        self.assertEqual(0, len(self.parent.children))
        self.assertIsNone(self.c1.parent)
        self.assertIsNone(self.c2.parent)
        # when
        self.parent.children.append(self.c1)
        # then
        self.assertIn(self.c1, self.parent.children)
        self.assertEqual(1, len(self.parent.children))
        self.assertEqual([self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIsNone(self.c2.parent)

    def test_append_already_in_silently_ignored(self):
        # given
        self.parent.children.append(self.c1)
        # precondition
        self.assertIn(self.c1, self.parent.children)
        self.assertEqual(1, len(self.parent.children))
        self.assertEqual([self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIsNone(self.c2.parent)
        # when
        self.parent.children.append(self.c1)
        # then
        self.assertIn(self.c1, self.parent.children)
        self.assertEqual(1, len(self.parent.children))
        self.assertEqual([self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIsNone(self.c2.parent)

    def test_remove(self):
        # given
        self.parent.children.append(self.c1)
        # precondition
        self.assertIn(self.c1, self.parent.children)
        self.assertEqual([self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIsNone(self.c2.parent)
        # when
        self.parent.children.remove(self.c1)
        # then
        self.assertEqual(0, len(self.parent.children))
        self.assertIsNone(self.c1.parent)
        self.assertIsNone(self.c2.parent)

    def test_remove_non_child_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.parent.children))
        self.assertIsNone(self.c1.parent)
        self.assertIsNone(self.c2.parent)
        # when
        self.parent.children.remove(self.c1)
        # then
        self.assertEqual(0, len(self.parent.children))
        self.assertIsNone(self.c1.parent)
        self.assertIsNone(self.c2.parent)

    def test_insert(self):
        # given
        self.parent.children.append(self.c1)
        # precondition
        self.assertIn(self.c1, self.parent.children)
        self.assertEqual(1, len(self.parent.children))
        self.assertEqual([self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIsNone(self.c2.parent)
        # when
        self.parent.children.insert(0, self.c2)
        self.assertIn(self.c1, self.parent.children)
        self.assertIn(self.c2, self.parent.children)
        self.assertEqual(2, len(self.parent.children))
        self.assertEqual([self.c2, self.c1], list(self.parent.children))
        self.assertIs(self.parent, self.c1.parent)
        self.assertIs(self.parent, self.c2.parent)
