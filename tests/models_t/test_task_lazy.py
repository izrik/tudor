#!/usr/bin/env python

import unittest

from models.task import Task


class TaskLazyParentTest(unittest.TestCase):
    def test_non_lazy_creation_parent_is_none_and_parent_lazy_is_none(self):
        # when
        task = Task('task')
        # then
        self.assertIsNone(task._parent)
        self.assertIsNone(task._parent_lazy)

    def test_lazy_is_none_parent_is_none_and_parent_lazy_is_none(self):
        # when
        task = Task('task', lazy=None)
        # then
        self.assertIsNone(task._parent)
        self.assertIsNone(task._parent_lazy)

    def test_lazy_is_empty_parent_is_none_and_parent_lazy_is_none(self):
        # when
        task = Task('task', lazy={})
        # then
        self.assertIsNone(task._parent)
        self.assertIsNone(task._parent_lazy)

    def test_lazy_parent_is_none_parent_is_none_and_parent_lazy_is_none(self):
        # when
        task = Task('task', lazy={'parent': None})
        # then
        self.assertIsNone(task._parent)
        self.assertIsNone(task._parent_lazy)

    def test_lazy_parent_is_not_none_but_returns_none_parent_lazy_is_set(self):
        # given
        def parent_source():
            return None
        # when
        task = Task('task', lazy={'parent': parent_source})
        # then
        self.assertIsNone(task._parent)
        self.assertIs(parent_source, task._parent_lazy)
        self.assertIsNone(task._parent_lazy())

    def test_lazy_parent_returns_object_parent_lazy_is_set(self):
        # given
        parent = Task('parent')

        def parent_source():
            return parent
        # when
        task = Task('task', lazy={'parent': parent_source})
        # then
        self.assertIsNone(task._parent)
        self.assertIs(parent_source, task._parent_lazy)
        self.assertIs(parent, task._parent_lazy())

    def test_accessing_parent_populates_it_and_removes_parent_lazy(self):
        # given
        parent = Task('parent')

        def parent_source():
            return parent
        task = Task('task', lazy={'parent': parent_source})
        # precondition
        self.assertIsNone(task._parent)
        self.assertIs(parent_source, task._parent_lazy)
        self.assertIs(parent, task._parent_lazy())
        # when
        result = task.parent
        # then
        self.assertIs(parent, result)
        self.assertIs(parent, task._parent)
        self.assertIsNone(task._parent_lazy)
