from models.object_types import ObjectTypes


class Option(object):
    FIELD_KEY = 'KEY'
    FIELD_VALUE = 'VALUE'

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @property
    def object_type(self):
        return ObjectTypes.Option

    @property
    def id(self):
        return self.key

    def __repr__(self):
        return 'Option(key={}, value={})'.format(repr(self.key),
                                                 repr(self.value))

    def to_dict(self, fields=None):
        d = {}
        if fields is None or self.FIELD_KEY in fields:
            d['key'] = self.key
        if fields is None or self.FIELD_VALUE in fields:
            d['value'] = self.value
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(key=d.get('key'), value=d.get('value'))
