
import logging_util
from models.user_base import UserBase
from persistence.in_memory.models.changeable import Changeable
from persistence.in_memory.models.interlinking import ManyToManySet


class User(Changeable, UserBase):
    _logger = logging_util.get_logger_by_name(__name__, 'User')

    _id = None
    _email = None
    _hashed_password = None
    _is_admin = None

    def __init__(self, email, hashed_password=None, is_admin=False):
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
        self._logger.debug('%s', self)
        return self._tasks

    def clear_relationships(self):
        self.tasks.clear()


class InterlinkedTasks(ManyToManySet):
    __change_field__ = UserBase.FIELD_TASKS
    __attr_counterpart__ = 'users'
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InterlinkedTasks')
