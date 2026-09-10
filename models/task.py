from dateutil.parser import parse as dparse

from conversions import str_from_datetime, money_from_str
from models.object_types import ObjectTypes


class Task(object):
    FIELD_ID = 'ID'
    FIELD_SUMMARY = 'SUMMARY'
    FIELD_DESCRIPTION = 'DESCRIPTION'
    FIELD_IS_DONE = 'IS_DONE'
    FIELD_IS_DELETED = 'IS_DELETED'
    FIELD_DEADLINE = 'DEADLINE'
    FIELD_EXPECTED_DURATION_MINUTES = 'EXPECTED_DURATION_MINUTES'
    FIELD_EXPECTED_COST = 'EXPECTED_COST'
    FIELD_ORDER_NUM = 'ORDER_NUM'
    FIELD_PARENT_ID = 'PARENT_ID'
    FIELD_IS_PUBLIC = 'IS_PUBLIC'
    FIELD_DATE_CREATED = 'DATE_CREATED'
    FIELD_DATE_LAST_UPDATED = 'DATE_LAST_UPDATED'

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=False,
                 date_created=None,
                 date_last_updated=None,
                 order_num=0,
                 parent_id=None,
                 id=None):
        self.id = id
        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_datetime(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = money_from_str(expected_cost)
        self.order_num = order_num
        self.parent_id = parent_id
        self.is_public = not not is_public
        self.date_created = self._clean_datetime(date_created)
        self.date_last_updated = self._clean_datetime(date_last_updated)

    @property
    def object_type(self):
        return ObjectTypes.Task

    def __repr__(self):
        return 'Task({}, id={})'.format(repr(self.summary), self.id)

    @staticmethod
    def _clean_datetime(dt):
        if isinstance(dt, str):
            return dparse(dt)
        return dt

    def to_dict(self, fields=None):
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
        if fields is None or self.FIELD_PARENT_ID in fields:
            d['parent_id'] = self.parent_id
        if fields is None or self.FIELD_IS_PUBLIC in fields:
            d['is_public'] = self.is_public
        if fields is None or self.FIELD_DATE_CREATED in fields:
            d['date_created'] = str_from_datetime(self.date_created)
        if fields is None or self.FIELD_DATE_LAST_UPDATED in fields:
            d['date_last_updated'] = str_from_datetime(self.date_last_updated)
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            summary=d.get('summary'),
            description=d.get('description', ''),
            is_done=d.get('is_done', False),
            is_deleted=d.get('is_deleted', False),
            deadline=d.get('deadline'),
            expected_duration_minutes=d.get('expected_duration_minutes'),
            expected_cost=d.get('expected_cost'),
            order_num=d.get('order_num', 0),
            parent_id=d.get('parent_id'),
            is_public=d.get('is_public', False),
            date_created=d.get('date_created'),
            date_last_updated=d.get('date_last_updated'))
