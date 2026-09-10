from models.object_types import ObjectTypes


class User(object):
    FIELD_ID = 'ID'
    FIELD_EMAIL = 'EMAIL'
    FIELD_HASHED_PASSWORD = 'HASHED_PASSWORD'
    FIELD_IS_ADMIN = 'IS_ADMIN'

    _is_authenticated = True
    _is_anonymous = False

    def __init__(self, email, hashed_password=None, is_admin=False, id=None):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    @property
    def object_type(self):
        return ObjectTypes.User

    def __repr__(self):
        return 'User({}, id={})'.format(repr(self.email), self.id)

    def to_dict(self, fields=None):
        d = {}
        if fields is None or self.FIELD_ID in fields:
            d['id'] = self.id
        if fields is None or self.FIELD_EMAIL in fields:
            d['email'] = self.email
        if fields is None or self.FIELD_HASHED_PASSWORD in fields:
            d['hashed_password'] = self.hashed_password
        if fields is None or self.FIELD_IS_ADMIN in fields:
            d['is_admin'] = self.is_admin
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            email=d.get('email'),
            hashed_password=d.get('hashed_password'),
            is_admin=d.get('is_admin', False))

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @property
    def is_anonymous(self):
        return self._is_anonymous
