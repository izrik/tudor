
from __future__ import absolute_import

from models.changeable import Changeable
import logging_util
from models.interlinking import ManyToManySet
from models.tag_base import TagBase


class Tag(Changeable, TagBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Tag')

    _id = None
    _value = None
    _description = None

    _tasks = None

    def __init__(self, value, description=None, lazy=None):
        super(Tag, self).__init__(value=value, description=description)
        self._logger.debug(u'Tag.__init__ %s', self)

        if lazy is None:
            lazy = {}

        self._tasks = InterlinkedTasks(self, lazy=lazy.get('tasks'))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug(u'%s: %s -> %s', self, self._id, value)
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._logger.debug(u'%s: %s -> %s', self, self._value, value)
            self._on_attr_changing(self.FIELD_VALUE, self._value)
            self._value = value
            self._on_attr_changed(self.FIELD_VALUE, self.OP_SET, self._value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._logger.debug(u'%s: %s -> %s', self, self._description, value)
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
    __change_field__ = TagBase.FIELD_TASKS
    __attr_counterpart__ = 'tags'
