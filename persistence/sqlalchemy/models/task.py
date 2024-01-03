
import logging_util
from models.task_base import TaskBase


def generate_task_class(pl, tags_tasks_table, users_tasks_table,
                        task_dependencies_table, task_prioritize_table):
    db = pl.db

    class DbTask(db.Model, TaskBase):
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

        date_created = db.Column(db.DateTime)
        date_last_updated = db.Column(db.DateTime)

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None,
                     expected_duration_minutes=None, expected_cost=None,
                     is_public=False,
                     date_created=None,
                     date_last_updated=None,
                     lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            db.Model.__init__(self)
            TaskBase.__init__(
                self, summary=summary, description=description,
                is_done=is_done, is_deleted=is_deleted, deadline=deadline,
                expected_duration_minutes=expected_duration_minutes,
                expected_cost=expected_cost, is_public=is_public,
                date_created=date_created,
                date_last_updated=date_last_updated,
            )

        @classmethod
        def from_dict(cls, d, lazy=None):
            if lazy:
                raise ValueError('parameter \'lazy\' must be None or empty')
            return super(DbTask, cls).from_dict(d=d, lazy=None)

        def clear_relationships(self):
            self._logger.debug('%s', self)
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
