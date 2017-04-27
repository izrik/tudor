
from dateutil.parser import parse as dparse

from conversions import str_from_datetime


def generate_task_class(db, tags_tasks_table, users_tasks_table,
                        task_dependencies_table):
    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        summary = db.Column(db.String(100))
        description = db.Column(db.String(4000))
        is_done = db.Column(db.Boolean)
        is_deleted = db.Column(db.Boolean)
        order_num = db.Column(db.Integer, nullable=False, default=0)
        deadline = db.Column(db.DateTime)
        expected_duration_minutes = db.Column(db.Integer)
        expected_cost = db.Column(db.Numeric)
        tags = db.relationship('Tag', secondary=tags_tasks_table,
                               backref=db.backref('tasks', lazy='dynamic'))
        users = db.relationship('User', secondary=users_tasks_table,
                                backref=db.backref('tasks', lazy='dynamic'))

        parent_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                              nullable=True)
        parent = db.relationship('Task', remote_side=[id],
                                 backref=db.backref('children',
                                                    lazy='dynamic'))

        dependees = db.relationship(
            'Task', secondary=task_dependencies_table,
            primaryjoin=task_dependencies_table.c.depender_id==id,
            secondaryjoin=task_dependencies_table.c.dependee_id==id,
            backref='dependers')

        depth = 0

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None,
                     expected_duration_minutes=None, expected_cost=None):
            self.summary = summary
            self.description = description
            self.is_done = is_done
            self.is_deleted = is_deleted
            if isinstance(deadline, basestring):
                deadline = dparse(deadline)
            self.deadline = deadline
            self.expected_duration_minutes = expected_duration_minutes
            self.expected_cost = expected_cost

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

        def get_siblings(self, include_deleted=True, ordered=False):
            if self.parent_id is not None:
                return self.parent.get_children(include_deleted, ordered)

            siblings = Task.query.filter(Task.parent_id == None)

            if not include_deleted:
                siblings = siblings.filter(Task.is_deleted == False)

            if ordered:
                siblings = siblings.order_by(Task.order_num.desc())

            return siblings

        def get_children(self, include_deleted=True, ordered=False):
            children = self.children

            if not include_deleted:
                children = children.filter(Task.is_deleted == False)

            if ordered:
                children = children.order_by(Task.order_num.desc())

            return children

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

        def get_expected_cost_for_export(self):
            if self.expected_cost is None:
                return None
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


    return Task
