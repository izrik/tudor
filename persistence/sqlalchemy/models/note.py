
from __future__ import absolute_import

import logging_util
from models.changeable import Changeable
from models.note_base import NoteBase


def generate_note_class(db):
    class DbNote(db.Model, NoteBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbNote')

        __tablename__ = 'note'

        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(4000))
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('notes', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            NoteBase.__init__(self, content, timestamp)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbNote, cls).from_dict(d=d, lazy=None)

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_CONTENT,
                         self.FIELD_TIMESTAMP, self.FIELD_TASK):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_CONTENT:
                self.content = value
            elif field == self.FIELD_TIMESTAMP:
                self.timestamp = value
            else:  # field == self.FIELD_TASK
                self.task = value

    return DbNote
