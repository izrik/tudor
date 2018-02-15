
class OptionBase(object):

    FIELD_KEY = 'KEY'
    FIELD_VALUE = 'VALUE'

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        cls = type(self).__name__
        return '{}(key={}, value={})'.format(cls, repr(self.key),
                                             repr(self.value))

    def __str__(self):
        cls = type(self).__name__
        return '{}(key={}, value={}, id=[{}])'.format(
            cls, repr(self.key), repr(self.value), id(self))

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

    @classmethod
    def from_dict(cls, d, lazy=None):
        key = d.get('key')
        value = d.get('value', None)
        return cls(key, value)

    def update_from_dict(self, d):
        if 'key' in d and d['key'] is not None:
            self.key = d['key']
        if 'value' in d:
            self.value = d['value']
