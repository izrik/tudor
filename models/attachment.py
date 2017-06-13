
import datetime
import os
from dateutil.parser import parse as dparse

from conversions import str_from_datetime


def generate_attachment_class(db):
    class Attachment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.DateTime, nullable=False)
        path = db.Column(db.String(1000), nullable=False)
        filename = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(100), nullable=False, default='')

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('Task',
                               backref=db.backref('attachments',
                                                  lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, path, description=None, timestamp=None,
                     filename=None):
            if description is None:
                description = ''
            if timestamp is None:
                timestamp = datetime.datetime.utcnow()
            if isinstance(timestamp, basestring):
                timestamp = dparse(timestamp)
            if filename is None:
                filename = os.path.basename(path)
            self.timestamp = timestamp
            self.path = path
            self.filename = filename
            self.description = description

        def to_dict(self):
            return {
                'id': self.id,
                'timestamp': str_from_datetime(self.timestamp),
                'path': self.path,
                'filename': self.filename,
                'description': self.description,
                'task_id': self.task_id
            }

        @staticmethod
        def from_dict(d):
            attachment_id = d.get('id', None)
            timestamp = d.get('timestamp', None)
            path = d.get('path')
            filename = d.get('filename', None)
            description = d.get('description', None)
            task_id = d.get('task_id')

            attachment = Attachment(path, description, timestamp, filename)
            if attachment_id is not None:
                attachment.id = attachment_id
            attachment.task_id = task_id
            return attachment

    return Attachment
