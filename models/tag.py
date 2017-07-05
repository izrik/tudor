
import collections
import logging

from changeable import Changeable
import logging_util


class TagBase(object):

    def __init__(self, value, description=None):
        self._logger = logging_util.get_logger(__name__, self)
        self.value = value
        self.description = description

    def to_dict(self):
        self._logger.debug('{} ({})'.format(self.value, self.id))
        return {
            'id': self.id,
            'value': self.value,
            'description': self.description,
        }

    def update_from_dict(self, d):
        self._logger.debug('{} ({})'.format(self.value, self.id))
        if 'id' in d:
            self.id = d['id']
        if 'value' in d:
            self.value = d['value']
        if 'description' in d:
            self.description = d['description']

    @property
    def id2(self):
        return '[{}] {} ({})'.format(id(self), self.value, self.id)


class Tag(Changeable, TagBase):

    _id = None
    _value = None
    _description = None

    _tasks = None

    def __init__(self, value, description=None):
        super(Tag, self).__init__(value=value, description=description)
        self._tasks = InterlinkedTasks(self)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._id, value))
            self._id = value
            self._on_attr_changed()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._value, value))
            self._value = value
            self._on_attr_changed()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self._description, value))
            self._description = value
            self._on_attr_changed()

    @property
    def tasks(self):
        return self._tasks

    @staticmethod
    def from_dict(d):
        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = Tag(value, description)
        logger = logging_util.get_logger(__name__, tag)
        logger.debug('{} ({}) [{}]'.format(tag.value, tag.id, id(tag)))
        if tag_id is not None:
            tag.id = tag_id
        return tag


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
            self.set.add(task)
            task.tags.add(self.container)
            self.container._on_attr_changed()

    def append(self, task):
        self._logger.debug('{}: {}'.format(self.c.id2, task.id2))
        self.add(task)

    def discard(self, task):
        self._logger.debug('{}: {}'.format(self.c.id2, task.id2))
        if task in self.set:
            self.set.discard(task)
            task.tags.discard(self.container)
            self.container._on_attr_changed()
