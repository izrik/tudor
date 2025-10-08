
import logging_util
from collections_util import assign
from models.object_types import ObjectTypes


class TagBase(object):
    _logger = logging_util.get_logger_by_name(__name__, 'TagBase')

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

        return d

    def to_flat_dict(self, fields=None):
        d = self.to_dict(fields=fields)
        return d

    @classmethod
    def from_dict(cls, d):
        cls._logger.debug('d: %s', d)

        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = cls(value, description)
        if tag_id is not None:
            tag.id = tag_id
        cls._logger.debug('tag: %s', tag)
        return tag

    def update_from_dict(self, d):
        self._logger.debug('%s: %s', self, d)
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'value' in d:
            self.value = d['value']
        if 'description' in d:
            self.description = d['description']
