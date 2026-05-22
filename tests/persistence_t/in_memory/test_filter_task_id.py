import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.in_memory.models.attachment import Attachment
from persistence.in_memory.models.comment import Comment
from persistence.in_memory.models.task import Task


class FilterByTaskIdTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()

        self.task1 = Task(summary='t1')
        self.task2 = Task(summary='t2')
        self.pl.add(self.task1)
        self.pl.add(self.task2)
        self.pl.commit()

        self.c1 = Comment(content='c1')
        self.c1.task = self.task1
        self.c2 = Comment(content='c2')
        self.c2.task = self.task1
        self.c3 = Comment(content='c3')
        self.c3.task = self.task2
        self.pl.add(self.c1)
        self.pl.add(self.c2)
        self.pl.add(self.c3)

        self.a1 = Attachment(path='/a1')
        self.a1.task = self.task1
        self.a2 = Attachment(path='/a2')
        self.a2.task = self.task2
        self.pl.add(self.a1)
        self.pl.add(self.a2)
        self.pl.commit()

    def test_get_comments_filtered_by_task_id(self):
        result = list(self.pl.get_comments(task_id=self.task1.id))
        self.assertEqual(len(result), 2)
        self.assertIn(self.c1, result)
        self.assertIn(self.c2, result)
        self.assertNotIn(self.c3, result)

    def test_get_comments_without_filter_returns_all(self):
        result = list(self.pl.get_comments())
        self.assertEqual(len(result), 3)

    def test_count_comments_filtered_by_task_id(self):
        self.assertEqual(self.pl.count_comments(task_id=self.task1.id), 2)
        self.assertEqual(self.pl.count_comments(task_id=self.task2.id), 1)

    def test_get_attachments_filtered_by_task_id(self):
        result = list(self.pl.get_attachments(task_id=self.task1.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.a1)

    def test_count_attachments_filtered_by_task_id(self):
        self.assertEqual(self.pl.count_attachments(task_id=self.task1.id), 1)
        self.assertEqual(self.pl.count_attachments(task_id=self.task2.id), 1)
