
import logging_util
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from .object_types import ObjectTypes


class AttachmentBase(object):
    _logger = logging_util.get_logger_by_name(__name__, 'AttachmentBase')

    FIELD_ID = 'ID'
    FIELD_PATH = 'PATH'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_FILENAME = 'FILENAME'
    FIELD_TASK = 'TASK'

    def __init__(self, path, description='', timestamp=None,
                 filename=None):
        timestamp = self._clean_timestamp(timestamp)
        self.timestamp = timestamp
        self.path = path
        self.filename = filename
        self.description = description

    @property
    def object_type(self):
        return ObjectTypes.Attachment

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.path), self.id)

    def __str__(self):
        cls = type(self).__name__
        return '{}({}, attachment id={}, id=[{}])'.format(
            cls, repr(self.path), self.id, id(self))

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

        return d

    def to_flat_dict(self, fields=None):
        d = self.to_dict(fields=fields)
        return d

    @classmethod
    def from_dict(cls, d):
        attachment_id = d.get('id', None)
        timestamp = d.get('timestamp', None)
        path = d.get('path')
        filename = d.get('filename', None)
        description = d.get('description', None)

        attachment = cls(path, description, timestamp, filename)
        if attachment_id is not None:
            attachment.id = attachment_id
        return attachment

    def update_from_dict(self, d):
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'path' in d:
            self.path = d['path']
        if 'filename' in d:
            self.filename = d['filename']
        if 'description' in d:
            self.description = d['description']
