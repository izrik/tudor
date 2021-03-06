#!/usr/bin/env python

import unittest

from models.object_types import ObjectTypes
from tests.logic_t.layer.LogicLayer.util import generate_ll


class DbLoaderTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        self.ll = generate_ll()
        self.task_ids = {}
        self.pl = self.ll.pl
        pl = self.pl
        # summary,
        # description='',
        # is_done=False,
        # is_deleted=False,
        # deadline=None):

        self.user = self.pl.create_user('name@example.org', None, True)
        pl.add(self.user)

        normal = self.pl.create_task(summary='normal')
        pl.add(normal)

        parent = self.pl.create_task(summary='parent')
        child = self.pl.create_task(summary='child')
        child.parent = parent
        pl.add(parent)
        pl.add(child)

        parent2 = self.pl.create_task(summary='parent2')
        child2 = self.pl.create_task(summary='child2')
        child2.parent = parent2
        child3 = self.pl.create_task(summary='child3')
        child3.parent = parent2
        grandchild = self.pl.create_task(summary='grandchild')
        grandchild.parent = child3
        great_grandchild = self.pl.create_task(summary='great_grandchild')
        great_grandchild.parent = grandchild
        great_great_grandchild = self.pl.create_task(summary='great_great_grandchild')
        great_great_grandchild.parent = great_grandchild
        pl.add(parent2)
        pl.add(child2)
        pl.add(child3)
        pl.add(grandchild)
        pl.add(great_grandchild)
        pl.add(great_great_grandchild)

        pl.commit()

        for t in [normal, parent, child, parent2, child2, child3, grandchild,
                  great_grandchild, great_great_grandchild]:
            self.task_ids[t.summary] = t.id

    def test_loader_no_params(self):
        tasks = self.ll.load(self.user)
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_single_root(self):
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent'])
        self.assertEqual(1, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(self.task_ids['parent'], tasks[0].id)

    def test_loader_with_max_depth_1(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=1)

        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent2', 'child2', 'child3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_2(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=2)

        # then
        self.assertEqual(4, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_3(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=3)

        # then
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_4(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=4)

        # then
        self.assertEqual(6, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_None(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=None)

        # then
        self.assertEqual(6, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)

        expected_summaries = {'parent2', 'child2', 'child3', 'grandchild',
                              'great_grandchild', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_with_max_depth_None_2(self):

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent'],
                             max_depth=None)

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'parent', 'child'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)


class DbLoaderDoneDeletedTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        pl = self.pl
        self.task_ids = {}

        self.user = self.pl.create_user('name@example.org', None, True)
        pl.add(self.user)

        normal = self.pl.create_task(summary='normal')
        pl.add(normal)

        done = self.pl.create_task(summary='done')
        done.is_done = True
        pl.add(done)

        deleted = self.pl.create_task(summary='deleted')
        deleted.is_deleted = True
        pl.add(deleted)

        done_and_deleted = self.pl.create_task(summary='done_and_deleted')
        done_and_deleted.is_done = True
        done_and_deleted.is_deleted = True
        pl.add(done_and_deleted)

        parent1 = self.pl.create_task(summary='parent1')
        child1 = self.pl.create_task(summary='child1')
        child1.parent = parent1
        child1.is_done = True
        pl.add(parent1)
        pl.add(child1)

        parent2 = self.pl.create_task(summary='parent2')
        parent2.is_done = True
        child2 = self.pl.create_task(summary='child2')
        child2.parent = parent2
        pl.add(parent2)
        pl.add(child2)

        parent3 = self.pl.create_task(summary='parent3')
        child3 = self.pl.create_task(summary='child3')
        child3.parent = parent3
        grandchild3 = self.pl.create_task(summary='grandchild3')
        grandchild3.parent = child3
        great_grandchild3 = self.pl.create_task(summary='great_grandchild3')
        great_grandchild3.is_done = True
        great_grandchild3.parent = grandchild3
        great_great_grandchild3 = self.pl.create_task(summary='great_great_grandchild3')
        great_great_grandchild3.parent = great_grandchild3
        pl.add(parent3)
        pl.add(child3)
        pl.add(grandchild3)
        pl.add(great_grandchild3)
        pl.add(great_great_grandchild3)

        parent4 = self.pl.create_task(summary='parent4')
        child4 = self.pl.create_task(summary='child4')
        child4.parent = parent4
        grandchild4 = self.pl.create_task(summary='grandchild4')
        grandchild4.parent = child4
        great_grandchild4 = self.pl.create_task(summary='great_grandchild4')
        great_grandchild4.is_deleted = True
        great_grandchild4.parent = grandchild4
        great_great_grandchild4 = self.pl.create_task(summary='great_great_grandchild4')
        great_great_grandchild4.parent = great_grandchild4
        pl.add(parent4)
        pl.add(child4)
        pl.add(grandchild4)
        pl.add(great_grandchild4)
        pl.add(great_great_grandchild4)

        parent5 = self.pl.create_task(summary='parent5')
        child5 = self.pl.create_task(summary='child5')
        child5.parent = parent5
        grandchild5 = self.pl.create_task(summary='grandchild5')
        grandchild5.parent = child5
        great_grandchild5 = self.pl.create_task(summary='great_grandchild5')
        great_grandchild5.is_done = True
        great_grandchild5.id_deleted = True
        great_grandchild5.parent = grandchild5
        great_great_grandchild5 = self.pl.create_task(summary='great_great_grandchild5')
        great_great_grandchild5.parent = great_grandchild5
        pl.add(parent5)
        pl.add(child5)
        pl.add(grandchild5)
        pl.add(great_grandchild5)
        pl.add(great_great_grandchild5)

        parent6 = self.pl.create_task(summary='parent6')
        parent6.is_deleted = True
        child6 = self.pl.create_task(summary='child6')
        child6.parent = parent6
        pl.add(parent6)
        pl.add(child6)

        pl.commit()

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
        tasks = self.ll.load(self.user)
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent1',
                              'parent3', 'parent4', 'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_done_no_roots(self):
        tasks = self.ll.load(self.user, include_done=True)
        self.assertEqual(7, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'done', 'parent1', 'parent2',
                              'parent3', 'parent4', 'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_dont_include_done_no_roots(self):
        tasks = self.ll.load(self.user, include_done=False)
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent1', 'parent3', 'parent4',
                              'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_stop_search(self):
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent3'],
                             max_depth=None)
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_done_children_dont_stop_search_if_included(self):
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent3'],
                             max_depth=None, include_done=True)
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'great_grandchild3', 'great_great_grandchild3'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_deleted_no_roots(self):
        tasks = self.ll.load(self.user, include_deleted=True)
        self.assertEqual(7, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'deleted', 'parent1',
                              'parent3', 'parent4', 'parent5', 'parent6'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_do_not_include_deleted_no_roots(self):
        tasks = self.ll.load(self.user, include_deleted=False)
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent1', 'parent3', 'parent4',
                              'parent5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_include_done_and_deleted_no_roots(self):
        tasks = self.ll.load(self.user, include_done=True,
                             include_deleted=True)
        self.assertEqual(10, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[7].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[8].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[9].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'done', 'deleted', 'done_and_deleted',
                              'parent1', 'parent2', 'parent3', 'parent4',
                              'parent5', 'parent6'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_deleted_children_stop_search(self):
        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent3'],
                             max_depth=None)
        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent4'],
                             max_depth=None)
        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent4', 'child4', 'grandchild4'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent5'],
                             max_depth=None)
        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent5', 'child5', 'grandchild5'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_deleted_children_do_not_stop_search_if_included(self):
        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent3'],
                             max_depth=None, include_deleted=True)
        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent4'],
                             max_depth=None, include_deleted=True)
        # then
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent4', 'child4', 'grandchild4',
                              'great_grandchild4', 'great_great_grandchild4'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent5'],
                             max_depth=None, include_deleted=True)
        # then
        self.assertEqual(3, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)

        expected_summaries = {'parent5', 'child5', 'grandchild5'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

    def test_done_and_deleted_children_do_not_stop_search_if_included(self):
        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent3'],
                             max_depth=None, include_done=True,
                             include_deleted=True)
        # then
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent3', 'child3', 'grandchild3',
                              'great_grandchild3', 'great_great_grandchild3'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent4'],
                             max_depth=None, include_done=True,
                             include_deleted=True)
        # then
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent4', 'child4', 'grandchild4',
                              'great_grandchild4', 'great_great_grandchild4'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent5'],
                             max_depth=None, include_done=True,
                             include_deleted=True)
        # then
        self.assertEqual(5, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)

        expected_summaries = {'parent5', 'child5', 'grandchild5',
                              'great_grandchild5', 'great_great_grandchild5'}
        summaries = set((t.summary for t in tasks))
        self.assertEqual(expected_summaries, summaries)


class DbLoaderDeadlinedTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        pl = self.pl
        self.task_ids = {}

        self.user = self.pl.create_user('name@example.org', None, True)
        pl.add(self.user)

        no_deadline = self.pl.create_task(summary='no_deadline')
        pl.add(no_deadline)

        with_deadline = self.pl.create_task(summary='with_deadline', deadline='2015-10-05')
        pl.add(with_deadline)

        parent1 = self.pl.create_task(summary='parent1')
        child1 = self.pl.create_task(summary='child1')
        child1.parent = parent1
        grandchild1 = self.pl.create_task(summary='grandchild1')
        grandchild1.parent = child1
        great_grandchild1 = self.pl.create_task(summary='great_grandchild1',
                                 deadline='2015-10-05')
        great_grandchild1.parent = grandchild1
        great_great_grandchild1 = self.pl.create_task(summary='great_great_grandchild1')
        great_great_grandchild1.parent = great_grandchild1
        pl.add(parent1)
        pl.add(child1)
        pl.add(grandchild1)
        pl.add(great_grandchild1)
        pl.add(great_great_grandchild1)

        parent2 = self.pl.create_task(summary='parent2', deadline='2015-10-05')
        child2 = self.pl.create_task(summary='child2', deadline='2015-10-05')
        child2.parent = parent2
        grandchild2 = self.pl.create_task(summary='grandchild2', deadline='2015-10-05')
        grandchild2.parent = child2
        great_grandchild2 = self.pl.create_task(summary='great_grandchild2')
        great_grandchild2.parent = grandchild2
        great_great_grandchild2 = self.pl.create_task(summary='great_great_grandchild2',
                                       deadline='2015-10-05')
        great_great_grandchild2.parent = great_grandchild2
        pl.add(parent2)
        pl.add(child2)
        pl.add(grandchild2)
        pl.add(great_grandchild2)
        pl.add(great_great_grandchild2)

        pl.commit()

        for t in [no_deadline, with_deadline,

                  parent1, child1, grandchild1, great_grandchild1,
                  great_great_grandchild1,

                  parent2, child2, grandchild2, great_grandchild2,
                  great_great_grandchild2]:

            self.task_ids[t.summary] = t.id

    def test_loader_do_not_exclude_no_roots(self):
        tasks = self.ll.load(self.user)
        self.assertEqual(4, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)

        expected_summaries = {'no_deadline', 'with_deadline', 'parent1',
                              'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_explicit_do_not_exclude_no_roots(self):
        tasks = self.ll.load(self.user, exclude_undeadlined=False)
        self.assertEqual(4, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)

        expected_summaries = {'no_deadline', 'with_deadline', 'parent1',
                              'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_exclude_undeadlined_no_roots(self):
        tasks = self.ll.load(self.user, exclude_undeadlined=True)
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'with_deadline', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_undeadlined_do_not_stop_search_if_not_excluded(self):
        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent1'],
                             max_depth=None)
        # then
        self.assertEqual(5, len(tasks))
        self.assertTrue(all(t.object_type == ObjectTypes.Task for t in tasks))

        expected_summaries = {'parent1', 'child1', 'grandchild1',
                              'great_grandchild1', 'great_great_grandchild1'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=None)
        # then
        self.assertEqual(5, len(tasks))
        self.assertTrue(all(t.object_type == ObjectTypes.Task for t in tasks))

        expected_summaries = {'parent2', 'child2', 'grandchild2',
                              'great_grandchild2', 'great_great_grandchild2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_loader_undeadlined_stop_search_if_excluded(self):
        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent1'],
                             max_depth=None, exclude_undeadlined=True)
        # then
        self.assertEqual(0, len(tasks))

        # when
        tasks = self.ll.load(self.user, root_task_id=self.task_ids['parent2'],
                             max_depth=None, exclude_undeadlined=True)
        # then
        self.assertEqual(3, len(tasks))
        self.assertTrue(all(t.object_type == ObjectTypes.Task for t in tasks))

        expected_summaries = {'parent2', 'child2', 'grandchild2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)


class DbLoadNoHierarchyTest(unittest.TestCase):

    task_ids = None

    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        pl = self.pl
        self.task_ids = {}

        self.user = self.pl.create_user('name@example.org', None, True)
        pl.add(self.user)

        self.abcd = abcd = self.pl.create_tag('abcd')
        self.efgh = efgh = self.pl.create_tag('efgh')
        self.ijkl = ijkl = self.pl.create_tag('ijkl')

        pl.add(abcd)
        pl.add(efgh)
        pl.add(ijkl)

        self.normal = normal = self.pl.create_task(summary='normal')
        pl.add(normal)

        self.parent = parent = self.pl.create_task(summary='parent')
        self.child = child = self.pl.create_task(summary='child')
        child.parent = parent
        pl.add(parent)
        pl.add(child)

        self.parent2 = parent2 = self.pl.create_task(summary='parent2')
        self.child2 = child2 = self.pl.create_task(summary='child2', is_done=True,
                                    deadline='2016-01-01')
        child2.parent = parent2
        self.child3 = child3 = self.pl.create_task(summary='child3', is_deleted=True)
        child3.parent = parent2
        self.grandchild = grandchild = self.pl.create_task(summary='grandchild')
        grandchild.parent = child3
        self.great_grandchild = great_grandchild = self.pl.create_task(
            summary='great_grandchild', deadline='2016-12-31')
        great_grandchild.parent = grandchild
        self.great_great_grandchild = great_great_grandchild = self.pl.create_task(
            summary='great_great_grandchild')
        great_great_grandchild.parent = great_grandchild
        pl.add(parent2)
        pl.add(child2)
        pl.add(child3)
        pl.add(grandchild)
        pl.add(great_grandchild)
        pl.add(great_great_grandchild)

        normal.tags.append(abcd)
        normal.tags.append(efgh)
        normal.tags.append(ijkl)
        parent.tags.append(ijkl)
        parent2.tags.append(efgh)
        great_great_grandchild.tags.append(abcd)

        pl.commit()

        for t in [normal, parent, child, parent2, child2, child3, grandchild,
                  great_grandchild, great_great_grandchild]:
            self.task_ids[t.summary] = t.id

    def test_no_params_yields_all(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user)

        # then
        self.assertEqual(7, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent', 'child', 'parent2',
                              'grandchild', 'great_grandchild',
                              'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_include_done_includes_done(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True)

        # then
        self.assertEqual(8, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[7].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent', 'child', 'parent2', 'child2',
                              'grandchild', 'great_grandchild',
                              'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_include_deleted_includes_deleted(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_deleted=True)

        # then
        self.assertEqual(8, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[7].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent', 'child', 'parent2', 'child3',
                              'grandchild', 'great_grandchild',
                              'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_include_both_includes_both(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True)

        # then
        self.assertEqual(9, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[2].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[3].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[4].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[5].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[6].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[7].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[8].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent', 'child', 'parent2', 'child2',
                              'child3', 'grandchild', 'great_grandchild',
                              'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_exclude_undeadlined_only_returns_tasks_with_deadlines(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, exclude_undeadlined=True)

        # then
        self.assertEqual(1, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual('great_grandchild', tasks[0].summary)

    def test_exclude_undeadlined_only_returns_tasks_with_deadlines2(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True,
                                          exclude_undeadlined=True)

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'child2', 'great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_single_tag_returns_only_tasks_with_that_tag_1(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True,
                                          tag='abcd')

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_single_tag_returns_only_tasks_with_that_tag_2(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True,
                                          tag='efgh')

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent2'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_single_tag_returns_only_tasks_with_that_tag_3(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True,
                                          tag='ijkl')

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'parent'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_tag_object_also_works(self):
        # when
        tasks = self.ll.load_no_hierarchy(self.user, include_done=True,
                                          include_deleted=True,
                                          tag=self.abcd)

        # then
        self.assertEqual(2, len(tasks))
        self.assertEqual(tasks[0].object_type, ObjectTypes.Task)
        self.assertEqual(tasks[1].object_type, ObjectTypes.Task)

        expected_summaries = {'normal', 'great_great_grandchild'}
        summaries = set(t.summary for t in tasks)
        self.assertEqual(expected_summaries, summaries)

    def test_unknown_tag_object_type_raises_exception(self):
        # expect
        self.assertRaises(TypeError, self.ll.load_no_hierarchy,
                          self.user, include_done=True, include_deleted=True,
                          tag=1234)
