#!/usr/bin/env python

import unittest

from models.task import Task


class TaskPrioritizeTest(unittest.TestCase):
    def test_setting_task_as_before_sets_other_task_as_after(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')

        # precondition
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))

        # when
        t1.prioritize_before.append(t2)

        # then
        self.assertEqual(1, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(1, len(t2.prioritize_after))
        self.assertTrue(t2 in t1.prioritize_before)
        self.assertTrue(t1 in t2.prioritize_after)

    def test_setting_task_as_after_sets_other_task_as_before(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')

        # precondition
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(0, len(t1.prioritize_after))
        self.assertEqual(0, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))

        # when
        t1.prioritize_after.append(t2)

        # then
        self.assertEqual(0, len(t1.prioritize_before))
        self.assertEqual(1, len(t1.prioritize_after))
        self.assertEqual(1, len(t2.prioritize_before))
        self.assertEqual(0, len(t2.prioritize_after))
        self.assertTrue(t2 in t1.prioritize_after)
        self.assertTrue(t1 in t2.prioritize_before)

    def test_cycle_check_yields_false_for_no_cycles(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)

        # expect
        self.assertFalse(t1.contains_priority_cycle())
        self.assertFalse(t2.contains_priority_cycle())

    def test_cycle_check_yields_true_for_cycles(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t1.prioritize_before.append(t2)
        t2.prioritize_before.append(t1)

        # expect
        self.assertTrue(t1.contains_priority_cycle())
        self.assertTrue(t2.contains_priority_cycle())

    def test_cycle_check_yields_true_for_long_cycles(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t3 = Task('t3')
        t4 = Task('t4')
        t5 = Task('t5')
        t6 = Task('t6')
        t1.prioritize_before.append(t2)
        t2.prioritize_before.append(t3)
        t3.prioritize_before.append(t4)
        t4.prioritize_before.append(t5)
        t5.prioritize_before.append(t6)
        t6.prioritize_before.append(t1)

        # expect
        self.assertTrue(t1.contains_priority_cycle())
        self.assertTrue(t2.contains_priority_cycle())
        self.assertTrue(t3.contains_priority_cycle())
        self.assertTrue(t4.contains_priority_cycle())
        self.assertTrue(t5.contains_priority_cycle())
        self.assertTrue(t6.contains_priority_cycle())

    def test_cycle_check_yields_false_for_trees(self):
        # given
        t1 = Task('t1')
        t2 = Task('t2')
        t3 = Task('t3')
        t4 = Task('t4')
        t1.prioritize_before.append(t2)
        t1.prioritize_before.append(t3)
        t2.prioritize_before.append(t4)
        t3.prioritize_before.append(t4)

        # expect
        self.assertFalse(t1.contains_priority_cycle())
        self.assertFalse(t2.contains_priority_cycle())
        self.assertFalse(t3.contains_priority_cycle())
        self.assertFalse(t4.contains_priority_cycle())

