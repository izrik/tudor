from datetime import datetime

from models.tag import Tag
from models.task import Task
from models.user import User
from tests.in_memory_persistence_layer_t.in_memory_test_base import \
    InMemoryTestBase


# copied from ../test_get_tasks.py


class GetTaskTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_done=True)
        self.pl.add(self.t2)
        self.t3 = Task('t3', is_deleted=True)
        self.t3.parent = self.t2
        self.pl.add(self.t3)
        self.t4 = Task('t4', is_done=True, is_deleted=True)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_get_tasks(self):
        # when
        results = self.pl.get_tasks()

        # then
        self.assertEqual({self.t1, self.t2, self.t3, self.t4}, set(results))

    def test_get_tasks_is_done_true_excludes_undone(self):
        # when
        results = self.pl.get_tasks(is_done=True)

        # then
        self.assertEqual({self.t2, self.t4}, set(results))

    def test_get_tasks_is_done_false_excludes_done(self):
        # when
        results = self.pl.get_tasks(is_done=False)

        # then
        self.assertEqual({self.t1, self.t3}, set(results))

    def test_get_tasks_is_deleted_true_excludes_undeleted(self):
        # when
        results = self.pl.get_tasks(is_deleted=True)

        # then
        self.assertEqual({self.t3, self.t4}, set(results))

    def test_get_tasks_is_deleted_false_excludes_deleted(self):
        # when
        results = self.pl.get_tasks(is_deleted=False)

        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_get_tasks_is_done_is_deleted_combos(self):
        # when
        results = self.pl.get_tasks(is_done=False, is_deleted=False)

        # then
        self.assertEqual({self.t1}, set(results))

        # when
        results = self.pl.get_tasks(is_done=True, is_deleted=False)

        # then
        self.assertEqual({self.t2}, set(results))

        # when
        results = self.pl.get_tasks(is_done=False, is_deleted=True)

        # then
        self.assertEqual({self.t3}, set(results))

        # when
        results = self.pl.get_tasks(is_done=True, is_deleted=True)

        # then
        self.assertEqual({self.t4}, set(results))

    def test_get_tasks_parent_id_none_yields_top_level(self):
        # when
        results = self.pl.get_tasks(parent_id=None)
        # then
        self.assertEqual({self.t1, self.t2, self.t4}, set(results))

    def test_get_tasks_parent_id_non_null_yields_indicated(self):
        # when
        results = self.pl.get_tasks(parent_id=self.t2.id)
        # then
        self.assertEqual({self.t3}, set(results))

    def test_get_tasks_users_contains(self):
        # given
        user1 = User('name@example.com')
        user2 = User('name2@example.com')
        user3 = User('name3@example.com')
        self.pl.add(user1)
        self.pl.add(user2)
        self.pl.add(user3)
        self.t1.users.add(user1)
        self.t2.users.add(user2)
        self.t3.users.add(user1)
        self.t3.users.add(user2)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.commit()

        # when
        results = self.pl.get_tasks(users_contains=user1)
        # then
        self.assertEqual({self.t1, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(users_contains=user2)
        # then
        self.assertEqual({self.t2, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(users_contains=user3)
        # then
        self.assertEqual(set(), set(results))


class GetTasksIsPublicTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1', is_public=True)
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_public=False)
        self.pl.add(self.t2)
        self.pl.commit()

    def test_get_tasks_is_public_not_specified_returns_all_tasks(self):
        # when
        result = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2}, set(result))

    def test_get_tasks_is_public_true_returns_only_public_tasks(self):
        # when
        result = self.pl.get_tasks(is_public=True)
        # then
        self.assertEqual({self.t1}, set(result))

    def test_get_tasks_is_public_false_returns_only_non_public_tasks(self):
        # when
        result = self.pl.get_tasks(is_public=False)
        # then
        self.assertEqual({self.t2}, set(result))


class GetTasksIsPublicOrUsersContainsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1', is_public=True)
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_public=False)
        self.pl.add(self.t2)
        self.user = User('email')
        self.pl.add(self.user)
        self.pl.commit()

    def test_user_not_authorized_returns_only_public_task(self):
        # precondition
        self.assertEqual(set(), set(self.t1.users))
        self.assertEqual(set(), set(self.t2.users))
        self.assertEqual(set(), set(self.user.tasks))
        # when
        result = self.pl.get_tasks(is_public_or_users_contains=self.user)
        # then
        self.assertEqual({self.t1}, set(result))

    def test_user_authorized_on_public_task_returns_only_public_task(self):
        # given
        self.t1.users.add(self.user)
        self.pl.commit()
        # precondition
        self.assertEqual({self.user}, set(self.t1.users))
        self.assertEqual(set(), set(self.t2.users))
        self.assertEqual({self.t1}, set(self.user.tasks))
        # when
        result = self.pl.get_tasks(is_public_or_users_contains=self.user)
        # then
        self.assertEqual({self.t1}, set(result))

    def test_user_authorized_on_private_task_returns_both_tasks(self):
        # given
        self.t2.users.add(self.user)
        self.pl.commit()
        # precondition
        self.assertEqual(set(), set(self.t1.users))
        self.assertEqual({self.user}, set(self.t2.users))
        self.assertEqual({self.t2}, set(self.user.tasks))
        # when
        result = self.pl.get_tasks(is_public_or_users_contains=self.user)
        # then
        self.assertEqual({self.t1, self.t2}, set(result))

    def test_user_authorized_on_both_tasks_returns_both_tasks(self):
        # given
        self.t1.users.add(self.user)
        self.t2.users.add(self.user)
        self.pl.commit()
        # precondition
        self.assertEqual({self.user}, set(self.t1.users))
        self.assertEqual({self.user}, set(self.t2.users))
        self.assertEqual({self.t1, self.t2}, set(self.user.tasks))
        # when
        result = self.pl.get_tasks(is_public_or_users_contains=self.user)
        # then
        self.assertEqual({self.t1, self.t2}, set(result))


class OrderByTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.id = 5
        self.pl.add(self.t1)
        self.t2 = Task('t2', is_done=True)
        self.t2.id = 7
        self.pl.add(self.t2)
        self.t3 = Task('t3', is_deleted=True)
        self.t3.parent = self.t2
        self.t3.id = 11
        self.pl.add(self.t3)
        self.t4 = Task('t4', is_done=True, is_deleted=True)
        self.t4.id = 13
        self.pl.add(self.t4)

        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.t4.order_num = 4
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)

        self.pl.commit()

    def test_get_tasks_order_by_order_num_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list(self):

        # when
        results = self.pl.get_tasks(order_by=[self.pl.ORDER_NUM])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_direction_in_list_raises(self):

        # expect
        self.assertRaises(Exception,
                          self.pl.get_tasks,
                          order_by=[self.pl.ORDER_NUM, self.pl.ASCENDING])

    def test_get_tasks_order_by_order_num_list_list(self):

        # when
        results = self.pl.get_tasks(order_by=[[self.pl.ORDER_NUM]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_order_num_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.ORDER_NUM, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))

    def test_get_tasks_order_by_unknown_direction_raises(self):

        # expect
        self.assertRaises(Exception,
                          self.pl.get_tasks,
                          order_by=[[self.pl.ORDER_NUM, 123]])

    def test_get_tasks_order_by_task_id_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.TASK_ID)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_task_id_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.TASK_ID, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_task_id_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.TASK_ID, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))


class OrderByDeadlineTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1', deadline='2017-01-01')
        self.t2 = Task('t2', deadline='2017-01-02')
        self.t3 = Task('t3', deadline='2017-01-03')
        self.t4 = Task('t4', deadline='2017-01-04')

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_get_tasks_order_by_deadline_single(self):

        # when
        results = self.pl.get_tasks(order_by=self.pl.DEADLINE)
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_deadline_list_list_with_asc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.DEADLINE, self.pl.ASCENDING]])
        # then
        self.assertEqual([self.t1, self.t2, self.t3, self.t4], list(results))

    def test_get_tasks_order_by_deadline_list_list_with_desc(self):

        # when
        results = self.pl.get_tasks(
            order_by=[[self.pl.DEADLINE, self.pl.DESCENDING]])
        # then
        self.assertEqual([self.t4, self.t3, self.t2, self.t1], list(results))


class IdInTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_id_in(self):
        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t2.id, self.t3.id])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t3.id, self.t2.id, self.t1.id])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_some_missing(self):
        # when
        results = self.pl.get_tasks(task_id_in=[self.t1.id, self.t2.id])
        # then
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_get_tasks_id_in_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids.append(next_id)
        # when
        results = self.pl.get_tasks(task_id_in=ids)
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_in_empty(self):
        # when
        results = self.pl.get_tasks(task_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_in_with_order_by(self):
        # given
        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.commit()

        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3], list(results))

        # when
        results = self.pl.get_tasks(task_id_in=[], order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))

    def test_get_tasks_id_not_in(self):
        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t1.id, self.t2.id, self.t3.id])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t3.id, self.t2.id, self.t1.id])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_some_missing(self):
        # when
        results = self.pl.get_tasks(task_id_not_in=[self.t1.id, self.t2.id])
        # then
        self.assertEqual({self.t3}, set(results))

    def test_get_tasks_id_not_in_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids.append(next_id)
        # when
        results = self.pl.get_tasks(task_id_not_in=ids)
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_id_not_in_some_missing_some_extra(self):
        # given
        ids = [self.t1.id, self.t2.id, self.t3.id]
        next_id = max(ids) + 1
        ids = [self.t2.id, self.t3.id, next_id]
        # when
        results = self.pl.get_tasks(task_id_not_in=ids)
        # then
        self.assertEqual({self.t1}, set(results))

    def test_get_tasks_id_not_in_empty(self):
        # when
        results = self.pl.get_tasks(task_id_not_in=[])
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_id_not_in_with_order_by(self):
        # given
        self.t1.order_num = 1
        self.t2.order_num = 2
        self.t3.order_num = 3
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.commit()

        # when
        results = self.pl.get_tasks(
            task_id_not_in=[self.t1.id, self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))

        # when
        results = self.pl.get_tasks(task_id_not_in=[],
                                    order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t1, self.t2, self.t3], list(results))

    def test_get_tasks_both_params(self):

        # when
        results = self.pl.get_tasks(
            task_id_in=[self.t1.id, self.t3.id],
            task_id_not_in=[self.t2.id, self.t3.id])
        # then
        self.assertEqual({self.t1}, set(results))


class LimitTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t1.order_num = 1
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.t2.order_num = 2
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.t3.order_num = 3
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_no_limit(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual(3, len(list(results)))

    def test_get_tasks_with_limit(self):
        # when
        results = self.pl.get_tasks(limit=2)
        # then
        self.assertEqual(2, len(list(results)))

    def test_get_tasks_limit_greater_than_count_returns_count(self):
        # when
        results = self.pl.get_tasks(limit=4)
        # then
        self.assertEqual(3, len(list(results)))

    def test_get_tasks_limit_zero_returns_zero(self):
        # when
        results = self.pl.get_tasks(limit=0)
        # then
        self.assertEqual(0, len(list(results)))

    def test_get_tasks_limit_negative_returns_all(self):
        # when
        results = self.pl.get_tasks(limit=-1)
        # then
        self.assertEqual(3, len(list(results)))


class DeadLineIsNotNoneTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1', deadline=datetime(2017, 1, 1))
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3', deadline=datetime(2017, 1, 2))
        self.pl.add(self.t3)

        self.pl.commit()

    def test_get_tasks_not_specified_does_not_filter(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_false_does_not_filter(self):
        # when
        results = self.pl.get_tasks(deadline_is_not_none=False)
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_true_excludes_null_deadlines(self):
        # when
        results = self.pl.get_tasks(deadline_is_not_none=True)
        # then
        self.assertEqual({self.t1, self.t3}, set(results))


class ParentIdInTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.pl.add(self.t1)
        self.t2 = Task('t2')
        self.pl.add(self.t2)
        self.t3 = Task('t3')
        self.t3.parent = self.t2
        self.pl.add(self.t3)
        self.t4 = Task('t4')
        self.t4.parent = self.t3
        self.pl.add(self.t4)
        self.t5 = Task('t5')
        self.t5.parent = self.t2
        self.pl.add(self.t5)
        self.t6 = Task('t6')
        self.pl.add(self.t6)
        self.t7 = Task('t7')
        self.t7.parent = self.t6
        self.pl.add(self.t7)

        self.pl.commit()

    def test_get_tasks_parent_id_in(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id, self.t6.id])
        # then
        self.assertEqual({self.t3, self.t5, self.t7}, set(results))

    def test_get_tasks_parent_id_in_order_does_not_matter(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t6.id, self.t2.id])
        # then
        self.assertEqual({self.t3, self.t5, self.t7}, set(results))

    def test_get_tasks_parent_id_in_some_missing(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id])
        # then
        self.assertEqual({self.t3, self.t5}, set(results))

    def test_get_tasks_parent_id_in_invalid_values_have_no_effect(self):
        # given
        next_id = max([self.t1.id, self.t2.id, self.t3.id, self.t4.id,
                       self.t5.id, self.t6.id, self.t7.id]) + 1
        # when
        results = self.pl.get_tasks(parent_id_in=[self.t2.id, next_id])
        # then
        self.assertEqual({self.t3, self.t5}, set(results))

    def test_get_tasks_parent_id_in_empty(self):
        # when
        results = self.pl.get_tasks(parent_id_in=[])
        # then
        self.assertEqual(set(), set(results))

    def test_get_tasks_parent_id_in_with_order_by(self):
        # given
        self.t3.order_num = 101
        self.t4.order_num = 313
        self.t5.order_num = 207
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.add(self.t5)
        self.pl.commit()

        # when
        results = self.pl.get_tasks(
            parent_id_in=[self.t2.id, self.t3.id],
            order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([self.t3, self.t5, self.t4], list(results))

        # when
        results = self.pl.get_tasks(task_id_in=[], order_by=self.pl.ORDER_NUM)
        # then
        self.assertEqual([], list(results))


class TagsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.t1 = Task('t1')
        self.t2 = Task('t2')
        self.t3 = Task('t3')
        self.tag1 = Tag('tag1')
        self.tag2 = Tag('tag2')
        self.t2.tags.add(self.tag1)
        self.t3.tags.add(self.tag1)
        self.t3.tags.add(self.tag2)
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.tag1)
        self.pl.add(self.tag2)

        self.pl.commit()

    def test_get_tasks_tag_unspecified_yields_all_tasks(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3}, set(results))

    def test_get_tasks_tag_specified_yields_only_tasks_with_that_tag(self):
        # when
        results = self.pl.get_tasks(tags_contains=self.tag1)
        # then
        self.assertEqual({self.t2, self.t3}, set(results))

        # when
        results = self.pl.get_tasks(tags_contains=self.tag2)
        # then
        self.assertEqual({self.t3}, set(results))


class SearchTermTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

        self.t1 = Task('t1', description='qwerty')
        self.t2 = Task('t2', description='abc')
        self.t3 = Task('t3 abc', description='qwerty')
        self.t4 = Task('t4 abc', description='abc')

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_specifying_search_term_yiels_all_tasks_that_match(self):
        # when
        results = self.pl.get_tasks(summary_description_search_term='abc')
        # then
        self.assertEqual({self.t2, self.t3, self.t4}, set(results))

    def test_partial_word_matches(self):
        # when
        results = self.pl.get_tasks(summary_description_search_term='wer')
        # then
        results = list(results)
        self.assertEqual({self.t1, self.t3}, set(results))


class OrderNumberGreaterLessEqualTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

        self.t1 = Task('t1')
        self.t1.order_num = 2
        self.t2 = Task('t2')
        self.t2.order_num = 3
        self.t3 = Task('t3')
        self.t3.order_num = 5
        self.t4 = Task('t4')
        self.t4.order_num = 7

        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.t3)
        self.pl.add(self.t4)
        self.pl.commit()

    def test_unspecified_yields_all_tasks(self):
        # when
        results = self.pl.get_tasks()
        # then
        self.assertEqual({self.t1, self.t2, self.t3, self.t4}, set(results))

    def test_order_num_g_equal_returns_matching_task(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=7)
        # then
        results = list(results)
        self.assertEqual({self.t4}, set(results))

    def test_order_num_greater_returns_all_matching_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=4)
        # then
        results = list(results)
        self.assertEqual({self.t3, self.t4}, set(results))

    def test_order_num_l_equal_returns_matching_task(self):
        # when
        results = self.pl.get_tasks(order_num_lesseq_than=2)
        # then
        results = list(results)
        self.assertEqual({self.t1}, set(results))

    def test_order_num_less_returns_all_matching_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_lesseq_than=4)
        # then
        results = list(results)
        self.assertEqual({self.t1, self.t2}, set(results))

    def test_order_num_both_sets_upper_and_lower_bounds(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=3,
                                    order_num_lesseq_than=6)
        # then
        results = list(results)
        self.assertEqual({self.t2, self.t3}, set(results))

    def test_order_num_mismatched_bounds_yields_no_tasks(self):
        # when
        results = self.pl.get_tasks(order_num_greq_than=6,
                                    order_num_lesseq_than=3)
        # then
        results = list(results)
        self.assertEqual(set(), set(results))
