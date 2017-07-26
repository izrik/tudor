
import datetime
from dateutil.parser import parse as dparse

import logging_util
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
        return '{}({}, id={})'.format(cls, repr(self.content), self.id)

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
        if 'task' in d:
            self.task = d['task']

    @property
    def id2(self):
        if len(self.content) > 20:
            return '[{}] {}... ({})'.format(id(self), repr(self.content[:20]),
                                            self.id)
        return '[{}] {} ({})'.format(id(self), repr(self.content), self.id)


class Note(Changeable, NoteBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Note')

    _id = None
    _content = ''
    _timestamp = None

    _task = None

    _dbobj = None

    def __init__(self, content, timestamp=None, lazy=None):
        super(Note, self).__init__(content, timestamp)
        self._logger.debug('Note.__init__ {}'.format(self.id2))

        if lazy is None:
            lazy = {}

        self._task_lazy = lazy.get('task')

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
        if self._task_lazy:
            self.task = self._task_lazy()
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
        self._task_lazy = None

    @staticmethod
    def from_dict(d, lazy=None):
        note_id = d.get('id', None)
        content = d.get('content')
        timestamp = d.get('timestamp', None)
        task = d.get('task')

        note = Note(content, timestamp)
        if note_id is not None:
            note.id = note_id
        note.task = task
        return note

    def clear_relationships(self):
        self.task = None
