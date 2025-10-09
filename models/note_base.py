
import logging_util
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from models.object_types import ObjectTypes


class NoteBase(object):
    _logger = logging_util.get_logger_by_name(__name__, 'NoteBase')

    FIELD_ID = 'ID'
    FIELD_CONTENT = 'CONTENT'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_TASK = 'TASK'

    def __init__(self, content, timestamp=None):
        self.content = content
        self.timestamp = self._clean_timestamp(timestamp)
        self.task_id = None

    @property
    def object_type(self):
        return ObjectTypes.Note

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.content), self.id)

    def __str__(self):
        cls = type(self).__name__
        if self.content is not None and len(self.content) > 20:
            return '{}({}..., note id={}, id=[{}])'.format(
                cls, repr(self.content[:20]), self.id, id(self))
        return '{}({}, note id={}, id=[{}])'.format(
            cls, repr(self.content), self.id, id(self))

    @staticmethod
    def _clean_timestamp(timestamp):
        if timestamp is None:
            return None
        if isinstance(timestamp, str):
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
        if fields is None or 'task_id' in (fields or []):
            d['task_id'] = getattr(self, 'task_id', None)

        return d

    def to_flat_dict(self, fields=None):
        d = self.to_dict(fields=fields)
        return d

    @classmethod
    def from_dict(cls, d):
        note_id = d.get('id', None)
        content = d.get('content')
        timestamp = d.get('timestamp', None)

        note = cls(content, timestamp)
        if note_id is not None:
            note.id = note_id
        if 'task_id' in d:
            note.task_id = d['task_id']
        return note

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'content' in d:
            self.content = d['content']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'task_id' in d:
            self.task_id = d['task_id']


class Note2(NoteBase):
    def __init__(self, content, timestamp=None, task_id=None):
        super().__init__(content=content, timestamp=timestamp)
        self.task_id = task_id
        self._id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._id is not None:
            raise ValueError("id already set")
        self._id = value
