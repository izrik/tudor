
from __future__ import absolute_import

import logging_util
from models.changeable import Changeable
from models.tag_base import TagBase


def generate_tag_class(db, tags_tasks_table):
    class DbTag(db.Model, TagBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbTag')

        __tablename__ = 'tag'

        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.String(100), nullable=False, unique=True)
        description = db.Column(db.String(4000), nullable=True)

        tasks = db.relationship('DbTask', secondary=tags_tasks_table,
                                back_populates='tags')

        def __init__(self, value, description=None, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            TagBase.__init__(self, value, description)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbTag, cls).from_dict(d=d, lazy=None)

        def make_change(self, field, operation, value):
            if operation == Changeable.OP_CHANGING:
                raise ValueError('Invalid operation "{}"'.format(operation))

            if field in (self.FIELD_ID, self.FIELD_VALUE,
                         self.FIELD_DESCRIPTION):
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
            elif field == self.FIELD_VALUE:
                self.value = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            else:  # field == self.FIELD_TASKS
                if operation == Changeable.OP_ADD:
                    if value not in self.tasks:
                        self.tasks.append(value)
                elif operation == Changeable.OP_REMOVE:
                    if value in self.tasks:
                        self.tasks.remove(value)

    return DbTag
