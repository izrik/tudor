
from __future__ import absolute_import

import logging_util
from models.attachment_base import AttachmentBase
from models.changeable import Changeable


def generate_attachment_class(db):
    class DbAttachment(db.Model, AttachmentBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbAttachment')

        __tablename__ = 'attachment'

        id = db.Column(db.Integer, primary_key=True)
        path = db.Column(db.String(1000), nullable=False)
        timestamp = db.Column(db.DateTime)
        filename = db.Column(db.String(100))
        description = db.Column(db.String(100), default=None)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('DbTask',
                               backref=db.backref('attachments',
                                                  lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, path, description=None, timestamp=None,
                     filename=None, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            AttachmentBase.__init__(self, path, description, timestamp,
                                    filename)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbAttachment, cls).from_dict(d=d, lazy=None)

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_PATH,
                         self.FIELD_DESCRIPTION, self.FIELD_TIMESTAMP,
                         self.FIELD_FILENAME, self.FIELD_TASK):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_PATH:
                self.path = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            elif field == self.FIELD_TIMESTAMP:
                self.timestamp = value
            elif field == self.FIELD_FILENAME:
                self.filename = value
            else:  # field == self.FIELD_TASK
                self.task = value

        def clear_relationships(self):
            self.task = None

    return DbAttachment
