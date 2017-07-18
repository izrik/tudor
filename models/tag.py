
import collections
import logging

from changeable import Changeable
import logging_util
from collections_util import assign


class TagBase(object):

    FIELD_ID = 'ID'
    FIELD_VALUE = 'VALUE'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TASKS = 'TASKS'

    def __init__(self, value, description=None):
        self._logger = logging_util.get_logger(__name__, self)
        self._logger.debug('TagBase.__init__ {}'.format(self.id2))
        self.value = value
        self.description = description

    @staticmethod
    def get_related_fields(field):
        return ()

    @staticmethod
    def get_autochange_fields():
        return (Tag.FIELD_ID,)

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, self.value, self.id)

    def to_dict(self, fields=None):

        self._logger.debug('{}'.format(self.id2))

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d[self.FIELD_ID] = self.id
        if fields is None or self.FIELD_VALUE in fields:
            d[self.FIELD_VALUE] = self.value
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d[self.FIELD_DESCRIPTION] = self.description

        if fields is None or self.FIELD_TASKS in fields:
            d[self.FIELD_TASKS] = list(self.tasks)

        return d

    def update_from_dict(self, d):
        self._logger.debug('{}: {}'.format(self.id2, d))
        if self.FIELD_ID in d and d[self.FIELD_ID] is not None:
            self.id = d[self.FIELD_ID]
        if self.FIELD_VALUE in d:
            self.value = d[self.FIELD_VALUE]
        if self.FIELD_DESCRIPTION in d:
            self.description = d[self.FIELD_DESCRIPTION]
        if self.FIELD_TASKS in d:
            assign(self.tasks, d[self.FIELD_TASKS])

    @property
    def id2(self):
        return '[{}] {} ({})'.format(id(self), self.value, self.id)


class Tag(Changeable, TagBase):

    _id = None
    _value = None
    _description = None

    _tasks = None

    _dbobj = None

    def __init__(self, value, description=None):
        super(Tag, self).__init__(value=value, description=description)
        self._logger.debug('Tag.__init__ {}'.format(self.id2))
        self._tasks = InterlinkedTasks(self)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._id, value))
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._value, value))
            self._on_attr_changing(self.FIELD_VALUE, self._value)
            self._value = value
            self._on_attr_changed(self.FIELD_VALUE, self.OP_SET, self._value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._description, value))
            self._on_attr_changing(self.FIELD_DESCRIPTION, self._description)
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION, self.OP_SET,
                                  self._description)

    @property
    def tasks(self):
        return self._tasks

    @staticmethod
    def from_dict(d):
        logger = logging_util.get_logger_by_class(__name__, Tag)
        logger.debug('d: {}'.format(d))

        tag_id = d.get(Tag.FIELD_ID, None)
        value = d.get(Tag.FIELD_VALUE)
        description = d.get(Tag.FIELD_DESCRIPTION, None)

        tag = Tag(value, description)
        logger = logging_util.get_logger(__name__, tag)
        logger.debug('{}'.format(tag.id2))
        if tag_id is not None:
            tag.id = tag_id
        logger.debug('tag: {}'.format(tag))
        return tag

    def clear_relationships(self):
        self.tasks.clear()


class InterlinkedTasks(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, task):
        return self.set.__contains__(task)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, task):
        self._logger.debug('{}: {}'.format(self.c.id2, task.id2))
        if task not in self.set:
            self.container._on_attr_changing(Tag.FIELD_TASKS, None)
            self.set.add(task)
            task.tags.add(self.container)
            self.container._on_attr_changed(Tag.FIELD_TASKS, Tag.OP_ADD, task)

    def append(self, task):
        self._logger.debug('{}: {}'.format(self.c.id2, task.id2))
        self.add(task)

    def discard(self, task):
        self._logger.debug('{}: {}'.format(self.c.id2, task.id2))
        if task in self.set:
            self.container._on_attr_changing(Tag.FIELD_TASKS, None)
            self.set.discard(task)
            task.tags.discard(self.container)
            self.container._on_attr_changed(Tag.FIELD_TASKS, Tag.OP_REMOVE,
                                            task)
