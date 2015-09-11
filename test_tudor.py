#!/usr/bin/env python

import unittest
import argparse
import logging
from tudor import generate_app


class DbLoaderTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.app = app
        self.task_ids = {}
        db = app.db
        db.create_all()
        Task = app.Task
        # summary,
        # description='',
        # is_done=False,
        # is_deleted=False,
        # deadline=None):

        normal = Task(summary='normal')
        db.session.add(normal)

        parent = Task(summary='parent')
        child = Task(summary='child')
        child.parent = parent
        db.session.add(parent)
        db.session.add(child)

        parent2 = Task(summary='parent2')
        child2 = Task(summary='child2')
        child2.parent = parent2
        child3 = Task(summary='child3')
        child3.parent = parent2
        grandchild = Task(summary='grandchild')
        grandchild.parent = child3
        great_grandchild = Task(summary='great_grandchild')
        great_grandchild.parent = grandchild
        great_great_grandchild = Task(summary='great_great_grandchild')
        great_great_grandchild.parent = great_grandchild
        db.session.add(parent2)
        db.session.add(child2)
        db.session.add(child3)
        db.session.add(grandchild)
        db.session.add(great_grandchild)
        db.session.add(great_great_grandchild)

        db.session.commit()

        for t in [normal, parent, child, parent2, child2, child3, grandchild,
                  great_grandchild, great_great_grandchild]:
            self.task_ids[t.summary] = t.id

    def test_loader_no_params(self):
        tasks = self.app.Task.load()
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        expected_summaries = {'normal', 'parent', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_single_root(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent']])
        self.assertEqual(1, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertEqual(self.task_ids['parent'], tasks[0].id)

    def test_loader_with_multiple_roots(self):
        roots = [self.task_ids['parent'], self.task_ids['parent2']]
        tasks = self.app.Task.load(roots=roots)
        self.assertEqual(2, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)

        ids = set(t.id for t in tasks)
        self.assertEqual(set(roots), ids)

    def test_loader_with_max_depth_1(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent2'], max_depth=1)

        # then
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'child3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_2(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent2'], max_depth=2)

        # then
        self.assertEqual(4, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_3(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent2'], max_depth=3)

        # then
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_4(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent2'], max_depth=4)

        # then
        self.assertEqual(6, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_None(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent2'],
                                   max_depth=None)

        # then
        self.assertEqual(6, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_None_2(self):

        # when
        tasks = self.app.Task.load(roots=self.task_ids['parent'],
                                   max_depth=None)

        # then
        self.assertEqual(2, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)

        expected_summaries = {'parent', 'child'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)


class DbLoaderDoneDeletedTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.app = app
        self.task_ids = {}
        db = app.db
        db.create_all()
        Task = app.Task

        normal = Task(summary='normal')
        db.session.add(normal)

        done = Task(summary='done')
        done.is_done = True
        db.session.add(done)

        parent1 = Task(summary='parent1')
        child1 = Task(summary='child1')
        child1.parent = parent1
        child1.is_done = True
        db.session.add(parent1)
        db.session.add(child1)

        parent2 = Task(summary='parent2')
        child2 = Task(summary='child2')
        child2.parent = parent2
        grandchild2 = Task(summary='grandchild2')
        grandchild2.parent = child2
        great_grandchild2 = Task(summary='great_grandchild2')
        great_grandchild2.is_done = True
        great_grandchild2.parent = grandchild2
        great_great_grandchild2 = Task(summary='great_great_grandchild2')
        great_great_grandchild2.parent = great_grandchild2
        db.session.add(parent2)
        db.session.add(child2)
        db.session.add(grandchild2)
        db.session.add(great_grandchild2)
        db.session.add(great_great_grandchild2)

        parent3 = Task(summary='parent3')
        parent3.is_done = True
        child3 = Task(summary='child3')
        child3.parent = parent3
        db.session.add(parent3)
        db.session.add(child3)

        db.session.commit()

        for t in [normal, done, parent1, child1, parent2, child2, grandchild2,
                  great_grandchild2, great_great_grandchild2, parent3, child3]:
            self.task_ids[t.summary] = t.id

    def test_loader_include_done_no_roots(self):
        tasks = self.app.Task.load(include_done=True)
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'normal', 'done', 'parent1', 'parent2',
                              'parent3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_dont_include_done_no_roots(self):
        tasks = self.app.Task.load(include_done=False)
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        expected_summaries = {'normal', 'parent1', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_stop_search(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent2']],
                                   max_depth=None)
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'grandchild2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_dont_stop_search_if_included(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent2']],
                                   max_depth=None,
                                   include_done=True)
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'parent2', 'child2', 'grandchild2',
                              'great_grandchild2', 'great_great_grandchild2'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-log', action='store_true',
                        help='Print the log.')
    args = parser.parse_args()

    if args.print_log:
        logging.basicConfig(level=logging.DEBUG,
                            format=('%(asctime)s %(levelname)s:%(name)s:'
                                    '%(funcName)s:'
                                    '%(filename)s(%(lineno)d):'
                                    '%(threadName)s(%(thread)d):%(message)s'))

    unittest.main(argv=[''])

if __name__ == '__main__':
    run()
