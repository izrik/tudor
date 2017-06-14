
class OptionBase(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }


class Option(OptionBase):
    key = None
    value = None

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
