
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class PagerTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = self.pl.create_task('t1')
        self.t1.order_num = 11
        self.t2 = self.pl.create_task('t2')
        self.t2.order_num = 23
        self.t3 = self.pl.create_task('t3')
        self.t3.order_num = 37
        self.t4 = self.pl.create_task('t4')
        self.t4.order_num = 47
        self.t5 = self.pl.create_task('t5')
        self.t5.order_num = 53
        self.t6 = self.pl.create_task('t6')
        self.t5.order_num = 67
        self.t7 = self.pl.create_task('t7')
        self.t5.order_num = 71
        self.t8 = self.pl.create_task('t8')
        self.t5.order_num = 83
        self.t9 = self.pl.create_task('t9')
        self.t5.order_num = 97
        self.t10 = self.pl.create_task('t10')
        self.t5.order_num = 101
        self.t11 = self.pl.create_task('t11')
        self.t5.order_num = 113
        self.t12 = self.pl.create_task('t12')
        self.t12.order_num = 127
        self.t13 = self.pl.create_task('t13')
        self.t13.order_num = 131
        self.t14 = self.pl.create_task('t14')
        self.t14.order_num = 149
        self.t15 = self.pl.create_task('t15')
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
