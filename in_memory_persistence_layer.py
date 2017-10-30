
import logging_util
from models.attachment import Attachment
from models.note import Note
from models.option import Option
from models.tag import Tag
from models.task import Task
from models.user import User


class InMemoryPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InMemoryPersistenceLayer')

    def __init__(self):
        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._values_by_object = {}

        self._tasks = []
        self._tasks_by_id = {}
        self._tags = []
        self._tags_by_id = {}
        self._tags_by_value = {}

    def create_all(self):
        pass

    def get_task(self, task_id):
        return self._tasks_by_id.get(task_id)

    def get_tag(self, tag_id):
        return self._tags_by_id.get(tag_id)

    def get_tag_by_value(self, value):
        return self._tags_by_value.get(value)

    def add(self, obj):
        d = obj.to_dict()
        self._values_by_object[obj] = d
        self._added_objects.add(obj)

    def commit(self):
        for domobj in list(self._added_objects):
            tt = self._get_object_type(domobj)
            if tt == Attachment:
                pass
            elif tt == Note:
                pass
            elif tt == Task:
                if domobj.id is None:
                    domobj.id = self._get_next_task_id()
                else:
                    if domobj.id in self._tasks_by_id:
                        raise Exception(
                            'There already exists a task with id {}'.format(domobj.id))
                self._tasks.append(domobj)
                self._tasks_by_id[domobj.id] = domobj
            elif tt == Tag:
                self._tags.append(domobj)
                self._tags_by_id[domobj.id] = domobj
                self._tags_by_value[domobj.value] = domobj
                pass
            elif tt == Option:
                pass
            elif tt == User:
                pass
            self._added_objects.remove(domobj)
        self._added_objects.clear()

        for domobj in self._tasks:
            self._values_by_object[domobj] = domobj.to_dict()

    def _get_next_task_id(self):
        if not self._tasks_by_id:
            return 1
        return max(self._tasks_by_id.iterkeys()) + 1

    def rollback(self):
        for t in self._added_objects:
            del self._values_by_object[t]
        self._added_objects.clear()
        for t, d in self._values_by_object.iteritems():
            t.update_from_dict(d)

    def _get_object_type(self, domobj):
        if isinstance(domobj, Attachment):
            return Attachment
        if isinstance(domobj, Note):
            return Note
        if isinstance(domobj, Option):
            return Option
        if isinstance(domobj, Tag):
            return Tag
        if isinstance(domobj, Task):
            return Task
        if isinstance(domobj, User):
            return User
        raise Exception(
            'Unknown object type: {}, {}'.format(domobj,
                                                 type(domobj).__name__))
