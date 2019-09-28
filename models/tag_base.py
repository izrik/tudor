
from collections_util import assign
from models.object_types import ObjectTypes


class TagBase(object):

    FIELD_ID = 'ID'
    FIELD_VALUE = 'VALUE'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TASKS = 'TASKS'

    def __init__(self, value, description=None):
        self._logger.debug('TagBase.__init__ %s', self)
        self.value = value
        self.description = description

    @property
    def object_type(self):
        return ObjectTypes.Tag

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.value), self.id)

    def __str__(self):
        cls = type(self).__name__
        return '{}({}, tag id={}, id=[{}])'.format(cls, repr(self.value),
                                                   self.id, id(self))

    def to_dict(self, fields=None):

        self._logger.debug('%s', self)

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
        logger.debug('d: %s', d)

        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = cls(value, description, lazy=lazy)
        if tag_id is not None:
            tag.id = tag_id
        if not lazy:
            if 'tasks' in d:
                assign(tag.tasks, d['tasks'])
        logger.debug('tag: %s', tag)
        return tag

    def update_from_dict(self, d):
        self._logger.debug('%s: %s', self, d)
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'value' in d:
            self.value = d['value']
        if 'description' in d:
            self.description = d['description']
        if 'tasks' in d:
            assign(self.tasks, d['tasks'])
