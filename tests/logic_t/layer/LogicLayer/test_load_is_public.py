#!/usr/bin/env python

import unittest

from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User, GuestUser
from tests.logic_t.layer.LogicLayer.util import generate_ll


class LoadIsPublicTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl

        self.tp = Task('tp', is_public=True)
        self.tpp = Task('tpp', is_public=True)
        self.tpp.parent = self.tp
        self.tppp = Task('tppp', is_public=True)
        self.tppp.parent = self.tpp
        self.tppr = Task('tppr', is_public=False)
        self.tppr.parent = self.tpp
        self.tpr = Task('tpr', is_public=False)
        self.tpr.parent = self.tp
        self.tprp = Task('tprp', is_public=True)
        self.tprp.parent = self.tpr
        self.tprr = Task('tprr', is_public=False)
        self.tprr.parent = self.tpr
        self.tr = Task('tr', is_public=False)
        self.trp = Task('trp', is_public=True)
        self.trp.parent = self.tr
        self.trpp = Task('trpp', is_public=True)
        self.trpp.parent = self.trp
        self.trpr = Task('trpr', is_public=False)
        self.trpr.parent = self.trp
        self.trr = Task('trr', is_public=False)
        self.trr.parent = self.tr
        self.trrp = Task('trrp', is_public=True)
        self.trrp.parent = self.trr
        self.trrr = Task('trrr', is_public=False)
        self.trrr.parent = self.trr

        self.pl.add(self.tp)
        self.pl.add(self.tpp)
        self.pl.add(self.tppp)
        self.pl.add(self.tppr)
        self.pl.add(self.tpr)
        self.pl.add(self.tprp)
        self.pl.add(self.tprr)
        self.pl.add(self.tr)
        self.pl.add(self.trp)
        self.pl.add(self.trpp)
        self.pl.add(self.trpr)
        self.pl.add(self.trr)
        self.pl.add(self.trrp)
        self.pl.add(self.trrr)
        self.pl.commit()

    def test_admin_sees_all_tasks(self):
        # given
        admin = User('email', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=admin, root_task_id=self.tp.id,
                             max_depth=None)
        # then
        self.assertEqual(
            {self.tp, self.tpp, self.tppp, self.tppr, self.tpr, self.tprp,
             self.tprr},
            set(tasks))

    def test_admin_sees_all_tasks2(self):
        # given
        admin = User('email', is_admin=True)
        self.pl.add(admin)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=admin, root_task_id=self.tr.id,
                             max_depth=None)
        # then
        self.assertEqual(
            {self.tr, self.trp, self.trpp, self.trpr, self.trr, self.trrp,
             self.trrr},
            set(tasks))

    def test_guest_sees_only_public_tasks(self):
        # given
        guest = GuestUser()
        # when
        tasks = self.ll.load(current_user=guest, root_task_id=self.tp.id,
                             max_depth=None)
        # then
        self.assertEqual({self.tp, self.tpp, self.tppp}, set(tasks))

    def test_guest_sees_only_public_tasks2(self):
        # given
        guest = GuestUser()
        # when
        tasks = self.ll.load(current_user=guest, root_task_id=self.tr.id,
                             max_depth=None)
        # then
        self.assertEqual(set(), set(tasks))


class LoadIsPublicRegularUserTest(unittest.TestCase):
    def setUp(self):
        self.ll = generate_ll(db_uri='sqlite://')
        self.pl = self.ll.pl

    def test_regular_user_sees_own_and_public_tasks_1(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_2(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_3(self):
        # given
        p = Task('p')
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_4(self):
        # given
        p = Task('p')
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_5(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_6(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_7(self):
        # given
        p = Task('p')
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_8(self):
        # given
        p = Task('p')
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        p.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_9(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_10(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_11(self):
        # given
        p = Task('p')
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual(set(), set(tasks))

    def test_regular_user_sees_own_and_public_tasks_12(self):
        # given
        p = Task('p')
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        c.users.append(user)
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual(set(), set(tasks))

    def test_regular_user_sees_own_and_public_tasks_13(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p, c}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_14(self):
        # given
        p = Task('p', is_public=True)
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual({p}, set(tasks))

    def test_regular_user_sees_own_and_public_tasks_15(self):
        # given
        p = Task('p')
        c = Task('c', is_public=True)
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual(set(), set(tasks))

    def test_regular_user_sees_own_and_public_tasks_16(self):
        # given
        p = Task('p')
        c = Task('c')
        self.pl.add(p)
        self.pl.add(c)
        user = User('email')
        self.pl.add(user)
        self.pl.commit()
        c.parent = p
        self.pl.commit()
        # when
        tasks = self.ll.load(current_user=user, root_task_id=p.id,
                             max_depth=None)
        # then
        self.assertEqual(set(), set(tasks))

# if the user is authorized for the parent, the parent is visible
# if the parent is public, the parent is visible
# parent_visible = (the user is auth'd for the parent or the parent is public)
# if parent_visible and the user is auth'd for the child, the child is visible
# if parent_visible and the child is public, the child is visible
# if not parent_visible, the child is not visible
# if not parent_visible, maybe should raise

# def gen_cases():
#     cases = [
#         ['zp', 'zp', 3],
#         ['zp', 'zr', 3],
#         ['zr', 'zp', 3],
#         ['zr', 'zr', 3],
#         ['zp', 'xp', 3],
#         ['zp', 'xr', 1],
#         ['zr', 'xp', 3],
#         ['zr', 'xr', 1],
#         ['xp', 'zp', 3],
#         ['xp', 'zr', 3],
#         ['xr', 'zp', 0],
#         ['xr', 'zr', 0],
#         ['xp', 'xp', 3],
#         ['xp', 'xr', 1],
#         ['xr', 'xp', 0],
#         ['xr', 'xr', 0]]
#     i = 0
#     for parent, child, result in cases:
#         i += 1
#         print('    def test_regular_user_sees_own_and_public_tasks_{}('
#               'self):'.format(i))
#         print("        # given")
#         if parent[1] == 'p':
#             print("        p = Task('p', is_public=True)")
#         else:
#             print("        p = Task('p')")
#         if child[1] == 'p':
#             print("        c = Task('c', is_public=True)")
#         else:
#             print("        c = Task('c')")
#
#         print("        self.pl.add(p)")
#         print("        self.pl.add(c)")
#         print("        user = User('email')")
#         print("        self.pl.add(user)")
#         print("        self.pl.commit()")
#         print("        c.parent = p")
#         if parent[0] == 'z':
#             print("        p.users.append(user)")
#         if child[0] == 'z':
#             print("        c.users.append(user)")
#         print("        self.pl.commit()")
#         print("        # when")
#         print("        tasks = self.ll.load(current_user=user, root_task_id="
#               "p.id,")
#         print("                             max_depth=None)")
#         print("        # then")
#
#         if result == 3:
#             print("        self.assertEqual({p, c}, set(tasks))")
#         elif result == 1:
#             print("        self.assertEqual({p}, set(tasks))")
#         elif result == 0:
#             print("        self.assertEqual(set(), set(tasks))")
#         else:
#             raise Exception()
#         print("")
