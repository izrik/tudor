
import datetime
from dateutil.parser import parse as dparse

from conversions import str_from_datetime


class NoteBase(object):
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


class Note(NoteBase):
    id = None
    content = ''
    timestamp = None

    task_id = None
    task = None

    @staticmethod
    def from_dict(d):
        note_id = d.get('id', None)
        content = d.get('content')
        timestamp = d.get('timestamp', None)
        task_id = d.get('task_id')

        note = Note(content, timestamp)
        if note_id is not None:
            note.id = note_id
        note.task_id = task_id
        return note


def generate_note_class(db):
    class DbNote(db.Model, NoteBase):

        __tablename__ = 'note'

        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.String(4000))
        timestamp = db.Column(db.DateTime)

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('Task',
                               backref=db.backref('notes', lazy='dynamic',
                                                  order_by=timestamp))

        def __init__(self, content, timestamp=None):
            db.Model.__init__(self)
            NoteBase.__init__(self, content, timestamp)

        @staticmethod
        def from_dict(d):
            note_id = d.get('id', None)
            content = d.get('content')
            timestamp = d.get('timestamp', None)
            task_id = d.get('task_id')

            note = DbNote(content, timestamp)
            if note_id is not None:
                note.id = note_id
            note.task_id = task_id
            return note

    return DbNote
