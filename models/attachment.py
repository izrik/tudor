
import datetime
import os
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class AttachmentBase(object):

    def __init__(self, path, description=None, timestamp=None,
                 filename=None):
        if description is None:
            description = ''
        timestamp = self._clean_timestamp(timestamp)
        if filename is None:
            filename = os.path.basename(path)
        self.timestamp = timestamp
        self.path = path
        self.filename = filename
        self.description = description

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
            'timestamp': str_from_datetime(self.timestamp),
            'path': self.path,
            'filename': self.filename,
            'description': self.description,
            'task_id': self.task_id
        }

    def update_from_dict(self, d):
        if 'id' in d:
            self.id = d['id']
        if 'timestamp' in d:
            self.timestamp = self._clean_timestamp(d['timestamp'])
        if 'path' in d:
            self.path = d['path']
        if 'filename' in d:
            self.filename = d['filename']
        if 'description' in d:
            self.description = d['description']
        if 'task_id' in d:
            self.task_id = d['task_id']


class Attachment(Changeable, AttachmentBase):

    _id = None
    _timestamp = None
    _path = None
    _filename = None
    _description = ''

    _task = None
    _task_id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value
        self._on_attr_changed()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self._on_attr_changed()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
        self._on_attr_changed()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
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
        attachment_id = d.get('id', None)
        timestamp = d.get('timestamp', None)
        path = d.get('path')
        filename = d.get('filename', None)
        description = d.get('description', None)
        task_id = d.get('task_id')

        attachment = Attachment(path, description, timestamp, filename)
        if attachment_id is not None:
            attachment.id = attachment_id
        attachment.task_id = task_id
        return attachment
