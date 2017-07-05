
from changeable import Changeable


class OptionBase(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    @property
    def id(self):
        return self.key

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }

    def update_from_dict(self, d):
        if 'key' in d:
            self.key = d['key']
        if 'value' in d:
            self.value = d['value']

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
            self._key = value
            self._on_attr_changed()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self._on_attr_changed()

    @staticmethod
    def from_dict(d):
        key = d.get('key')
        value = d.get('value', None)
        return Option(key, value)
