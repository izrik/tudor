#!/usr/bin/env python

import unittest
from datetime import datetime

from tudor import generate_app
from persistence_layer import PersistenceLayer
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User


class PersistenceLayerTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_done=True)
        self.pl.add(self.t2)
        self.t3 = Task('t3', is_deleted=True)
        self.t3.parent = self.t2
        self.pl.add(self.t3)
        self.t4 = Task('t4', is_done=True, is_deleted=True)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_get_tasks(self):
        # when
        results = self.pl.get_tasks()

        # then
        self.assertEqual({self.t1, self.t2, self.t3, self.t4}, set(results))

    def test_get_tasks_is_done_true_excludes_undone(self):
        # when
        results = self.pl.get_tasks(is_done=True)

        # then
        self.assertEqual({self.t2, self.t4}, set(results))

    def test_get_tasks_is_done_false_excludes_done(self):
        # when
        results = self.pl.get_tasks(is_done=False)

        # then
        self.assertEqual({self.t1, self.t3}, set(results))

    def test_get_tasks_is_deleted_true_excludes_undeleted(self):
        # when
        results = self.pl.get_tasks(is_deleted=True)

        # then
        self.assertEqual({self.t3, self.t4}, set(results))

    def test_get_tasks_is_deleted_false_excludes_deleted(self):
        # when
        results = self.pl.get_tasks(is_deleted=False)

        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_get_tasks_is_done_is_deleted_combos(self):
        # when
        results = self.pl.get_tasks(is_done=False, is_deleted=False)

        # then
        self.assertEqual({self.t1}, set(results))

        # when
        results = self.pl.get_tasks(is_done=True, is_deleted=False)

        # then
        self.assertEqual({self.t2}, set(results))

        # when
        results = self.pl.get_tasks(is_done=False, is_deleted=True)

        # then
        self.assertEqual({self.t3}, set(results))

        # when
        results = self.pl.get_tasks(is_done=True, is_deleted=True)

        # then
        self.assertEqual({self.t4}, set(results))

    def test_get_tasks_parent_id_none_yields_top_level(self):
        # when
        results = self.pl.get_tasks(parent_id=None)
        # then
        self.assertEqual({self.t1, self.t2, self.t4}, set(results))

    def test_get_tasks_parent_id_non_null_yields_indicated(self):
        # when
        results = self.pl.get_tasks(parent_id=self.t2.id)
        # then
        self.assertEqual({self.t3}, set(results))

    def test_get_tasks_users_contains(self):
        # given
        user1 = User('name@example.com')
        user2 = User('name2@example.com')
        user3 = User('name3@example.com')
        self.pl.add(user1)
        self.pl.add(user2)
        self.pl.add(user3)
        self.t1.users.append(user1)
        self.t2.users.append(user2)
        self.t3.users.append(user1)
        self.t3.users.append(user2)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.commit()

        # when
        results = self.pl.get_tasks(users_contains=user1)
        # then
        self.assertEqual({self.t1, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(users_contains=user2)
        # then
        self.assertEqual({self.t2, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(users_contains=user3)
        # then
        self.assertEqual(set(), set(results))


class PersistenceLayerOrderByTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.id = 5
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_done=True)
        self.t2.id = 7
        self.pl.add(self.t2)
        self.t3 = Task('t3', is_deleted=True)
        self.t3.parent = self.t2
        self.t3.id = 11
        self.pl.add(self.t3)
        self.t4 = Task('t4', is_done=True, is_deleted=True)
        self.t4.id = 13
        self.pl.add(self.t4)

        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.t4.order_num = 4
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)

        self.pl.commit()

    def test_get_tasks_order_by_order_num_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list(self):

        # when
        results = self.pl.get_tasks(order_by=[self.pl.ORDER_NUM])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_direction_in_list_raises(self):

        # expect
        self.assertRaises(Exception,
                          self.pl.get_tasks,
                          order_by=[self.pl.ORDER_NUM, self.pl.ASCENDING])

    def test_get_tasks_order_by_order_num_list_list(self):

        # when
        results = self.pl.get_tasks(order_by=[[self.pl.ORDER_NUM]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))

    def test_get_tasks_order_by_unknown_direction_raises(self):

        # expect
        self.assertRaises(Exception,
                          self.pl.get_tasks,
                          order_by=[[self.pl.ORDER_NUM, 123]])

    def test_get_tasks_order_by_task_id_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.TASK_ID)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_task_id_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.TASK_ID, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_task_id_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.TASK_ID, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))


class PersistenceLayerOrderByDeadlineTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1', deadline='2017-01-01')
        self.t2 = Task('t2', deadline='2017-01-02')
        self.t3 = Task('t3', deadline='2017-01-03')
        self.t4 = Task('t4', deadline='2017-01-04')

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_get_tasks_order_by_deadline_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.DEADLINE)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_deadline_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.DEADLINE, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_deadline_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.DEADLINE, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))


class PersistenceLayerIdInTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_id_in(self):
        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t2.id, self.t3.id])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t3.id, self.t2.id, self.t1.id])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_some_missing(self):
        # when
        results = self.pl.get_tasks(task_id_in=[self.t1.id, self.t2.id])
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_get_tasks_id_in_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids.append(next_id)
        # when
        results = self.pl.get_tasks(task_id_in=ids)
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_empty(self):
        # when
        results = self.pl.get_tasks(task_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_in_with_order_by(self):
        # given
        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)

        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3], list(results))

        # when
        results = self.pl.get_tasks(task_id_in=[], order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))

    def test_get_tasks_id_not_in(self):
        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t1.id, self.t2.id, self.t3.id])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t3.id, self.t2.id, self.t1.id])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_some_missing(self):
        # when
        results = self.pl.get_tasks(task_id_not_in=[self.t1.id, self.t2.id])
        # then
        self.assertEqual({self.t3}, set(results))

    def test_get_tasks_id_not_in_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids.append(next_id)
        # when
        results = self.pl.get_tasks(task_id_not_in=ids)
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_some_missing_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids = [self.t2.id, self.t3.id, next_id]
        # when
        results = self.pl.get_tasks(task_id_not_in=ids)
        # then
        self.assertEqual({self.t1}, set(results))

    def test_get_tasks_id_not_in_empty(self):
        # when
        results = self.pl.get_tasks(task_id_not_in=[])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_not_in_with_order_by(self):
        # given
        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)

        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t1.id, self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))

        # when
        results = self.pl.get_tasks(task_id_not_in=[],
                                    order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3], list(results))

    def test_get_tasks_both_params(self):

        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t3.id],
            task_id_not_in=[self.t2.id, self.t3.id])
        # then
        self.assertEqual({self.t1}, set(results))


class PersistenceLayerLimitTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.order_num = 1
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.t2.order_num = 2
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.t3.order_num = 3
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_no_limit(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual(3, len(list(results)))

    def test_get_tasks_with_limit(self):
        # when
        results = self.pl.get_tasks(limit=2)
        # then
        self.assertEqual(2, len(list(results)))

    def test_get_tasks_limit_greater_than_count_returns_count(self):
        # when
        results = self.pl.get_tasks(limit=4)
        # then
        self.assertEqual(3, len(list(results)))

    def test_get_tasks_limit_zero_returns_zero(self):
        # when
        results = self.pl.get_tasks(limit=0)
        # then
        self.assertEqual(0, len(list(results)))

    def test_get_tasks_limit_negative_returns_all(self):
        # when
        results = self.pl.get_tasks(limit=-1)
        # then
        self.assertEqual(3, len(list(results)))


class PersistenceLayerDeadLineIsNotNoneTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1', deadline=datetime(2017, 1, 1))
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3', deadline=datetime(2017, 1, 2))
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_not_specified_does_not_filter(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_false_does_not_filter(self):
        # when
        results = self.pl.get_tasks(deadline_is_not_none=False)
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_true_excludes_null_deadlines(self):
        # when
        results = self.pl.get_tasks(deadline_is_not_none=True)
        # then
        self.assertEqual({self.t1, self.t3}, set(results))


class PersistenceLayerParentIdInTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.t3.parent = self.t2
        self.pl.add(self.t3)
        self.t4 = Task('t4')
        self.t4.parent = self.t3
        self.pl.add(self.t4)
        self.t5 = Task('t5')
        self.t5.parent = self.t2
        self.pl.add(self.t5)
        self.t6 = Task('t6')
        self.pl.add(self.t6)
        self.t7 = Task('t7')
        self.t7.parent = self.t6
        self.pl.add(self.t7)

        self.pl.commit()

    def test_get_tasks_parent_id_in(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id, self.t6.id])
        # then
        self.assertEqual({self.t3, self.t5, self.t7}, set(results))

    def test_get_tasks_parent_id_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t6.id, self.t2.id])
        # then
        self.assertEqual({self.t3, self.t5, self.t7}, set(results))

    def test_get_tasks_parent_id_in_some_missing(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id])
        # then
        self.assertEqual({self.t3, self.t5}, set(results))

    def test_get_tasks_parent_id_in_invalid_values_have_no_effect(self):
        # given
        next_id = max([self.t1.id, self.t2.id, self.t3.id, self.t4.id,
                       self.t5.id, self.t6.id, self.t7.id]) + 1
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id, next_id])
        # then
        self.assertEqual({self.t3, self.t5}, set(results))

    def test_get_tasks_parent_id_in_empty(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_parent_id_in_with_order_by(self):
        # given
        self.t3.order_num = 101
        self.t4.order_num = 313
        self.t5.order_num = 207
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)

        # when
        results = self.pl.get_tasks(
            parent_id_in=[self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t3, self.t5, self.t4], list(results))

        # when
        results = self.pl.get_tasks(task_id_in=[], order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))


class PersistenceLayerTagsTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t2 = Task('t2')
        self.t3 = Task('t3')
        self.tag1 = Tag('tag1')
        self.tag2 = Tag('tag2')
        self.t2.tags.append(self.tag1)
        self.t3.tags.append(self.tag1)
        self.t3.tags.append(self.tag2)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)

        self.pl.commit()

    def test_get_tasks_tag_unspecified_yields_all_tasks(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_tag_specified_yields_only_tasks_with_that_tag(self):
        # when
        results = self.pl.get_tasks(tags_contains=self.tag1)
        # then
        self.assertEqual({self.t2, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(tags_contains=self.tag2)
        # then
        self.assertEqual({self.t3}, set(results))


class PersistenceLayerPaginatedTasksTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.order_num = 11
        self.t2 = Task('t2')
        self.t2.order_num = 23
        self.t3 = Task('t3')
        self.t3.order_num = 37
        self.t4 = Task('t4')
        self.t4.order_num = 47
        self.t5 = Task('t5')
        self.t5.order_num = 53
        self.tag1 = Tag('tag1')
        self.tag2 = Tag('tag2')
        self.t2.tags.append(self.tag1)
        self.t3.tags.append(self.tag1)
        self.t3.tags.append(self.tag2)
        self.t4.tags.append(self.tag1)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)

    def test_get_paginated_tasks_tasks_per_page_returns_that_number_1(self):
        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=1)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(1, len(items))
        self.assertIn(items[0], {self.t1, self.t2, self.t3, self.t4, self.t5})

    def test_get_paginated_tasks_tasks_per_page_returns_that_number_2(self):
        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=2)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(2, len(items))
        self.assertIn(items[0], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[1], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertEqual(2, len(set(items)))

    def test_get_paginated_tasks_tasks_per_page_returns_that_number_3(self):
        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=3)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(3, len(items))
        self.assertIn(items[0], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[1], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[2], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertEqual(3, len(set(items)))

    def test_get_paginated_tasks_tasks_per_page_returns_that_number_4(self):
        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=4)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(4, len(items))
        self.assertIn(items[0], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[1], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[2], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertIn(items[3], {self.t1, self.t2, self.t3, self.t4, self.t5})
        self.assertEqual(4, len(set(items)))

    def test_get_paginated_tasks_tasks_per_page_returns_that_number_5(self):
        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=5)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(5, len(items))
        self.assertEqual(set(items),
                         {self.t1, self.t2, self.t3, self.t4, self.t5})

    def test_get_paginated_tasks_per_page_greater_than_max_returns_max(self):

        # when
        pager = self.pl.get_paginated_tasks(tasks_per_page=6)
        # then
        self.assertIsNotNone(pager)
        self.assertIsNotNone(pager.items)
        items = list(pager.items)
        self.assertEqual(5, len(items))
        self.assertEqual(set(items),
                         {self.t1, self.t2, self.t3, self.t4, self.t5})

    def test_get_paginated_tasks_order_by_returns_tasks_in_order(self):
        # when
        pager = self.pl.get_paginated_tasks(page_num=1, tasks_per_page=2,
                                            order_by=self.pl.ORDER_NUM)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(5, pager.total)
        self.assertEqual([self.t1, self.t2], list(pager.items))
        # when
        pager = self.pl.get_paginated_tasks(page_num=2, tasks_per_page=2,
                                            order_by=self.pl.ORDER_NUM)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(2, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(5, pager.total)
        self.assertEqual([self.t3, self.t4], list(pager.items))
        # when
        pager = self.pl.get_paginated_tasks(page_num=3, tasks_per_page=2,
                                            order_by=self.pl.ORDER_NUM)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(3, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(5, pager.total)
        self.assertEqual([self.t5], list(pager.items))

    def test_get_paginated_tasks_filtered_by_tag_tag1_page_1(self):
        # when
        pager = self.pl.get_paginated_tasks(page_num=1, tasks_per_page=2,
                                            tags_contains=self.tag1)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(3, pager.total)
        items = list(pager.items)
        self.assertEqual(2, len(items))
        self.assertIn(self.tag1, items[0].tags)
        self.assertIn(items[0], {self.t2, self.t3, self.t4})
        self.assertIn(self.tag1, items[1].tags)
        self.assertIn(items[1], {self.t2, self.t3, self.t4})

    def test_get_paginated_tasks_filtered_by_tag_tag1_page_2(self):
        # when
        pager = self.pl.get_paginated_tasks(page_num=2, tasks_per_page=2,
                                            tags_contains=self.tag1)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(2, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(3, pager.total)
        items = list(pager.items)
        self.assertEqual(1, len(items))
        self.assertIn(self.tag1, items[0].tags)
        self.assertIn(items[0], {self.t2, self.t3, self.t4})

    def test_get_paginated_tasks_filtered_by_tag_tag2_page_1(self):
        # when
        pager = self.pl.get_paginated_tasks(page_num=1, tasks_per_page=2,
                                            tags_contains=self.tag2)
        # then
        self.assertIsNotNone(pager)
        self.assertEqual(1, pager.page)
        self.assertEqual(2, pager.per_page)
        self.assertEqual(1, pager.total)
        items = list(pager.items)
        self.assertEqual(1, len(items))
        self.assertIn(self.tag1, items[0].tags)
        self.assertIs(self.t3, items[0])


class PersistenceLayerPagerTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.order_num = 11
        self.t2 = Task('t2')
        self.t2.order_num = 23
        self.t3 = Task('t3')
        self.t3.order_num = 37
        self.t4 = Task('t4')
        self.t4.order_num = 47
        self.t5 = Task('t5')
        self.t5.order_num = 53
        self.t6 = Task('t6')
        self.t5.order_num = 67
        self.t7 = Task('t7')
        self.t5.order_num = 71
        self.t8 = Task('t8')
        self.t5.order_num = 83
        self.t9 = Task('t9')
        self.t5.order_num = 97
        self.t10 = Task('t10')
        self.t5.order_num = 101
        self.t11 = Task('t11')
        self.t5.order_num = 113
        self.t12 = Task('t12')
        self.t12.order_num = 127
        self.t13 = Task('t13')
        self.t13.order_num = 131
        self.t14 = Task('t14')
        self.t14.order_num = 149
        self.t15 = Task('t15')
        self.t15.order_num = 151
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)
        self.pl.add(self.t6)
        self.pl.add(self.t7)
        self.pl.add(self.t8)
        self.pl.add(self.t9)
        self.pl.add(self.t10)
        self.pl.add(self.t11)
        self.pl.add(self.t12)
        self.pl.add(self.t13)
        self.pl.add(self.t14)
        self.pl.add(self.t15)
        self.pager = self.pl.get_paginated_tasks(page_num=4, tasks_per_page=2,
                                                 order_by=self.pl.ORDER_NUM)

    def test_pager_num_pages(self):
        # expect
        self.assertEqual(8, self.pager.num_pages)
        self.assertEqual(8, self.pager.pages)

    def test_pager_prev_next(self):
        # expect
        self.assertTrue(self.pager.has_prev)
        self.assertEqual(3, self.pager.prev_num)
        self.assertTrue(self.pager.has_next)
        self.assertEqual(5, self.pager.next_num)

    def test_pager_iter_items_1(self):
        # when
        pages = list(self.pager.iter_pages(1, 1, 1, 1))
        # then
        self.assertEqual([1, None, 3, 4, None, 8], pages)

    def test_pager_iter_items_2(self):
        # when
        pages = list(self.pager.iter_pages(1, 1, 1, 2))
        # then
        self.assertEqual([1, None, 3, 4, None, 7, 8], pages)

    def test_pager_iter_items_3(self):
        # when
        pages = list(self.pager.iter_pages(1, 1, 1, 3))
        # then
        self.assertEqual([1, None, 3, 4, None, 6, 7, 8], pages)

    def test_pager_iter_items_4(self):
        # when
        pages = list(self.pager.iter_pages(1, 1, 2, 1))
        # then
        self.assertEqual([1, None, 3, 4, 5, None, 8], pages)

    def test_pager_iter_items_5(self):
        # when
        pages = list(self.pager.iter_pages(1, 1, 3, 1))
        # then
        self.assertEqual([1, None, 3, 4, 5, 6, None, 8], pages)

    def test_pager_iter_items_6(self):
        # when
        pages = list(self.pager.iter_pages(1, 2, 1, 1))
        # then
        self.assertEqual([1, 2, 3, 4, None, 8], pages)

    def test_pager_iter_items_7(self):
        # when
        pages = list(self.pager.iter_pages(1, 3, 1, 1))
        # then
        self.assertEqual([1, 2, 3, 4, None, 8], pages)

    def test_pager_iter_items_8(self):
        # when
        pages = list(self.pager.iter_pages(2, 1, 1, 1))
        # then
        self.assertEqual([1, 2, 3, 4, None, 8], pages)

    def test_pager_iter_items_9(self):
        # when
        pages = list(self.pager.iter_pages(3, 1, 1, 1))
        # then
        self.assertEqual([1, 2, 3, 4, None, 8], pages)

    def test_pager_iter_items_10(self):
        # when
        pages = list(self.pager.iter_pages(2, 2, 2, 2))
        # then
        self.assertEqual([1, 2, 3, 4, 5, None, 7, 8], pages)

    def test_pager_iter_items_11(self):

        # when
        pages = list(self.pager.iter_pages(3, 3, 3, 3))
        # then
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 8], pages)

    def test_pager_iter_items_zero_raises(self):
        # when
        generator = self.pager.iter_pages(0, 1, 1, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, 0, 1, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, 1, 0, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, 1, 1, 0)
        # then
        self.assertRaises(ValueError, generator.next)

    def test_pager_iter_items_negative_raises(self):
        # when
        generator = self.pager.iter_pages(-1, 1, 1, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, -1, 1, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, 1, -1, 1)
        # then
        self.assertRaises(ValueError, generator.next)
        # when
        generator = self.pager.iter_pages(1, 1, 1, -1)
        # then
        self.assertRaises(ValueError, generator.next)


class PersistenceLayerSearchTermTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()

        self.t1 = Task('t1', description='qwerty')
        self.t2 = Task('t2', description='abc')
        self.t3 = Task('t3 abc', description='qwerty')
        self.t4 = Task('t4 abc', description='abc')

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_specifying_search_term_yiels_all_tasks_that_match(self):
        # when
        results = self.pl.get_tasks(summary_description_search_term='abc')
        # then
        self.assertEqual({self.t2, self.t3, self.t4}, set(results))

    def test_partial_word_matches(self):
        # when
        results = self.pl.get_tasks(summary_description_search_term='wer')
        # then
        results = list(results)
        self.assertEqual({self.t1, self.t3}, set(results))


class PersistenceLayerOrderNumberGreaterLessEqualTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()

        self.t1 = Task('t1')
        self.t1.order_num = 2
        self.t2 = Task('t2')
        self.t2.order_num = 3
        self.t3 = Task('t3')
        self.t3.order_num = 5
        self.t4 = Task('t4')
        self.t4.order_num = 7

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_unspecified_yields_all_tasks(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3, self.t4}, set(results))

    def test_order_num_g_equal_returns_matching_task(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=7)
        # then
        results = list(results)
        self.assertEqual({self.t4}, set(results))

    def test_order_num_greater_returns_all_matching_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=4)
        # then
        results = list(results)
        self.assertEqual({self.t3, self.t4}, set(results))

    def test_order_num_l_equal_returns_matching_task(self):
        # when
        results = self.pl.get_tasks(order_num_lesseq_than=2)
        # then
        results = list(results)
        self.assertEqual({self.t1}, set(results))

    def test_order_num_less_returns_all_matching_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_lesseq_than=4)
        # then
        results = list(results)
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_order_num_both_sets_upper_and_lower_bounds(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=3,
                                    order_num_lesseq_than=6)
        # then
        results = list(results)
        self.assertEqual({self.t2, self.t3}, set(results))

    def test_order_num_mismatched_bounds_yields_no_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=6,
                                    order_num_lesseq_than=3)
        # then
        results = list(results)
        self.assertEqual(set(), set(results))


class PersistenceLayerGetTagsTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.t1 = Tag('t1')
        self.pl.add(self.t1)
        self.t2 = Tag('t2')
        self.pl.add(self.t2)
        self.pl.commit()

    def test_get_tags_without_params_returns_all_tags(self):
        # when
        results = self.pl.get_tags()
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_specifying_value_filters_tags_1(self):
        # when
        results = self.pl.get_tags(value='t1')
        # then
        self.assertEqual({self.t1}, set(results))

    def test_specifying_value_filters_tags_2(self):
        # when
        results = self.pl.get_tags(value='t2')
        # then
        self.assertEqual({self.t2}, set(results))

    def test_non_existing_value_yields_empty(self):
        # when
        results = self.pl.get_tags(value='tx')
        # then
        self.assertEqual(set(), set(results))

    def test_limit_yields_only_that_many_tags(self):
        # when
        results = self.pl.get_tags(limit=1)
        # then
        results = list(results)
        self.assertEqual(1, len(results))
        self.assertIn(results[0], {self.t1, self.t2})

    def test_limit_greater_than_max_yields_max(self):
        # when
        results = self.pl.get_tags(limit=3)
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_limit_zero_yields_empty(self):
        # when
        results = self.pl.get_tags(limit=0)
        # then
        self.assertEqual(set(), set(results))

    def test_count_tags_without_params_returns_total_count(self):
        # when
        results = self.pl.count_tags()
        # then
        self.assertEqual(2, results)

    def test_count_tags_specifying_value_returns_one(self):
        # when
        results = self.pl.count_tags(value='t1')
        # then
        self.assertEqual(1, results)

    def test_count_tags_specifying_limit_returns_that_limit(self):
        # given
        t3 = Tag('t3')
        self.pl.add(t3)
        self.pl.commit()
        # when
        results = self.pl.count_tags(limit=1)
        # then
        self.assertEqual(1, results)
        # when
        results = self.pl.count_tags(limit=2)
        # then
        self.assertEqual(2, results)
        # when
        results = self.pl.count_tags(limit=3)
        # then
        self.assertEqual(3, results)

    def test_count_tags_limit_greater_than_max_yields_max(self):
        # given
        t3 = Tag('t3')
        self.pl.add(t3)
        self.pl.commit()
        # when
        results = self.pl.count_tags(limit=4)
        # then
        self.assertEqual(3, results)

    def test_get_tag_by_value_tag_present_returns_tag(self):
        # when
        results = self.pl.get_tag_by_value('t1')
        # then
        self.assertIsNotNone(results)
        self.assertIsInstance(results, Tag)
        self.assertIs(self.t1, results)

    def test_get_tag_by_value_tag_missing_returns_none(self):
        # when
        results = self.pl.get_tag_by_value('x')
        # then
        self.assertIsNone(results)


class PersistenceLayerGetNotesTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.n1 = Note('n1')
        self.pl.add(self.n1)
        self.n2 = Note('n2')
        self.pl.add(self.n2)
        self.pl.commit()

    def test_get_notes_without_params_returns_all_notes(self):
        # when
        results = self.pl.get_notes()
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_count_notes_without_params_returns_all_notes(self):
        # expect
        self.assertEqual(2, self.pl.count_notes())

    def test_get_notes_note_id_in_filters_only_matching_notes(self):
        # when
        results = self.pl.get_notes(note_id_in=[self.n1.id])
        # then
        self.assertEqual({self.n1}, set(results))
        # when
        results = self.pl.get_notes(note_id_in=[self.n2.id])
        # then
        self.assertEqual({self.n2}, set(results))
        # when
        results = self.pl.get_notes(note_id_in=[self.n1.id, self.n2.id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_notes_note_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.get_notes(
            note_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual({self.n1, self.n2}, set(results))

    def test_get_notes_note_id_in_empty_yields_no_notes(self):
        # when
        results = self.pl.get_notes(note_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_notes_note_id_in_filters_only_matching_notes(self):
        # expect
        self.assertEqual(1, self.pl.count_notes(note_id_in=[self.n1.id]))
        # expect
        self.assertEqual(1, self.pl.count_notes(note_id_in=[self.n2.id]))
        # expect
        self.assertEqual(2, self.pl.count_notes(
            note_id_in=[self.n1.id, self.n2.id]))

    def test_count_notes_note_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.n1.id, self.n2.id]) + 1
        # when
        results = self.pl.count_notes(
            note_id_in=[self.n1.id, self.n2.id, next_id])
        # then
        self.assertEqual(2, results)

    def test_count_notes_note_id_in_empty_yields_no_notes(self):
        # expect
        self.assertEqual(0, self.pl.count_notes(note_id_in=[]))


class PersistenceLayerGetAttachmentsTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.a1 = Attachment('a1.txt')
        self.pl.add(self.a1)
        self.a2 = Attachment('a2.txt')
        self.pl.add(self.a2)
        self.pl.commit()

    def test_get_attachments_without_params_returns_all_attachments(self):
        # when
        results = self.pl.get_attachments()
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_count_attachments_without_params_returns_all_attachments(self):
        # expect
        self.assertEqual(2, self.pl.count_attachments())

    def test_get_attachments_attachment_id_in_filters_only_matching_atts(self):
        # when
        results = self.pl.get_attachments(attachment_id_in=[self.a1.id])
        # then
        self.assertEqual({self.a1}, set(results))
        # when
        results = self.pl.get_attachments(attachment_id_in=[self.a2.id])
        # then
        self.assertEqual({self.a2}, set(results))
        # when
        results = self.pl.get_attachments(
            attachment_id_in=[self.a1.id, self.a2.id])
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_get_attachments_att_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.a1.id, self.a2.id]) + 1
        # when
        results = self.pl.get_attachments(
            attachment_id_in=[self.a1.id, self.a2.id, next_id])
        # then
        self.assertEqual({self.a1, self.a2}, set(results))

    def test_get_attachments_attachment_id_in_empty_yields_no_atts(self):
        # when
        results = self.pl.get_attachments(attachment_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_attachments_att_id_in_filters_only_matching_atts(self):
        # expect
        self.assertEqual(1, self.pl.count_attachments(
            attachment_id_in=[self.a1.id]))
        # expect
        self.assertEqual(1, self.pl.count_attachments(
            attachment_id_in=[self.a2.id]))
        # expect
        self.assertEqual(2, self.pl.count_attachments(
            attachment_id_in=[self.a1.id, self.a2.id]))

    def test_count_attachments_att_id_in_unmatching_ids_do_not_filter(self):
        # given
        next_id = max([self.a1.id, self.a2.id]) + 1
        # when
        results = self.pl.count_attachments(
            attachment_id_in=[self.a1.id, self.a2.id, next_id])
        # then
        self.assertEqual(2, results)

    def test_count_attachments_attachment_id_in_empty_yields_no_atts(self):
        # expect
        self.assertEqual(0, self.pl.count_attachments(attachment_id_in=[]))


class PersistenceLayerGetUsersTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.user1 = User('admin@example.com', is_admin=True)
        self.pl.add(self.user1)
        self.user2 = User('name@example.com')
        self.pl.add(self.user2)
        self.pl.commit()

    def test_get_user_by_email(self):
        # when
        results = self.pl.get_user_by_email('admin@example.com')
        # then
        self.assertIs(self.user1, results)
        # when
        results = self.pl.get_user_by_email('name@example.com')
        # then
        self.assertIs(self.user2, results)

    def test_get_user_by_email_invalid_email_yields_none(self):
        # when
        results = self.pl.get_user_by_email('someone@example.org')
        # then
        self.assertIsNone(results)

    def test_get_users_without_params_returns_all_users(self):
        # when
        results = self.pl.get_users()
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_count_users_without_params_returns_all_users(self):
        # expect
        self.assertEqual(2, self.pl.count_users())

    def test_get_users_email_in_filters_only_matching_users(self):
        # when
        results = self.pl.get_users(email_in=[self.user1.email])
        # then
        self.assertEqual({self.user1}, set(results))
        # when
        results = self.pl.get_users(email_in=[self.user2.email])
        # then
        self.assertEqual({self.user2}, set(results))
        # when
        results = self.pl.get_users(
            email_in=[self.user1.email, self.user2.email])
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_get_users_email_in_unmatching_emails_do_not_filter(self):
        # given
        next_email = (list({self.user1.email, self.user2.email}))[0] + 'a'
        # when
        results = self.pl.get_users(
            email_in=[self.user1.email, self.user2.email, next_email])
        # then
        self.assertEqual({self.user1, self.user2}, set(results))

    def test_get_users_email_in_empty_yields_no_users(self):
        # when
        results = self.pl.get_users(email_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_users_email_in_filters_only_matching_users(self):
        # expect
        self.assertEqual(1, self.pl.count_users(email_in=[self.user1.email]))
        # expect
        self.assertEqual(1, self.pl.count_users(email_in=[self.user2.email]))
        # expect
        self.assertEqual(2, self.pl.count_users(
            email_in=[self.user1.email, self.user2.email]))

    def test_count_users_email_in_unmatching_emails_do_not_filter(self):
        # given
        next_email = (list({self.user1.email, self.user2.email}))[0] + 'a'
        # when
        results = self.pl.count_users(
            email_in=[self.user1.email, self.user2.email, next_email])
        # then
        self.assertEqual(2, results)

    def test_count_users_email_in_empty_yields_no_users(self):
        # expect
        self.assertEqual(0, self.pl.count_users(email_in=[]))


class PersistenceLayerGetOptionsTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()
        self.option1 = Option('option1', 'value1')
        self.pl.add(self.option1)
        self.option2 = Option('option2', 'value2')
        self.pl.add(self.option2)
        self.pl.commit()

    def test_get_options_without_params_returns_all_options(self):
        # when
        results = self.pl.get_options()
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_count_options_without_params_returns_all_options(self):
        # expect
        self.assertEqual(2, self.pl.count_options())

    def test_get_options_key_in_filters_only_matching_options(self):
        # when
        results = self.pl.get_options(key_in=[self.option1.key])
        # then
        self.assertEqual({self.option1}, set(results))
        # when
        results = self.pl.get_options(key_in=[self.option2.key])
        # then
        self.assertEqual({self.option2}, set(results))
        # when
        results = self.pl.get_options(
            key_in=[self.option1.key, self.option2.key])
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_get_options_key_in_unmatching_keys_do_not_filter(self):
        # given
        next_key = 'option3'
        # when
        results = self.pl.get_options(
            key_in=[self.option1.key, self.option2.key, next_key])
        # then
        self.assertEqual({self.option1, self.option2}, set(results))

    def test_get_options_key_in_empty_yields_no_options(self):
        # when
        results = self.pl.get_options(key_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_count_options_key_in_filters_only_matching_options(self):
        # expect
        self.assertEqual(1, self.pl.count_options(key_in=[self.option1.key]))
        # expect
        self.assertEqual(1, self.pl.count_options(key_in=[self.option2.key]))
        # expect
        self.assertEqual(2, self.pl.count_options(
            key_in=[self.option1.key, self.option2.key]))

    def test_count_options_key_in_unmatching_keys_do_not_filter(self):
        # given
        next_key = 'option3'
        # when
        results = self.pl.count_options(
            key_in=[self.option1.key, self.option2.key, next_key])
        # then
        self.assertEqual(2, results)

    def test_count_options_key_in_empty_yields_no_options(self):
        # expect
        self.assertEqual(0, self.pl.count_options(key_in=[]))


class PersistenceLayerDatabaseInteractionTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.pl.create_all()

    def test_adding_task_does_not_create_id(self):
        # given
        task = Task('summary')
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.add(task)
        # then
        self.assertIsNone(task.id)

    def test_committing_task_creates_id(self):
        # given
        task = Task('summary')
        self.pl.add(task)
        # precondition
        self.assertIsNone(task.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(task.id)

    def test_adding_tag_does_not_create_id(self):
        # given
        tag = Tag('value')
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.add(tag)
        # then
        self.assertIsNone(tag.id)

    def test_committing_tag_creates_id(self):
        # given
        tag = Tag('value')
        self.pl.add(tag)
        # precondition
        self.assertIsNone(tag.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(tag.id)

    def test_adding_note_does_not_create_id(self):
        # given
        note = Note('note')
        # precondition
        self.assertIsNone(note.id)
        # when
        self.pl.add(note)
        # then
        self.assertIsNone(note.id)

    def test_committing_note_creates_id(self):
        # given
        note = Note('note')
        self.pl.add(note)
        # precondition
        self.assertIsNone(note.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(note.id)

    def test_adding_attachment_does_not_create_id(self):
        # given
        attachment = Attachment('attachment')
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.add(attachment)
        # then
        self.assertIsNone(attachment.id)

    def test_committing_attachment_creates_id(self):
        # given
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        # precondition
        self.assertIsNone(attachment.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(attachment.id)

    def test_adding_user_does_not_create_id(self):
        # given
        user = User('name@example.com')
        # precondition
        self.assertIsNone(user.id)
        # when
        self.pl.add(user)
        # then
        self.assertIsNone(user.id)

    def test_committing_user_creates_id(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        # precondition
        self.assertIsNone(user.id)
        # when
        self.pl.commit()
        # then
        self.assertIsNotNone(user.id)

    def test_rollback_reverts_changes(self):
        task = Task('task')
        tag = Tag('tag', description='a')
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        tag2 = self.pl.get_tag_by_value('tag')
        self.assertIsNotNone(tag2)
        self.assertEqual('a', tag2.description)
        self.assertEqual('a', tag.description)

    def test_rollback_does_not_reverts_changes_on_unadded_new_objects(self):
        tag = Tag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_changes_to_objects_are_tracked_automatically(self):
        tag = Tag('tag', description='a')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.commit()
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag', description='a')
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # when
        task.tags.append(tag)
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

    def test_adding_child_also_sets_parent_id(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_adding_task_dependee_also_adds_other_task_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertNotIn(t1, t2.dependees)
        self.assertNotIn(t1, t2.dependants)
        self.assertNotIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        t1.dependees.append(t2)
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        self.pl.commit()
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertNotIn(t1, t2.dependees)
        self.assertIn(t1, t2.dependants)
        self.assertIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)

    def test_adding_task_after_also_adds_other_task_before(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertNotIn(t1, t2.dependees)
        self.assertNotIn(t1, t2.dependants)
        self.assertNotIn(t2, t1.dependees)
        self.assertNotIn(t2, t1.dependants)
        # when
        t1.prioritize_after.append(t2)
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)
        # when
        self.pl.commit()
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertNotIn(t1, t2.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)
        self.assertIn(t2, t1.prioritize_after)
        self.assertNotIn(t2, t1.prioritize_before)

    def test_adding_user_to_task_also_adds_task_to_user(self):
        # given
        task = Task('task')
        user = User('name@example.com')
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertNotIn(user, task.users)
        self.assertNotIn(task, user.tasks)
        # when
        task.users.append(user)
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

    def test_setting_id_before_adding_succeeds(self):
        # given
        task = Task('task')
        task.id = 1
        # precondition
        self.assertEqual(1, task.id)
        # when
        self.pl.add(task)
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.commit()
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.commit()
        # then
        self.assertEqual(1, task.id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual(1, task.id)

    def test_conflicting_id_when_committing_raises_exception(self):
        # given
        t1 = Task('t1')
        t1.id = 1
        self.pl.add(t1)
        t2 = Task('t1')
        t2.id = 1
        self.pl.add(t2)
        # precondition
        self.assertEqual(1, t1.id)
        self.assertEqual(1, t2.id)
        # expect
        self.assertRaises(Exception, self.pl.commit)


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.pl = self.app.pl
        self.bridge = self.pl.bridge
        self.pl.create_all()

    def test_db_task_is_db_object(self):
        # given
        task = self.pl.Task('task')
        # expect
        self.assertTrue(self.bridge.is_db_object(task))

    def test_db_task_is_not_domain_object(self):
        # given
        task = self.pl.Task('task')
        # expect
        self.assertFalse(self.bridge.is_domain_object(task))

    def test_domain_task_is_not_db_object(self):
        # given
        task = Task('task')
        # expect
        self.assertFalse(self.bridge.is_db_object(task))

    def test_domain_task_is_domain_object(self):
        # given
        task = Task('task')
        # expect
        self.assertTrue(self.bridge.is_domain_object(task))

    def test_get_domain_object_db_task_returns_domain_task(self):
        # given
        task = self.pl.Task('task')
        # when
        result = self.bridge.get_domain_object_from_db_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Task)

    def test_get_db_object_db_task_raises(self):
        # given
        task = self.pl.Task('task')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          task)

    def test_get_domain_object_domain_task_raises(self):
        # given
        task = Task('task')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          task)

    def test_get_db_object_domain_task_returns_db_task(self):
        # given
        task = Task('task')
        # when
        result = self.bridge.get_db_object_from_domain_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.Task)

    def test_db_tag_is_db_object(self):
        # given
        tag = self.pl.Tag('tag')
        # expect
        self.assertTrue(self.bridge.is_db_object(tag))

    def test_db_tag_is_not_domain_object(self):
        # given
        tag = self.pl.Tag('tag')
        # expect
        self.assertFalse(self.bridge.is_domain_object(tag))

    def test_domain_tag_is_not_db_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertFalse(self.bridge.is_db_object(tag))

    def test_domain_tag_is_domain_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertTrue(self.bridge.is_domain_object(tag))

    def test_get_domain_object_db_tag_returns_domain_tag(self):
        # given
        tag = self.pl.Tag('tag')
        # when
        result = self.bridge.get_domain_object_from_db_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)

    def test_get_domain_object_domain_tag_raises(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          tag)

    def test_get_db_object_db_tag_raises(self):
        # given
        tag = self.pl.Tag('tag')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          tag)

    def test_get_db_object_domain_tag_returns_dg_tag(self):
        # given
        tag = Tag('tag')
        # when
        result = self.bridge.get_db_object_from_domain_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.Tag)

    def test_db_note_is_db_object(self):
        # given
        note = self.pl.Note('note')
        # expect
        self.assertTrue(self.bridge.is_db_object(note))

    def test_domain_note_is_not_db_object(self):
        # given
        note = Note('note')
        # expect
        self.assertFalse(self.bridge.is_db_object(note))

    def test_domain_note_is_domain_object(self):
        # given
        note = Note('note')
        # expect
        self.assertTrue(self.bridge.is_domain_object(note))

    def test_db_note_is_not_domain_object(self):
        # given
        note = self.pl.Note('note')
        # expect
        self.assertFalse(self.bridge.is_domain_object(note))

    def test_get_domain_object_db_note_returns_domain_object(self):
        # given
        note = self.pl.Note('note')
        # when
        result = self.bridge.get_domain_object_from_db_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)

    def test_get_db_object_db_note_raises(self):
        # given
        note = self.pl.Note('note')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          note)

    def test_get_domain_object_domain_note_raises(self):
        # given
        note = Note('note')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          note)

    def test_get_db_object_domain_note_returns_db_object(self):
        # given
        note = Note('note')
        # when
        result = self.bridge.get_db_object_from_domain_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.Note)

    def test_db_attachment_is_db_object(self):
        # given
        attachment = self.pl.Attachment('attachment')
        # expect
        self.assertTrue(self.bridge.is_db_object(attachment))

    def test_domain_attachment_is_not_db_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertFalse(self.bridge.is_db_object(attachment))

    def test_db_attachment_is_not_domain_object(self):
        # given
        attachment = self.pl.Attachment('attachment')
        # expect
        self.assertFalse(self.bridge.is_domain_object(attachment))

    def test_domain_attachment_is_domain_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertTrue(self.bridge.is_domain_object(attachment))

    def test_get_domain_object_domain_attachment_raises(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          attachment)

    def test_get_domain_object_db_attachment_returns_domain(self):
        # given
        attachment = self.pl.Attachment('attachment')
        # when
        result = self.bridge.get_domain_object_from_db_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Attachment)

    def test_get_db_object_db_attachment_raises(self):
        # given
        attachment = self.pl.Attachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          attachment)

    def test_get_db_object_domain_attachment_returns_db(self):
        # given
        attachment = Attachment('attachment')
        # when
        result = self.bridge.get_db_object_from_domain_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.Attachment)

    def test_db_user_is_db_object(self):
        # given
        user = self.pl.User('name@example.com')
        # expect
        self.assertTrue(self.bridge.is_db_object(user))

    def test_db_user_is_not_domain_object(self):
        # given
        user = self.pl.User('name@example.com')
        # expect
        self.assertFalse(self.bridge.is_domain_object(user))

    def test_domain_user_is_not_db_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertFalse(self.bridge.is_db_object(user))

    def test_domain_user_is_domain_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertTrue(self.bridge.is_domain_object(user))

    def test_get_domain_object_db_user_returns_domain_user(self):
        # given
        user = self.pl.User('name@example.com')
        # when
        result = self.bridge.get_domain_object_from_db_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)

    def test_get_domain_object_domain_user_raises(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          user)

    def test_get_db_object_db_user_raises(self):
        # given
        user = self.pl.User('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          user)

    def test_get_db_object_domain_user_returns_db_user(self):
        # given
        user = User('name@example.com')
        # when
        result = self.bridge.get_db_object_from_domain_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.User)

    def test_db_option_is_db_object(self):
        # given
        option = self.pl.Option('key', 'value')
        # expect
        self.assertTrue(self.bridge.is_db_object(option))

    def test_domain_option_is_not_db_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertFalse(self.bridge.is_db_object(option))

    def test_db_option_is_not_domain_object(self):
        # given
        option = self.pl.Option('key', 'value')
        # expect
        self.assertFalse(self.bridge.is_domain_object(option))

    def test_domain_option_is_domain_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertTrue(self.bridge.is_domain_object(option))

    def test_get_domain_object_domain_option_raises(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_domain_object_from_db_object,
                          option)

    def test_get_domain_object_db_option_returns_domain_object(self):
        # given
        option = self.pl.Option('key', 'value')
        # when
        result = self.bridge.get_domain_object_from_db_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Option)

    def test_get_db_object_domain_option_returns_db_object(self):
        # given
        option = Option('key', 'value')
        # when
        result = self.bridge.get_db_object_from_domain_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.Option)

    def test_get_db_object_db_option_raises(self):
        # given
        option = self.pl.Option('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.bridge.get_db_object_from_domain_object,
                          option)
