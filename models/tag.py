
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


class Tag(TagBase):

    id = None
    value = None
    description = None

    @staticmethod
    def from_dict(d):
        tag_id = d.get('id', None)
        value = d.get('value')
        description = d.get('description', None)

        tag = Tag(value, description)
        if tag_id is not None:
            tag.id = tag_id
        return tag


def generate_tag_class(db):
    class DbTag(db.Model, TagBase):

        __tablename__ = 'tag'

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.String(4000), nullable=True)

        def __init__(self, value, description=None):
            db.Model.__init__(self)
            TagBase.__init__(self, value, description)

        def to_dict(self):
            return {
                'id': self.id,
                'value': self.value,
                'description': self.description,
            }

        @staticmethod
        def from_dict(d):
            tag_id = d.get('id', None)
            value = d.get('value')
            description = d.get('description', None)

            tag = DbTag(value, description)
            if tag_id is not None:
                tag.id = tag_id
            return tag

    return DbTag
