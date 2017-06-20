
from dateutil.parser import parse as dparse

from conversions import str_from_datetime
from changeable import Changeable


class TaskBase(object):
    depth = 0

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        self.summary = summary
        self.description = description
        self.is_done = not not is_done
        self.is_deleted = not not is_deleted
        self.deadline = self._clean_deadline(deadline)
        self.expected_duration_minutes = expected_duration_minutes
        self.expected_cost = expected_cost

    @staticmethod
    def _clean_deadline(deadline):
        if isinstance(deadline, basestring):
            return dparse(deadline)
        return deadline

    def to_dict(self):
        return {
            'id': self.id,
            'summary': self.summary,
            'description': self.description,
            'is_done': self.is_done,
            'is_deleted': self.is_deleted,
            'order_num': self.order_num,
            'deadline': str_from_datetime(self.deadline),
            'parent_id': self.parent_id,
            'expected_duration_minutes':
                self.expected_duration_minutes,
            'expected_cost': self.get_expected_cost_for_export(),
            'tag_ids': [tag.id for tag in self.tags],
            'user_ids': [user.id for user in self.users]
        }

    def update_from_dict(self, d):
        if 'id' in d:
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
        if 'parent_id' in d:
            self.parent_id = d['parent_id']

    def get_expected_cost_for_export(self):
        if self.expected_cost is None:
            return None
        return '{:.2f}'.format(self.expected_cost)


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
    _parent_id = None
    _parent = None

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False, deadline=None,
                 expected_duration_minutes=None, expected_cost=None):
        super(Task, self).__init__(
            summary, description, is_done, is_deleted, deadline,
            expected_duration_minutes, expected_cost)

        self.dependees = list()
        self.dependants = list()
        self.prioritize_before = list()
        self.prioritize_after = list()
        self.tags = list()
        self.users = list()
        self.children = list()

        self.id = None
        self.parent = None
        self.parent_id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._on_attr_changed()

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = value
        self._on_attr_changed()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._on_attr_changed()

    @property
    def is_done(self):
        return self._is_done

    @is_done.setter
    def is_done(self, value):
        self._is_done = value
        self._on_attr_changed()

    @property
    def is_deleted(self):
        return self._is_deleted

    @is_deleted.setter
    def is_deleted(self, value):
        self._is_deleted = value
        self._on_attr_changed()

    @property
    def order_num(self):
        return self._order_num

    @order_num.setter
    def order_num(self, value):
        self._order_num = value
        self._on_attr_changed()

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        self._deadline = value
        self._on_attr_changed()

    @property
    def expected_duration_minutes(self):
        return self._expected_duration_minutes

    @expected_duration_minutes.setter
    def expected_duration_minutes(self, value):
        self._expected_duration_minutes = value
        self._on_attr_changed()

    @property
    def expected_cost(self):
        return self._expected_cost

    @expected_cost.setter
    def expected_cost(self, value):
        self._expected_cost = value
        self._on_attr_changed()

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._parent_id = value
        self._on_attr_changed()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self._on_attr_changed()

    @staticmethod
    def from_dict(d):
        task_id = d.get('id', None)
        summary = d.get('summary')
        description = d.get('description', '')
        is_done = d.get('is_done', False)
        is_deleted = d.get('is_deleted', False)
        order_num = d.get('order_num', 0)
        deadline = d.get('deadline', None)
        parent_id = d.get('parent_id', None)
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
        task.parent_id = parent_id
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


def generate_task_class(pl, tags_tasks_table, users_tasks_table,
                        task_dependencies_table, task_prioritize_table):
    db = pl.db

    class DbTask(db.Model, TaskBase):

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
        tags = db.relationship('DbTag', secondary=tags_tasks_table,
                               backref=db.backref('tasks', lazy='dynamic'))
        users = db.relationship('DbUser', secondary=users_tasks_table,
                                backref=db.backref('tasks', lazy='dynamic'))

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
        # self has lower priority that self.prioritize_before's
        # self is before self.prioritize_after's
        # self has higher priority that self.prioritize_after's
        prioritize_before = db.relationship(
            'DbTask', secondary=task_prioritize_table,
            primaryjoin=task_prioritize_table.c.prioritize_after_id == id,
            secondaryjoin=task_prioritize_table.c.prioritize_before_id == id,
            backref='prioritize_after')

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None,
                     expected_duration_minutes=None, expected_cost=None):
            db.Model.__init__(self)
            TaskBase.__init__(
                self, summary=summary, description=description,
                is_done=is_done, is_deleted=is_deleted, deadline=deadline,
                expected_duration_minutes=expected_duration_minutes,
                expected_cost=expected_cost)

        @staticmethod
        def from_dict(d):
            task_id = d.get('id', None)
            summary = d.get('summary')
            description = d.get('description', '')
            is_done = d.get('is_done', False)
            is_deleted = d.get('is_deleted', False)
            order_num = d.get('order_num', 0)
            deadline = d.get('deadline', None)
            parent_id = d.get('parent_id', None)
            expected_duration_minutes = d.get('expected_duration_minutes',
                                              None)
            expected_cost = d.get('expected_cost', None)
            # 'tag_ids': [tag.id for tag in self.tags],
            # 'user_ids': [user.id for user in self.users]

            task = DbTask(summary=summary, description=description,
                          is_done=is_done, is_deleted=is_deleted,
                          deadline=deadline,
                          expected_duration_minutes=expected_duration_minutes,
                          expected_cost=expected_cost)
            if task_id is not None:
                task.id = task_id
            task.order_num = order_num
            task.parent_id = parent_id
            return task

    return DbTask
