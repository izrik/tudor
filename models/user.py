
from changeable import Changeable


class UserBase(object):
    authenticated = True

    def __init__(self, email, hashed_password, is_admin=False):

        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'is_admin': self.is_admin
        }

    def update_from_dict(self, d):
        if 'id' in d:
            self.id = d['id']
        if 'email' in d:
            self.email = d['email']
        if 'hashed_password' in d:
            self.hashed_password = d['hashed_password']
        if 'is_admin' in d:
            self.is_admin = d['is_admin']

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class User(Changeable, UserBase):
    _id = None
    _email = None
    _hashed_password = None
    _is_admin = None
    _authenticated = None

    def __init__(self, email, hashed_password=None, is_admin=False):
        if hashed_password is None:
            hashed_password = ''
        super(User, self).__init__(email=email,
                                   hashed_password=hashed_password,
                                   is_admin=is_admin)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value
        self._on_attr_changed()

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value):
        self._hashed_password = value
        self._on_attr_changed()

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        self._is_admin = value
        self._on_attr_changed()

    @property
    def authenticated(self):
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value):
        self._authenticated = value
        self._on_attr_changed()

    @staticmethod
    def from_dict(d):
        user_id = d.get('id', None)
        email = d.get('email')
        hashed_password = d.get('hashed_password', None)
        is_admin = d.get('is_admin', False)

        user = User(email, hashed_password, is_admin)
        if user_id is not None:
            user.id = user_id
        return user
