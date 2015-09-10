#!/usr/bin/env python

import unittest
import argparse
import logging
from tudor import generate_app


class DbLoaderTest(unittest.TestCase):

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.app = app
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
        db.session.commit()

        self.parent_id = parent.id

    def test_loader_no_params(self):
        tasks = self.app.Task.load()
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

    def test_loader_with_roots(self):
        all_tasks = self.app.Task.load()
        tasks = self.app.Task.load(roots=[self.parent_id])
        self.assertEqual(1, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertEqual(self.parent_id, tasks[0].id)


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
