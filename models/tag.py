
from changeable import Changeable


class TagBase(object):
    def __init__(self, value, description=None):
        self.value = value
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'description': self.description,
        }

    def update_from_dict(self, d):
        if 'id' in d:
            self.id = d['id']
        if 'value' in d:
            self.value = d['value']
        if 'description' in d:
            self.description = d['description']


class Tag(Changeable, TagBase):

    _id = None
    _value = None
    _description = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._on_attr_changed()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._on_attr_changed()

    @staticmethod
    def from_dict(d):
        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = Tag(value, description)
        if tag_id is not None:
            tag.id = tag_id
        return tag
