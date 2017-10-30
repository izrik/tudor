
import logging_util


class InMemoryPersistenceLayer(object):
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InMemoryPersistenceLayer')

    def __init__(self):
        self._added_objects = set()
        self._deleted_objects = set()
        self._changed_objects = set()
        self._changed_objects_original_values = {}

        self._tasks = []
        self._tasks_by_id = {}

    def create_all(self):
        pass

    def get_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def add(self, obj):
        self._added_objects.add(obj)

    def commit(self):
        for t in list(self._added_objects):
            if t.id is None:
                t.id = self._get_next_task_id()
            else:
                if t.id in self._tasks_by_id:
                    raise Exception(
                        'There already exists a task with id {}'.format(t.id))
            self._tasks.append(t)
            self._tasks_by_id[t.id] = t
            self._added_objects.remove(t)
        self._added_objects.clear()

    def _get_next_task_id(self):
        if not self._tasks_by_id:
            return 1
        return max(self._tasks_by_id.iterkeys()) + 1
