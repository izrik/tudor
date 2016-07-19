#!/usr/bin/env python

import unittest
import argparse
import logging
from tudor import generate_app, bool_from_str, int_from_str, str_from_datetime
from tudor import money_from_str
from datetime import datetime


class DbLoaderTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.app = app
        self.task_ids = {}
        db = app.ds.db
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
        db = app.ds.db
        db.create_all()
        Task = app.Task

        normal = Task(summary='normal')
        db.session.add(normal)

        done = Task(summary='done')
        done.is_done = True
        db.session.add(done)

        deleted = Task(summary='deleted')
        deleted.is_deleted = True
        db.session.add(deleted)

        done_and_deleted = Task(summary='done_and_deleted')
        done_and_deleted.is_done = True
        done_and_deleted.is_deleted = True
        db.session.add(done_and_deleted)

        parent1 = Task(summary='parent1')
        child1 = Task(summary='child1')
        child1.parent = parent1
        child1.is_done = True
        db.session.add(parent1)
        db.session.add(child1)

        parent2 = Task(summary='parent2')
        parent2.is_done = True
        child2 = Task(summary='child2')
        child2.parent = parent2
        db.session.add(parent2)
        db.session.add(child2)

        parent3 = Task(summary='parent3')
        child3 = Task(summary='child3')
        child3.parent = parent3
        grandchild3 = Task(summary='grandchild3')
        grandchild3.parent = child3
        great_grandchild3 = Task(summary='great_grandchild3')
        great_grandchild3.is_done = True
        great_grandchild3.parent = grandchild3
        great_great_grandchild3 = Task(summary='great_great_grandchild3')
        great_great_grandchild3.parent = great_grandchild3
        db.session.add(parent3)
        db.session.add(child3)
        db.session.add(grandchild3)
        db.session.add(great_grandchild3)
        db.session.add(great_great_grandchild3)

        parent4 = Task(summary='parent4')
        child4 = Task(summary='child4')
        child4.parent = parent4
        grandchild4 = Task(summary='grandchild4')
        grandchild4.parent = child4
        great_grandchild4 = Task(summary='great_grandchild4')
        great_grandchild4.is_deleted = True
        great_grandchild4.parent = grandchild4
        great_great_grandchild4 = Task(summary='great_great_grandchild4')
        great_great_grandchild4.parent = great_grandchild4
        db.session.add(parent4)
        db.session.add(child4)
        db.session.add(grandchild4)
        db.session.add(great_grandchild4)
        db.session.add(great_great_grandchild4)

        parent5 = Task(summary='parent5')
        child5 = Task(summary='child5')
        child5.parent = parent5
        grandchild5 = Task(summary='grandchild5')
        grandchild5.parent = child5
        great_grandchild5 = Task(summary='great_grandchild5')
        great_grandchild5.is_done = True
        great_grandchild5.id_deleted = True
        great_grandchild5.parent = grandchild5
        great_great_grandchild5 = Task(summary='great_great_grandchild5')
        great_great_grandchild5.parent = great_grandchild5
        db.session.add(parent5)
        db.session.add(child5)
        db.session.add(grandchild5)
        db.session.add(great_grandchild5)
        db.session.add(great_great_grandchild5)

        parent6 = Task(summary='parent6')
        parent6.is_deleted = True
        child6 = Task(summary='child6')
        child6.parent = parent6
        db.session.add(parent6)
        db.session.add(child6)

        db.session.commit()

        for t in [normal, done, deleted, done_and_deleted,

                  parent1, child1,

                  parent2, child2,

                  parent3, child3, grandchild3, great_grandchild3,
                  great_great_grandchild3,

                  parent4, child4, grandchild4, great_grandchild4,
                  great_great_grandchild4,

                  parent5, child5, grandchild5, great_grandchild5,
                  great_great_grandchild5,

                  parent6, child6]:

            self.task_ids[t.summary] = t.id

    def test_loader_do_not_include_no_roots(self):
        tasks = self.app.Task.load()
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'normal', 'parent1',
                              'parent3', 'parent4', 'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_done_no_roots(self):
        tasks = self.app.Task.load(include_done=True)
        self.assertEqual(7, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)
        self.assertIsInstance(tasks[6], self.app.Task)

        expected_summaries = {'normal', 'done', 'parent1', 'parent2',
                              'parent3', 'parent4', 'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_dont_include_done_no_roots(self):
        tasks = self.app.Task.load(include_done=False)
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'normal', 'parent1', 'parent3', 'parent4',
                              'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_stop_search(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent3']],
                                   max_depth=None)
        self.assertEqual(3, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_dont_stop_search_if_included(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent3']],
                                   max_depth=None,
                                   include_done=True)
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'great_grandchild3', 'great_great_grandchild3'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_deleted_no_roots(self):
        tasks = self.app.Task.load(include_deleted=True)
        self.assertEqual(7, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)
        self.assertIsInstance(tasks[6], self.app.Task)

        expected_summaries = {'normal', 'deleted', 'parent1',
                              'parent3', 'parent4', 'parent5', 'parent6'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_do_not_include_deleted_no_roots(self):
        tasks = self.app.Task.load(include_deleted=False)
        self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'normal', 'parent1', 'parent3', 'parent4',
                              'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_done_and_deleted_no_roots(self):
        tasks = self.app.Task.load(include_done=True, include_deleted=True)
        self.assertEqual(10, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)
        self.assertIsInstance(tasks[6], self.app.Task)
        self.assertIsInstance(tasks[7], self.app.Task)
        self.assertIsInstance(tasks[8], self.app.Task)
        self.assertIsInstance(tasks[9], self.app.Task)

        expected_summaries = {'normal', 'done', 'deleted', 'done_and_deleted',
                              'parent1', 'parent2', 'parent3', 'parent4',
                              'parent5', 'parent6'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_deleted_children_stop_search(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent3'],
                                          self.task_ids['parent4'],
                                          self.task_ids['parent5']],
                                   max_depth=None)
        self.assertEqual(9, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)
        self.assertIsInstance(tasks[5], self.app.Task)
        self.assertIsInstance(tasks[6], self.app.Task)
        self.assertIsInstance(tasks[7], self.app.Task)
        self.assertIsInstance(tasks[8], self.app.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'parent4', 'child4', 'grandchild4',
                              'parent5', 'child5', 'grandchild5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_deleted_children_do_not_stop_search_if_included(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent3'],
                                          self.task_ids['parent4'],
                                          self.task_ids['parent5']],
                                   max_depth=None,
                                   include_deleted=True)
        # self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'parent4', 'child4', 'grandchild4',
                              'great_grandchild4', 'great_great_grandchild4',
                              'parent5', 'child5', 'grandchild5'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

    def test_done_and_deleted_children_do_not_stop_search_if_included(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent3'],
                                          self.task_ids['parent4'],
                                          self.task_ids['parent5']],
                                   max_depth=None,
                                   include_done=True,
                                   include_deleted=True)
        # self.assertEqual(5, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)
        self.assertIsInstance(tasks[4], self.app.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'great_grandchild3', 'great_great_grandchild3',
                              'parent4', 'child4', 'grandchild4',
                              'great_grandchild4', 'great_great_grandchild4',
                              'parent5', 'child5', 'grandchild5',
                              'great_grandchild5', 'great_great_grandchild5'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)


class DbLoaderDeadlinedTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        app = generate_app(db_uri='sqlite://')
        self.app = app
        self.task_ids = {}
        db = app.ds.db
        db.create_all()
        Task = app.Task

        no_deadline = Task(summary='no_deadline')
        db.session.add(no_deadline)

        with_deadline = Task(summary='with_deadline', deadline='2015-10-05')
        db.session.add(with_deadline)

        parent1 = Task(summary='parent1')
        child1 = Task(summary='child1')
        child1.parent = parent1
        grandchild1 = Task(summary='grandchild1')
        grandchild1.parent = child1
        great_grandchild1 = Task(summary='great_grandchild1',
                                 deadline='2015-10-05')
        great_grandchild1.parent = grandchild1
        great_great_grandchild1 = Task(summary='great_great_grandchild1')
        great_great_grandchild1.parent = great_grandchild1
        db.session.add(parent1)
        db.session.add(child1)
        db.session.add(grandchild1)
        db.session.add(great_grandchild1)
        db.session.add(great_great_grandchild1)

        parent2 = Task(summary='parent2', deadline='2015-10-05')
        child2 = Task(summary='child2', deadline='2015-10-05')
        child2.parent = parent2
        grandchild2 = Task(summary='grandchild2', deadline='2015-10-05')
        grandchild2.parent = child2
        great_grandchild2 = Task(summary='great_grandchild2')
        great_grandchild2.parent = grandchild2
        great_great_grandchild2 = Task(summary='great_great_grandchild2',
                                       deadline='2015-10-05')
        great_great_grandchild2.parent = great_grandchild2
        db.session.add(parent2)
        db.session.add(child2)
        db.session.add(grandchild2)
        db.session.add(great_grandchild2)
        db.session.add(great_great_grandchild2)

        db.session.commit()

        for t in [no_deadline, with_deadline,

                  parent1, child1, grandchild1, great_grandchild1,
                  great_great_grandchild1,

                  parent2, child2, grandchild2, great_grandchild2,
                  great_great_grandchild2]:

            self.task_ids[t.summary] = t.id

    def test_loader_do_not_exclude_no_roots(self):
        tasks = self.app.Task.load()
        self.assertEqual(4, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)

        expected_summaries = {'no_deadline', 'with_deadline', 'parent1',
                              'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_explicit_do_not_exclude_no_roots(self):
        tasks = self.app.Task.load(exclude_undeadlined=False)
        self.assertEqual(4, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)
        self.assertIsInstance(tasks[2], self.app.Task)
        self.assertIsInstance(tasks[3], self.app.Task)

        expected_summaries = {'no_deadline', 'with_deadline', 'parent1',
                              'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_exclude_undeadlined_no_roots(self):
        tasks = self.app.Task.load(exclude_undeadlined=True)
        self.assertEqual(2, len(tasks))
        self.assertIsInstance(tasks[0], self.app.Task)
        self.assertIsInstance(tasks[1], self.app.Task)

        expected_summaries = {'with_deadline', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_undeadlined_do_not_stop_search_if_not_excluded(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent1'],
                                          self.task_ids['parent2']],
                                   max_depth=None)
        self.assertEqual(10, len(tasks))
        self.assertTrue(all(isinstance(t, self.app.Task) for t in tasks))

        expected_summaries = {'parent1', 'child1', 'grandchild1',
                              'great_grandchild1', 'great_great_grandchild1',
                              'parent2', 'child2', 'grandchild2',
                              'great_grandchild2', 'great_great_grandchild2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_undeadlined_stop_search_if_excluded(self):
        tasks = self.app.Task.load(roots=[self.task_ids['parent1'],
                                          self.task_ids['parent2']],
                                   max_depth=None,
                                   exclude_undeadlined=True)
        self.assertEqual(3, len(tasks))
        self.assertTrue(all(isinstance(t, self.app.Task) for t in tasks))

        expected_summaries = {'parent2', 'child2', 'grandchild2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)


class ConvertTaskToTagTest(unittest.TestCase):

    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.ds = self.app.ds
        self.db = self.ds.db
        self.db.create_all()
        self.Task = self.app.Task
        self.Tag = self.app.Tag
        self.TaskTagLink = self.app.TaskTagLink

    def test_old_task_becomes_a_tag(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)
        self.db.session.commit()

        self.assertEquals(0, self.Tag.query.count())

        # when
        tag = self.app._convert_task_to_tag(task.id)

        # then
        self.assertIsNotNone(tag)
        self.assertEquals(1, self.Tag.query.count())
        self.assertIs(tag, self.Tag.query.first())

    def test_old_task_gets_deleted(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)
        self.db.session.commit()

        self.assertEquals(1, self.Task.query.count())

        # when
        tag = self.app._convert_task_to_tag(task.id)

        # then
        self.assertEquals(0, self.Task.query.count())

    def test_child_tasks_get_the_new_tag(self):
        # given
        task = self.Task('some_task')
        self.db.session.add(task)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(4, self.Task.query.count())
        self.assertEquals(0, child1.tags.count())
        self.assertEquals(0, child2.tags.count())
        self.assertEquals(0, child3.tags.count())

        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id)

        # then
        self.assertEquals(3, self.Task.query.count())
        self.assertEquals(1, child1.tags.count())
        self.assertEquals(1, child2.tags.count())
        self.assertEquals(1, child3.tags.count())

        self.assertIsNone(child1.parent)
        self.assertIsNone(child2.parent)
        self.assertIsNone(child3.parent)

    def test_child_tasks_get_the_old_tasks_tags(self):
        # given

        tag1 = self.Tag('tag1')
        self.db.session.add(tag1)

        task = self.Task('some_task')
        self.db.session.add(task)

        self.db.session.commit()

        ttl = self.TaskTagLink(task.id, tag1.id)
        self.db.session.add(ttl)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(1, tag1.tasks.count())
        self.assertEquals(0, child1.tags.count())
        self.assertEquals(0, child2.tags.count())
        self.assertEquals(0, child3.tags.count())

        # when
        tag = self.app._convert_task_to_tag(task.id)

        # then
        self.assertEquals(3, tag1.tasks.count())
        self.assertEquals(2, child1.tags.count())
        self.assertEquals(2, child2.tags.count())
        self.assertEquals(2, child3.tags.count())

    def test_children_of_old_task_become_children_of_old_tasks_parent(self):
        # given

        grand_parent = self.Task('grand_parent')
        self.db.session.add(grand_parent)

        task = self.Task('some_task')
        task.parent = grand_parent
        self.db.session.add(task)

        child1 = self.Task('child1')
        child1.parent = task
        self.db.session.add(child1)
        child2 = self.Task('child2')
        child2.parent = task
        self.db.session.add(child2)
        child3 = self.Task('child3')
        child3.parent = task
        self.db.session.add(child3)

        self.db.session.commit()

        self.assertEquals(1, grand_parent.children.count())
        self.assertIs(task, child1.parent)
        self.assertIs(task, child2.parent)
        self.assertIs(task, child3.parent)

        # when
        tag = self.app._convert_task_to_tag(task.id)

        # then
        self.assertEquals(3, grand_parent.children.count())
        self.assertIs(grand_parent, child1.parent)
        self.assertIs(grand_parent, child2.parent)
        self.assertIs(grand_parent, child3.parent)


class TypeConversionFunctionTest(unittest.TestCase):
    def test_bool_from_str(self):
        # true, unsurprising
        self.assertTrue(bool_from_str('True'))
        self.assertTrue(bool_from_str('true'))
        self.assertTrue(bool_from_str('tRuE'))
        self.assertTrue(bool_from_str('t'))
        self.assertTrue(bool_from_str('1'))
        self.assertTrue(bool_from_str('y'))

        # true, surprising
        self.assertTrue(bool_from_str('tr'))
        self.assertTrue(bool_from_str('tru'))
        self.assertTrue(bool_from_str('truee'))
        self.assertTrue(bool_from_str('ye'))
        self.assertTrue(bool_from_str('yes'))

        # false, unsurprising
        self.assertFalse(bool_from_str('False'))
        self.assertFalse(bool_from_str('false'))
        self.assertFalse(bool_from_str('fAlSe'))
        self.assertFalse(bool_from_str('f'))
        self.assertFalse(bool_from_str('0'))
        self.assertFalse(bool_from_str('n'))

        # false, surprising
        self.assertTrue(bool_from_str('no'))
        self.assertTrue(bool_from_str('fa'))
        self.assertTrue(bool_from_str('fal'))
        self.assertTrue(bool_from_str('fals'))
        self.assertTrue(bool_from_str('falsee'))

        # true, non-string, somewhat surprising
        self.assertTrue(bool_from_str(1))
        self.assertTrue(bool_from_str([1]))
        self.assertTrue(bool_from_str([False]))

        # false, non-string
        self.assertFalse(bool_from_str([]))
        self.assertFalse(bool_from_str(''))
        self.assertFalse(bool_from_str(None))

    def test_int_from_str(self):
        self.assertEquals(1, int_from_str('1'))
        self.assertEquals(123, int_from_str('123'))
        self.assertEquals(-123, int_from_str('-123'))
        self.assertIsNone(int_from_str(None))
        self.assertIsNone(int_from_str(''))
        self.assertIsNone(int_from_str([]))
        self.assertIsNone(int_from_str([1]))
        self.assertEquals(1, int_from_str(True))

    def test_str_from_datetime(self):
        self.assertIsNone(None, str_from_datetime(None))
        self.assertEquals('2016-02-03 00:00:00',
                          str_from_datetime(datetime(2016, 2, 3)))
        self.assertEquals('2016-02-03 12:34:56',
                          str_from_datetime(datetime(2016, 2, 3, 12, 34, 56)))

        self.assertEquals('2016-02-03', str_from_datetime('2016-02-03'))
        self.assertEquals('abcdefgh', str_from_datetime('abcdefgh'))

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
