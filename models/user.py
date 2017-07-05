
import collections

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

    @property
    def id2(self):
        return '[{}] {} ({})'.format(id(self), self.email, self.id)


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
        self._tasks = InterlinkedTasks(self)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._id = value
            self._on_attr_changed()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if value != self._email:
            self._email = value
            self._on_attr_changed()

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value):
        if value != self._hashed_password:
            self._hashed_password = value
            self._on_attr_changed()

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        if value != self._is_admin:
            self._is_admin = value
            self._on_attr_changed()

    @property
    def authenticated(self):
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value):
        if value != self._authenticated:
            self._authenticated = value
            self._on_attr_changed()

    @property
    def tasks(self):
        return self._tasks

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


class InterlinkedTasks(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __len__(self):
        return len(self.set)

    def __contains__(self, task):
        return self.set.__contains__(task)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, task):
        if task not in self.set:
            self.set.add(task)
            task.users.add(self.container)
            self.container._on_attr_changed()

    def append(self, task):
        self.add(task)

    def discard(self, task):
        if task in self.set:
            self.set.discard(task)
            task.users.discard(self.container)
            self.container._on_attr_changed()
