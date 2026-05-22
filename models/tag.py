from models.object_types import ObjectTypes


class Tag(object):
    FIELD_ID = 'ID'
    FIELD_VALUE = 'VALUE'
    FIELD_DESCRIPTION = 'DESCRIPTION'

    def __init__(self, value, description=None, id=None):
        self.id = id
        self.value = value
        self.description = description

    @property
    def object_type(self):
        return ObjectTypes.Tag

    def __repr__(self):
        return 'Tag({}, id={})'.format(repr(self.value), self.id)

    def to_dict(self, fields=None):
        d = {}
        if fields is None or self.FIELD_ID in fields:
            d['id'] = self.id
        if fields is None or self.FIELD_VALUE in fields:
            d['value'] = self.value
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d['description'] = self.description
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            value=d.get('value'),
            description=d.get('description'))
