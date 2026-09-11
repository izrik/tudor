import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.in_memory.models.task import Task


class FilterGraphTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.a = Task(summary='a')
        self.b = Task(summary='b')
        self.c = Task(summary='c')
        self.pl.add(self.a)
        self.pl.add(self.b)
        self.pl.add(self.c)
        self.pl.commit()
        # a depends on b (b is a dependee of a; a is a dependant of b)
        self.a.dependees.append(self.b)
        # c is prioritized before a (do c, then a)
        self.a.prioritize_before.append(self.c)

    def test_dependee_of_returns_tasks_x_depends_on(self):
        # X = a; X depends on b → result should contain b
        result = list(self.pl.get_tasks(dependee_of=self.a.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.b)

    def test_dependant_of_returns_tasks_that_depend_on_x(self):
        # X = b; a depends on b → result should contain a
        result = list(self.pl.get_tasks(dependant_of=self.b.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.a)

    def test_prioritized_before_returns_tasks_to_do_before_x(self):
        # X = a; c is prioritized before a → result should contain c
        result = list(self.pl.get_tasks(prioritized_before=self.a.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.c)

    def test_prioritized_after_returns_tasks_to_do_after_x(self):
        # X = c; c is prioritized before a → a is after c → result contains a
        result = list(self.pl.get_tasks(prioritized_after=self.c.id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.a)
