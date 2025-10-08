import logging_util
from dateutil.parser import parse as dparse

from conversions import str_from_datetime, money_from_str
from collections_util import assign
from models.object_types import ObjectTypes


class TaskBase(object):
    _logger = logging_util.get_logger_by_name(__name__, 'TaskBase')
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
    FIELD_DATE_CREATED = 'DATE_CREATED'
    FIELD_DATE_LAST_UPDATED = 'DATE_LAST_UPDATED'

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=False,
                 date_created=None,
                 date_last_updated=None):
        self._logger.debug('TaskBase.__init__ %s', self)

        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_datetime(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = money_from_str(expected_cost)
        self.order_num = 0
        self.is_public = not not is_public
        self.date_created = self._clean_datetime(date_created)
        self.date_last_updated = self._clean_datetime(date_last_updated)

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
    def _clean_datetime(dt):
        if isinstance(dt, str):
            return dparse(dt)
        return dt

    def to_dict(self, fields=None):

        self._logger.debug('%s', self)

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
        if fields is None or self.FIELD_IS_PUBLIC in fields:
            d['is_public'] = self.is_public
        if fields is None or self.FIELD_DATE_CREATED in fields:
            d['date_created'] = str_from_datetime(self.date_created)
        if fields is None or self.FIELD_DATE_LAST_UPDATED in fields:
            d['date_last_updated'] = str_from_datetime(self.date_last_updated)

        return d

    def to_flat_dict(self, fields=None):
        d = self.to_dict(fields=fields)
        if 'parent' in d and d['parent'] is not None:
            d['parent_id'] = d['parent'].id
            del d['parent']
        if 'children' in d:
            d['children_ids'] = [x.id for x in d['children']]
            del d['children']
        if 'dependees' in d:
            d['dependee_ids'] = [x.id for x in d['dependees']]
            del d['dependees']
        if 'dependants' in d:
            d['dependant_ids'] = [x.id for x in d['dependants']]
            del d['dependants']
        if 'expected_cost' in d and d['expected_cost'] is not None:
            d['expected_cost'] = str(d['expected_cost'])
        return d

    @classmethod
    def from_dict(cls, d):
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
        date_created = d.get('date_created', None)
        date_last_updated = d.get('date_last_updated', None)

        task = cls(summary=summary, description=description,
                    is_done=is_done, is_deleted=is_deleted,
                    deadline=deadline,
                    expected_duration_minutes=expected_duration_minutes,
                    expected_cost=expected_cost, is_public=is_public,
                    date_created=date_created,
                    date_last_updated=date_last_updated)
        if task_id is not None:
            task.id = task_id
        task.order_num = order_num
        if 'parent_id' in d:
            task.parent_id = d['parent_id']
        return task

    def update_from_dict(self, d):
        self._logger.debug('%s: %s', self, d)
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
            self.deadline = self._clean_datetime(d['deadline'])
        if 'expected_duration_minutes' in d:
            self.expected_duration_minutes = d['expected_duration_minutes']
        if 'expected_cost' in d:
            self.expected_cost = d['expected_cost']
        if 'is_public' in d:
            self.is_public = d['is_public']
        if 'date_created' in d:
            self.date_created = d['date_created']
        if 'date_last_updated' in d:
            self.date_last_updated = d['date_last_updated']

    def get_expected_cost_for_export(self):
        value = money_from_str(self.expected_cost)
        if value is None:
            return None
        return '{:.2f}'.format(value)



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
