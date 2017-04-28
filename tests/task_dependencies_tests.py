#!/usr/bin/env python

import unittest

from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from tudor import generate_app


class TaskDependenciesTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.db = self.app.ds.db
        self.db.create_all()
        self.Task = self.app.Task

    def test_setting_task_as_dependee_sets_other_task_as_depender(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependees.append(t2)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependers)

    def test_setting_task_as_depender_sets_other_task_as_dependee(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # when
        t1.dependers.append(t2)

        # then
        self.assertEqual(1, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(1, len(t2.dependees))
        self.assertTrue(t2 in t1.dependers)
        self.assertTrue(t1 in t2.dependees)

    def test_cycle_check_yields_false_for_no_cycles(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t1.dependers.append(t2)

        # expect
        self.assertFalse(t1.contains_dependency_cycle())
        self.assertFalse(t2.contains_dependency_cycle())

    def test_cycle_check_yields_true_for_cycles(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t1.dependers.append(t2)
        t2.dependers.append(t1)

        # expect
        self.assertTrue(t1.contains_dependency_cycle())
        self.assertTrue(t2.contains_dependency_cycle())

    def test_cycle_check_yields_true_for_long_cycles(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t3 = self.Task('t3')
        t4 = self.Task('t4')
        t5 = self.Task('t5')
        t6 = self.Task('t6')
        t1.dependers.append(t2)
        t2.dependers.append(t3)
        t3.dependers.append(t4)
        t4.dependers.append(t5)
        t5.dependers.append(t6)
        t6.dependers.append(t1)

        # expect
        self.assertTrue(t1.contains_dependency_cycle())
        self.assertTrue(t2.contains_dependency_cycle())
        self.assertTrue(t3.contains_dependency_cycle())
        self.assertTrue(t4.contains_dependency_cycle())
        self.assertTrue(t5.contains_dependency_cycle())
        self.assertTrue(t6.contains_dependency_cycle())

    def test_cycle_check_yields_false_for_trees(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t3 = self.Task('t3')
        t4 = self.Task('t4')
        t1.dependers.append(t2)
        t1.dependers.append(t3)
        t2.dependers.append(t4)
        t3.dependers.append(t4)

        # expect
        self.assertFalse(t1.contains_dependency_cycle())
        self.assertFalse(t2.contains_dependency_cycle())
        self.assertFalse(t3.contains_dependency_cycle())
        self.assertFalse(t4.contains_dependency_cycle())


class TaskDependenciesLogicLayerTest(unittest.TestCase):
    def setUp(self):
        self.app = generate_app(db_uri='sqlite://')
        self.db = self.app.ds.db
        self.db.create_all()
        self.ll = self.app.ll
        self.Task = self.app.Task
        self.User = self.app.User

    def test_add_dependee_adds_dependee(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # when
        results = self.ll.do_add_dependee_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependers)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_if_already_added_still_succeeds(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        t1.dependees.append(t2)
        user = self.User('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependers)

        # when
        results = self.ll.do_add_dependee_to_task(t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(1, len(t1.dependees))
        self.assertEqual(1, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertTrue(t2 in t1.dependees)
        self.assertTrue(t1 in t2.dependers)
        self.assertIsNotNone(results)
        self.assertEqual([t1, t2], list(results))

    def test_null_ids_raises_exception(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
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
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

    def test_null_users_raises_exception(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t1.users.append(user)
        t2.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(ValueError, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, None)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

    def test_user_not_authorized_for_task_raises_exception(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t2.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

    def test_user_not_authorized_for_dependee_raises_exception(self):
        # given
        t1 = self.Task('t1')
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t1.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

        # expect
        self.assertRaises(Forbidden, self.ll.do_add_dependee_to_task,
                          t1.id, t2.id, user)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))

    def test_task_not_found_raises_exception(self):
        # given
        t2 = self.Task('t2')
        user = self.User('name@example.com')
        t2.users.append(user)
        self.db.session.add(t2)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.app.ds.Task.query.get(t2.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependee_to_task,
                          t2.id + 1, t2.id, user)

        # then
        self.assertEqual(0, len(t2.dependers))
        self.assertEqual(0, len(t2.dependees))
        self.assertIsNone(self.app.ds.Task.query.get(t2.id+1))

    def test_dependee_not_found_raises_exception(self):
        # given
        t1 = self.Task('t1')
        user = self.User('name@example.com')
        t1.users.append(user)
        self.db.session.add(t1)
        self.db.session.add(user)
        self.db.session.commit()

        # precondition
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.app.ds.Task.query.get(t1.id + 1))

        # expect
        self.assertRaises(NotFound, self.ll.do_add_dependee_to_task,
                          t1.id, t1.id + 1, user)

        # then
        self.assertEqual(0, len(t1.dependers))
        self.assertEqual(0, len(t1.dependees))
        self.assertIsNone(self.app.ds.Task.query.get(t1.id + 1))
