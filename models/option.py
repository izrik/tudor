
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
        return '{}(key{}, value={})'.format(cls, self.key, self.value)

    @property
    def id(self):
        return self.key

    def to_dict(self, fields=None):

        d = {}
        if fields is None or self.FIELD_KEY in fields:
            d[self.FIELD_KEY] = self.key
        if fields is None or self.FIELD_VALUE in fields:
            d[self.FIELD_VALUE] = self.value

        return d

    def update_from_dict(self, d):
        if self.FIELD_KEY in d and d[self.FIELD_KEY] is not None:
            self.key = d[self.FIELD_KEY]
        if self.FIELD_VALUE in d:
            self.value = d[self.FIELD_VALUE]

    @property
    def id2(self):
        return '[{}] {}={}'.format(id(self), self.key, self.value)


class Option(Changeable, OptionBase):
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
        key = d.get(Option.FIELD_KEY)
        value = d.get(Option.FIELD_VALUE, None)
        return Option(key, value)

    def clear_relationships(self):
        pass
