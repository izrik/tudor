import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.in_memory.models.task import Task
from persistence.sqlalchemy.layer import RecordNotFound


class SetParentTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.t1 = Task(summary='t1')
        self.t2 = Task(summary='t2')
        self.t3 = Task(summary='t3')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.commit()

    def test_set_parent_to_task(self):
        self.pl.set_parent(self.t2.id, self.t1.id)
        self.assertEqual(self.t2.parent_id, self.t1.id)

    def test_set_parent_to_none_clears(self):
        self.pl.set_parent(self.t2.id, self.t1.id)
        self.pl.set_parent(self.t2.id, None)
        self.assertIsNone(self.t2.parent_id)

    def test_set_parent_unknown_task_raises(self):
        with self.assertRaises(RecordNotFound):
            self.pl.set_parent(999, self.t1.id)

    def test_set_parent_to_unknown_parent_raises(self):
        with self.assertRaises(RecordNotFound):
            self.pl.set_parent(self.t2.id, 999)
