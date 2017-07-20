import logging_util
from changeable import Changeable


class OptionBase(object):

    FIELD_KEY = 'KEY'
    FIELD_VALUE = 'VALUE'

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @staticmethod
    def get_related_fields(field):
        return ()

    @staticmethod
    def get_autochange_fields():
        return ()

    def __repr__(self):
        cls = type(self).__name__
        return '{}(key{}, value={})'.format(cls, repr(self.key),
                                            repr(self.value))

    @property
    def id(self):
        return self.key

    def to_dict(self, fields=None):

        d = {}
        if fields is None or self.FIELD_KEY in fields:
            d['key'] = self.key
        if fields is None or self.FIELD_VALUE in fields:
            d['value'] = self.value

        return d

    def update_from_dict(self, d):
        if 'key' in d and d['key'] is not None:
            self.key = d['key']
        if 'value' in d:
            self.value = d['value']

    @property
    def id2(self):
        return '[{}] {}={}'.format(id(self), repr(self.key), repr(self.value))


class Option(Changeable, OptionBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Option')

    _key = None
    _value = None

    _dbobj = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        if value != self._key:
            self._on_attr_changing(self.FIELD_KEY, self._key)
            self._key = value
            self._on_attr_changed(self.FIELD_KEY, self.OP_SET, self._key)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._on_attr_changing(self.FIELD_VALUE,
                                   self._value)
            self._value = value
            self._on_attr_changed(self.FIELD_VALUE, self.OP_SET, self._value)

    @staticmethod
    def from_dict(d):
        key = d.get('key')
        value = d.get('value', None)
        return Option(key, value)

    def clear_relationships(self):
        pass
