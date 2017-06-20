
from changeable import Changeable


class OptionBase(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

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


class Option(Changeable, OptionBase):
    _key = None
    _value = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value
        self._on_attr_changed()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._on_attr_changed()

    @staticmethod
    def from_dict(d):
        key = d.get('key')
        value = d.get('value', None)
        return Option(key, value)


def generate_option_class(db):
    class DbOption(db.Model, OptionBase):

        __tablename__ = 'option'

        key = db.Column(db.String(100), primary_key=True)
        value = db.Column(db.String(100), nullable=True)

        def __init__(self, key, value):
            db.Model.__init__(self)
            OptionBase.__init__(self, key, value)

        @staticmethod
        def from_dict(d):
            key = d.get('key')
            value = d.get('value', None)
            return DbOption(key, value)

    return DbOption
