import logging

from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task
from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class PaginatedTasksTest(PersistenceLayerTestBase):
    def setUp(self):
        self._logger = logging.getLogger('test')
        self._logger.debug(u'setUp generate_app')
        self.pl = self.generate_pl()
        self._logger.debug(u'setUp create_all')
        self.pl.db.drop_all()
        self.pl.create_all()
        self._logger.debug(u'setUp create objects')

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
        self._logger.debug(u'setUp connect objects')
        self.t2.tags.add(self.tag1)
        self.t3.tags.add(self.tag1)
        self.t3.tags.add(self.tag2)
        self.t4.tags.add(self.tag1)
        self._logger.debug(u'setUp add objects')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)
        self._logger.debug(u'setUp commit')
        self.pl.commit()

        self._logger.debug(u'setUp finished')

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
        self._logger.debug(u'when')
        tasks = self.pl.get_tasks(tags_contains=self.tag1)
        # then
        self._logger.debug(u'then')
        tasks2 = set(tasks)
        self.assertEqual({self.t2, self.t3, self.t4}, tasks2)
        # when
        self._logger.debug(u'when')
        count = self.pl.count_tasks(tags_contains=self.tag1)
        # then
        self._logger.debug(u'then')
        self.assertEqual(3, count)
        # expect
        self._logger.debug(u'expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))
        # expect
        self._logger.debug(u'expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))
        # expect
        self._logger.debug(u'expect')
        self.assertEqual(3, self.pl.count_tasks(tags_contains=self.tag1))

        # when
        self._logger.debug(u'when')
        pager = self.pl.get_paginated_tasks(page_num=1, tasks_per_page=2,
                                            tags_contains=self.tag1)
        # then
        self._logger.debug(u'then 1')
        self.assertIsNotNone(pager)
        self._logger.debug(u'then 2')
        self.assertEqual(1, pager.page)
        self._logger.debug(u'then 3')
        self.assertEqual(2, pager.per_page)
        self._logger.debug(u'then 4')
        self.assertEqual(3, pager.total)
        self._logger.debug(u'then 5')
        items = list(pager.items)
        self._logger.debug(u'then 6')
        self.assertEqual(2, len(items))
        self._logger.debug(u'then 7')
        self.assertIn(self.tag1, items[0].tags)
        self._logger.debug(u'then 8')
        self.assertIn(items[0], {self.t2, self.t3, self.t4})
        self._logger.debug(u'then 9')
        self.assertIn(self.tag1, items[1].tags)
        self._logger.debug(u'then 10')
        self.assertIn(items[1], {self.t2, self.t3, self.t4})
        self._logger.debug(u'when 11')

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


class PaginatedTasksNullTasksPerPageTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.pl.add(Task('t1'))
        self.pl.add(Task('t2'))
        self.pl.add(Task('t3'))
        self.pl.add(Task('t4'))
        self.pl.add(Task('t5'))
        self.pl.add(Task('t6'))
        self.pl.add(Task('t7'))
        self.pl.add(Task('t8'))
        self.pl.add(Task('t9'))
        self.pl.add(Task('t10'))
        self.pl.add(Task('t11'))
        self.pl.add(Task('t12'))
        self.pl.add(Task('t13'))
        self.pl.add(Task('t14'))
        self.pl.add(Task('t15'))
        self.pl.add(Task('t16'))
        self.pl.add(Task('t17'))
        self.pl.add(Task('t18'))
        self.pl.add(Task('t19'))
        self.pl.add(Task('t20'))
        self.pl.add(Task('t21'))
        self.pl.commit()

    def test_test_get_paginated_tasks_none_tasks_per_page_default_twenty(self):
        # precondition
        self.assertEqual(21, self.pl.count_tasks())
        # when
        result = self.pl.get_paginated_tasks(page_num=1)
        # then
        self.assertEqual(20, len(result.items))
        self.assertEqual(1, result.page)

    def test_get_paginate_tasks_string_page_num_raises(self):
        # expect
        self.assertRaises(
            TypeError,
            self.pl.get_paginated_tasks,
            page_num='1')

    def test_get_paginate_tasks_non_number_page_num_raises(self):
        # expect
        self.assertRaises(TypeError, self.pl.get_paginated_tasks,
                          page_num='asdf')

    def test_get_paginate_tasks_zero_page_num_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_paginated_tasks,
                          page_num=0)

    def test_get_paginate_tasks_negative_page_num_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_paginated_tasks,
                          page_num=-1)

    def test_get_paginate_tasks_string_tasks_per_page_raises(self):
        # expect
        self.assertRaises(
            TypeError,
            self.pl.get_paginated_tasks,
            tasks_per_page='1')

    def test_get_paginate_tasks_non_number_tasks_per_page_raises(self):
        # expect
        self.assertRaises(TypeError, self.pl.get_paginated_tasks,
                          tasks_per_page='asdf')

    def test_get_paginate_tasks_zero_tasks_per_page_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_paginated_tasks,
                          tasks_per_page=0)

    def test_get_paginate_tasks_negative_tasks_per_page_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_paginated_tasks,
                          tasks_per_page=-1)
