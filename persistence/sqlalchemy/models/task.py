
from __future__ import absolute_import

import logging_util
from models.changeable import Changeable
from models.task_base import TaskBase


def generate_task_class(pl, tags_tasks_table, users_tasks_table,
                        task_dependencies_table, task_prioritize_table):
    db = pl.db

    class DbTask(Changeable, db.Model, TaskBase):
        _logger = logging_util.get_logger_by_name(__name__, 'DbTask')

        __tablename__ = 'task'

        id = db.Column(db.Integer, primary_key=True)
        summary = db.Column(db.String(100))
        description = db.Column(db.String(4000))
        is_done = db.Column(db.Boolean)
        is_deleted = db.Column(db.Boolean)
        order_num = db.Column(db.Integer, nullable=False, default=0)
        deadline = db.Column(db.DateTime)
        expected_duration_minutes = db.Column(db.Integer)
        expected_cost = db.Column(db.Numeric)
        is_public = db.Column(db.Boolean)
        tags = db.relationship('DbTag', secondary=tags_tasks_table,
                               back_populates="tasks")

        users = db.relationship('DbUser', secondary=users_tasks_table,
                                back_populates="tasks")

        parent_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                              nullable=True)
        parent = db.relationship('DbTask', remote_side=[id],
                                 backref=db.backref('children',
                                                    lazy='dynamic'))

        # self depends on self.dependees
        # self.dependants depend on self
        dependees = db.relationship(
            'DbTask', secondary=task_dependencies_table,
            primaryjoin=task_dependencies_table.c.dependant_id == id,
            secondaryjoin=task_dependencies_table.c.dependee_id == id,
            backref='dependants')

        # self is after self.prioritize_before's
        # self has lower priority than self.prioritize_before's
        # self is before self.prioritize_after's
        # self has higher priority than self.prioritize_after's
        prioritize_before = db.relationship(
            'DbTask', secondary=task_prioritize_table,
            primaryjoin=task_prioritize_table.c.prioritize_after_id == id,
            secondaryjoin=task_prioritize_table.c.prioritize_before_id == id,
            backref='prioritize_after')

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None,
                     expected_duration_minutes=None, expected_cost=None,
                     is_public=False, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            TaskBase.__init__(
                self, summary=summary, description=description,
                is_done=is_done, is_deleted=is_deleted, deadline=deadline,
                expected_duration_minutes=expected_duration_minutes,
                expected_cost=expected_cost, is_public=is_public)

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbTask, cls).from_dict(d=d, lazy=None)

        def make_change(self, field, operation, value):
            if field in (self.FIELD_ID, self.FIELD_SUMMARY,
                         self.FIELD_DESCRIPTION, self.FIELD_IS_DONE,
                         self.FIELD_IS_DELETED, self.FIELD_DEADLINE,
                         self.FIELD_EXPECTED_DURATION_MINUTES,
                         self.FIELD_EXPECTED_COST, self.FIELD_ORDER_NUM,
                         self.FIELD_PARENT, self.FIELD_IS_PUBLIC):
                if operation != Changeable.OP_SET:
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            elif field in (self.FIELD_CHILDREN, self.FIELD_DEPENDEES,
                           self.FIELD_DEPENDANTS, self.FIELD_PRIORITIZE_BEFORE,
                           self.FIELD_PRIORITIZE_AFTER, self.FIELD_TAGS,
                           self.FIELD_USERS, self.FIELD_NOTES,
                           self.FIELD_ATTACHMENTS):
                if operation not in (Changeable.OP_ADD, Changeable.OP_REMOVE):
                    raise ValueError(
                        'Invalid operation "{}" for field "{}"'.format(
                            operation, field))
            else:
                raise ValueError('Unknown field "{}"'.format(field))

            if field == self.FIELD_ID:
                self.id = value
            elif field == self.FIELD_SUMMARY:
                self.summary = value
            elif field == self.FIELD_DESCRIPTION:
                self.description = value
            elif field == self.FIELD_IS_DONE:
                self.is_done = value
            elif field == self.FIELD_IS_DELETED:
                self.is_deleted = value
            elif field == self.FIELD_DEADLINE:
                self.deadline = value
            elif field == self.FIELD_EXPECTED_DURATION_MINUTES:
                self.expected_duration_minutes = value
            elif field == self.FIELD_EXPECTED_COST:
                self.expected_cost = value
            elif field == self.FIELD_ORDER_NUM:
                self.order_num = value
            elif field == self.FIELD_PARENT:
                self.parent = value
            elif field == self.FIELD_IS_PUBLIC:
                self.is_public = value
            elif field == self.FIELD_CHILDREN:
                collection = self.children
            elif field == self.FIELD_DEPENDEES:
                collection = self.dependees
            elif field == self.FIELD_DEPENDANTS:
                collection = self.dependants
            elif field == self.FIELD_PRIORITIZE_BEFORE:
                collection = self.prioritize_before
            elif field == self.FIELD_PRIORITIZE_AFTER:
                collection = self.prioritize_after
            elif field == self.FIELD_TAGS:
                collection = self.tags
            elif field == self.FIELD_USERS:
                collection = self.users
            elif field == self.FIELD_NOTES:
                collection = self.notes
            elif field == self.FIELD_ATTACHMENTS:
                collection = self.attachments

            if operation == Changeable.OP_ADD:
                if value not in collection:
                    collection.append(value)
            elif operation == Changeable.OP_REMOVE:
                if value in collection:
                    collection.remove(value)

        def clear_relationships(self):
            self._logger.debug(u'%s', self)
            self.parent = None
            self.children = []
            self.tags = []
            self.users = []
            self.notes = []
            self.attachments = []
            self.dependees = []
            self.dependants = []
            self.prioritize_before = []
            self.prioritize_after = []

    return DbTask
