import logging_util
from models.task_base import TaskBase
from persistence.in_memory.models.changeable import Changeable


class IMTask(Changeable, TaskBase):
    _logger = logging_util.get_logger_by_name(__name__, 'IMTask')

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
    _date_created = None
    _date_last_updated = None

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None,
                 is_public=False,
                 date_created=None,
                 date_last_updated=None):
        super(IMTask, self).__init__(
            summary, description, is_done, is_deleted, deadline,
            expected_duration_minutes, expected_cost, is_public,
            date_created,
            date_last_updated)
        self._logger.debug('Task.__init__ %s', self)


    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value != self._id:
            self._logger.debug('%s: %s -> %s', self, self.id, value)
            self._on_attr_changing(self.FIELD_ID, self._id)
            self._id = value
            self._on_attr_changed(self.FIELD_ID, self.OP_SET, self._id)

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if value != self._summary:
            self._logger.debug('%s: %s -> %s',
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
            self._logger.debug('%s: %s -> %s', self, self.description, value)
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
            self._logger.debug('%s: %s -> %s', self, self.is_done, value)
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
            self._logger.debug('%s: %s -> %s', self, self.is_deleted, value)
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
            self._logger.debug('%s: %s -> %s', self, self.order_num, value)
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
            self._logger.debug('%s: %s -> %s', self, self.deadline, value)
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
            self._logger.debug('%s: %s -> %s', self,
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
            self._logger.debug('%s: %s -> %s', self, self.expected_cost,
                               value)
            self._on_attr_changing(self.FIELD_EXPECTED_COST,
                                   self._expected_cost)
            self._expected_cost = value
            self._on_attr_changed(self.FIELD_EXPECTED_COST, self.OP_SET,
                                  self._expected_cost)



    @property
    def is_public(self):
        return self._is_public

    @is_public.setter
    def is_public(self, value):
        if value != self._is_public:
            self._logger.debug('%s: %s -> %s', self, self.is_public, value)
            self._on_attr_changing(self.FIELD_IS_PUBLIC,
                                   self._is_public)
            self._is_public = value
            self._on_attr_changed(self.FIELD_IS_PUBLIC, self.OP_SET,
                                  self._is_public)

    @property
    def date_created(self):
        return self._date_created

    @date_created.setter
    def date_created(self, value):
        if value != self._date_created:
            self._logger.debug('%s: %s -> %s', self, self.date_created, value)
            self._on_attr_changing(self.FIELD_DATE_CREATED,
                                   self._date_created)
            self._date_created = value
            self._on_attr_changed(self.FIELD_DATE_CREATED, self.OP_SET,
                                  self._date_created)

    @property
    def date_last_updated(self):
        return self._date_last_updated

    @date_last_updated.setter
    def date_last_updated(self, value):
        if value != self._date_last_updated:
            self._logger.debug(
                '%s: %s -> %s', self, self.date_last_updated, value)
            self._on_attr_changing(self.FIELD_DATE_LAST_UPDATED,
                                   self._date_last_updated)
            self._date_last_updated = value
            self._on_attr_changed(self.FIELD_DATE_LAST_UPDATED, self.OP_SET,
                                  self._date_last_updated)




