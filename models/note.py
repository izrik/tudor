
import datetime
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class NoteBase(object):

    FIELD_ID = 'ID'
    FIELD_CONTENT = 'CONTENT'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_TASK_ID = 'TASK_ID'
    FIELD_TASK = 'TASK'

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

    def to_dict(self, fields=None):

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d['id'] = self.id
        if fields is None or self.FIELD_TIMESTAMP in fields:
            d['timestamp'] = str_from_datetime(self.timestamp)
        if fields is None or self.FIELD_CONTENT in fields:
            d['content'] = self.content
        if fields is None or self.FIELD_TASK_ID in fields:
            d['task_id'] = self.task_id
        if fields is None or self.FIELD_TASK in fields:
            d['task'] = self.task

        return d

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'content' in d:
            self.content = d['content']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'task_id' in d:
            self.task_id = d['task_id']

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

    _task_id = None
    _task = None

    _dbobj = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._id = value
            self._on_attr_changed(self.FIELD_ID)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if value != self._content:
            self._content = value
            self._on_attr_changed(self.FIELD_CONTENT)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if value != self._timestamp:
            self._timestamp = value
            self._on_attr_changed(self.FIELD_TIMESTAMP)

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        if value != self._task_id:
            self._task_id = value
            self._on_attr_changed(self.FIELD_TASK_ID)

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        if value != self._task:
            self._task = value
            self._on_attr_changed(self.FIELD_TASK)

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
