
from __future__ import absolute_import

import logging_util
from models.changeable import Changeable
from models.user_base import UserBase


def generate_user_class(db, users_tasks_table):
    class DbUser(db.Model, UserBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbUser')

        __tablename__ = 'user'

        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), nullable=False, unique=True)
        hashed_password = db.Column(db.String(100))
        is_admin = db.Column(db.Boolean, nullable=False, default=False)

        tasks = db.relationship('DbTask', secondary=users_tasks_table,
                                back_populates='users')

        def __init__(self, email, hashed_password=None, is_admin=False,
                     lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            UserBase.__init__(self, email=email,
                              hashed_password=hashed_password,
                              is_admin=is_admin)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbUser, cls).from_dict(d=d, lazy=None)

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_EMAIL,
                         self.FIELD_HASHED_PASSWORD, self.FIELD_IS_ADMIN):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            elif field == self.FIELD_TASKS:
                if operation not in (Changeable.OP_ADD, Changeable.OP_REMOVE):
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_EMAIL:
                self.email = value
            elif field == self.FIELD_HASHED_PASSWORD:
                self.hashed_password = value
            elif field == self.FIELD_IS_ADMIN:
                self.is_admin = value
            else:  # field == self.FIELD_TASKS
                if operation == Changeable.OP_ADD:
                    if value not in self.tasks:
                        self.tasks.append(value)
                elif operation == Changeable.OP_REMOVE:
                    if value in self.tasks:
                        self.tasks.remove(value)

    return DbUser
