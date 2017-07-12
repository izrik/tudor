
import datetime
import os
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class AttachmentBase(object):

    FIELD_ID = 'ID'
    FIELD_PATH = 'PATH'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_TIMESTAMP = 'TIMESTAMP'
    FIELD_FILENAME = 'FILENAME'
    FIELD_TASK_ID = 'TASK_ID'
    FIELD_TASK = 'TASK'

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
    def get_related_fields(field):
        if field == AttachmentBase.FIELD_TASK:
            return (AttachmentBase.FIELD_TASK_ID,)
        if field == AttachmentBase.FIELD_TASK_ID:
            return (AttachmentBase.FIELD_TASK,)
        return ()

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
        if fields is None or self.FIELD_PATH in fields:
            d['path'] = self.path
        if fields is None or self.FIELD_FILENAME in fields:
            d['filename'] = self.filename
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d['description'] = self.description
        if fields is None or self.FIELD_TASK_ID in fields:
            d['task_id'] = self.task_id
        if fields is None or self.FIELD_TASK in fields:
            d['task'] = self.task

        return d

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
        if 'task_id' in d:
            self.task_id = d['task_id']

    @property
    def id2(self):
        return '[{}] {} ({})'.format(id(self), self.filename, self.id)


class Attachment(Changeable, AttachmentBase):

    _id = None
    _timestamp = None
    _path = None
    _filename = None
    _description = ''

    _task = None
    _task_id = None

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
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if value != self._timestamp:
            self._timestamp = value
            self._on_attr_changed(self.FIELD_TIMESTAMP)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value != self._path:
            self._path = value
            self._on_attr_changed(self.FIELD_PATH)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if value != self._filename:
            self._filename = value
            self._on_attr_changed(self.FIELD_FILENAME)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION)

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
            if self._task is not None:
                self._task.attachments.discard(self)
            self._task = value
            if self._task is not None:
                self._task.attachments.add(self)
            self._on_attr_changed(self.FIELD_TASK)

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
