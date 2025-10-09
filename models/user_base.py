
import logging_util
from collections_util import assign
from models.object_types import ObjectTypes


class UserBase(object):
    _logger = logging_util.get_logger_by_name(__name__, 'UserBase')

    FIELD_ID = 'ID'
    FIELD_EMAIL = 'EMAIL'
    FIELD_HASHED_PASSWORD = 'HASHED_PASSWORD'
    FIELD_IS_ADMIN = 'IS_ADMIN'
    FIELD_TASKS = 'TASKS'

    _is_authenticated = True
    _is_anonymous = False

    def __init__(self, email, hashed_password, is_admin=False):

        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    @property
    def object_type(self):
        return ObjectTypes.User

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.email), self.id)

    def __str__(self):
        cls = type(self).__name__
        return '{}({}, user id={}, id=[{}])'.format(cls, repr(self.email),
                                                    self.id, id(self))

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

    def to_flat_dict(self, fields=None):
        d = self.to_dict(fields=fields)
        return d

    @classmethod
    def from_dict(cls, d):
        user_id = d.get('id', None)
        email = d.get('email')
        hashed_password = d.get('hashed_password', None)
        is_admin = d.get('is_admin', False)

        user = cls(email, hashed_password, is_admin)
        if user_id is not None:
            user.id = user_id
        return user

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'email' in d:
            self.email = d['email']
        if 'hashed_password' in d:
            self.hashed_password = d['hashed_password']
        if 'is_admin' in d:
            self.is_admin = d['is_admin']


class User2(UserBase):
    def __init__(self, email, hashed_password, is_admin=False):
        super().__init__(email=email, hashed_password=hashed_password,
                         is_admin=is_admin)
        self._id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._id is not None:
            raise ValueError("id already set")
        self._id = value

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
