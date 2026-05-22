import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User


class FilterNMTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.t1 = Task(summary='t1')
        self.t2 = Task(summary='t2')
        self.tag1 = Tag(value='red')
        self.tag2 = Tag(value='blue')
        self.u1 = User(email='a@b')
        self.u2 = User(email='c@d')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)
        self.pl.add(self.u1)
        self.pl.add(self.u2)
        self.pl.commit()

        self.t1.tags.append(self.tag1)
        self.t2.tags.append(self.tag2)
        self.t1.users.append(self.u1)
        self.t2.users.append(self.u2)

    def test_get_tasks_filtered_by_tag_id(self):
        result = list(self.pl.get_tasks(tag_id=self.tag1.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.t1)

    def test_get_tasks_filtered_by_user_id(self):
        result = list(self.pl.get_tasks(user_id=self.u2.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.t2)

    def test_get_tags_filtered_by_task_id(self):
        result = list(self.pl.get_tags(task_id=self.t1.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.tag1)

    def test_get_users_filtered_by_task_id(self):
        result = list(self.pl.get_users(task_id=self.t2.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.u2)
