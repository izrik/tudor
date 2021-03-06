#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden, Conflict

from tests.logic_t.layer.LogicLayer.util import generate_ll


class LongOrderChangeTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_reorders_tasks(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        task_to_move.order_num = 1
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        target.order_num = 2
        self.pl.add(target)
        admin = self.pl.create_user('user@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertEqual(1, task_to_move.order_num)
        self.assertEqual(2, target.order_num)
        # when
        result = self.ll.do_long_order_change(task_to_move.id, target.id,
                                              admin)
        self.pl.commit()
        # then
        self.assertEqual(4, task_to_move.order_num)
        self.assertEqual(2, target.order_num)
        # and
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        self.assertIs(task_to_move, result[0])
        self.assertIs(target, result[1])

    def test_task_to_move_id_is_none_raises(self):
        # given
        target = self.pl.create_task('target')
        self.pl.add(target)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_long_order_change,
            None, target.id, admin)

    def test_task_to_move_not_found_raises(self):
        # given
        target = self.pl.create_task('target')
        self.pl.add(target)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIsNone(self.pl.get_task(target.id + 1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_long_order_change,
            target.id + 1, target.id, admin)

    def test_target_id_is_none_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_long_order_change,
            task_to_move.id, None, admin)

    def test_target_not_found_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        admin = self.pl.create_user('admin@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIsNone(self.pl.get_task(task_to_move.id + 1))
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_long_order_change,
            task_to_move.id, task_to_move.id + 1, admin)

    def test_current_user_is_none_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        self.pl.add(target)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_long_order_change,
            task_to_move.id, target.id, None)

    def test_user_not_authorized_on_either_task_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        self.pl.add(target)
        user = self.pl.create_user('user@example.com')
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertNotIn(task_to_move, user.tasks)
        self.assertNotIn(user, task_to_move.users)
        self.assertNotIn(target, user.tasks)
        self.assertNotIn(user, target.users)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_long_order_change,
            task_to_move.id, target.id, user)

    def test_user_not_authorized_on_task_to_move_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        self.pl.add(target)
        user = self.pl.create_user('user@example.com')
        target.users.append(user)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertNotIn(task_to_move, user.tasks)
        self.assertNotIn(user, task_to_move.users)
        self.assertIn(target, user.tasks)
        self.assertIn(user, target.users)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_long_order_change,
            task_to_move.id, target.id, user)

    def test_user_not_authorized_on_target_raises(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        self.pl.add(target)
        user = self.pl.create_user('user@example.com')
        task_to_move.users.append(user)
        self.pl.add(user)
        self.pl.commit()
        # precondition
        self.assertIn(task_to_move, user.tasks)
        self.assertIn(user, task_to_move.users)
        self.assertNotIn(target, user.tasks)
        self.assertNotIn(user, target.users)
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_long_order_change,
            task_to_move.id, target.id, user)

    def test_different_parents_raises(self):
        # given
        p1 = self.pl.create_task('p1')
        self.pl.add(p1)
        p2 = self.pl.create_task('p2')
        self.pl.add(p2)
        task_to_move = self.pl.create_task('task_to_move')
        task_to_move.order_num = 1
        task_to_move.parent = p1
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        target.order_num = 2
        target.parent = p2
        self.pl.add(target)
        admin = self.pl.create_user('user@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertIsNot(task_to_move.parent, target.parent)
        self.assertNotEqual(task_to_move.parent_id, target.parent_id)
        # when
        self.assertRaises(
            Conflict,
            self.ll.do_long_order_change,
            task_to_move.id, target.id, admin)

    def test_reorders_all_siblings_even_those_not_involved_in_the_move(self):
        # given
        task_to_move = self.pl.create_task('task_to_move')
        task_to_move.order_num = 43
        self.pl.add(task_to_move)
        target = self.pl.create_task('target')
        target.order_num = 47
        self.pl.add(target)
        s1 = self.pl.create_task('s1')
        s1.order_num = 41
        self.pl.add(s1)
        s2 = self.pl.create_task('s2')
        s2.order_num = 42
        self.pl.add(s2)

        s3 = self.pl.create_task('s3')
        s3.order_num = 44
        self.pl.add(s3)
        s4 = self.pl.create_task('s4')
        s4.order_num = 45
        self.pl.add(s4)
        s5 = self.pl.create_task('s5')
        s5.order_num = 46
        self.pl.add(s5)
        s6 = self.pl.create_task('s6')
        s6.order_num = 48
        self.pl.add(s6)
        s7 = self.pl.create_task('s7')
        s7.order_num = 49
        self.pl.add(s7)
        s8 = self.pl.create_task('s8')
        s8.order_num = 50
        self.pl.add(s8)

        admin = self.pl.create_user('user@example.com', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # precondition
        self.assertEqual(41, s1.order_num)
        self.assertEqual(42, s2.order_num)
        self.assertEqual(43, task_to_move.order_num)
        self.assertEqual(44, s3.order_num)
        self.assertEqual(45, s4.order_num)
        self.assertEqual(46, s5.order_num)
        self.assertEqual(47, target.order_num)
        self.assertEqual(48, s6.order_num)
        self.assertEqual(49, s7.order_num)
        self.assertEqual(50, s8.order_num)
        # when
        self.ll.do_long_order_change(task_to_move.id, target.id, admin)
        self.pl.commit()
        # then
        self.assertEqual(2, s1.order_num)
        self.assertEqual(4, s2.order_num)
        self.assertEqual(6, s3.order_num)
        self.assertEqual(8, s4.order_num)
        self.assertEqual(10, s5.order_num)
        self.assertEqual(12, target.order_num)
        self.assertEqual(14, task_to_move.order_num)  # this one moved
        self.assertEqual(16, s6.order_num)
        self.assertEqual(18, s7.order_num)
        self.assertEqual(20, s8.order_num)
