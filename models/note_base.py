
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from models.object_types import ObjectTypes


class NoteBase(object):

    FIELD_ID = 'ID'
    FIELD_CONTENT = 'CONTENT'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_TASK = 'TASK'

    def __init__(self, content, timestamp=None):
        self.content = content
        self.timestamp = self._clean_timestamp(timestamp)

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
        if fields is None or self.FIELD_TASK in fields:
            d['task'] = self.task

        return d

    @classmethod
    def from_dict(cls, d, lazy=None):
        note_id = d.get('id', None)
        content = d.get('content')
        timestamp = d.get('timestamp', None)
        task = d.get('task')

        note = cls(content, timestamp, lazy=lazy)
        if note_id is not None:
            note.id = note_id
        if not lazy:
            note.task = task
        return note

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'content' in d:
            self.content = d['content']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'task' in d:
            self.task = d['task']
