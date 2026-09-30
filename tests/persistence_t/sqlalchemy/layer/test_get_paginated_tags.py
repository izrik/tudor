from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class GetPaginatedTagsTest(PersistenceLayerTestBase):
    def setUp(self):
        super().setUp()
        self.b = self.pl.create_tag('b')
        self.pl.add(self.b)
        self.c = self.pl.create_tag('c')
        self.pl.add(self.c)
        self.a = self.pl.create_tag('a')
        self.pl.add(self.a)
        self.pl.commit()

    def test_defaults_return_all_tags_on_one_page(self):
        # when
        pager = self.pl.get_paginated_tags()
        # then
        self.assertEqual(1, pager.page)
        self.assertEqual(20, pager.per_page)
        self.assertEqual(3, pager.total)
        self.assertEqual(1, pager.pages)
        self.assertEqual({self.a, self.b, self.c}, set(pager.items))

    def test_tags_per_page_limits_items(self):
        # when
        pager = self.pl.get_paginated_tags(
            order_by=[[self.pl.TAG_VALUE, self.pl.ASCENDING]],
            tags_per_page=2)
        # then
        self.assertEqual(3, pager.total)
        self.assertEqual(2, pager.pages)
        self.assertEqual([self.a, self.b], pager.items)

    def test_page_num_selects_page(self):
        # when
        pager = self.pl.get_paginated_tags(
            order_by=[[self.pl.TAG_VALUE, self.pl.ASCENDING]],
            page_num=2, tags_per_page=2)
        # then
        self.assertEqual(2, pager.page)
        self.assertEqual([self.c], pager.items)

    def test_order_by_value_descending(self):
        # when
        pager = self.pl.get_paginated_tags(
            order_by=[[self.pl.TAG_VALUE, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.c, self.b, self.a], pager.items)

    def test_order_by_id_ascending(self):
        # when
        pager = self.pl.get_paginated_tags(order_by=[self.pl.TAG_ID])
        # then
        self.assertEqual([self.b, self.c, self.a], pager.items)

    def test_order_by_id_descending(self):
        # when
        pager = self.pl.get_paginated_tags(
            order_by=[[self.pl.TAG_ID, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.a, self.c, self.b], pager.items)

    def test_invalid_page_num_raises(self):
        self.assertRaises(ValueError, self.pl.get_paginated_tags, page_num=0)
        self.assertRaises(TypeError, self.pl.get_paginated_tags,
                          page_num='1')

    def test_invalid_tags_per_page_raises(self):
        self.assertRaises(ValueError, self.pl.get_paginated_tags,
                          tags_per_page=0)
        self.assertRaises(TypeError, self.pl.get_paginated_tags,
                          tags_per_page='1')

    def test_unknown_order_field_raises(self):
        self.assertRaises(Exception, self.pl.get_paginated_tags,
                          order_by=[self.pl.ORDER_NUM])
