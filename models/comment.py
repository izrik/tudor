from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from models.object_types import ObjectTypes


class Comment(object):
    FIELD_ID = 'ID'
    FIELD_CONTENT = 'CONTENT'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_DATE_LAST_UPDATED = 'DATE_LAST_UPDATED'
    FIELD_TASK_ID = 'TASK_ID'

    def __init__(self, content, timestamp=None, date_last_updated=None,
                 task_id=None, id=None):
        self.id = id
        self.content = content
        self.timestamp = self._clean_timestamp(timestamp)
        self.date_last_updated = self._clean_timestamp(date_last_updated)
        self.task_id = task_id

    @property
    def object_type(self):
        return ObjectTypes.Comment

    def __repr__(self):
        return 'Comment({}, id={})'.format(repr(self.content), self.id)

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
        if fields is None or self.FIELD_DATE_LAST_UPDATED in fields:
            d['date_last_updated'] = str_from_datetime(self.date_last_updated)
        if fields is None or self.FIELD_CONTENT in fields:
            d['content'] = self.content
        if fields is None or self.FIELD_TASK_ID in fields:
            d['task_id'] = self.task_id
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            content=d.get('content'),
            timestamp=d.get('timestamp'),
            date_last_updated=d.get('date_last_updated'),
            task_id=d.get('task_id'))
