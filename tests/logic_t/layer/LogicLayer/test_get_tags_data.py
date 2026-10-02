#!/usr/bin/env python

import unittest

from tests.logic_t.layer.LogicLayer.util import generate_ll


class GetTagsDataTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.b = self.pl.create_tag('b')
        self.pl.add(self.b)
        self.c = self.pl.create_tag('c')
        self.pl.add(self.c)
        self.a = self.pl.create_tag('a')
        self.pl.add(self.a)
        self.pl.commit()

    def test_defaults_sort_by_name_ascending(self):
        # when
        result = self.ll.get_tags_data()
        # then
        self.assertEqual('name', result['sort'])
        self.assertEqual('asc', result['order'])
        self.assertEqual(20, result['pager'].per_page)
        self.assertEqual([self.a, self.b, self.c], result['pager'].items)

    def test_sort_by_name_descending(self):
        # when
        result = self.ll.get_tags_data(sort='name', order='desc')
        # then
        self.assertEqual([self.c, self.b, self.a], result['pager'].items)

    def test_sort_by_id_ascending(self):
        # when
        result = self.ll.get_tags_data(sort='id', order='asc')
        # then
        self.assertEqual([self.b, self.c, self.a], result['pager'].items)

    def test_sort_by_id_descending(self):
        # when
        result = self.ll.get_tags_data(sort='id', order='desc')
        # then
        self.assertEqual([self.a, self.c, self.b], result['pager'].items)

    def test_paginates(self):
        # when
        result = self.ll.get_tags_data(page_num=2, tags_per_page=2)
        # then
        pager = result['pager']
        self.assertEqual(2, pager.page)
        self.assertEqual(2, pager.pages)
        self.assertEqual(3, pager.total)
        self.assertEqual([self.c], pager.items)

    def test_task_counts_respect_visibility(self):
        # given
        user = self.pl.create_user('user@example.org')
        admin = self.pl.create_user('admin@example.org', is_admin=True)
        public = self.pl.create_task('public', is_public=True)
        private = self.pl.create_task('private')
        mine = self.pl.create_task('mine', is_done=True)
        mine.users.append(user)
        public.tags.extend([self.a, self.b])
        private.tags.append(self.a)
        mine.tags.append(self.a)
        for obj in [user, admin, public, private, mine]:
            self.pl.add(obj)
        self.pl.commit()
        # expect
        self.assertEqual({self.a.id: 1, self.b.id: 1},
                         self.ll.get_tags_data()['task_counts'])
        self.assertEqual({self.a.id: 2, self.b.id: 1},
                         self.ll.get_tags_data(user)['task_counts'])
        self.assertEqual({self.a.id: 3, self.b.id: 1},
                         self.ll.get_tags_data(admin)['task_counts'])

    def test_task_counts_only_include_tags_on_page(self):
        # given
        task = self.pl.create_task('task', is_public=True)
        task.tags.extend([self.a, self.c])
        self.pl.add(task)
        self.pl.commit()
        # when
        result = self.ll.get_tags_data(page_num=1, tags_per_page=2)
        # then
        self.assertEqual({self.a.id: 1}, result['task_counts'])

    def test_unknown_sort_raises(self):
        self.assertRaises(ValueError, self.ll.get_tags_data, sort='value')

    def test_unknown_order_raises(self):
        self.assertRaises(ValueError, self.ll.get_tags_data, order='up')
