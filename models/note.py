
import datetime
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class NoteBase(object):
    def __init__(self, content, timestamp=None):
        self.content = content
        self.timestamp = self._clean_timestamp(timestamp)

    @staticmethod
    def _clean_timestamp(timestamp):
        if timestamp is None:
            return datetime.datetime.utcnow()
        if isinstance(timestamp, basestring):
            return dparse(timestamp)
        return timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': str_from_datetime(self.timestamp),
            'task_id': self.task_id
        }

    def update_from_dict(self, d):
        if 'id' in d:
            self.id = d['id']
        if 'content' in d:
            self.content = d['content']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'task_id' in d:
            self.task_id = d['task_id']


class Note(Changeable, NoteBase):
    _id = None
    _content = ''
    _timestamp = None

    _task_id = None
    _task = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._on_attr_changed()

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value
        self._on_attr_changed()

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        self._task_id = value
        self._on_attr_changed()

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        self._task = value
        self._on_attr_changed()

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
        task = db.relationship('DbTask',
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
