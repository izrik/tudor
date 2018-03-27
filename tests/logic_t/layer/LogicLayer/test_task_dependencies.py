#!/usr/bin/env python

import unittest

from werkzeug.exceptions import NotFound, Forbidden

from tests.logic_t.layer.LogicLayer.util import generate_ll


class TaskDependeesLogicLayerTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_add_dependee_adds_dependee(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # when
        results = self.ll.do_add_dependee_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_if_already_added_still_succeeds(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        t1.dependees.append(t2)
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # when
        results = self.ll.do_add_dependee_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_null_ids_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependee_to_task,
                          None, t2.id, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependee_to_task,
                          t1.id, None, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependee_to_task,
                          None, None, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

    def test_null_user_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, None)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

    def test_user_not_authorized_for_task_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

    def test_user_not_authorized_for_dependee_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

    def test_task_not_found_raises_exception(self):
        # given
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.pl.get_task(t2.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependee_to_task,
                          t2.id + 1, t2.id, user)

        # then
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.pl.get_task(t2.id+1))

    def test_dependee_not_found_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependee_to_task,
                          t1.id, t1.id + 1, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

    def test_remove_dependee_removes_dependee(self):

        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # when
        results = self.ll.do_remove_dependee_from_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_if_dependee_already_removed_still_succeeds(self):

        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))

        # when
        results = self.ll.do_remove_dependee_from_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_remove_dependee_with_null_ids_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependee_from_task,
                          None, t2.id, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependee_from_task,
                          t1.id, None, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependee_from_task,
                          None, None, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

    def test_remove_dependee_with_null_user_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependee_from_task,
                          t1.id, t2.id, None)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

    def test_remove_dependee_user_unauthorized_for_task_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()
        # note that this situation shouldn't happen anyways. a task shouldn't
        # be able to depend on another task unless both share a common set of
        # one or more authorized users

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # expect
        self.assertRaises(Forbidden, self.ll.do_remove_dependee_from_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

    def test_remove_user_not_authorized_for_dependee_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t1.dependees.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()
        # note that this situation shouldn't happen anyways. a task shouldn't
        # be able to depend on another task unless both share a common set of
        # one or more authorized users

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

        # expect
        self.assertRaises(Forbidden, self.ll.do_remove_dependee_from_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependants)

    def test_remove_dependee_task_not_found_raises_exception(self):
        # given
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.pl.get_task(t2.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_remove_dependee_from_task,
                          t2.id + 1, t2.id, user)

        # then
        self.assertEqual(0, len(t2.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.pl.get_task(t2.id+1))

    def test_remove_dependee_dependee_not_found_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_remove_dependee_from_task,
                          t1.id, t1.id + 1, user)

        # then
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.pl.get_task(t1.id + 1))


class TaskDependantsLogicLayerTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll()
        self.pl = self.ll.pl

    def test_add_dependant_adds_dependant(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # when
        results = self.ll.do_add_dependant_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_if_already_added_still_succeeds(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        t1.dependants.append(t2)
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # when
        results = self.ll.do_add_dependant_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_null_ids_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependant_to_task,
                          None, t2.id, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependant_to_task,
                          t1.id, None, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependant_to_task,
                          None, None, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

    def test_null_user_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependant_to_task,
                          t1.id, t2.id, None)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

    def test_user_not_authorized_for_task_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependant_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

    def test_user_not_authorized_for_dependant_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependant_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

    def test_task_not_found_raises_exception(self):
        # given
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNone(self.pl.get_task(t2.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependant_to_task,
                          t2.id + 1, t2.id, user)

        # then
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNone(self.pl.get_task(t2.id+1))

    def test_dependant_not_found_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependant_to_task,
                          t1.id, t1.id + 1, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

    def test_remove_dependant_removes_dependant(self):

        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # when
        results = self.ll.do_remove_dependant_from_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_if_dependant_already_removed_still_succeeds(self):

        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))

        # when
        results = self.ll.do_remove_dependant_from_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_remove_dependant_with_null_ids_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependant_from_task,
                          None, t2.id, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependant_from_task,
                          t1.id, None, user)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependant_from_task,
                          None, None, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

    def test_remove_dependant_with_null_user_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # expect
        self.assertRaises(ValueError, self.ll.do_remove_dependant_from_task,
                          t1.id, t2.id, None)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

    def test_rem_dependant_user_unauthorized_for_task_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()
        # note that this situation shouldn't happen anyways. a task shouldn't
        # be able to depend on another task unless both share a common set of
        # one or more authorized users

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # expect
        self.assertRaises(Forbidden, self.ll.do_remove_dependant_from_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

    def test_remove_user_not_authorized_for_dependant_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        t1.dependants.append(t2)
        self.pl.add(t1)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()
        # note that this situation shouldn't happen anyways. a task shouldn't
        # be able to depend on another task unless both share a common set of
        # one or more authorized users

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

        # expect
        self.assertRaises(Forbidden, self.ll.do_remove_dependant_from_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(1, len(t1.dependants))
        self.assertEqual(1, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertTrue(t2 in t1.dependants)
        self.assertTrue(t1 in t2.dependees)

    def test_remove_dependant_task_not_found_raises_exception(self):
        # given
        t2 = self.pl.create_task('t2')
        user = self.pl.create_user('name@example.com')
        t2.users.append(user)
        self.pl.add(t2)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNone(self.pl.get_task(t2.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_remove_dependant_from_task,
                          t2.id + 1, t2.id, user)

        # then
        self.assertEqual(0, len(t2.dependees))
        self.assertEqual(0, len(t2.dependants))
        self.assertIsNone(self.pl.get_task(t2.id+1))

    def test_remove_dependant_dependant_not_found_raises_exception(self):
        # given
        t1 = self.pl.create_task('t1')
        user = self.pl.create_user('name@example.com')
        t1.users.append(user)
        self.pl.add(t1)
        self.pl.add(user)
        self.pl.commit()

        # precondition
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertIsNone(self.pl.get_task(t1.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_remove_dependant_from_task,
                          t1.id, t1.id + 1, user)

        # then
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t1.dependants))
        self.assertIsNone(self.pl.get_task(t1.id + 1))
