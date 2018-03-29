
from __future__ import absolute_import

import logging_util
from models.task_base import TaskBase
from persistence.in_memory.models.changeable import Changeable
from persistence.in_memory.models.interlinking import OneToManySet, \
    ManyToManySet


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

        self._logger.debug(u'Task.__init__ %s', self)

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
            self._logger.debug(u'%s: %s -> %s', self, self.id, value)
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if value != self._summary:
            self._logger.debug(u'%s: %s -> %s',
                               self, repr(self.summary), repr(value))
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
            self._logger.debug(u'%s: %s -> %s', self, self.description, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.is_done, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.is_deleted, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.order_num, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.deadline, value)
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
            self._logger.debug(u'%s: %s -> %s', self,
                               self.expected_duration_minutes, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.expected_cost,
                               value)
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
            self._logger.debug(u'populating parent from lazy %s', self)
            value = self._parent_lazy()
            self._parent_lazy = None
            self.parent = value

    @property
    def parent(self):
        self._populate_parent()
        return self._parent

    @parent.setter
    def parent(self, value):
        self._logger.debug(u'%s', self)
        self._populate_parent()
        if value != self._parent:
            self._logger.debug(u'%s: %s -> %s', self, self._parent, value)
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
            self._logger.debug(u'%s: %s -> %s', self, self.is_public, value)
            self._on_attr_changing(self.FIELD_IS_PUBLIC,
                                   self._is_public)
            self._is_public = value
            self._on_attr_changed(self.FIELD_IS_PUBLIC, self.OP_SET,
                                  self._is_public)

    def contains_dependency_cycle(self, visited=None):
        self._logger.debug(u'%s', self)
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
        self._logger.debug(u'%s', self)
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
        self._logger.debug(u'%s', self)
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
    __change_field__ = TaskBase.FIELD_CHILDREN
    __attr_counterpart__ = 'parent'
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedChildren')


class InterlinkedTags(ManyToManySet):
    __change_field__ = TaskBase.FIELD_TAGS
    __attr_counterpart__ = 'tasks'
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedTags')


class InterlinkedUsers(ManyToManySet):
    __change_field__ = TaskBase.FIELD_USERS
    __attr_counterpart__ = 'tasks'
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedUsers')


class InterlinkedDependees(ManyToManySet):
    __change_field__ = TaskBase.FIELD_DEPENDEES
    __attr_counterpart__ = 'dependants'
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedDependees')


class InterlinkedDependants(ManyToManySet):
    __change_field__ = TaskBase.FIELD_DEPENDANTS
    __attr_counterpart__ = 'dependees'
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InterlinkedDependants')


class InterlinkedPrioritizeBefore(ManyToManySet):
    __change_field__ = TaskBase.FIELD_PRIORITIZE_BEFORE
    __attr_counterpart__ = 'prioritize_after'
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InterlinkedPrioritizeBefore')


class InterlinkedPrioritizeAfter(ManyToManySet):
    __change_field__ = TaskBase.FIELD_PRIORITIZE_AFTER
    __attr_counterpart__ = 'prioritize_before'
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InterlinkedPrioritizeAfter')


class InterlinkedNotes(OneToManySet):
    __change_field__ = TaskBase.FIELD_NOTES
    __attr_counterpart__ = 'task'
    _logger = logging_util.get_logger_by_name(__name__, 'InterlinkedNotes')


class InterlinkedAttachments(OneToManySet):
    __change_field__ = TaskBase.FIELD_ATTACHMENTS
    __attr_counterpart__ = 'task'
    _logger = logging_util.get_logger_by_name(__name__,
                                              'InterlinkedAttachments')
