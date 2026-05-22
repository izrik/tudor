import unittest

from persistence.in_memory.layer import InMemoryPersistenceLayer
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task
from persistence.in_memory.models.user import User
from persistence.sqlalchemy.layer import RecordNotFound


class AssociationSettersTest(unittest.TestCase):
    def setUp(self):
        self.pl = InMemoryPersistenceLayer()
        self.t1 = Task(summary='t1')
        self.t2 = Task(summary='t2')
        self.tag = Tag(value='red')
        self.user = User(email='a@b')
        self.pl.add(self.t1)
        self.pl.add(self.t2)
        self.pl.add(self.tag)
        self.pl.add(self.user)
        self.pl.commit()

    def test_add_tag_to_task(self):
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.assertIn(self.tag, self.t1.tags)

    def test_add_tag_to_task_is_idempotent(self):
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.assertEqual(list(self.t1.tags).count(self.tag), 1)

    def test_remove_tag_from_task(self):
        self.pl.add_tag_to_task(self.t1.id, self.tag.id)
        self.pl.remove_tag_from_task(self.t1.id, self.tag.id)
        self.assertNotIn(self.tag, self.t1.tags)

    def test_add_tag_to_unknown_task_raises(self):
        with self.assertRaises(RecordNotFound):
            self.pl.add_tag_to_task(999, self.tag.id)

    def test_add_user_to_task(self):
        self.pl.add_user_to_task(self.t1.id, self.user.id)
        self.assertIn(self.user, self.t1.users)

    def test_remove_user_from_task(self):
        self.pl.add_user_to_task(self.t1.id, self.user.id)
        self.pl.remove_user_from_task(self.t1.id, self.user.id)
        self.assertNotIn(self.user, self.t1.users)

    def test_add_dependency(self):
        self.pl.add_dependency(self.t1.id, self.t2.id)
        self.assertIn(self.t2, self.t1.dependees)
        self.assertIn(self.t1, self.t2.dependants)

    def test_remove_dependency(self):
        self.pl.add_dependency(self.t1.id, self.t2.id)
        self.pl.remove_dependency(self.t1.id, self.t2.id)
        self.assertNotIn(self.t2, self.t1.dependees)

    def test_add_priority(self):
        self.pl.add_priority(self.t1.id, self.t2.id)
        self.assertIn(self.t1, self.t2.prioritize_before)
        self.assertIn(self.t2, self.t1.prioritize_after)

    def test_remove_priority(self):
        self.pl.add_priority(self.t1.id, self.t2.id)
        self.pl.remove_priority(self.t1.id, self.t2.id)
        self.assertNotIn(self.t1, self.t2.prioritize_before)
