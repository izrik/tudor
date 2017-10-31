
import logging_util
from models.tag import Tag
from models.task import Task
from tests.persistence_layer_t.in_memory_persistence_layer.\
    in_memory_test_base import InMemoryTestBase


# copied from ../test_internals.py, with removals


class InternalsTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_added_domain_objects_are_added_to_list_of_added_objects(self):
        # given
        task = Task('task1')
        # precondition
        self.assertEquals(0, len(self.pl._added_objects))
        # when
        self.pl.add(task)
        # then
        self.assertEqual(1, len(self.pl._added_objects))
        self.assertIn(task, self.pl._added_objects)

    def test_deleted_domain_objects_are_added_to_list_of_deleted_objects(self):
        # given
        task = Task('task1')
        self.pl.add(task)
        self.pl.commit()
        # precondition
        self.assertEquals(0, len(self.pl._deleted_objects))
        # when
        self.pl.delete(task)
        # then
        self.assertEqual(1, len(self.pl._deleted_objects))
        self.assertIn(task, self.pl._deleted_objects)

    def test_adding_tag_to_task_also_adds_task_to_tag(self):
        # given
        logger = logging_util.get_logger_by_object(__name__, self)
        logger.debug(u'before create task')
        task = Task('task')
        logger.debug(u'after create task')
        logger.debug(u'before create tag')
        tag = Tag('tag', description='a')
        logger.debug(u'after create tag')
        logger.debug(u'before add task')
        self.pl.add(task)
        logger.debug(u'after add task')
        logger.debug(u'before add tag')
        self.pl.add(tag)
        logger.debug(u'after add tag')
        logger.debug(u'before commit')
        self.pl.commit()
        logger.debug(u'after commit')
