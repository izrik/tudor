import unittest

from models.task import Task
from tudor import generate_app, make_task_public, make_task_private


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.app.pl.create_all()

    def test_make_task_public(self):
        # given
        task = Task('task')
        task.id = 1
        self.app.pl.add(task)
        self.app.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertFalse(task.is_public)
        # when
        make_task_public(self.app, task.id, printer=printer)
        # then
        self.assertTrue(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", public'], output)

    def test_make_task_public_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.app.pl.count_tasks())
        # when
        make_task_public(self.app, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)

    def test_make_task_public_and_descendants(self):
        # given
        t1 = Task('t1', is_public=False)
        t1.id = 1
        self.app.pl.add(t1)
        t2 = Task('t2', is_public=False)
        t2.id = 2
        self.app.pl.add(t2)
        t2.parent = t1
        t3 = Task('t3', is_public=False)
        t3.id = 3
        self.app.pl.add(t3)
        t3.parent = t2
        t4 = Task('t4', is_public=False)
        t4.id = 4
        self.app.pl.add(t4)
        t4.parent = t1
        t5 = Task('t5', is_public=False)
        t5.id = 5
        self.app.pl.add(t5)
        self.app.pl.commit()
        output = set()

        def printer(*args):
            output.add(args[0])

        # precondition
        self.assertFalse(t1.is_public)
        self.assertFalse(t2.is_public)
        self.assertFalse(t3.is_public)
        self.assertFalse(t4.is_public)
        self.assertFalse(t5.is_public)
        # when
        make_task_public(self.app, t1.id, printer=printer, descendants=True)
        # then
        self.assertTrue(t1.is_public)
        self.assertTrue(t2.is_public)
        self.assertTrue(t3.is_public)
        self.assertTrue(t4.is_public)
        self.assertFalse(t5.is_public)
        # and
        self.assertEqual({'Made task 1, "t1", public',
                          'Made task 2, "t2", public',
                          'Made task 3, "t3", public',
                          'Made task 4, "t4", public'}, output)

    def test_make_task_private(self):
        # given
        task = Task('task', is_public=True)
        task.id = 1
        self.app.pl.add(task)
        self.app.pl.commit()
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertTrue(task.is_public)
        # when
        make_task_private(self.app, task.id, printer=printer)
        # then
        self.assertFalse(task.is_public)
        # and
        self.assertEqual(['Made task 1, "task", private'], output)

    def test_make_task_private_non_existent(self):
        # given
        output = [None]

        def printer(*args):
            output[0] = args[0]

        # precondition
        self.assertEqual(0, self.app.pl.count_tasks())
        # when
        make_task_private(self.app, 1, printer=printer)
        # then
        self.assertEqual(['No task found by the id "1"'], output)

    def test_make_task_private_and_descendants(self):
        # given
        t1 = Task('t1', is_public=True)
        t1.id = 1
        self.app.pl.add(t1)
        t2 = Task('t2', is_public=True)
        t2.id = 2
        self.app.pl.add(t2)
        t2.parent = t1
        t3 = Task('t3', is_public=True)
        t3.id = 3
        self.app.pl.add(t3)
        t3.parent = t2
        t4 = Task('t4', is_public=True)
        t4.id = 4
        self.app.pl.add(t4)
        t4.parent = t1
        t5 = Task('t5', is_public=True)
        t5.id = 5
        self.app.pl.add(t5)
        self.app.pl.commit()
        output = set()

        def printer(*args):
            output.add(args[0])

        # precondition
        self.assertTrue(t1.is_public)
        self.assertTrue(t2.is_public)
        self.assertTrue(t3.is_public)
        self.assertTrue(t4.is_public)
        self.assertTrue(t5.is_public)
        # when
        make_task_private(self.app, t1.id, printer=printer, descendants=True)
        # then
        self.assertFalse(t1.is_public)
        self.assertFalse(t2.is_public)
        self.assertFalse(t3.is_public)
        self.assertFalse(t4.is_public)
        self.assertTrue(t5.is_public)
        # and
        self.assertEqual({'Made task 1, "t1", private',
                          'Made task 2, "t2", private',
                          'Made task 3, "t3", private',
                          'Made task 4, "t4", private'}, output)
