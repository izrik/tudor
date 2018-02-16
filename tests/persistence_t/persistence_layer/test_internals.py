import unittest

import logging_util
from persistence.in_memory.models.tag import Tag
from persistence.in_memory.models.task import Task
from tests.persistence_t.persistence_layer.util import PersistenceLayerTestBase


class InternalsTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_create_db_object_from_domain_object(self):
        # given
        task = Task('task1')
        # when
        result = self.pl._create_db_object_from_domain_object(task)
        # then
        self.assertIsNotNone(result)
        self.assertIsInstance(result, self.pl.DbTask)
        self.assertEqual('task1', result.summary)

    def test_get_db_object_from_cache_when_none_exist_returns_none(self):
        # given
        task = Task('task1')
        # when
        result = self.pl._get_db_object_from_domain_object_in_cache(task)
        # then
        self.assertIsNone(result)

    def test_get_db_object_from_cache_when_some_exist_returns_none(self):
        # given
        task = Task('task1')
        dbtask = self.pl._create_db_object_from_domain_object(task)
        self.pl._db_by_domain[task] = dbtask
        # when
        result = self.pl._get_db_object_from_domain_object_in_cache(task)
        # then
        self.assertIsNotNone(result)
        self.assertIs(dbtask, result)

    def test_get_db_object_from_domain_object_by_id(self):
        # given
        task = Task('task1')
        dbtask = self.pl._create_db_object_from_domain_object(task)
        self.pl.db.session.add(dbtask)
        self.pl.db.session.commit()
        # precondition
        self.assertIsNotNone(dbtask.id)
        task.id = dbtask.id
        # when
        result = self.pl._get_db_object_from_domain_object_by_id(task)
        # then
        self.assertIs(dbtask, result)

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
