import logging_util
from models.task_base import TaskBase


class GenericTask(TaskBase):
    id = None
    summary = None
    description = None
    is_done = None
    is_deleted = None
    deadline = None
    expected_duration_minutes = None
    expected_cost = None
    order_num = None
    parent = None
    children = None
    dependees = None
    dependants = None
    prioritize_before = None
    prioritize_after = None
    tags = None
    users = None
    notes = None
    attachments = None
    is_public = None

    _logger = logging_util.get_logger_by_name(__name__, 'Task')

    def __init__(self, summary=None, description=None, is_done=None,
                 is_deleted=None, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=None, id=None, parent=None, children=None,
                 dependees=None, dependants=None, prioritize_before=None,
                 prioritize_after=None, tags=None, users=None, notes=None,
                 attachments=None):
        super(GenericTask, self).__init__(
            summary=summary, description=description, is_done=is_done,
            is_deleted=is_deleted, deadline=deadline,
            expected_duration_minutes=expected_duration_minutes,
            expected_cost=expected_cost, is_public=is_public)
        self.id = id
        self.parent = parent

        self.children = []
        self.dependees = []
        self.dependants = []
        self.prioritize_before = []
        self.prioritize_after = []
        self.tags = []
        self.users = []
        self.notes = []
        self.attachments = []

        if children:
            self.children.extend(children)
        if dependees:
            self.dependees.extend(dependees)
        if dependants:
            self.dependants.extend(dependants)
        if prioritize_before:
            self.prioritize_before.extend(prioritize_before)
        if prioritize_after:
            self.prioritize_after.extend(prioritize_after)
        if tags:
            self.tags.extend(tags)
        if users:
            self.users.extend(users)
        if notes:
            self.notes.extend(notes)
        if attachments:
            self.attachments.extend(attachments)


class Item:
    __id = 0

    def __init__(self):
        self.id = Item.__id
        Item.__id += 1
