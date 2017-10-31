from models.tag import Tag
from models.task import Task
from tests.in_memory_persistence_layer.in_memory_test_base import \
    InMemoryTestBase


# copied from ../test_db_interaction.py, with modifications


class DatabaseInteraction2Test(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_changes_after_get_are_also_tracked(self):
        # given
        tag1 = Tag('tag', description='a')
        self.pl.add(tag1)
        self.pl.commit()
        tag = self.pl.get_tag_by_value('tag')
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.commit()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', tag1.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', tag1.description)

    def test_rollback_undeletes_deleted_objects(self):
        # given
        task = Task('task')
        self.pl.add(task)
        self.pl.commit()
        self.pl.delete(task)
        # precondition
        self.assertIn(task, self.pl._tasks)
        self.assertIn(task, self.pl._deleted_objects)
        # when
        self.pl.rollback()
        # then
        self.assertIn(task, self.pl._tasks)
        self.assertNotIn(task, self.pl._deleted_objects)
