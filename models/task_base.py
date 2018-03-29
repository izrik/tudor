
from dateutil.parser import parse as dparse

from conversions import str_from_datetime, money_from_str
from collections_util import assign
from models.object_types import ObjectTypes


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
        self._logger.debug(u'TaskBase.__init__ %s', self)

        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_deadline(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = money_from_str(expected_cost)
        self.order_num = 0
        self.is_public = not not is_public

    @property
    def object_type(self):
        return ObjectTypes.Task

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

        self._logger.debug(u'%s', self)

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
        self._logger.debug(u'%s: %s', self, d)
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

    def get_tag_values(self):
        for tag in self.tags:
            yield tag.value

    def is_user_authorized(self, user):
        self._logger.debug(u'%s', self)
        return user in self.users

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
