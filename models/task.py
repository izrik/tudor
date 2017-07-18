
import collections
import logging

from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable, id2
from collections_util import assign
import logging_util


class TaskBase(object):
    depth = 0

    FIELD_ID = 'ID'
    FIELD_SUMMARY = 'SUMMARY'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_IS_DONE = 'IS_DONE'
    FIELD_IS_DELETED = 'IS_DELETED'
    FIELD_DEADLINE = 'DEADLINE'
    FIELD_EXPECTED_DURATION_MINUTES = 'EXPECTED_DURATION_MINUTES'
    FIELD_EXPECTED_COST = 'EXPECTED_COST'
    FIELD_ORDER_NUM = 'ORDER_NUM'
    FIELD_PARENT = 'PARENT'  # related: PARENT_ID
    FIELD_PARENT_ID = 'PARENT_ID'  # related: PARENT
    FIELD_CHILDREN = 'CHILDREN'
    FIELD_DEPENDEES = 'DEPENDEES'
    FIELD_DEPENDANTS = 'DEPENDANTS'
    FIELD_PRIORITIZE_BEFORE = 'PRIORITIZE_BEFORE'
    FIELD_PRIORITIZE_AFTER = 'PRIORITIZE_AFTER'
    FIELD_TAGS = 'TAGS'
    FIELD_USERS = 'USERS'
    FIELD_NOTES = 'NOTES'
    FIELD_ATTACHMENTS = 'ATTACHMENTS'

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        self._logger = logging_util.get_logger(__name__, self)
        self._logger.debug('TaskBase.__init__ {}'.format(self.id2))

        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_deadline(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = expected_cost
        self.order_num = 0

    @staticmethod
    def get_related_fields(field):
        if field == TaskBase.FIELD_PARENT:
            return (TaskBase.FIELD_PARENT_ID,)
        if field == TaskBase.FIELD_PARENT_ID:
            return (TaskBase.FIELD_PARENT,)
        return ()

    @staticmethod
    def get_autochange_fields():
        return (TaskBase.FIELD_ID, TaskBase.FIELD_PARENT_ID,
                TaskBase.FIELD_PARENT)

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, self.summary, self.id)

    @staticmethod
    def _clean_deadline(deadline):
        if isinstance(deadline, basestring):
            return dparse(deadline)
        return deadline

    def to_dict(self, fields=None):

        self._logger.debug('{}'.format(self.id2))

        d = {}
        if fields is None or self.FIELD_ID in fields:
            d['id'] = self.id
        if fields is None or self.FIELD_SUMMARY in fields:
            d['summary'] = self.summary
        if fields is None or self.FIELD_DESCRIPTION in fields:
            d['description'] = self.description
        if fields is None or self.FIELD_IS_DONE in fields:
            d['is_done'] = self.is_done
        if fields is None or self.FIELD_IS_DELETED in fields:
            d['is_deleted'] = self.is_deleted
        if fields is None or self.FIELD_DEADLINE in fields:
            d['deadline'] = str_from_datetime(self.deadline)
        if fields is None or self.FIELD_EXPECTED_DURATION_MINUTES in fields:
            d['expected_duration_minutes'] = self.expected_duration_minutes
        if fields is None or self.FIELD_EXPECTED_COST in fields:
            d['expected_cost'] = self.get_expected_cost_for_export()
        if fields is None or self.FIELD_ORDER_NUM in fields:
            d['order_num'] = self.order_num
        if fields is None or self.FIELD_PARENT in fields:
            d['parent'] = self.parent
        if fields is None or self.FIELD_PARENT_ID in fields:
            d['parent_id'] = self.parent_id

        if fields is None or self.FIELD_CHILDREN in fields:
            d['children'] = list(self.children)
        if fields is None or self.FIELD_DEPENDEES in fields:
            d['dependees'] = list(self.dependees)
        if fields is None or self.FIELD_DEPENDANTS in fields:
            d['dependants'] = list(self.dependants)
        if fields is None or self.FIELD_PRIORITIZE_BEFORE in fields:
            d['prioritize_before'] = list(self.prioritize_before)
        if fields is None or self.FIELD_PRIORITIZE_AFTER in fields:
            d['prioritize_after'] = list(self.prioritize_after)
        if fields is None or self.FIELD_TAGS in fields:
            d['tags'] = list(self.tags)
        if fields is None or self.FIELD_USERS in fields:
            d['users'] = list(self.users)
        if fields is None or self.FIELD_NOTES in fields:
            d['notes'] = list(self.notes)
        if fields is None or self.FIELD_ATTACHMENTS in fields:
            d['attachments'] = list(self.attachments)

        return d

    def update_from_dict(self, d):
        self._logger.debug('{}: {}'.format(id2(self), d))
        if 'id' in d and d['id'] is not None:
            self.id = d['id']
        if 'summary' in d:
            self.summary = d['summary']
        if 'description' in d:
            self.description = d['description']
        if 'is_done' in d:
            self.is_done = d['is_done']
        if 'is_deleted' in d:
            self.is_deleted = d['is_deleted']
        if 'order_num' in d:
            self.order_num = d['order_num']
        if 'deadline' in d:
            self.deadline = self._clean_deadline(d['deadline'])
        if 'expected_duration_minutes' in d:
            self.expected_duration_minutes = d['expected_duration_minutes']
        if 'expected_cost' in d:
            self.expected_cost = d['expected_cost']
        if 'parent' in d:
            self.parent = d['parent']
        if 'children' in d:
            assign(self.children, d['children'])
        if 'tags' in d:
            assign(self.tags, d['tags'])
        if 'users' in d:
            assign(self.users, d['users'])
        if 'dependees' in d:
            assign(self.dependees, d['dependees'])
        if 'dependants' in d:
            assign(self.dependants, d['dependants'])
        if 'prioritize_before' in d:
            assign(self.prioritize_before, d['prioritize_before'])
        if 'prioritize_after' in d:
            assign(self.prioritize_after, d['prioritize_after'])
        if 'notes' in d:
            assign(self.notes, d['notes'])
        if 'attachments' in d:
            assign(self.attachments, d['attachments'])

    def get_expected_cost_for_export(self):
        if self.expected_cost is None:
            return None
        return '{:.2f}'.format(self.expected_cost)

    @property
    def id2(self):
        return '[{}] {} ({})'.format(id(self), self.summary, self.id)


class Task(Changeable, TaskBase):

    _id = None
    _summary = None
    _description = None
    _is_done = None
    _is_deleted = None
    _order_num = None
    _deadline = None
    _expected_duration_minutes = None
    _expected_cost = None
    _parent = None

    _dbobj = None

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        super(Task, self).__init__(
            summary, description, is_done, is_deleted, deadline,
            expected_duration_minutes, expected_cost)

        self._logger.debug('Task.__init__ {}'.format(self.id2))

        self._dependees = InterlinkedDependees(self)
        self._dependants = InterlinkedDependants(self)
        self._prioritize_before = InterlinkedPrioritizeBefore(self)
        self._prioritize_after = InterlinkedPrioritizeAfter(self)
        self._tags = InterlinkedTags(self)
        self._users = InterlinkedUsers(self)
        self._children = InterlinkedChildren(self)
        self._notes = InterlinkedNotes(self)
        self._attachments = InterlinkedAttachments(self)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug('{}: {} -> {}'.format(self.id2, self.id, value))
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if value != self._summary:
            self._logger.debug('{}: {} -> {}'.format(self.id2, self.summary,
                                                     value))
            self._on_attr_changing(self.FIELD_SUMMARY, self._summary)
            self._summary = value
            self._on_attr_changed(self.FIELD_SUMMARY, self.OP_SET,
                                  self._summary)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value != self._description:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.description, value))
            self._on_attr_changing(self.FIELD_DESCRIPTION, self._description)
            self._description = value
            self._on_attr_changed(self.FIELD_DESCRIPTION, self.OP_SET,
                                  self._description)

    @property
    def is_done(self):
        return self._is_done

    @is_done.setter
    def is_done(self, value):
        if value != self._is_done:
            self._logger.debug('{}: {} -> {}'.format(self.id2, self.is_done,
                                                     value))
            self._on_attr_changing(self.FIELD_IS_DONE, self._is_done)
            self._is_done = value
            self._on_attr_changed(self.FIELD_IS_DONE, self.OP_SET,
                                  self._is_done)

    @property
    def is_deleted(self):
        return self._is_deleted

    @is_deleted.setter
    def is_deleted(self, value):
        if value != self._is_deleted:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.is_deleted, value))
            self._on_attr_changing(self.FIELD_IS_DELETED, self._is_deleted)
            self._is_deleted = value
            self._on_attr_changed(self.FIELD_IS_DELETED, self.OP_SET,
                                  self._is_deleted)

    @property
    def order_num(self):
        return self._order_num

    @order_num.setter
    def order_num(self, value):
        if value != self._order_num:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.order_num, value))
            self._on_attr_changing(self.FIELD_ORDER_NUM, self._order_num)
            self._order_num = value
            self._on_attr_changed(self.FIELD_ORDER_NUM, self.OP_SET,
                                  self._order_num)

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        if value != self._deadline:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.deadline, value))
            self._on_attr_changing(self.FIELD_DEADLINE, self._deadline)
            self._deadline = value
            self._on_attr_changed(self.FIELD_DEADLINE, self.OP_SET,
                                  self._deadline)

    @property
    def expected_duration_minutes(self):
        return self._expected_duration_minutes

    @expected_duration_minutes.setter
    def expected_duration_minutes(self, value):
        if value != self._expected_duration_minutes:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.expected_duration_minutes,
                                      value))
            self._on_attr_changing(self.FIELD_EXPECTED_DURATION_MINUTES, self._expected_duration_minutes)
            self._expected_duration_minutes = value
            self._on_attr_changed(self.FIELD_EXPECTED_DURATION_MINUTES,
                                  self.OP_SET, self._expected_duration_minutes)

    @property
    def expected_cost(self):
        return self._expected_cost

    @expected_cost.setter
    def expected_cost(self, value):
        if value != self._expected_cost:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.expected_cost, value))
            self._on_attr_changing(self.FIELD_EXPECTED_COST, self._expected_cost)
            self._expected_cost = value
            self._on_attr_changed(self.FIELD_EXPECTED_COST, self.OP_SET,
                                  self._expected_cost)

    @property
    def parent_id(self):
        if self._parent:
            return self.parent.id
        return None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._logger.debug('{}'.format(self.id2))
        if value != self._parent:
            self._logger.debug(
                '{}: {} -> {}'.format(self.id2, self.parent, value))
            self._on_attr_changing(self.FIELD_PARENT, self._parent)
            if self._parent is not None:
                self._parent.children.discard(self)
            self._parent = value
            if self._parent is not None:
                self._parent.children.append(self)
            self._on_attr_changed(self.FIELD_PARENT, self.OP_SET, self._parent)

    @property
    def children(self):
        return self._children

    @property
    def tags(self):
        return self._tags

    @property
    def users(self):
        return self._users

    @property
    def dependees(self):
        return self._dependees

    @property
    def dependants(self):
        return self._dependants

    @property
    def prioritize_before(self):
        return self._prioritize_before

    @property
    def prioritize_after(self):
        return self._prioritize_after

    @property
    def notes(self):
        return self._notes

    @property
    def attachments(self):
        return self._attachments

    @staticmethod
    def from_dict(d):
        task_id = d.get('id', None)
        summary = d.get('summary')
        description = d.get('description', '')
        is_done = d.get('is_done', False)
        is_deleted = d.get('is_deleted', False)
        order_num = d.get('order_num', 0)
        deadline = d.get('deadline', None)
        expected_duration_minutes = d.get('expected_duration_minutes',
                                          None)
        expected_cost = d.get('expected_cost', None)
        # 'tag_ids': [tag.id for tag in self.tags],
        # 'user_ids': [user.id for user in self.users]

        task = Task(summary=summary, description=description,
                    is_done=is_done, is_deleted=is_deleted,
                    deadline=deadline,
                    expected_duration_minutes=expected_duration_minutes,
                    expected_cost=expected_cost)
        if task_id is not None:
            task.id = task_id
        task.order_num = order_num
        if 'parent' in d:
            task.parent = d['parent']
        elif 'parent_id' in d:
            task.parent_id = d['parent_id']
        if 'children' in d:
            assign(task.children, d['children'])
        if 'tags' in d:
            assign(task.tags, d['tags'])
        if 'users' in d:
            assign(task.users, d['users'])
        if 'dependees' in d:
            assign(task.dependees, d['dependees'])
        if 'dependants' in d:
            assign(task.dependants, d['dependants'])
        if 'prioritize_before' in d:
            assign(task.prioritize_before, d['prioritize_before'])
        if 'prioritize_after' in d:
            assign(task.prioritize_after, d['prioritize_after'])
        if 'notes' in d:
            assign(task.notes, d['notes'])
        if 'attachments' in d:
            assign(task.attachments, d['attachments'])
        return task

    def get_css_class(self):
        if self.is_deleted and self.is_done:
            return 'done-deleted'
        if self.is_deleted:
            return 'not-done-deleted'
        if self.is_done:
            return 'done-not-deleted'
        return ''

    def get_css_class_attr(self):
        cls = self.get_css_class()
        if cls:
            return ' class="{}" '.format(cls)
        return ''

    def get_tag_values(self):
        for tag in self.tags:
            yield tag.value

    def get_expected_duration_for_viewing(self):
        if self.expected_duration_minutes is None:
            return ''
        if self.expected_duration_minutes == 1:
            return '1 minute'
        return '{} minutes'.format(self.expected_duration_minutes)

    def get_expected_cost_for_viewing(self):
        if self.expected_cost is None:
            return ''
        return '{:.2f}'.format(self.expected_cost)

    def is_user_authorized(self, user):
        return user in self.users

    def contains_dependency_cycle(self, visited=None):
        if visited is None:
            visited = set()
        if self in visited:
            return True
        visited = set(visited)
        visited.add(self)
        for dependee in self.dependees:
            if dependee.contains_dependency_cycle(visited):
                return True

        return False

    def contains_priority_cycle(self, visited=None):
        if visited is None:
            visited = set()
        if self in visited:
            return True
        visited = set(visited)
        visited.add(self)
        for before in self.prioritize_before:
            if before.contains_priority_cycle(visited):
                return True
        return False

    def clear_relationships(self):
        self.parent = None
        self.children.clear()
        self.tags.clear()
        self.users.clear()
        self.notes.clear()
        self.attachments.clear()
        self.dependees.clear()
        self.dependants.clear()
        self.prioritize_before.clear()
        self.prioritize_after.clear()


class InterlinkedChildren(collections.MutableSet):
    def __init__(self, container):
        self._logger = logging_util.get_logger(__name__, self)
        if container is None:
            raise ValueError('container cannot be None')

        self.container = container
        self.set = set()

    def __repr__(self):
        cls = type(self).__name__
        return '{}({})'.format(cls, self.set)

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, value):
        return self.set.__contains__(value)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item not in self.set:
            self.container._on_attr_changing(Task.FIELD_CHILDREN, None)
            self.set.add(item)
            item.parent = self.container
            self.container._on_attr_changed(Task.FIELD_CHILDREN, Task.OP_ADD,
                                            item)

    def append(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        self.add(item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item in self.set:
            self.container._on_attr_changing(Task.FIELD_CHILDREN, None)
            self.set.discard(item)
            item.parent = None
            self.container._on_attr_changed(Task.FIELD_CHILDREN,
                                            Task.OP_REMOVE, item)

    def __str__(self):
        return str(self.set)


class InterlinkedTags(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, tag):
        return self.set.__contains__(tag)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, tag):
        self._logger.debug('{}: {}'.format(self.c.id2, tag.id2))
        if tag not in self.set:
            self.container._on_attr_changing(Task.FIELD_TAGS, None)
            self.set.add(tag)
            tag.tasks.add(self.container)
            self.container._on_attr_changed(Task.FIELD_TAGS, Task.OP_ADD, tag)

    def append(self, tag):
        self._logger.debug('{}: {}'.format(self.c.id2, tag.id2))
        self.add(tag)

    def discard(self, tag):
        self._logger.debug('{}: {}'.format(self.c.id2, tag.id2))
        if tag in self.set:
            self.container._on_attr_changing(Task.FIELD_TAGS, None)
            self.set.discard(tag)
            tag.tasks.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_TAGS, Task.OP_REMOVE,
                                            tag)


class InterlinkedUsers(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, user):
        return self.set.__contains__(user)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, user):
        self._logger.debug('{}: {}'.format(self.c.id2, user.id2))
        if user not in self.set:
            self.container._on_attr_changing(Task.FIELD_USERS, None)
            self.set.add(user)
            user.tasks.add(self.container)
            self.container._on_attr_changed(Task.FIELD_USERS, Task.OP_ADD,
                                            user)

    def append(self, user):
        self._logger.debug('{}: {}'.format(self.c.id2, user.id2))
        self.add(user)

    def discard(self, user):
        self._logger.debug('{}: {}'.format(self.c.id2, user.id2))
        if user in self.set:
            self.container._on_attr_changing(Task.FIELD_USERS, None)
            self.set.discard(user)
            user.tasks.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_USERS, Task.OP_REMOVE,
                                            user)


class InterlinkedDependees(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, dependee):
        return self.set.__contains__(dependee)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, dependee):
        self._logger.debug('{}: {}'.format(self.c.id2, dependee.id2))
        if dependee not in self.set:
            self.container._on_attr_changing(Task.FIELD_DEPENDEES, None)
            self.set.add(dependee)
            dependee.dependants.add(self.container)
            self.container._on_attr_changed(Task.FIELD_DEPENDEES, Task.OP_ADD,
                                            dependee)

    def append(self, dependee):
        self._logger.debug('{}: {}'.format(self.c.id2, dependee.id2))
        self.add(dependee)

    def discard(self, dependee):
        self._logger.debug('{}: {}'.format(self.c.id2, dependee.id2))
        if dependee in self.set:
            self.container._on_attr_changing(Task.FIELD_DEPENDEES, None)
            self.set.discard(dependee)
            dependee.dependants.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_DEPENDEES,
                                            Task.OP_REMOVE, dependee)


class InterlinkedDependants(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, dependant):
        return self.set.__contains__(dependant)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, dependant):
        self._logger.debug('{}: {}'.format(self.c.id2, dependant.id2))
        if dependant not in self.set:
            self.container._on_attr_changing(Task.FIELD_DEPENDANTS, None)
            self.set.add(dependant)
            dependant.dependees.add(self.container)
            self.container._on_attr_changed(Task.FIELD_DEPENDANTS, Task.OP_ADD,
                                            dependant)

    def append(self, dependant):
        self._logger.debug('{}: {}'.format(self.c.id2, dependant.id2))
        self.add(dependant)

    def discard(self, dependant):
        self._logger.debug('{}: {}'.format(self.c.id2, dependant.id2))
        if dependant in self.set:
            self.container._on_attr_changing(Task.FIELD_DEPENDANTS, None)
            self.set.discard(dependant)
            dependant.dependees.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_DEPENDANTS,
                                            Task.OP_REMOVE, dependant)


class InterlinkedPrioritizeBefore(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, before):
        return self.set.__contains__(before)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, before):
        self._logger.debug('{}: {}'.format(self.c.id2, before.id2))
        if before not in self.set:
            self.container._on_attr_changing(Task.FIELD_PRIORITIZE_BEFORE,
                                             None)
            self.set.add(before)
            before.prioritize_after.add(self.container)
            self.container._on_attr_changed(Task.FIELD_PRIORITIZE_BEFORE,
                                            Task.OP_ADD, before)

    def append(self, before):
        self._logger.debug('{}: {}'.format(self.c.id2, before.id2))
        self.add(before)

    def discard(self, before):
        self._logger.debug('{}: {}'.format(self.c.id2, before.id2))
        if before in self.set:
            self.container._on_attr_changing(Task.FIELD_PRIORITIZE_BEFORE,
                                             None)
            self.set.discard(before)
            before.prioritize_after.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_PRIORITIZE_BEFORE,
                                            Task.OP_REMOVE, before)


class InterlinkedPrioritizeAfter(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, after):
        return self.set.__contains__(after)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, after):
        self._logger.debug('{}: {}'.format(self.c.id2, after.id2))
        if after not in self.set:
            self.container._on_attr_changing(Task.FIELD_PRIORITIZE_AFTER, None)
            self.set.add(after)
            after.prioritize_before.add(self.container)
            self.container._on_attr_changed(Task.FIELD_PRIORITIZE_AFTER,
                                            Task.OP_ADD, after)

    def append(self, after):
        self._logger.debug('{}: {}'.format(self.c.id2, after.id2))
        self.add(after)

    def discard(self, after):
        self._logger.debug('{}: {}'.format(self.c.id2, after.id2))
        if after in self.set:
            self.container._on_attr_changing(Task.FIELD_PRIORITIZE_AFTER, None)
            self.set.discard(after)
            after.prioritize_before.discard(self.container)
            self.container._on_attr_changed(Task.FIELD_PRIORITIZE_AFTER,
                                            Task.OP_REMOVE, after)


class InterlinkedNotes(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    def __repr__(self):
        cls = type(self).__name__
        return '{}({})'.format(cls, self.set)

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, item):
        return self.set.__contains__(item)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item not in self.set:
            self.container._on_attr_changing(Task.FIELD_NOTES, None)
            self.set.add(item)
            item.task = self.container
            self.container._on_attr_changed(Task.FIELD_NOTES, Task.OP_ADD,
                                            item)

    def append(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        self.add(item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item in self.set:
            self.container._on_attr_changing(Task.FIELD_NOTES, None)
            self.set.discard(item)
            item.task = None
            self.container._on_attr_changed(Task.FIELD_NOTES, Task.OP_REMOVE,
                                            item)

    def __str__(self):
        return str(self.set)


class InterlinkedAttachments(collections.MutableSet):

    def __init__(self, container):
        if container is None:
            raise ValueError('container cannot be None')

        self._logger = logging_util.get_logger(__name__, self)

        self.container = container
        self.set = set()

    def __repr__(self):
        cls = type(self).__name__
        return '{}({})'.format(cls, self.set)

    @property
    def c(self):
        return self.container

    def __len__(self):
        return len(self.set)

    def __contains__(self, item):
        return self.set.__contains__(item)

    def __iter__(self):
        return self.set.__iter__()

    def add(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item not in self.set:
            self.container._on_attr_changing(Task.FIELD_ATTACHMENTS, None)
            self.set.add(item)
            item.task = self.container
            self.container._on_attr_changed(Task.FIELD_ATTACHMENTS,
                                            Task.OP_ADD, item)

    def append(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        self.add(item)

    def discard(self, item):
        self._logger.debug('{}: {}'.format(self.c.id2, item.id2))
        if item in self.set:
            self.container._on_attr_changing(Task.FIELD_ATTACHMENTS, None)
            self.set.discard(item)
            item.task = None
            self.container._on_attr_changed(Task.FIELD_ATTACHMENTS,
                                            Task.OP_REMOVE, item)

    def __str__(self):
        return str(self.set)
