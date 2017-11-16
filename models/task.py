
from dateutil.parser import parse as dparse

from conversions import str_from_datetime, money_from_str
from changeable import Changeable
from collections_util import assign
import logging_util
from models.interlinking import OneToManySet, ManyToManySet


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
    FIELD_PARENT = 'PARENT'
    FIELD_CHILDREN = 'CHILDREN'
    FIELD_DEPENDEES = 'DEPENDEES'
    FIELD_DEPENDANTS = 'DEPENDANTS'
    FIELD_PRIORITIZE_BEFORE = 'PRIORITIZE_BEFORE'
    FIELD_PRIORITIZE_AFTER = 'PRIORITIZE_AFTER'
    FIELD_TAGS = 'TAGS'
    FIELD_USERS = 'USERS'
    FIELD_NOTES = 'NOTES'
    FIELD_ATTACHMENTS = 'ATTACHMENTS'
    FIELD_IS_PUBLIC = 'IS_PUBLIC'

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=False):
        self._logger.debug(u'TaskBase.__init__ {}'.format(self))

        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_deadline(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = money_from_str(expected_cost)
        self.order_num = 0
        self.is_public = not not is_public

    def __repr__(self):
        cls = type(self).__name__
        return '{}({}, id={})'.format(cls, repr(self.summary), self.id)

    def __str__(self):
        cls = type(self).__name__
        return '{}({}, task id={}, id=[{}])'.format(cls, repr(self.summary),
                                                    self.id, id(self))

    @staticmethod
    def _clean_deadline(deadline):
        if isinstance(deadline, basestring):
            return dparse(deadline)
        return deadline

    def to_dict(self, fields=None):

        self._logger.debug(u'{}'.format(self))

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
            d['expected_cost'] = self.expected_cost
        if fields is None or self.FIELD_ORDER_NUM in fields:
            d['order_num'] = self.order_num
        if fields is None or self.FIELD_PARENT in fields:
            d['parent'] = self.parent
        if fields is None or self.FIELD_IS_PUBLIC in fields:
            d['is_public'] = self.is_public

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

    @classmethod
    def from_dict(cls, d, lazy=None):
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
        is_public = d.get('is_public', False)

        task = cls(summary=summary, description=description,
                   is_done=is_done, is_deleted=is_deleted,
                   deadline=deadline,
                   expected_duration_minutes=expected_duration_minutes,
                   expected_cost=expected_cost, is_public=is_public, lazy=lazy)
        if task_id is not None:
            task.id = task_id
        task.order_num = order_num
        if not lazy:
            if 'parent' in d:
                task.parent = d['parent']
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

    def update_from_dict(self, d):
        self._logger.debug(u'{}: {}'.format(self, d))
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
        if 'is_public' in d:
            self.is_public = d['is_public']

    def get_expected_cost_for_export(self):
        value = money_from_str(self.expected_cost)
        if value is None:
            return None
        return '{:.2f}'.format(value)


class Task(Changeable, TaskBase):
    _logger = logging_util.get_logger_by_name(__name__, 'Task')

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
    _is_public = None

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=False, lazy=None):
        super(Task, self).__init__(
            summary, description, is_done, is_deleted, deadline,
            expected_duration_minutes, expected_cost, is_public)

        self._logger.debug(u'Task.__init__ {}'.format(self))

        if lazy is None:
            lazy = {}

        self._parent_lazy = lazy.get('parent')

        # self depends on self.dependees
        self._dependees = InterlinkedDependees(
            self, lazy=lazy.get('dependees'))
        # self.dependants depend on self
        self._dependants = InterlinkedDependants(
            self, lazy=lazy.get('dependants'))
        # self is after self.prioritize_before's
        # self has lower priority than self.prioritize_before's
        self._prioritize_before = InterlinkedPrioritizeBefore(
            self, lazy=lazy.get('prioritize_before'))
        # self is before self.prioritize_after's
        # self has higher priority than self.prioritize_after's
        self._prioritize_after = InterlinkedPrioritizeAfter(
            self, lazy=lazy.get('prioritize_after'))
        self._tags = InterlinkedTags(self, lazy=lazy.get('tags'))
        self._users = InterlinkedUsers(self, lazy=lazy.get('users'))
        self._children = InterlinkedChildren(self, lazy=lazy.get('children'))
        self._notes = InterlinkedNotes(self, lazy=lazy.get('notes'))
        self._attachments = InterlinkedAttachments(
            self, lazy=lazy.get('attachments'))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug(u'{}: {} -> {}'.format(self, self.id, value))
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if value != self._summary:
            self._logger.debug(u'{}: {} -> {}'.format(
                self, repr(self.summary), repr(value)))
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
                u'{}: {} -> {}'.format(self, self.description, value))
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
            self._logger.debug(u'{}: {} -> {}'.format(self, self.is_done,
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
                u'{}: {} -> {}'.format(self, self.is_deleted, value))
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
                u'{}: {} -> {}'.format(self, self.order_num, value))
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
                u'{}: {} -> {}'.format(self, self.deadline, value))
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
                u'{}: {} -> {}'.format(self, self.expected_duration_minutes,
                                       value))
            self._on_attr_changing(self.FIELD_EXPECTED_DURATION_MINUTES,
                                   self._expected_duration_minutes)
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
                u'{}: {} -> {}'.format(self, self.expected_cost, value))
            self._on_attr_changing(self.FIELD_EXPECTED_COST,
                                   self._expected_cost)
            self._expected_cost = value
            self._on_attr_changed(self.FIELD_EXPECTED_COST, self.OP_SET,
                                  self._expected_cost)

    @property
    def parent_id(self):
        if self.parent:
            return self.parent.id
        return None

    def _populate_parent(self):
        if self._parent_lazy:
            self._logger.debug(u'populating parent from lazy {}'.format(self))
            value = self._parent_lazy()
            self._parent_lazy = None
            self.parent = value

    @property
    def parent(self):
        self._populate_parent()
        return self._parent

    @parent.setter
    def parent(self, value):
        self._logger.debug(u'{}'.format(self))
        self._populate_parent()
        if value != self._parent:
            self._logger.debug(
                u'{}: {} -> {}'.format(self, self._parent, value))
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

    @property
    def is_public(self):
        return self._is_public

    @is_public.setter
    def is_public(self, value):
        if value != self._is_public:
            self._logger.debug(
                u'{}: {} -> {}'.format(self, self.is_public, value))
            self._on_attr_changing(self.FIELD_IS_PUBLIC,
                                   self._is_public)
            self._is_public = value
            self._on_attr_changed(self.FIELD_IS_PUBLIC, self.OP_SET,
                                  self._is_public)

    def get_css_class(self):
        if self.is_deleted and self.is_done:
            return u'done-deleted'
        if self.is_deleted:
            return u'not-done-deleted'
        if self.is_done:
            return u'done-not-deleted'
        return ''

    def get_css_class_attr(self):
        cls = self.get_css_class()
        if cls:
            return u' class="{}" '.format(cls)
        return u''

    def get_tag_values(self):
        for tag in self.tags:
            yield tag.value

    def get_expected_duration_for_viewing(self):
        if self.expected_duration_minutes is None:
            return ''
        if self.expected_duration_minutes == 1:
            return u'1 minute'
        return u'{} minutes'.format(self.expected_duration_minutes)

    def get_expected_cost_for_viewing(self):
        if self.expected_cost is None:
            return ''
        return u'{:.2f}'.format(self.expected_cost)

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


class InterlinkedChildren(OneToManySet):
    __change_field__ = Task.FIELD_CHILDREN
    __attr_counterpart__ = 'parent'


class InterlinkedTags(ManyToManySet):
    __change_field__ = Task.FIELD_TAGS
    __attr_counterpart__ = 'tasks'


class InterlinkedUsers(ManyToManySet):
    __change_field__ = Task.FIELD_USERS
    __attr_counterpart__ = 'tasks'


class InterlinkedDependees(ManyToManySet):
    __change_field__ = Task.FIELD_DEPENDEES
    __attr_counterpart__ = 'dependants'


class InterlinkedDependants(ManyToManySet):
    __change_field__ = Task.FIELD_DEPENDANTS
    __attr_counterpart__ = 'dependees'


class InterlinkedPrioritizeBefore(ManyToManySet):
    __change_field__ = Task.FIELD_PRIORITIZE_BEFORE
    __attr_counterpart__ = 'prioritize_after'


class InterlinkedPrioritizeAfter(ManyToManySet):
    __change_field__ = Task.FIELD_PRIORITIZE_AFTER
    __attr_counterpart__ = 'prioritize_before'


class InterlinkedNotes(OneToManySet):
    __change_field__ = Task.FIELD_NOTES
    __attr_counterpart__ = 'task'


class InterlinkedAttachments(OneToManySet):
    __change_field__ = Task.FIELD_ATTACHMENTS
    __attr_counterpart__ = 'task'
