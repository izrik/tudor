#!/usr/bin/env python

import unittest

from models.task import Task
from models.tag import Tag
from models.user import User


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


class TaskTagsInterlinkingTest(unittest.TestCase):
    def setUp(self):
        self.task = Task('task')
        self.tag = Tag('tag')

    def test_in(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # when
        self.task.tags.set.add(self.tag)
        self.tag.tasks.set.add(self.task)
        # then
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)

    def test_add_tag(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # when
        self.task.tags.add(self.tag)
        # then
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)

    def test_add_tag_already_in_silently_ignored(self):
        # given
        self.task.tags.add(self.tag)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.task.tags.add(self.tag)
        # then
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)

    def test_remove_tag(self):
        # given
        self.task.tags.add(self.tag)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.task.tags.remove(self.tag)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)

    def test_remove_tag_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # expect
        self.assertRaises(KeyError, self.task.tags.remove, self.tag)

    def test_discard_tag(self):
        # given
        self.task.tags.add(self.tag)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.task.tags.discard(self.tag)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)

    def test_discard_tag_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # when
        self.task.tags.discard(self.tag)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)

    def test_add_task(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # when
        self.tag.tasks.add(self.task)
        # then
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)

    def test_add_task_already_in_silently_ignored(self):
        # given
        self.tag.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.tag.tasks.add(self.task)
        # then
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)

    def test_remove_task(self):
        # given
        self.tag.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.tag.tasks.remove(self.task)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)

    def test_remove_task_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # expect
        self.assertRaises(KeyError, self.tag.tasks.remove, self.task)

    def test_discard_task(self):
        # given
        self.tag.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.tags))
        self.assertEqual(1, len(self.tag.tasks))
        self.assertIn(self.tag, self.task.tags)
        self.assertIn(self.task, self.tag.tasks)
        # when
        self.tag.tasks.discard(self.task)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)

    def test_discard_task_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)
        # when
        self.tag.tasks.discard(self.task)
        # then
        self.assertEqual(0, len(self.task.tags))
        self.assertEqual(0, len(self.tag.tasks))
        self.assertNotIn(self.tag, self.task.tags)
        self.assertNotIn(self.task, self.tag.tasks)


class TaskUsersInterlinkingTest(unittest.TestCase):
    def setUp(self):
        self.task = Task('task')
        self.user = User('user')

    def test_in(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # when
        self.task.users.set.add(self.user)
        self.user.tasks.set.add(self.task)
        # then
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)

    def test_add_user(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # when
        self.task.users.add(self.user)
        # then
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)

    def test_add_user_already_in_silently_ignored(self):
        # given
        self.task.users.add(self.user)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.task.users.add(self.user)
        # then
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)

    def test_remove_user(self):
        # given
        self.task.users.add(self.user)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.task.users.remove(self.user)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)

    def test_remove_user_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # expect
        self.assertRaises(KeyError, self.task.users.remove, self.user)

    def test_discard_user(self):
        # given
        self.task.users.add(self.user)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.task.users.discard(self.user)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)

    def test_discard_user_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # when
        self.task.users.discard(self.user)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)

    def test_add_task(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # when
        self.user.tasks.add(self.task)
        # then
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)

    def test_add_task_already_in_silently_ignored(self):
        # given
        self.user.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.user.tasks.add(self.task)
        # then
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)

    def test_remove_task(self):
        # given
        self.user.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.user.tasks.remove(self.task)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)

    def test_remove_task_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # expect
        self.assertRaises(KeyError, self.user.tasks.remove, self.task)

    def test_discard_task(self):
        # given
        self.user.tasks.add(self.task)
        # precondition
        self.assertEqual(1, len(self.task.users))
        self.assertEqual(1, len(self.user.tasks))
        self.assertIn(self.user, self.task.users)
        self.assertIn(self.task, self.user.tasks)
        # when
        self.user.tasks.discard(self.task)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)

    def test_discard_task_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)
        # when
        self.user.tasks.discard(self.task)
        # then
        self.assertEqual(0, len(self.task.users))
        self.assertEqual(0, len(self.user.tasks))
        self.assertNotIn(self.user, self.task.users)
        self.assertNotIn(self.task, self.user.tasks)


class DependeesDependantsInterlinkingTest(unittest.TestCase):
    def setUp(self):
        self.t1 = Task('t1')
        self.t2 = Task('t2')

    def test_in(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.set.add(self.t2)
        self.t2.dependees.set.add(self.t1)
        # then
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)

    def test_add_user(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.add(self.t2)
        # then
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)

    def test_add_user_already_in_silently_ignored(self):
        # given
        self.t1.dependants.add(self.t2)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.add(self.t2)
        # then
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)

    def test_remove_user(self):
        # given
        self.t1.dependants.add(self.t2)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.remove(self.t2)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)

    def test_remove_user_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # expect
        self.assertRaises(KeyError, self.t1.dependants.remove, self.t2)

    def test_discard_user(self):
        # given
        self.t1.dependants.add(self.t2)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.discard(self.t2)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)

    def test_discard_user_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # when
        self.t1.dependants.discard(self.t2)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)

    def test_add_task(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # when
        self.t2.dependees.add(self.t1)
        # then
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)

    def test_add_task_already_in_silently_ignored(self):
        # given
        self.t2.dependees.add(self.t1)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t2.dependees.add(self.t1)
        # then
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)

    def test_remove_task(self):
        # given
        self.t2.dependees.add(self.t1)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t2.dependees.remove(self.t1)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)

    def test_remove_task_not_already_in_raises(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # expect
        self.assertRaises(KeyError, self.t2.dependees.remove, self.t1)

    def test_discard_task(self):
        # given
        self.t2.dependees.add(self.t1)
        # precondition
        self.assertEqual(1, len(self.t1.dependants))
        self.assertEqual(1, len(self.t2.dependees))
        self.assertIn(self.t2, self.t1.dependants)
        self.assertIn(self.t1, self.t2.dependees)
        # when
        self.t2.dependees.discard(self.t1)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)

    def test_discard_task_not_already_in_silently_ignored(self):
        # precondition
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
        # when
        self.t2.dependees.discard(self.t1)
        # then
        self.assertEqual(0, len(self.t1.dependants))
        self.assertEqual(0, len(self.t2.dependees))
        self.assertNotIn(self.t2, self.t1.dependants)
        self.assertNotIn(self.t1, self.t2.dependees)
