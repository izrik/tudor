
import datetime
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class NoteBase(object):

    FIELD_ID = 'ID'
    FIELD_CONTENT = 'CONTENT'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_TASK = 'TASK'

    def __init__(self, content, timestamp=None):
        self.content = content
        self.timestamp = self._clean_timestamp(timestamp)

    @staticmethod
    def get_related_fields(field):
        return ()

    @staticmethod
    def get_autochange_fields():
        return (NoteBase.FIELD_ID, NoteBase.FIELD_TASK)

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, self.content, self.id)

    @staticmethod
    def _clean_timestamp(timestamp):
        if timestamp is None:
            return datetime.datetime.utcnow()
        if isinstance(timestamp, basestring):
            return dparse(timestamp)
        return timestamp

    def to_dict(self, fields=None):

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d[self.FIELD_ID] = self.id
        if fields is None or self.FIELD_TIMESTAMP in fields:
            d[self.FIELD_TIMESTAMP] = str_from_datetime(self.timestamp)
        if fields is None or self.FIELD_CONTENT in fields:
            d[self.FIELD_CONTENT] = self.content
        if fields is None or self.FIELD_TASK in fields:
            d[self.FIELD_TASK] = self.task

        return d

    def update_from_dict(self, d):
        if self.FIELD_ID in d and d[self.FIELD_ID] is not None:
            self.id = d[self.FIELD_ID]
        if self.FIELD_CONTENT in d:
            self.content = d[self.FIELD_CONTENT]
        if self.FIELD_TIMESTAMP in d:
            self.timestamp = self._clean_timestamp(d[self.FIELD_TIMESTAMP])
        if self.FIELD_TASK in d:
            self.task = d[self.FIELD_TASK]

    @property
    def id2(self):
        if len(self.content) > 20:
            return '[{}] {}... ({})'.format(id(self), self.content[:20],
                                            self.id)
        return '[{}] {} ({})'.format(id(self), self.content, self.id)


class Note(Changeable, NoteBase):
    _id = None
    _content = ''
    _timestamp = None

    _task = None

    _dbobj = None

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
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if value != self._content:
            self._on_attr_changing(self.FIELD_CONTENT, self._content)
            self._content = value
            self._on_attr_changed(self.FIELD_CONTENT, self.OP_SET,
                                  self._content)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if value != self._timestamp:
            self._on_attr_changing(self.FIELD_TIMESTAMP, self._timestamp)
            self._timestamp = value
            self._on_attr_changed(self.FIELD_TIMESTAMP, self.OP_SET,
                                  self._timestamp)

    @property
    def task_id(self):
        if self.task:
            return self.task.id
        return None

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        if value != self._task:
            self._on_attr_changing(self.FIELD_TASK, self._task)
            if self._task is not None:
                self._task.notes.discard(self)
            self._task = value
            if self._task is not None:
                self._task.notes.add(self)
            self._on_attr_changed(self.FIELD_TASK, self.OP_SET, self._task)

    @staticmethod
    def from_dict(d):
        note_id = d.get(Note.FIELD_ID, None)
        content = d.get(Note.FIELD_CONTENT)
        timestamp = d.get(Note.FIELD_TIMESTAMP, None)
        task = d.get(Note.FIELD_TASK)

        note = Note(content, timestamp)
        if note_id is not None:
            note.id = note_id
        note.task = task
        return note

    def clear_relationships(self):
        self.task = None
