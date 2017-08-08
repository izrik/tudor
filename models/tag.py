
from changeable import Changeable
import logging_util
from collections_util import assign
from interlinking import ManyToManySet


class TagBase(object):

    FIELD_ID = 'ID'
    FIELD_VALUE = 'VALUE'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TASKS = 'TASKS'

    def __init__(self, value, description=None):
        self._logger.debug('TagBase.__init__ {}'.format(self))
        self.value = value
        self.description = description

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.value), self.id)

    def __str__(self):
        cls = type(self).__name__
        return '{}({}, tag id={}, id=[{}])'.format(cls, repr(self.value),
                                                   self.id, id(self))

    def to_dict(self, fields=None):

        self._logger.debug('{}'.format(self))

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d['id'] = self.id
        if fields is None or self.FIELD_VALUE in fields:
            d['value'] = self.value
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d['description'] = self.description

        if fields is None or self.FIELD_TASKS in fields:
            d['tasks'] = list(self.tasks)

        return d

    @classmethod
    def from_dict(cls, d, lazy=None):
        logger = cls._logger
        logger.debug('d: {}'.format(d))

        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = cls(value, description, lazy=lazy)
        if tag_id is not None:
            tag.id = tag_id
        if not lazy:
            if 'tasks' in d:
                assign(tag.tasks, d['tasks'])
        logger.debug('tag: {}'.format(tag))
        return tag

    def update_from_dict(self, d):
        self._logger.debug('{}: {}'.format(self, d))
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'value' in d:
            self.value = d['value']
        if 'description' in d:
            self.description = d['description']
        if 'tasks' in d:
            assign(self.tasks, d['tasks'])


class Tag(Changeable, TagBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Tag')

    _id = None
    _value = None
    _description = None

    _tasks = None

    def __init__(self, value, description=None, lazy=None):
        super(Tag, self).__init__(value=value, description=description)
        self._logger.debug('Tag.__init__ {}'.format(self))

        if lazy is None:
            lazy = {}

        self._tasks = InterlinkedTasks(self, lazy=lazy.get('tasks'))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug(
                '{}: {} -> {}'.format(self, self._id, value))
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
                '{}: {} -> {}'.format(self, self._value, value))
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
                '{}: {} -> {}'.format(self, self._description, value))
            self._on_attr_changing(self.FIELD_DESCRIPTION, self._description)
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION, self.OP_SET,
                                  self._description)

    @property
    def tasks(self):
        return self._tasks

    def clear_relationships(self):
        self.tasks.clear()


class InterlinkedTasks(ManyToManySet):
    __change_field__ = Tag.FIELD_TASKS
    __attr_counterpart__ = 'tags'
