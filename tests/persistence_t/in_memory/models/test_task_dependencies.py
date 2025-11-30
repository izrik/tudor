#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import IMTask


class TaskDependenciesTest(unittest.TestCase):

    def test_setting_task_as_dependee_sets_other_task_as_dependant(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependees.append(t2)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

    def test_setting_task_as_dependant_sets_other_task_as_dependee(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependants.append(t2)

        # then
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

    def test_cycle_check_yields_false_for_no_cycles(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')
        t1.dependants.append(t2)

        # expect
        self.assertFalse(t1.contains_dependency_cycle())
        self.assertFalse(t2.contains_dependency_cycle())

    def test_cycle_check_yields_true_for_cycles(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')
        t1.dependants.append(t2)
        t2.dependants.append(t1)

        # expect
        self.assertTrue(t1.contains_dependency_cycle())
        self.assertTrue(t2.contains_dependency_cycle())

    def test_cycle_check_yields_true_for_long_cycles(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')
        t3 = IMTask('t3')
        t4 = IMTask('t4')
        t5 = IMTask('t5')
        t6 = IMTask('t6')
        t1.dependants.append(t2)
        t2.dependants.append(t3)
        t3.dependants.append(t4)
        t4.dependants.append(t5)
        t5.dependants.append(t6)
        t6.dependants.append(t1)

        # expect
        self.assertTrue(t1.contains_dependency_cycle())
        self.assertTrue(t2.contains_dependency_cycle())
        self.assertTrue(t3.contains_dependency_cycle())
        self.assertTrue(t4.contains_dependency_cycle())
        self.assertTrue(t5.contains_dependency_cycle())
        self.assertTrue(t6.contains_dependency_cycle())

    def test_cycle_check_yields_false_for_trees(self):
        # given
        t1 = IMTask('t1')
        t2 = IMTask('t2')
        t3 = IMTask('t3')
        t4 = IMTask('t4')
        t1.dependants.append(t2)
        t1.dependants.append(t3)
        t2.dependants.append(t4)
        t3.dependants.append(t4)

        # expect
        self.assertFalse(t1.contains_dependency_cycle())
        self.assertFalse(t2.contains_dependency_cycle())
        self.assertFalse(t3.contains_dependency_cycle())
        self.assertFalse(t4.contains_dependency_cycle())
