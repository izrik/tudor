#!/usr/bin/env python
import unittest
from datetime import datetime
import logging
import types
from decimal import Decimal

from tudor import generate_app
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User
import logging_util
from persistence_layer import as_iterable


def generate_pl():
    app = generate_app(db_uri='sqlite://')
    return app.pl


class PersistenceLayerTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
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
        self.t1.users.add(user1)
        self.t2.users.add(user2)
        self.t3.users.add(user1)
        self.t3.users.add(user2)
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl.commit()

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
        self.pl.commit()

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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl.commit()

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
        self.pl = generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t2 = Task('t2')
        self.t3 = Task('t3')
        self.tag1 = Tag('tag1')
        self.tag2 = Tag('tag2')
        self.t2.tags.add(self.tag1)
        self.t3.tags.add(self.tag1)
        self.t3.tags.add(self.tag2)
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
        self._logger = logging.getLogger('test')
        self._logger.debug('setUp generate_app')
        self.pl = generate_pl()
        self._logger.debug('setUp create_all')
        self.pl.db.drop_all()
        self.pl.create_all()
        self._logger.debug('setUp create objects')

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
        self._logger.debug('setUp connect objects')
        self.t2.tags.add(self.tag1)
        self.t3.tags.add(self.tag1)
        self.t3.tags.add(self.tag2)
        self.t4.tags.add(self.tag1)
        self._logger.debug('setUp add objects')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)
        self._logger.debug('setUp commit')
        self.pl.commit()

        self._logger.debug('setUp finished')

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
        self._logger.debug('when')
        tasks = self.pl.get_tasks(tags_contains=self.tag1)
        # then
        self._logger.debug('then')
        tasks2 = set(tasks)
        self.assertEqual({self.t2, self.t3, self.t4}, tasks2)
        # when
        self._logger.debug('when')
        count = self.pl.count_tasks(tags_contains=self.tag1)
        # then
        self._logger.debug('then')
        self.assertEqual(3, count)
        # expect
        self._logger.debug('expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))
        # expect
        self._logger.debug('expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))
        # expect
        self._logger.debug('expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))

        # when
        self._logger.debug('when')
        pager = self.pl.get_paginated_tasks(page_num=1, tasks_per_page=2,
                                            tags_contains=self.tag1)
        # then
        self._logger.debug('then 1')
        self.assertIsNotNone(pager)
        self._logger.debug('then 2')
        self.assertEqual(1, pager.page)
        self._logger.debug('then 3')
        self.assertEqual(2, pager.per_page)
        self._logger.debug('then 4')
        self.assertEqual(3, pager.total)
        self._logger.debug('then 5')
        items = list(pager.items)
        self._logger.debug('then 6')
        self.assertEqual(2, len(items))
        self._logger.debug('then 7')
        self.assertIn(self.tag1, items[0].tags)
        self._logger.debug('then 8')
        self.assertIn(items[0], {self.t2, self.t3, self.t4})
        self._logger.debug('then 9')
        self.assertIn(self.tag1, items[1].tags)
        self._logger.debug('then 10')
        self.assertIn(items[1], {self.t2, self.t3, self.t4})
        self._logger.debug('when 11')

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
        self.pl = generate_pl()
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
        self.pl.commit()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        self.pl = generate_pl()
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
        tag = Tag('tag', description='a')
        self.pl.add(tag)
        self.pl.commit()
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
        # then
        tag2 = self.pl.get_tag_by_value('tag')
        self.assertIsNotNone(tag2)
        self.assertEqual('a', tag2.description)
        self.assertEqual('a', tag.description)

    def test_rollback_reverts_changes_to_collections(self):
        # given:
        task = Task('task')
        tag1 = Tag('tag1')
        tag2 = Tag('tag2')
        tag3 = Tag('tag3')
        task.tags.add(tag1)
        task.tags.add(tag2)
        self.pl.add(task)
        self.pl.add(tag1)
        self.pl.add(tag2)
        self.pl.add(tag3)
        self.pl.commit()

        # precondition:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

        task.tags.discard(tag1)
        task.tags.add(tag3)

        # precondition:
        self.assertNotIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertIn(tag3, task.tags)
        self.assertNotIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertIn(task, tag3.tasks)

        # when:
        self.pl.rollback()

        # then:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

    def test_rollback_does_not_reverts_changes_on_unadded_new_objects(self):
        tag = Tag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.rollback()
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
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_changes_after_get_are_also_tracked(self):
        # given
        dbtag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        tag = self.pl.get_tag_by_value('tag')
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
        self.assertEqual('b', dbtag.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', dbtag.description)

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
        task.tags.add(tag)
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.rollback()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

    def test_adding_child_also_sets_parent(self):
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
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_adding_child_also_sets_parent_id(self):
        # given
        parent = Task('parent')
        child = Task('child')
        self.pl.add(parent)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_setting_parent_also_sets_parent_id(self):
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
        child.parent = parent
        self.pl.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_setting_parent_also_adds_child(self):
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
        child.parent = parent
        self.pl.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_inconsistent_parent_parent_and_children_last_one_wins_1(self):
        # given
        p1 = Task('p1')
        p2 = Task('p2')
        p3 = Task('p3')
        child = Task('child')
        self.pl.add(p1)
        self.pl.add(p2)
        self.pl.add(p3)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        p3.children.append(child)
        child.parent = p2
        self.pl.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_inconsistent_parent_parent_and_children_last_one_wins_2(self):
        # given
        p1 = Task('p1')
        p2 = Task('p2')
        p3 = Task('p3')
        child = Task('child')
        self.pl.add(p1)
        self.pl.add(p2)
        self.pl.add(p3)
        self.pl.add(child)
        self.pl.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = p2
        p3.children.append(child)
        self.pl.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

    def test_db_only_rollback_reverts_changes(self):
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        tag2 = self.pl.DbTag.query.filter_by(value='tag').first()
        self.assertIsNotNone(tag2)
        self.assertEqual('a', tag2.description)
        self.assertEqual('a', tag.description)

    def test_db_only_rollback_reverts_changes_to_collections(self):
        # given:
        task = self.pl.DbTask('task')
        tag1 = self.pl.DbTag('tag1')
        tag2 = self.pl.DbTag('tag2')
        tag3 = self.pl.DbTag('tag3')
        task.tags.append(tag1)
        task.tags.append(tag2)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag1)
        self.pl.db.session.add(tag2)
        self.pl.db.session.add(tag3)
        self.pl.db.session.commit()

        # precondition:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

        task.tags.remove(tag1)
        task.tags.append(tag3)

        # precondition:
        self.assertNotIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertIn(tag3, task.tags)
        self.assertNotIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertIn(task, tag3.tasks)

        # when:
        self.pl.db.session.rollback()

        # then:
        self.assertIn(tag1, task.tags)
        self.assertIn(tag2, task.tags)
        self.assertNotIn(tag3, task.tags)
        self.assertIn(task, tag1.tasks)
        self.assertIn(task, tag2.tasks)
        self.assertNotIn(task, tag3.tasks)

    def test_db_only_rollback_does_not_reverts_changes_on_unadded_objs(self):
        tag = self.pl.DbTag('tag', description='a')
        tag.description = 'b'
        # precondition
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_db_only_changes_to_objects_are_tracked_automatically(self):
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.commit()
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertEqual('b', tag.description)

    def test_db_only_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag', description='a')
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(tag, task.tags)
        self.assertNotIn(task, tag.tasks)
        # when
        task.tags.append(tag)
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.db.session.commit()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

    def test_db_only_adding_child_also_sets_parent(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_adding_child_also_sets_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        parent.children.append(child)
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_also_sets_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.db.session.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_also_adds_child(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = parent
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_setting_parent_id_also_sets_parent(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent_id = parent.id
        self.pl.db.session.commit()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(parent, child.parent)
        self.assertEqual(parent.id, child.parent_id)

    def test_db_only_setting_parent_id_also_adds_child(self):
        # given
        parent = self.pl.DbTask('parent')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(parent)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(parent.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent_id = parent.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, parent.children)
        self.assertIsNotNone(child.parent)
        self.assertIs(parent, child.parent)

    def test_db_only_inconsistent_parent_always_overrides_parent_id(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = p2
        child.parent_id = p1.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_db_only_inconsistent_parent_children_overrides_parent_id(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        p3.children.append(child)
        child.parent_id = p1.id
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

    def test_db_only_incon_parent_parent_and_children_last_one_wins_1(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        p3.children.append(child)
        child.parent = p2
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p2.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p2, child.parent)
        self.assertEqual(p2.id, child.parent_id)

    def test_db_only_incon_parent_parent_and_children_last_one_wins_2(self):
        # given
        p1 = self.pl.DbTask('p1')
        p2 = self.pl.DbTask('p2')
        p3 = self.pl.DbTask('p3')
        child = self.pl.DbTask('child')
        self.pl.db.session.add(p1)
        self.pl.db.session.add(p2)
        self.pl.db.session.add(p3)
        self.pl.db.session.add(child)
        self.pl.db.session.commit()
        # precondition
        self.assertNotIn(child, p1.children)
        self.assertNotIn(child, p2.children)
        self.assertNotIn(child, p3.children)
        self.assertIsNone(child.parent)
        self.assertIsNone(child.parent_id)
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)
        self.assertIsNotNone(p3.id)
        self.assertIsNotNone(child.id)
        # when
        child.parent = p2
        p3.children.append(child)
        self.pl.db.session.commit()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)
        # when
        self.pl.db.session.rollback()
        # then
        self.assertIn(child, p3.children)
        self.assertIsNotNone(child.parent)
        self.assertIsNotNone(child.parent_id)
        self.assertIs(p3, child.parent)
        self.assertEqual(p3.id, child.parent_id)

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
        t1.dependees.add(t2)
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
        self.pl.rollback()
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
        t1.prioritize_after.add(t2)
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
        self.pl.rollback()
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
        task.users.add(user)
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.commit()
        # then
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)
        # when
        self.pl.rollback()
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
        self.pl.rollback()
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


class PersistenceLayerBridgeTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_db_task_is_db_object(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertTrue(self.pl._is_db_object(task))

    def test_db_task_is_not_domain_object(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertFalse(self.pl._is_domain_object(task))

    def test_domain_task_is_not_db_object(self):
        # given
        task = Task('task')
        # expect
        self.assertFalse(self.pl._is_db_object(task))

    def test_domain_task_is_domain_object(self):
        # given
        task = Task('task')
        # expect
        self.assertTrue(self.pl._is_domain_object(task))

    def test_get_domain_object_db_task_returns_domain_task(self):
        # given
        task = self.pl.DbTask('task')
        # when
        result = self.pl._get_domain_object_from_db_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Task)

    def test_get_db_object_db_task_raises(self):
        # given
        task = self.pl.DbTask('task')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          task)

    def test_get_domain_object_domain_task_raises(self):
        # given
        task = Task('task')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          task)

    def test_get_db_object_domain_task_returns_db_task(self):
        # given
        task = Task('task')
        # when
        result = self.pl._get_db_object_from_domain_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)

    def test_db_tag_is_db_object(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertTrue(self.pl._is_db_object(tag))

    def test_db_tag_is_not_domain_object(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertFalse(self.pl._is_domain_object(tag))

    def test_domain_tag_is_not_db_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertFalse(self.pl._is_db_object(tag))

    def test_domain_tag_is_domain_object(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertTrue(self.pl._is_domain_object(tag))

    def test_get_domain_object_db_tag_returns_domain_tag(self):
        # given
        tag = self.pl.DbTag('tag')
        # when
        result = self.pl._get_domain_object_from_db_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)

    def test_get_domain_object_domain_tag_raises(self):
        # given
        tag = Tag('tag')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          tag)

    def test_get_db_object_db_tag_raises(self):
        # given
        tag = self.pl.DbTag('tag')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          tag)

    def test_get_db_object_domain_tag_returns_dg_tag(self):
        # given
        tag = Tag('tag')
        # when
        result = self.pl._get_db_object_from_domain_object(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTag)

    def test_db_note_is_db_object(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertTrue(self.pl._is_db_object(note))

    def test_domain_note_is_not_db_object(self):
        # given
        note = Note('note')
        # expect
        self.assertFalse(self.pl._is_db_object(note))

    def test_domain_note_is_domain_object(self):
        # given
        note = Note('note')
        # expect
        self.assertTrue(self.pl._is_domain_object(note))

    def test_db_note_is_not_domain_object(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertFalse(self.pl._is_domain_object(note))

    def test_get_domain_object_db_note_returns_domain_object(self):
        # given
        note = self.pl.DbNote('note')
        # when
        result = self.pl._get_domain_object_from_db_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)

    def test_get_db_object_db_note_raises(self):
        # given
        note = self.pl.DbNote('note')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          note)

    def test_get_domain_object_domain_note_raises(self):
        # given
        note = Note('note')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          note)

    def test_get_db_object_domain_note_returns_db_object(self):
        # given
        note = Note('note')
        # when
        result = self.pl._get_db_object_from_domain_object(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbNote)

    def test_db_attachment_is_db_object(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertTrue(self.pl._is_db_object(attachment))

    def test_domain_attachment_is_not_db_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertFalse(self.pl._is_db_object(attachment))

    def test_db_attachment_is_not_domain_object(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertFalse(self.pl._is_domain_object(attachment))

    def test_domain_attachment_is_domain_object(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertTrue(self.pl._is_domain_object(attachment))

    def test_get_domain_object_domain_attachment_raises(self):
        # given
        attachment = Attachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          attachment)

    def test_get_domain_object_db_attachment_returns_domain(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # when
        result = self.pl._get_domain_object_from_db_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Attachment)

    def test_get_db_object_db_attachment_raises(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          attachment)

    def test_get_db_object_domain_attachment_returns_db(self):
        # given
        attachment = Attachment('attachment')
        # when
        result = self.pl._get_db_object_from_domain_object(attachment)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbAttachment)

    def test_db_user_is_db_object(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertTrue(self.pl._is_db_object(user))

    def test_db_user_is_not_domain_object(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertFalse(self.pl._is_domain_object(user))

    def test_domain_user_is_not_db_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertFalse(self.pl._is_db_object(user))

    def test_domain_user_is_domain_object(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertTrue(self.pl._is_domain_object(user))

    def test_get_domain_object_db_user_returns_domain_user(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # when
        result = self.pl._get_domain_object_from_db_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)

    def test_get_domain_object_domain_user_raises(self):
        # given
        user = User('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          user)

    def test_get_db_object_db_user_raises(self):
        # given
        user = self.pl.DbUser('name@example.com')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          user)

    def test_get_db_object_domain_user_returns_db_user(self):
        # given
        user = User('name@example.com')
        # when
        result = self.pl._get_db_object_from_domain_object(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbUser)

    def test_db_option_is_db_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertTrue(self.pl._is_db_object(option))

    def test_domain_option_is_not_db_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertFalse(self.pl._is_db_object(option))

    def test_db_option_is_not_domain_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertFalse(self.pl._is_domain_object(option))

    def test_domain_option_is_domain_object(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertTrue(self.pl._is_domain_object(option))

    def test_get_domain_object_domain_option_raises(self):
        # given
        option = Option('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_domain_object_from_db_object,
                          option)

    def test_get_domain_object_db_option_returns_domain_object(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # when
        result = self.pl._get_domain_object_from_db_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Option)

    def test_get_db_object_domain_option_returns_db_object(self):
        # given
        option = Option('key', 'value')
        # when
        result = self.pl._get_db_object_from_domain_object(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbOption)

    def test_get_db_object_db_option_raises(self):
        # given
        option = self.pl.DbOption('key', 'value')
        # expect
        self.assertRaises(Exception,
                          self.pl._get_db_object_from_domain_object,
                          option)


class PersistenceLayerInternalsTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_create_db_object_from_domain_object(self):
        # given
        task = Task('task1')
        # when
        result = self.pl._create_db_object_from_domain_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('task1', result.summary)

    def test_get_db_object_from_cache_when_none_exist_returns_none(self):
        # given
        task = Task('task1')
        # when
        result = self.pl._get_db_object_from_domain_object_in_cache(task)
        # then
        self.assertIsNone(result)

    def test_get_db_object_from_cache_when_some_exist_returns_none(self):
        # given
        task = Task('task1')
        dbtask = self.pl._create_db_object_from_domain_object(task)
        self.pl._db_by_domain[task] = dbtask
        # when
        result = self.pl._get_db_object_from_domain_object_in_cache(task)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbtask, result)

    def test_get_db_object_from_domain_object_by_id(self):
        # given
        task = Task('task1')
        dbtask = self.pl._create_db_object_from_domain_object(task)
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtask.id)
        task.id = dbtask.id
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIs(dbtask, result)

    def test_added_domain_objects_are_added_to_list_of_added_objects(self):
        # given
        task = Task('task1')
        # precondition
        self.assertEquals(0, len(self.pl._added_objects))
        # when
        self.pl.add(task)
        # then
        self.assertEqual(1, len(self.pl._added_objects))
        self.assertIn(task, self.pl._added_objects)

    def test_deleted_domain_objects_are_added_to_list_of_deleted_objects(self):
        # given
        task = Task('task1')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEquals(0, len(self.pl._deleted_objects))
        # when
        self.pl.delete(task)
        # then
        self.assertEqual(1, len(self.pl._deleted_objects))
        self.assertIn(task, self.pl._deleted_objects)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        logger = logging_util.get_logger_by_object(__name__, self)
        logger.debug('before create task')
        task = Task('task')
        logger.debug('after create task')
        logger.debug('before create tag')
        tag = Tag('tag', description='a')
        logger.debug('after create tag')
        logger.debug('before add task')
        self.pl.add(task)
        logger.debug('after add task')
        logger.debug('before add tag')
        self.pl.add(tag)
        logger.debug('after add tag')
        logger.debug('before commit')
        self.pl.commit()
        logger.debug('after commit')


class PersistenceLayerDbOnlyDeletionTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_db_only_deleting_task_removes_all_children(self):
        # given
        parent = self.pl.DbTask('parent')
        c1 = self.pl.DbTask('c1')
        c2 = self.pl.DbTask('c2')
        c3 = self.pl.DbTask('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.db.session.add(parent)
        self.pl.db.session.add(c1)
        self.pl.db.session.add(c2)
        self.pl.db.session.add(c3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(c1, parent.children)
        self.assertIn(c2, parent.children)
        self.assertIn(c3, parent.children)

        # when
        self.pl.db.session.delete(parent)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(c1, parent.children)
        self.assertNotIn(c2, parent.children)
        self.assertNotIn(c3, parent.children)
        self.assertEqual(0, len(parent.children.all()))

    def test_db_only_deleting_parent_task_nullifies_parent_and_parent_id(self):
        # given
        parent = self.pl.DbTask('parent')
        c1 = self.pl.DbTask('c1')
        c2 = self.pl.DbTask('c2')
        c3 = self.pl.DbTask('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.db.session.add(parent)
        self.pl.db.session.add(c1)
        self.pl.db.session.add(c2)
        self.pl.db.session.add(c3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(parent, c1.parent)
        self.assertIs(parent, c2.parent)
        self.assertIs(parent, c3.parent)

        # when
        self.pl.db.session.delete(parent)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(c1.parent)
        self.assertIsNone(c2.parent)
        self.assertIsNone(c3.parent)
        self.assertIsNone(c1.parent_id)
        self.assertIsNone(c2.parent_id)
        self.assertIsNone(c3.parent_id)

    def test_db_only_deleting_task_removes_task_from_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_notice_db_only_deleting_task_does_not_remove_tag_from_task(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIn(tag, task.tags)

    def test_db_only_deleting_tag_removes_tag_from_task(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(tag)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_notice_db_only_deleting_tag_does_not_remove_task_from_tag(self):
        # given
        task = self.pl.DbTask('task')
        tag = self.pl.DbTag('tag')
        task.tags.append(tag)
        self.pl.db.session.add(task)
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.db.session.delete(tag)
        self.pl.db.session.commit()

        # then
        self.assertIn(task, tag.tasks)

    def test_db_only_deleting_task_removes_task_from_user(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_notice_db_only_deleting_task_does_not_remove_user_from_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIn(user, task.users)

    def test_db_only_deleting_user_removes_user_from_task(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(user)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_notice_db_only_deleting_user_does_not_remove_task_from_user(self):
        # given
        task = self.pl.DbTask('task')
        user = self.pl.DbUser('user')
        task.users.append(user)
        self.pl.db.session.add(task)
        self.pl.db.session.add(user)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.db.session.delete(user)
        self.pl.db.session.commit()

        # then
        self.assertIn(task, user.tasks)

    def test_db_only_deleting_dependee_removes_dependee_from_dependant(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependees.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.dependees)

    def test_notice_db_only_deleting_dependee_does_not_remove_dependant(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependees.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.dependants)

    def test_db_only_deleting_dependant_removes_dependant_from_dependee(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependants.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.dependants)

    def test_notice_db_only_deleting_dependant_does_not_remove_dependee(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.dependants.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.dependees)

    def test_db_only_deleting_pbefore_removes_pbefore_from_pafter(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_before.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_before)

    def test_notice_db_only_deleting_pbefore_does_not_remove_pafter(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_before.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.prioritize_after)

    def test_db_only_deleting_pafter_removes_pafter_from_pbefore(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_after.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_after)

    def test_notice_db_only_deleting_pafter_does_not_remove_pbefore(self):
        # given
        t1 = self.pl.DbTask('t1')
        t2 = self.pl.DbTask('t2')
        t1.prioritize_after.append(t2)
        self.pl.db.session.add(t1)
        self.pl.db.session.add(t2)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.db.session.delete(t2)
        self.pl.db.session.commit()

        # then
        self.assertIn(t1, t2.prioritize_before)

    def test_db_only_deleting_task_removes_all_notes(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbNote('n1')
        n2 = self.pl.DbNote('n2')
        n3 = self.pl.DbNote('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(n1, task.notes)
        self.assertIn(n2, task.notes)
        self.assertIn(n3, task.notes)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(n1, task.notes)
        self.assertNotIn(n2, task.notes)
        self.assertNotIn(n3, task.notes)
        self.assertEqual(0, len(task.notes.all()))

    def test_db_only_deleting_task_of_notes_nullifies_task_and_task_id(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbNote('n1')
        n2 = self.pl.DbNote('n2')
        n3 = self.pl.DbNote('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)

    def test_db_only_deleting_task_removes_all_attachments(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbAttachment('n1')
        n2 = self.pl.DbAttachment('n2')
        n3 = self.pl.DbAttachment('n3')
        task.attachments.append(n1)
        task.attachments.append(n2)
        task.attachments.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIn(n1, task.attachments)
        self.assertIn(n2, task.attachments)
        self.assertIn(n3, task.attachments)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertNotIn(n1, task.attachments)
        self.assertNotIn(n2, task.attachments)
        self.assertNotIn(n3, task.attachments)
        self.assertEqual(0, len(task.attachments.all()))

    def test_db_only_deleting_task_of_atts_nullifies_task_and_task_id(self):
        # given
        task = self.pl.DbTask('task')
        n1 = self.pl.DbAttachment('n1')
        n2 = self.pl.DbAttachment('n2')
        n3 = self.pl.DbAttachment('n3')
        task.attachments.append(n1)
        task.attachments.append(n2)
        task.attachments.append(n3)
        self.pl.db.session.add(task)
        self.pl.db.session.add(n1)
        self.pl.db.session.add(n2)
        self.pl.db.session.add(n3)
        self.pl.db.session.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.db.session.delete(task)
        self.pl.db.session.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)


class PersistenceLayerDeletionTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_deleting_task_removes_all_children(self):
        # given
        parent = Task('parent')
        c1 = Task('c1')
        c2 = Task('c2')
        c3 = Task('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.add(parent)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)
        self.pl.commit()

        # precondition
        self.assertIn(c1, parent.children)
        self.assertIn(c2, parent.children)
        self.assertIn(c3, parent.children)

        # when
        self.pl.delete(parent)
        self.pl.commit()

        # then
        self.assertNotIn(c1, parent.children)
        self.assertNotIn(c2, parent.children)
        self.assertNotIn(c3, parent.children)
        self.assertEqual(0, len(parent.children))

    def test_deleting_parent_task_nullifies_parent_and_parent_id(self):
        # given
        parent = Task('parent')
        c1 = Task('c1')
        c2 = Task('c2')
        c3 = Task('c3')
        parent.children.append(c1)
        parent.children.append(c2)
        parent.children.append(c3)
        self.pl.add(parent)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)
        self.pl.commit()

        # precondition
        self.assertIs(parent, c1.parent)
        self.assertIs(parent, c2.parent)
        self.assertIs(parent, c3.parent)

        # when
        self.pl.delete(parent)
        self.pl.commit()

        # then
        self.assertIsNone(c1.parent)
        self.assertIsNone(c2.parent)
        self.assertIsNone(c3.parent)
        self.assertIsNone(c1.parent_id)
        self.assertIsNone(c2.parent_id)
        self.assertIsNone(c3.parent_id)

    def test_deleting_task_removes_task_from_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_deleting_task_removes_tag_from_task(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_deleting_tag_removes_tag_from_task(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(tag)
        self.pl.commit()

        # then
        self.assertNotIn(tag, task.tags)

    def test_deleting_tag_removes_task_from_tag(self):
        # given
        task = Task('task')
        tag = Tag('tag')
        task.tags.append(tag)
        self.pl.add(task)
        self.pl.add(tag)
        self.pl.commit()

        # precondition
        self.assertIn(tag, task.tags)
        self.assertIn(task, tag.tasks)

        # when
        self.pl.delete(tag)
        self.pl.commit()

        # then
        self.assertNotIn(task, tag.tasks)

    def test_deleting_task_removes_task_from_user(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_deleting_task_removes_user_from_task(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_deleting_user_removes_user_from_task(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(user)
        self.pl.commit()

        # then
        self.assertNotIn(user, task.users)

    def test_deleting_user_removes_task_from_user(self):
        # given
        task = Task('task')
        user = User('user')
        task.users.append(user)
        self.pl.add(task)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertIn(user, task.users)
        self.assertIn(task, user.tasks)

        # when
        self.pl.delete(user)
        self.pl.commit()

        # then
        self.assertNotIn(task, user.tasks)

    def test_deleting_dependee_removes_dependee_from_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.dependees)

    def test_deleting_dependee_removes_dependant(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependees)
        self.assertIn(t1, t2.dependants)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.dependants)

    def test_deleting_dependant_removes_dependant_from_dependee(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.dependants)

    def test_deleting_dependant_removes_dependee(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.dependants)
        self.assertIn(t1, t2.dependees)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.dependees)

    def test_deleting_pbefore_removes_pbefore_from_pafter(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_before)

    def test_deleting_pbefore_removes_pafter(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_before)
        self.assertIn(t1, t2.prioritize_after)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.prioritize_after)

    def test_deleting_pafter_removes_pafter_from_pbefore(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_after.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t2, t1.prioritize_after)

    def test_deleting_pafter_removes_pbefore(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_after.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()

        # precondition
        self.assertIn(t2, t1.prioritize_after)
        self.assertIn(t1, t2.prioritize_before)

        # when
        self.pl.delete(t2)
        self.pl.commit()

        # then
        self.assertNotIn(t1, t2.prioritize_before)

    def test_deleting_task_removes_all_notes(self):
        # given
        task = Task('task')
        n1 = Note('n1')
        n2 = Note('n2')
        n3 = Note('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.add(task)
        self.pl.add(n1)
        self.pl.add(n2)
        self.pl.add(n3)
        self.pl.commit()

        # precondition
        self.assertIn(n1, task.notes)
        self.assertIn(n2, task.notes)
        self.assertIn(n3, task.notes)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(n1, task.notes)
        self.assertNotIn(n2, task.notes)
        self.assertNotIn(n3, task.notes)
        self.assertEqual(0, len(task.notes))

    def test_deleting_task_of_notes_nullifies_task_and_task_id(self):
        # given
        task = Task('task')
        n1 = Note('n1')
        n2 = Note('n2')
        n3 = Note('n3')
        task.notes.append(n1)
        task.notes.append(n2)
        task.notes.append(n3)
        self.pl.add(task)
        self.pl.add(n1)
        self.pl.add(n2)
        self.pl.add(n3)
        self.pl.commit()

        # precondition
        self.assertIs(task, n1.task)
        self.assertIs(task, n2.task)
        self.assertIs(task, n3.task)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertIsNone(n1.task)
        self.assertIsNone(n2.task)
        self.assertIsNone(n3.task)
        self.assertIsNone(n1.task_id)
        self.assertIsNone(n2.task_id)
        self.assertIsNone(n3.task_id)

    def test_deleting_task_removes_all_attachments(self):
        # given
        task = Task('task')
        a1 = Attachment('a1')
        a2 = Attachment('a2')
        a3 = Attachment('a3')
        task.attachments.append(a1)
        task.attachments.append(a2)
        task.attachments.append(a3)
        self.pl.add(task)
        self.pl.add(a1)
        self.pl.add(a2)
        self.pl.add(a3)
        self.pl.commit()

        # precondition
        self.assertIn(a1, task.attachments)
        self.assertIn(a2, task.attachments)
        self.assertIn(a3, task.attachments)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertNotIn(a1, task.attachments)
        self.assertNotIn(a2, task.attachments)
        self.assertNotIn(a3, task.attachments)
        self.assertEqual(0, len(task.attachments))

    def test_deleting_task_of_atts_nullifies_task_and_task_id(self):
        # given
        task = Task('task')
        a1 = Attachment('a1')
        a2 = Attachment('a2')
        a3 = Attachment('a3')
        task.attachments.append(a1)
        task.attachments.append(a2)
        task.attachments.append(a3)
        self.pl.add(task)
        self.pl.add(a1)
        self.pl.add(a2)
        self.pl.add(a3)
        self.pl.commit()

        # precondition
        self.assertIs(task, a1.task)
        self.assertIs(task, a2.task)
        self.assertIs(task, a3.task)

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then
        self.assertIsNone(a1.task)
        self.assertIsNone(a2.task)
        self.assertIsNone(a3.task)
        self.assertIsNone(a1.task_id)
        self.assertIsNone(a2.task_id)
        self.assertIsNone(a3.task_id)


class AsIterableTest(unittest.TestCase):
    def test_iterable_returns_same(self):
        # expect
        self.assertEquals([1, 2, 3], as_iterable([1, 2, 3]))

    def test_non_iterable_returns_tuple(self):
        # expect
        self.assertEqual((4,), as_iterable(4))


class PersistenceLayerAddDeleteTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_add_after_add_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        # precondition
        self.assertIn(task, self.pl._added_objects)
        # when
        self.pl.add(task)
        # then
        self.assertIn(task, self.pl._added_objects)

    def test_delete_after_delete_silently_ignored(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertIn(task, self.pl._deleted_objects)
        # when
        self.pl.delete(task)
        # then
        self.assertIn(task, self.pl._deleted_objects)

    def test_delete_after_add_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        # precondition
        self.assertIn(task, self.pl._added_objects)
        self.assertNotIn(task, self.pl._deleted_objects)
        # when
        self.assertRaises(
            Exception,
            self.pl.delete,
            task)
        # then
        self.assertIn(task, self.pl._added_objects)
        self.assertNotIn(task, self.pl._deleted_objects)

    def test_add_after_delete_raises(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertNotIn(task, self.pl._added_objects)
        self.assertIn(task, self.pl._deleted_objects)
        # expect
        self.assertRaises(
            Exception,
            self.pl.add,
            task)
        # and
        self.assertNotIn(task, self.pl._added_objects)
        self.assertIn(task, self.pl._deleted_objects)


class PersistenceLayerDbDeletionTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_delete_of_db_only_object_gets_dbobj_from_db(self):
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()

        task = Task('task')
        task.id = dbtask.id

        # precondition
        self.assertEqual(0, len(self.pl._db_by_domain))
        self.assertEqual(0, len(self.pl._domain_by_db))
        self.assertEqual(0, len(self.pl._added_objects))
        self.assertEqual(0, len(self.pl._deleted_objects))

        # when
        self.pl.delete(task)
        self.pl.commit()

        # then nothing raised
        self.assertTrue(True)

    def test_delete_object_not_in_db_raises(self):

        # given
        task = Task('task')
        task.id = 1

        # expect
        self.assertRaises(Exception, self.pl.delete, task)

    def test_rollback_of_deleted_objects(self):

        # given
        task = Task('task')
        self.pl.add(task)
        task.description = 'a'
        self.pl.commit()
        self.pl.delete(task)
        task.description = 'b'

        # precondition
        self.assertIn(task, self.pl._deleted_objects)
        self.assertEqual('b', task.description)

        # when
        self.pl.rollback()

        # then
        self.assertNotIn(task, self.pl._deleted_objects)
        self.assertEqual('a', task.description)


class GetDbFromDomainTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            None)

    def test_cache_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            None)

    def test_by_id_domobj_is_none_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            None)

    def test_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object,
            self.pl.DbTask('task'))

    def test_cache_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_in_cache,
            self.pl.DbTask('task'))

    def test_by_id_not_domobj_raises(self):
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            1)
        self.assertRaises(
            Exception,
            self.pl._get_db_object_from_domain_object_by_id,
            self.pl.DbTask('task'))

    def test_id_is_none_returns_none(self):
        # given
        task = Task('task')
        # precondition
        self.assertIsNone(task.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIsNone(result)

    def test_get_attachment_from_domain(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(att.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(att)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbAttachment)
        self.assertEqual(att.timestamp, result.timestamp)
        self.assertEqual(att.path, result.path)
        self.assertEqual(att.filename, result.filename)
        self.assertEqual(att.description, result.description)

    def test_get_note_from_domain(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(note.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(note)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbNote)
        self.assertEqual(note.content, result.content)
        self.assertEqual(note.timestamp, result.timestamp)

    def test_get_task_from_domain(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(task.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(task.summary, result.summary)
        self.assertEqual(task.description, result.description)

    def test_get_tag_from_domain(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(tag.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(tag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTag)
        self.assertEqual(tag.value, result.value)
        self.assertEqual(tag.description, result.description)

    def test_get_user_from_domain(self):
        # given
        user = User('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(user)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbUser)
        self.assertEqual(user.email, result.email)
        self.assertEqual(user.hashed_password, result.hashed_password)

    def test_get_option_from_domain(self):
        # given
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(option.id)
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(option)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbOption)
        self.assertEqual(option.key, result.key)
        self.assertEqual(option.value, result.value)


class CreateDbFromDomainTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            None)

    def test_not_domain_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            self.pl.DbTask('task'))

    def test_already_cached_raises(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        task = self.pl.get_task(dbtask.id)
        # precondition
        self.assertIn(task, self.pl._db_by_domain)
        self.assertIn(dbtask, self.pl._domain_by_db)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_db_object_from_domain_object,
            task)


class GetDomainFromDbTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_none_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_domain_object_from_db_object(None))

    def test_cache_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            None)

    def test_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object,
            Task('task'))

    def test_cached_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._get_domain_object_from_db_object_in_cache,
            Task('task'))


class CreateDomainFromDbTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_none_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            None)

    def test_not_db_object_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            1)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            Task('task'))

    def test_already_cached_raises(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        task = self.pl.get_task(dbtask.id)
        # precondition
        self.assertIn(task, self.pl._db_by_domain)
        self.assertIn(dbtask, self.pl._domain_by_db)
        # expect
        self.assertRaises(
            Exception,
            self.pl._create_domain_object_from_db_object,
            dbtask)

    def test_create_attachment_from_db(self):
        # given
        dbatt = self.pl.DbAttachment('att')
        self.pl.db.session.add(dbatt)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbatt.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbatt)
        # then
        self.assertIsNotNone(result)

        self.assertIsInstance(result, Attachment)
        self.assertEqual(dbatt.timestamp, result.timestamp)
        self.assertEqual(dbatt.path, result.path)
        self.assertEqual(dbatt.filename, result.filename)
        self.assertEqual(dbatt.description, result.description)

    def test_create_note_from_db(self):
        # given
        dbnote = self.pl.DbNote('note')
        self.pl.db.session.add(dbnote)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbnote.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbnote)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Note)
        self.assertEqual(dbnote.content, result.content)
        self.assertEqual(dbnote.timestamp, result.timestamp)

    def test_create_task_from_db(self):
        # given
        dbtask = self.pl.DbTask('task')
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtask.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbtask)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Task)
        self.assertEqual(dbtask.summary, result.summary)
        self.assertEqual(dbtask.description, result.description)

    def test_create_tag_from_db(self):
        # given
        dbtag = self.pl.DbTag('tag')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtag.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbtag)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Tag)
        self.assertEqual(dbtag.value, result.value)
        self.assertEqual(dbtag.description, result.description)

    def test_create_user_from_db(self):
        # given
        dbuser = self.pl.DbUser('user')
        self.pl.db.session.add(dbuser)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbuser.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dbuser)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)
        self.assertEqual(dbuser.email, result.email)
        self.assertEqual(dbuser.hashed_password, result.hashed_password)

    def test_create_option_from_db(self):
        # given
        dboption = self.pl.DbOption('key', 'value')
        self.pl.db.session.add(dboption)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dboption.id)
        # when
        result = self.pl._create_domain_object_from_db_object(dboption)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Option)
        self.assertEqual(dboption.key, result.key)
        self.assertEqual(dboption.value, result.value)


class DomainAttrsFromDbTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_all_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._domain_attrs_from_db_all, None)

    def test_no_links_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_no_links,
            None)

    def test_links_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_links,
            None)

    def test_links_lazy_none_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl._domain_attrs_from_db_links_lazy,
            None)

    def test_all_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_all({}))

    def test_no_links_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_no_links({}))

    def test_links_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links({}))

    def test_links_lazy_empty_yields_empty(self):
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links_lazy({}))

    def test_no_links_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_no_links({}, d2)
        # then
        self.assertIs(d2, result)

    def test_links_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_links({}, d2)
        # then
        self.assertIs(d2, result)

    def test_links_lazy_passing_d2_returns_same(self):
        # given
        d2 = {}
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({}, d2)
        # then
        self.assertIs(d2, result)

    def test_no_links_parent_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'parent': 1}))

    def test_no_links_children_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'children': 1}))

    def test_no_links_tags_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'tags': 1}))

    def test_no_links_tasks_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'tasks': 1}))

    def test_no_links_users_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'users': 1}))

    def test_no_links_dependees_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'dependees': 1}))

    def test_no_links_dependants_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'dependants': 1}))

    def test_no_links_prioritize_before_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links(
                {'prioritize_before': 1}))

    def test_no_links_prioritize_after_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links(
                {'prioritize_after': 1}))

    def test_no_links_notes_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'notes': 1}))

    def test_no_links_attachments_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'attachments': 1}))

    def test_no_links_task_is_not_copied(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_no_links({'task': 1}))

    def test_no_links_non_relational_attrs_are_copied(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # when
        result = self.pl._domain_attrs_from_db_no_links(d)
        # then
        self.assertIsNot(d, result)
        self.assertEqual(d, result)

    def test_links_non_relational_attrs_are_ignored(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links(d))

    def test_links_parent_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'parent': None}))

    def test_links_children_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'children': None}))

    def test_links_tags_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'tags': None}))

    def test_links_tasks_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'tasks': None}))

    def test_links_users_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'users': None}))

    def test_links_dependees_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'dependees': None}))

    def test_links_dependants_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'dependants': None}))

    def test_links_prioritize_before_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links(
                {'prioritize_before': None}))

    def test_links_prioritize_after_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links(
                {'prioritize_after': None}))

    def test_links_notes_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'notes': None}))

    def test_links_attachments_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'attachments': None}))

    def test_links_task_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links({'task': None}))

    def test_links_parent_is_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'parent': dbtask})
        # then
        self.assertEqual({'parent': task}, result)

    def test_links_children_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'children': [dbtask]})
        # then
        self.assertEqual({'children': [task]}, result)

    def test_links_tags_are_translated(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        dbtag = self.pl._get_db_object_from_domain_object(tag)
        # when
        result = self.pl._domain_attrs_from_db_links({'tags': [dbtag]})
        # then
        self.assertEqual({'tags': [tag]}, result)

    def test_links_tasks_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'tasks': [dbtask]})
        # then
        self.assertEqual({'tasks': [task]}, result)

    def test_links_users_are_translated(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        self.pl.commit()
        dbuser = self.pl._get_db_object_from_domain_object(user)
        # when
        result = self.pl._domain_attrs_from_db_links({'users': [dbuser]})
        # then
        self.assertEqual({'users': [user]}, result)

    def test_links_dependees_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'dependees':
                                                      [dbtask]})
        # then
        self.assertEqual({'dependees': [task]}, result)

    def test_links_dependants_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'dependants':
                                                      [dbtask]})
        # then
        self.assertEqual({'dependants': [task]}, result)

    def test_links_prioritize_before_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'prioritize_before':
                                                      [dbtask]})
        # then
        self.assertEqual({'prioritize_before': [task]}, result)

    def test_links_prioritize_after_are_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'prioritize_after':
                                                      [dbtask]})
        # then
        self.assertEqual({'prioritize_after': [task]}, result)

    def test_links_notes_are_translated(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        dbnote = self.pl._get_db_object_from_domain_object(note)
        # when
        result = self.pl._domain_attrs_from_db_links({'notes': [dbnote]})
        # then
        self.assertEqual({'notes': [note]}, result)

    def test_links_attachments_are_translated(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        dbatt = self.pl._get_db_object_from_domain_object(att)
        # when
        result = self.pl._domain_attrs_from_db_links({'attachments':
                                                      [dbatt]})
        # then
        self.assertEqual({'attachments': [att]}, result)

    def test_links_task_is_translated(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links({'task': dbtask})
        # then
        self.assertEqual({'task': task}, result)

    def test_links_lazy_non_relational_attrs_are_ignored(self):
        # given
        d = {
            'timestamp': 123,
            'x': 456,
            0: 789,
            object(): None
        }
        # expect
        self.assertEqual({}, self.pl._domain_attrs_from_db_links_lazy(d))

    def test_links_lazy_parent_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'parent': None}))

    def test_links_lazy_children_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'children': None}))

    def test_links_lazy_tags_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'tags': None}))

    def test_links_lazy_tasks_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'tasks': None}))

    def test_links_lazy_users_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'users': None}))

    def test_links_lazy_dependees_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'dependees': None}))

    def test_links_lazy_dependants_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'dependants': None}))

    def test_links_lazy_prioritize_before_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy(
                {'prioritize_before': None}))

    def test_links_lazy_prioritize_after_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy(
                {'prioritize_after': None}))

    def test_links_lazy_notes_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'notes': None}))

    def test_links_lazy_attachments_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'attachments':
                                                          None}))

    def test_links_lazy_task_none_is_ignored(self):
        # expect
        self.assertEqual(
            {}, self.pl._domain_attrs_from_db_links_lazy({'task': None}))

    def test_links_lazy_parent_is_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'parent': dbtask})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('parent', result)
        self.assertTrue(callable(result['parent']))
        self.assertEqual(task, result['parent']())

    def test_links_lazy_children_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'children':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('children', result)
        self.assertIsInstance(result['children'], types.GeneratorType)
        self.assertEqual([task], list(result['children']))

    def test_links_lazy_tags_are_translated_lazily(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        dbtag = self.pl._get_db_object_from_domain_object(tag)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'tags': [dbtag]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('tags', result)
        self.assertIsInstance(result['tags'], types.GeneratorType)
        self.assertEqual([tag], list(result['tags']))

    def test_links_lazy_tasks_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'tasks': [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('tasks', result)
        self.assertIsInstance(result['tasks'], types.GeneratorType)
        self.assertEqual([task], list(result['tasks']))

    def test_links_lazy_users_are_translated_lazily(self):
        # given
        user = User('name@example.com')
        self.pl.add(user)
        self.pl.commit()
        dbuser = self.pl._get_db_object_from_domain_object(user)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'users': [dbuser]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('users', result)
        self.assertIsInstance(result['users'], types.GeneratorType)
        self.assertEqual([user], list(result['users']))

    def test_links_lazy_dependees_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'dependees':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('dependees', result)
        self.assertIsInstance(result['dependees'], types.GeneratorType)
        self.assertEqual([task], list(result['dependees']))

    def test_links_lazy_dependants_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'dependants':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('dependants', result)
        self.assertIsInstance(result['dependants'], types.GeneratorType)
        self.assertEqual([task], list(result['dependants']))

    def test_links_lazy_prioritize_before_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'prioritize_before':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('prioritize_before', result)
        self.assertIsInstance(result['prioritize_before'], types.GeneratorType)
        self.assertEqual([task], list(result['prioritize_before']))

    def test_links_lazy_prioritize_after_are_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'prioritize_after':
                                                           [dbtask]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('prioritize_after', result)
        self.assertIsInstance(result['prioritize_after'], types.GeneratorType)
        self.assertEqual([task], list(result['prioritize_after']))

    def test_links_lazy_notes_are_translated_lazily(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        dbnote = self.pl._get_db_object_from_domain_object(note)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'notes': [dbnote]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('notes', result)
        self.assertIsInstance(result['notes'], types.GeneratorType)
        self.assertEqual([note], list(result['notes']))

    def test_links_lazy_attachments_are_translated_lazily(self):
        # given
        att = Attachment('att')
        self.pl.add(att)
        self.pl.commit()
        dbatt = self.pl._get_db_object_from_domain_object(att)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'attachments':
                                                           [dbatt]})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('attachments', result)
        self.assertIsInstance(result['attachments'], types.GeneratorType)
        self.assertEqual([att], list(result['attachments']))

    def test_links_lazy_task_is_translated_lazily(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        dbtask = self.pl._get_db_object_from_domain_object(task)
        # when
        result = self.pl._domain_attrs_from_db_links_lazy({'task': dbtask})
        # then
        self.assertEqual(1, len(result))
        self.assertIn('task', result)
        self.assertTrue(callable(result['task']))
        self.assertEqual(task, result['task']())


class GetTagTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_tag_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_tag, None)

    def test_get_tag_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_tag(1))

    def test_get_tag_existing_yields_that_tag(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(tag.id)
        # when
        result = self.pl.get_tag(tag.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(tag, result)

    def test_get_db_tag_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_tag, None)

    def test_get_db_tag_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_tag(1))

    def test_get_db_tag_existing_yields_that_dbtag(self):
        # given
        dbtag = self.pl.DbTag('tag')
        self.pl.db.session.add(dbtag)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtag.id)
        # when
        result = self.pl._get_db_tag(dbtag.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbtag, result)


class GetNoteTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_note_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_note, None)

    def test_get_note_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_note(1))

    def test_get_note_existing_yields_that_note(self):
        # given
        note = Note('note')
        self.pl.add(note)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(note.id)
        # when
        result = self.pl.get_note(note.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(note, result)

    def test_get_db_note_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_note, None)

    def test_get_db_note_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_note(1))

    def test_get_db_note_existing_yields_that_dbnote(self):
        # given
        dbnote = self.pl.DbNote('note')
        self.pl.db.session.add(dbnote)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbnote.id)
        # when
        result = self.pl._get_db_note(dbnote.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbnote, result)


class GetAttachmentTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_attachment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_attachment, None)

    def test_get_attachment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_attachment(1))

    def test_get_attachment_existing_yields_that_attachment(self):
        # given
        attachment = Attachment('attachment')
        self.pl.add(attachment)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(attachment.id)
        # when
        result = self.pl.get_attachment(attachment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(attachment, result)

    def test_get_db_attachment_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_attachment, None)

    def test_get_db_attachment_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_attachment(1))

    def test_get_db_attachment_existing_yields_that_dbattachment(self):
        # given
        dbattachment = self.pl.DbAttachment('attachment')
        self.pl.db.session.add(dbattachment)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbattachment.id)
        # when
        result = self.pl._get_db_attachment(dbattachment.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbattachment, result)


class GetUserTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_user, None)

    def test_get_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_user(1))

    def test_get_user_existing_yields_that_user(self):
        # given
        user = User('user')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(user.id)
        # when
        result = self.pl.get_user(user.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(user, result)

    def test_get_db_user_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_user, None)

    def test_get_db_user_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_user(1))

    def test_get_db_user_existing_yields_that_dbuser(self):
        # given
        dbuser = self.pl.DbUser('user')
        self.pl.db.session.add(dbuser)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbuser.id)
        # when
        result = self.pl._get_db_user(dbuser.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbuser, result)


class GetOptionTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_get_option_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_option, None)

    def test_get_option_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_option(1))

    def test_get_option_existing_yields_that_option(self):
        # given
        option = Option('key', 'value')
        self.pl.add(option)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(option.id)
        # when
        result = self.pl.get_option(option.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(option, result)

    def test_get_db_option_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl._get_db_option, None)

    def test_get_db_option_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl._get_db_option(1))

    def test_get_db_option_existing_yields_that_dboption(self):
        # given
        dboption = self.pl.DbOption('key', 'value')
        self.pl.db.session.add(dboption)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dboption.id)
        # when
        result = self.pl._get_db_option(dboption.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dboption, result)


class DbTaskConstructorTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()

    def test_none_lazy_is_allowed(self):
        # when
        task = self.pl.DbTask('task', lazy={})
        # then
        self.assertIsInstance(task, self.pl.DbTask)

    def test_empty_lazy_is_allowed(self):
        # when
        task = self.pl.DbTask('task', lazy={})
        # then
        self.assertIsInstance(task, self.pl.DbTask)

    def test_non_empty_lazy_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.DbTask, 'task', lazy={'id': 1})


class DbTaskFromDictTest(unittest.TestCase):
    def setUp(self):
        self.pl = generate_pl()
        self.pl.create_all()

    def test_empty_yields_empty_dbtask(self):
        # when
        result = self.pl.DbTask.from_dict({})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.id)
        self.assertIsNone(result.summary)
        self.assertEqual('', result.description)
        self.assertFalse(result.is_done)
        self.assertFalse(result.is_deleted)
        self.assertEqual(0, result.order_num)
        self.assertIsNone(result.deadline)
        self.assertIsNone(result.expected_duration_minutes)
        self.assertIsNone(result.expected_cost)
        self.assertEqual([], list(result.tags))
        self.assertEqual([], list(result.users))
        self.assertIsNone(result.parent)
        self.assertIsNone(result.parent_id)
        self.assertEqual([], list(result.dependees))
        self.assertEqual([], list(result.dependants))
        self.assertEqual([], list(result.prioritize_before))
        self.assertEqual([], list(result.prioritize_after))

    def test_id_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'id': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.id)

    def test_valid_id_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'id': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.id)

    def test_summary_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'summary': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.summary)

    def test_valid_summary_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'summary': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('abc', result.summary)

    def test_description_none_becomes_none(self):
        # when
        result = self.pl.DbTask.from_dict({'description': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.description)

    def test_valid_description_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'description': 'abc'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('abc', result.description)

    def test_is_done_none_is_becomes_false(self):
        # when
        result = self.pl.DbTask.from_dict({'is_done': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertFalse(result.is_done)

    def test_valid_is_done_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'is_done': True})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertTrue(result.is_done)

    def test_is_deleted_none_becomes_false(self):
        # when
        result = self.pl.DbTask.from_dict({'is_deleted': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertFalse(result.is_deleted)

    def test_valid_is_deleted_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'is_deleted': True})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertTrue(result.is_deleted)

    def test_order_num_none_becomes_none(self):
        # when
        result = self.pl.DbTask.from_dict({'order_num': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.order_num)

    def test_valid_order_num_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'order_num': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.order_num)

    def test_deadline_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.deadline)

    def test_valid_deadline_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': datetime(2017, 01, 01)})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_string_deadline_becomes_datetime(self):
        # when
        result = self.pl.DbTask.from_dict({'deadline': '2017-01-01'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(datetime(2017, 01, 01), result.deadline)

    def test_expected_duration_minutes_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_duration_minutes': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.expected_duration_minutes)

    def test_valid_expected_duration_minutes_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_duration_minutes': 123})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual(123, result.expected_duration_minutes)

    def test_expected_cost_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.expected_cost)

    def test_valid_expected_cost_gets_set(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': Decimal(123.45)})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, Decimal)
        self.assertEqual(Decimal(123.45), result.expected_cost)

    def test_float_expected_cost_gets_set_as_float(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': 123.45})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, float)
        self.assertEqual(123.45, result.expected_cost)

    def test_string_expected_cost_gets_set_as_string(self):
        # when
        result = self.pl.DbTask.from_dict({'expected_cost': '123.45'})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsInstance(result.expected_cost, basestring)
        self.assertEqual('123.45', result.expected_cost)

    def test_parent_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'parent': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent)

    def test_valid_parent_gets_set(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent': parent})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIs(parent, result.parent)
        # and parent_id is not yet set
        self.assertIsNone(result.parent_id)

    def test_int_parent_raises(self):
        # expect
        self.assertRaises(
            Exception,
            self.pl.DbTask.from_dict,
            {'parent': 1})

    def test_parent_id_none_is_ignored(self):
        # when
        result = self.pl.DbTask.from_dict({'parent_id': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        # and parent is not yet set
        self.assertIsNone(result.parent)

    def test_valid_parent_id_is_ignored(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent_id': parent.id})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        # and parent is not yet set
        self.assertIsNone(result.parent)

    def test_non_int_parent_id_is_ignored(self):
        # given
        parent = self.pl.DbTask('parent')
        self.pl.db.session.add(parent)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'parent_id': parent})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.parent_id)
        self.assertIsNone(result.parent)

    def test_children_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'children': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.children))

    def test_children_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'children': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.children))

    def test_children_non_empty_yields_same(self):
        # given
        c1 = self.pl.DbTask('c1')
        self.pl.db.session.add(c1)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'children': [c1]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([c1], list(result.children))

    def test_tags_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'tags': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.tags))

    def test_tags_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'tags': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.tags))

    def test_tags_non_empty_yields_same(self):
        # given
        tag = self.pl.DbTag('tag')
        self.pl.db.session.add(tag)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'tags': [tag]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([tag], list(result.tags))

    def test_users_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'users': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.users))

    def test_users_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'users': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.users))

    def test_users_non_empty_yields_same(self):
        # given
        user = self.pl.DbUser('user')
        self.pl.db.session.add(user)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'users': [user]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([user], list(result.users))

    def test_dependees_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependees': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependees))

    def test_dependees_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependees': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependees))

    def test_dependees_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'dependees': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.dependees))

    def test_dependants_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependants': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependants))

    def test_dependants_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'dependants': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.dependants))

    def test_dependants_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'dependants': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.dependants))

    def test_prioritize_before_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_before))

    def test_prioritize_before_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'prioritize_before': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.prioritize_before))

    def test_prioritize_after_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.prioritize_after))

    def test_prioritize_after_non_empty_yields_same(self):
        # given
        task = self.pl.DbTask('task')
        self.pl.db.session.add(task)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'prioritize_after': [task]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([task], list(result.prioritize_after))

    def test_notes_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'notes': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.notes))

    def test_notes_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'notes': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.notes))

    def test_notes_non_empty_yields_same(self):
        # given
        note = self.pl.DbNote('note')
        self.pl.db.session.add(note)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'notes': [note]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([note], list(result.notes))

    def test_attachments_none_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'attachments': None})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.attachments))

    def test_attachments_empty_yields_empty(self):
        # when
        result = self.pl.DbTask.from_dict({'attachments': []})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([], list(result.attachments))

    def test_attachments_non_empty_yields_same(self):
        # given
        attachment = self.pl.DbAttachment('attachment')
        self.pl.db.session.add(attachment)
        self.pl.db.session.commit()
        # when
        result = self.pl.DbTask.from_dict({'attachments': [attachment]})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual([attachment], list(result.attachments))

    def test_none_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTask.from_dict({}, lazy=None)
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.id)
        self.assertIsNone(result.summary)
        self.assertEqual('', result.description)
        self.assertFalse(result.is_done)
        self.assertFalse(result.is_deleted)
        self.assertEqual(0, result.order_num)
        self.assertIsNone(result.deadline)
        self.assertIsNone(result.expected_duration_minutes)
        self.assertIsNone(result.expected_cost)
        self.assertEqual([], list(result.tags))
        self.assertEqual([], list(result.users))
        self.assertIsNone(result.parent)
        self.assertIsNone(result.parent_id)
        self.assertEqual([], list(result.dependees))
        self.assertEqual([], list(result.dependants))
        self.assertEqual([], list(result.prioritize_before))
        self.assertEqual([], list(result.prioritize_after))

    def test_empty_lazy_does_not_raise(self):
        # when
        result = self.pl.DbTask.from_dict({}, lazy={})
        # then
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertIsNone(result.id)
        self.assertIsNone(result.summary)
        self.assertEqual('', result.description)
        self.assertFalse(result.is_done)
        self.assertFalse(result.is_deleted)
        self.assertEqual(0, result.order_num)
        self.assertIsNone(result.deadline)
        self.assertIsNone(result.expected_duration_minutes)
        self.assertIsNone(result.expected_cost)
        self.assertEqual([], list(result.tags))
        self.assertEqual([], list(result.users))
        self.assertIsNone(result.parent)
        self.assertIsNone(result.parent_id)
        self.assertEqual([], list(result.dependees))
        self.assertEqual([], list(result.dependants))
        self.assertEqual([], list(result.prioritize_before))
        self.assertEqual([], list(result.prioritize_after))

    def test_non_none_lazy_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.pl.DbTask.from_dict,
            {},
            lazy={'attachments': None})
