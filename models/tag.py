
def generate_tag_class(db):
    class Tag(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.String(4000), nullable=True)

        def __init__(self, value, description=None):
            self.value = value
            self.description = description

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

            tag = Tag(value, description)
            if tag_id is not None:
                tag.id = tag_id
            return tag

    return Tag
