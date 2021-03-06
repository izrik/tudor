
import logging_util
from tests.persistence_t.in_memory.in_memory_test_base import InMemoryTestBase


# copied from ../test_internals.py, with removals


class InternalsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_added_domain_objects_are_added_to_list_of_added_objects(self):
        # given
        task = self.pl.create_task('task1')
        # precondition
        self.assertEqual(0, len(self.pl._added_objects))
        # when
        self.pl.add(task)
        # then
        self.assertEqual(1, len(self.pl._added_objects))
        self.assertIn(task, self.pl._added_objects)

    def test_deleted_domain_objects_are_added_to_list_of_deleted_objects(self):
        # given
        task = self.pl.create_task('task1')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEqual(0, len(self.pl._deleted_objects))
        # when
        self.pl.delete(task)
        # then
        self.assertEqual(1, len(self.pl._deleted_objects))
        self.assertIn(task, self.pl._deleted_objects)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        logger = logging_util.get_logger_by_object(__name__, self)
        logger.debug('before create task')
        task = self.pl.create_task('task')
        logger.debug('after create task')
        logger.debug('before create tag')
        tag = self.pl.create_tag('tag', description='a')
        logger.debug('after create tag')
        logger.debug('before add task')
        self.pl.add(task)
        logger.debug('after add task')
        logger.debug('before add tag')
        self.pl.add(tag)
        logger.debug('after add tag')
        logger.debug('before commit')
        self.pl.commit()
        logger.debug('after commit')
