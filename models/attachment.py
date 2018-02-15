
import logging_util
from changeable import Changeable
from models.attachment_base import AttachmentBase


class Attachment(Changeable, AttachmentBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Attachment')

    _id = None
    _timestamp = None
    _path = None
    _filename = None
    _description = ''

    _task = None

    def __init__(self, path, description=None, timestamp=None, filename=None,
                 lazy=None):
        super(Attachment, self).__init__(path, description, timestamp,
                                         filename)
        self._logger.debug(u'Attachment.__init__ %s', self)

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
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value != self._path:
            self._on_attr_changing(self.FIELD_PATH, self._path)
            self._path = value
            self._on_attr_changed(self.FIELD_PATH, self.OP_SET, self._path)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if value != self._filename:
            self._on_attr_changing(self.FIELD_FILENAME, self._filename)
            self._filename = value
            self._on_attr_changed(self.FIELD_FILENAME, self.OP_SET,
                                  self._filename)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._on_attr_changing(self.FIELD_DESCRIPTION, self._description)
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION, self.OP_SET,
                                  self._description)

    @property
    def task_id(self):
        if self.task:
            return self.task.id
        return None

    def _populate_task(self):
        if self._task_lazy:
            self._logger.debug(u'populating task from lazy %s', self)
            value = self._task_lazy()
            self._task_lazy = None
            self.task = value

    @property
    def task(self):
        self._populate_task()
        return self._task

    @task.setter
    def task(self, value):
        self._populate_task()
        if value != self._task:
            self._on_attr_changing(self.FIELD_TASK, self._task)
            if self._task is not None:
                self._task.attachments.discard(self)
            self._task = value
            if self._task is not None:
                self._task.attachments.add(self)
            self._on_attr_changed(self.FIELD_TASK, self.OP_SET, self._task)

    def clear_relationships(self):
        self.task = None
