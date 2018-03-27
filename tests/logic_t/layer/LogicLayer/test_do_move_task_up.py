#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from util import generate_ll


class DoMoveTaskUpTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl
        self.user = self.pl.create_user('name@example.com')
        self.task = self.pl.create_task('task')
        self.task.id = 1

    def test_task_id_none_raises(self):
        self.assertRaises(
            NotFound,
            self.ll.do_move_task_up,
            None, False, self.user)

    def test_non_existent_task(self):
        # given
        self.pl.add(self.user)
        self.pl.commit()
        # expect
        self.assertRaises(
            NotFound,
            self.ll.do_move_task_up,
            self.task.id + 1, False, self.user)

    def test_user_none_raises(self):
        # given
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_move_task_up,
            self.task.id, False, None)

    def test_not_authorized_user_raises(self):
        # given
        self.pl.add(self.user)
        self.pl.add(self.task)
        self.pl.commit()
        # expect
        self.assertRaises(
            Forbidden,
            self.ll.do_move_task_up,
            self.task.id, False, self.user)

    def test_moves_task_up(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 10
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 5
        t2.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertEqual(10, t1.order_num)
        self.assertEqual(5, t2.order_num)
        # when
        result = self.ll.do_move_task_up(t2.id, False, self.user)
        # then
        self.assertIs(t2, result)
        self.assertEqual(5, t1.order_num)
        self.assertEqual(10, t2.order_num)

    def test_move_does_not_affect_children(self):
        # given
        p1 = self.pl.create_task('p1')
        p1.order_num = 7
        p1.users.append(self.user)
        c1 = self.pl.create_task('c1')
        c1.parent = p1
        c1.order_num = 6
        c1.users.append(self.user)
        c2 = self.pl.create_task('c2')
        c2.parent = p1
        c2.order_num = 5
        c2.users.append(self.user)
        p2 = self.pl.create_task('p2')
        p2.order_num = 4
        p2.users.append(self.user)
        c3 = self.pl.create_task('c3')
        c3.parent = p2
        c3.order_num = 3
        c3.users.append(self.user)
        c4 = self.pl.create_task('c4')
        c4.parent = p2
        c4.order_num = 2
        c4.users.append(self.user)
        self.pl.add(p1)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(p2)
        self.pl.add(c3)
        self.pl.add(c4)
        self.pl.commit()
        # precondition
        self.assertEqual(7, p1.order_num)
        self.assertEqual(6, c1.order_num)
        self.assertEqual(5, c2.order_num)
        self.assertEqual(4, p2.order_num)
        self.assertEqual(3, c3.order_num)
        self.assertEqual(2, c4.order_num)
        # when
        result = self.ll.do_move_task_up(p2.id, False, self.user)
        # then
        self.assertIs(p2, result)
        self.assertEqual(4, p1.order_num)  #
        self.assertEqual(6, c1.order_num)
        self.assertEqual(5, c2.order_num)
        self.assertEqual(7, p2.order_num)  #
        self.assertEqual(3, c3.order_num)
        self.assertEqual(2, c4.order_num)

    def test_move_does_not_affect_other_siblings_nor_parent(self):
        # given
        p1 = self.pl.create_task('p1')
        p1.order_num = 7
        p1.users.append(self.user)
        c1 = self.pl.create_task('c1')
        c1.parent = p1
        c1.order_num = 6
        c1.users.append(self.user)
        c2 = self.pl.create_task('c2')
        c2.parent = p1
        c2.order_num = 5
        c2.users.append(self.user)
        c3 = self.pl.create_task('c3')
        c3.parent = p1
        c3.order_num = 4
        c3.users.append(self.user)
        c4 = self.pl.create_task('c4')
        c4.parent = p1
        c4.order_num = 3
        c4.users.append(self.user)
        c5 = self.pl.create_task('c5')
        c5.parent = p1
        c5.order_num = 2
        c5.users.append(self.user)
        self.pl.add(p1)
        self.pl.add(c1)
        self.pl.add(c2)
        self.pl.add(c3)
        self.pl.add(c4)
        self.pl.add(c5)
        self.pl.commit()
        # precondition
        self.assertEqual(7, p1.order_num)
        self.assertEqual(6, c1.order_num)
        self.assertEqual(5, c2.order_num)
        self.assertEqual(4, c3.order_num)
        self.assertEqual(3, c4.order_num)
        self.assertEqual(2, c5.order_num)
        # when
        result = self.ll.do_move_task_up(c3.id, False, self.user)
        # then
        self.assertIs(c3, result)
        self.assertEqual(7, p1.order_num)
        self.assertEqual(6, c1.order_num)
        self.assertEqual(4, c2.order_num)  #
        self.assertEqual(5, c3.order_num)  #
        self.assertEqual(3, c4.order_num)
        self.assertEqual(2, c5.order_num)

    def test_move_does_not_affect_top_most(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 6
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 5
        t2.users.append(self.user)
        t3 = self.pl.create_task('t3')
        t3.order_num = 4
        t3.users.append(self.user)
        t4 = self.pl.create_task('t4')
        t4.order_num = 3
        t4.users.append(self.user)
        t5 = self.pl.create_task('t5')
        t5.order_num = 2
        t5.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)
        self.pl.add(t5)
        self.pl.commit()
        # precondition
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)
        self.assertEqual(4, t3.order_num)
        self.assertEqual(3, t4.order_num)
        self.assertEqual(2, t5.order_num)
        # when
        result = self.ll.do_move_task_up(t3.id, False, self.user)
        # then
        self.assertIs(t3, result)
        self.assertEqual(6, t1.order_num)
        self.assertEqual(4, t2.order_num)  #
        self.assertEqual(5, t3.order_num)  #
        self.assertEqual(3, t4.order_num)
        self.assertEqual(2, t5.order_num)

    def test_move_does_not_move_first_task(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 6
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 5
        t2.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.commit()
        # precondition
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)
        # when
        result = self.ll.do_move_task_up(t1.id, False, self.user)
        # then
        self.assertIs(t1, result)
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)

    def test_move_show_deleted_false_skips_deleted_tasks(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 6
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 5
        t2.users.append(self.user)
        t3 = self.pl.create_task('t3', is_deleted=True)
        t3.order_num = 4
        t3.users.append(self.user)
        t4 = self.pl.create_task('t4')
        t4.order_num = 3
        t4.users.append(self.user)
        t5 = self.pl.create_task('t5')
        t5.order_num = 2
        t5.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)
        self.pl.add(t5)
        self.pl.commit()
        # precondition
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)
        self.assertEqual(4, t3.order_num)
        self.assertEqual(3, t4.order_num)
        self.assertEqual(2, t5.order_num)
        # when
        result = self.ll.do_move_task_up(t4.id, False, self.user)
        # then
        self.assertIs(t4, result)
        self.assertEqual(6, t1.order_num)
        self.assertEqual(3, t2.order_num)  #
        self.assertEqual(4, t3.order_num)  #
        self.assertEqual(5, t4.order_num)  #
        self.assertEqual(2, t5.order_num)

    def test_move_show_deleted_true_does_not_skip_deleted_tasks(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 6
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 5
        t2.users.append(self.user)
        t3 = self.pl.create_task('t3', is_deleted=True)
        t3.order_num = 4
        t3.users.append(self.user)
        t4 = self.pl.create_task('t4')
        t4.order_num = 3
        t4.users.append(self.user)
        t5 = self.pl.create_task('t5')
        t5.order_num = 2
        t5.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)
        self.pl.add(t5)
        self.pl.commit()
        # precondition
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)
        self.assertEqual(4, t3.order_num)
        self.assertEqual(3, t4.order_num)
        self.assertEqual(2, t5.order_num)
        # when
        result = self.ll.do_move_task_up(t4.id, True, self.user)
        # then
        self.assertIs(t4, result)
        self.assertEqual(6, t1.order_num)
        self.assertEqual(5, t2.order_num)
        self.assertEqual(3, t3.order_num)  #
        self.assertEqual(4, t4.order_num)  #
        self.assertEqual(2, t5.order_num)

    def test_move_same_order_num_causes_tasks_to_be_reordered(self):
        # given
        t1 = self.pl.create_task('t1')
        t1.order_num = 6
        t1.users.append(self.user)
        t2 = self.pl.create_task('t2')
        t2.order_num = 4
        t2.users.append(self.user)
        t3 = self.pl.create_task('t3')
        t3.order_num = 4
        t3.users.append(self.user)
        t4 = self.pl.create_task('t4')
        t4.order_num = 3
        t4.users.append(self.user)
        t5 = self.pl.create_task('t5')
        t5.order_num = 2
        t5.users.append(self.user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(t3)
        self.pl.add(t4)
        self.pl.add(t5)
        self.pl.commit()
        # precondition
        self.assertEqual(6, t1.order_num)
        self.assertEqual(4, t2.order_num)
        self.assertEqual(4, t3.order_num)
        self.assertEqual(3, t4.order_num)
        self.assertEqual(2, t5.order_num)
        # when
        result = self.ll.do_move_task_up(t3.id, False, self.user)
        # then
        self.assertIs(t3, result)
        self.assertEqual(10, t1.order_num)
        self.assertEqual(6, t2.order_num)
        self.assertEqual(8, t3.order_num)
        self.assertEqual(4, t4.order_num)
        self.assertEqual(2, t5.order_num)
