
import collections

from changeable import Changeable
from collections_util import assign


class UserBase(object):

    FIELD_ID = 'ID'
    FIELD_EMAIL = 'EMAIL'
    FIELD_HASHED_PASSWORD = 'HASHED_PASSWORD'
    FIELD_IS_ADMIN = 'IS_ADMIN'
    FIELD_TASKS = 'TASKS'

    authenticated = True

    def __init__(self, email, hashed_password, is_admin=False):

        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    @staticmethod
    def get_related_fields(field):
        return ()

    @staticmethod
    def get_autochange_fields():
        return (UserBase.FIELD_ID,)

    def to_dict(self, fields=None):

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d[self.FIELD_ID] = self.id
        if fields is None or self.FIELD_EMAIL in fields:
            d[self.FIELD_EMAIL] = self.email
        if fields is None or self.FIELD_HASHED_PASSWORD in fields:
            d[self.FIELD_HASHED_PASSWORD] = self.hashed_password
        if fields is None or self.FIELD_IS_ADMIN in fields:
            d[self.FIELD_IS_ADMIN] = self.is_admin

        if fields is None or self.FIELD_TASKS in fields:
            d[self.FIELD_TASKS] = list(self.tasks)

        return d

    def update_from_dict(self, d):
        if self.FIELD_ID in d and d[self.FIELD_ID] is not None:
            self.id = d[self.FIELD_ID]
        if self.FIELD_EMAIL in d:
            self.email = d[self.FIELD_EMAIL]
        if self.FIELD_HASHED_PASSWORD in d:
            self.hashed_password = d[self.FIELD_HASHED_PASSWORD]
        if self.FIELD_IS_ADMIN in d:
            self.is_admin = d[self.FIELD_IS_ADMIN]
        if self.FIELD_TASKS in d:
            assign(self.tasks, d[self.FIELD_TASKS])

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

    _dbobj = None

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
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if value != self._email:
            self._on_attr_changing(self.FIELD_EMAIL, self._email)
            self._email = value
            self._on_attr_changed(self.FIELD_EMAIL, self.OP_SET, self._email)

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value):
        if value != self._hashed_password:
            self._on_attr_changing(self.FIELD_HASHED_PASSWORD,
                                   self._hashed_password)
            self._hashed_password = value
            self._on_attr_changed(self.FIELD_HASHED_PASSWORD, self.OP_SET,
                                  self._hashed_password)

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        if value != self._is_admin:
            self._on_attr_changing(self.FIELD_IS_ADMIN, self._is_admin)
            self._is_admin = value
            self._on_attr_changed(self.FIELD_IS_ADMIN, self.OP_SET,
                                  self._is_admin)

    @property
    def tasks(self):
        return self._tasks

    @staticmethod
    def from_dict(d):
        user_id = d.get(User.FIELD_ID, None)
        email = d.get(User.FIELD_EMAIL)
        hashed_password = d.get(User.FIELD_HASHED_PASSWORD, None)
        is_admin = d.get(User.FIELD_IS_ADMIN, False)

        user = User(email, hashed_password, is_admin)
        if user_id is not None:
            user.id = user_id
        return user

    def clear_relationships(self):
        self.tasks.clear()


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
            self.container._on_attr_changing(User.FIELD_TASKS, None)
            self.set.add(task)
            task.users.add(self.container)
            self.container._on_attr_changed(User.FIELD_TASKS, User.OP_ADD,
                                            task)

    def append(self, task):
        self.add(task)

    def discard(self, task):
        if task in self.set:
            self.container._on_attr_changing(User.FIELD_TASKS, None)
            self.set.discard(task)
            task.users.discard(self.container)
            self.container._on_attr_changed(User.FIELD_TASKS, User.OP_REMOVE,
                                            task)
