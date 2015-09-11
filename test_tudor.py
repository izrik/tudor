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
        db.session.add(parent2)
        db.session.add(child2)
        db.session.add(child3)
        db.session.add(grandchild)

        db.session.commit()

        for t in [normal, parent, child, parent2, child2, child3, grandchild]:
            self.task_ids[t.summary] = t.id

    def test_loader_no_params(self):
        tasks = self.app.Task.load()
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        ids = [self.task_ids['normal'], self.task_ids['parent'],
               self.task_ids['parent2']]
        self.assertIn(tasks[0].id, ids)
        self.assertIn(tasks[1].id, ids)
        self.assertIn(tasks[2].id, ids)
        self.assertNotEqual(tasks[0].id, tasks[1].id)
        self.assertNotEqual(tasks[0].id, tasks[2].id)
        self.assertNotEqual(tasks[1].id, tasks[2].id)

    def test_loader_with_single_root(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent']])
        self.assertEqual(1, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertEqual(self.task_ids['parent'], tasks[0].id)

    def test_loader_with_multiple_roots(self):
        roots = [self.task_ids['parent'],self.task_ids['parent2']]
        tasks = self.app.Task.load(roots=roots)
        self.assertEqual(2, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)

        self.assertIn(tasks[0].id, roots)
        self.assertIn(tasks[1].id, roots)
        self.assertNotEqual(tasks[0].id, tasks[1].id)


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
