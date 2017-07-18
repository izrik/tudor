
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
        return ()

    @staticmethod
    def get_autochange_fields():
        return (AttachmentBase.FIELD_ID, AttachmentBase.FIELD_TASK)

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, self.path, self.id)

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
        if fields is None or self.FIELD_PATH in fields:
            d[self.FIELD_PATH] = self.path
        if fields is None or self.FIELD_FILENAME in fields:
            d[self.FIELD_FILENAME] = self.filename
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d[self.FIELD_DESCRIPTION] = self.description
        if fields is None or self.FIELD_TASK in fields:
            d[self.FIELD_TASK] = self.task

        return d

    def update_from_dict(self, d):
        if self.FIELD_ID in d and d[self.FIELD_ID] is not None:
            self.id = d[self.FIELD_ID]
        if self.FIELD_TIMESTAMP in d:
            self.timestamp = self._clean_timestamp(d[self.FIELD_TIMESTAMP])
        if self.FIELD_PATH in d:
            self.path = d[self.FIELD_PATH]
        if self.FIELD_FILENAME in d:
            self.filename = d[self.FIELD_FILENAME]
        if self.FIELD_DESCRIPTION in d:
            self.description = d[self.FIELD_DESCRIPTION]
        if self.FIELD_TASK in d:
            self.task = d[self.FIELD_TASK]

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
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if value != self._timestamp:
            self._on_attr_changing(self.FIELD_TIMESTAMP,
                                   self._timestamp)
            self._timestamp = value
            self._on_attr_changed(self.FIELD_TIMESTAMP, self.OP_SET,
                                  self._timestamp)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value != self._path:
            self._on_attr_changing(self.FIELD_PATH,
                                   self._path)
            self._path = value
            self._on_attr_changed(self.FIELD_PATH, self.OP_SET,
                                  self._path)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if value != self._filename:
            self._on_attr_changing(self.FIELD_FILENAME,
                                   self._filename)
            self._filename = value
            self._on_attr_changed(self.FIELD_FILENAME, self.OP_SET,
                                  self._filename)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._on_attr_changing(self.FIELD_DESCRIPTION,
                                   self._description)
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION, self.OP_SET,
                                  self._description)

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
            self._on_attr_changing(self.FIELD_TASK,
                                   self._task)
            if self._task is not None:
                self._task.attachments.discard(self)
            self._task = value
            if self._task is not None:
                self._task.attachments.add(self)
            self._on_attr_changed(self.FIELD_TASK, self.OP_SET, self._task)

    @staticmethod
    def from_dict(d):
        attachment_id = d.get(Attachment.FIELD_ID, None)
        timestamp = d.get(Attachment.FIELD_TIMESTAMP, None)
        path = d.get(Attachment.FIELD_PATH)
        filename = d.get(Attachment.FIELD_FILENAME, None)
        description = d.get(Attachment.FIELD_DESCRIPTION, None)
        task = d.get(Attachment.FIELD_TASK)

        attachment = Attachment(path, description, timestamp, filename)
        if attachment_id is not None:
            attachment.id = attachment_id
        attachment.task = task
        return attachment

    def clear_relationships(self):
        self.task = None
