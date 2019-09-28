
import logging_util
from models.note_base import NoteBase
from persistence.in_memory.models.changeable import Changeable


class Note(Changeable, NoteBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Note')

    _id = None
    _content = ''
    _timestamp = None

    _task = None

    def __init__(self, content, timestamp=None, lazy=None):
        super(Note, self).__init__(content, timestamp)
        self._logger.debug('Note.__init__ %s', self)

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

    def _populate_task(self):
        if self._task_lazy:
            self._logger.debug('populating task from lazy %s', self)
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
                self._task.notes.discard(self)
            self._task = value
            if self._task is not None:
                self._task.notes.add(self)
            self._on_attr_changed(self.FIELD_TASK, self.OP_SET, self._task)

    def clear_relationships(self):
        self.task = None
