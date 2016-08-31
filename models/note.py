
import datetime
from dateutil.parser import parse as dparse

from conversions import str_from_datetime


def generate_note_class(db):
    class Note(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(4000))
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('Task',
                               backref=db.backref('notes', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None):
            self.content = content
            if timestamp is None:
                timestamp = datetime.datetime.utcnow()
            if isinstance(timestamp, basestring):
                timestamp = dparse(timestamp)
            self.timestamp = timestamp

        def to_dict(self):
            return {
                'id': self.id,
                'content': self.content,
                'timestamp': str_from_datetime(self.timestamp),
                'task_id': self.task_id
            }

    return Note