from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from models.object_types import ObjectTypes


class Attachment(object):
    FIELD_ID = 'ID'
    FIELD_PATH = 'PATH'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_FILENAME = 'FILENAME'
    FIELD_TASK_ID = 'TASK_ID'

    def __init__(self, path, description='', timestamp=None, filename=None,
                 task_id=None, id=None):
        self.id = id
        self.path = path
        self.description = description
        self.timestamp = self._clean_timestamp(timestamp)
        self.filename = filename
        self.task_id = task_id

    @property
    def object_type(self):
        return ObjectTypes.Attachment

    def __repr__(self):
        return 'Attachment({}, id={})'.format(repr(self.path), self.id)

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
        if fields is None or self.FIELD_PATH in fields:
            d['path'] = self.path
        if fields is None or self.FIELD_FILENAME in fields:
            d['filename'] = self.filename
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d['description'] = self.description
        if fields is None or self.FIELD_TASK_ID in fields:
            d['task_id'] = self.task_id
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            path=d.get('path'),
            description=d.get('description', ''),
            timestamp=d.get('timestamp'),
            filename=d.get('filename'),
            task_id=d.get('task_id'))
