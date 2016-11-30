
from dateutil.parser import parse as dparse

from conversions import str_from_datetime


def generate_task_class(db, Tag, TaskTagLink):
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

        parent_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                              nullable=True)
        parent = db.relationship('Task', remote_side=[id],
                                 backref=db.backref('children',
                                                    lazy='dynamic'))

        depth = 0

        def __init__(self, summary, description=None, is_done=None,
                     is_deleted=None, deadline=None,
                     expected_duration_minutes=None, expected_cost=None):

            if description is None:
                description = ''
            if is_done is None:
                is_done = False
            if is_deleted is None:
                is_deleted = False

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
                'tag_ids': [ttl.tag_id for ttl in self.tags],
                'user_ids': [tul.user_id for tul in self.users]
            }

        def get_siblings(self, include_deleted=True, descending=False,
                         ascending=False):
            if self.parent_id is not None:
                return self.parent.get_children(include_deleted,
                                                descending, ascending)

            siblings = Task.query.filter(Task.parent_id == None)

            if not include_deleted:
                siblings = siblings.filter(Task.is_deleted == False)

            if descending:
                siblings = siblings.order_by(Task.order_num.desc())
            elif ascending:
                siblings = siblings.order_by(Task.order_num.asc())

            return siblings

        def get_children(self, include_deleted=True, descending=False,
                         ascending=False):
            children = self.children

            if not include_deleted:
                children = children.filter(Task.is_deleted == False)

            if descending:
                children = children.order_by(Task.order_num.desc())
            elif ascending:
                children = children.order_by(Task.order_num.asc())

            return children

        def get_all_descendants(self, include_deleted=True,
                                descending=False, ascending=False,
                                visited=None, result=None):
            if visited is None:
                visited = set()
            if result is None:
                result = []

            if self not in visited:
                visited.add(self)
                result.append(self)
                for child in self.get_children(include_deleted, descending,
                                               ascending):
                    child.get_all_descendants(include_deleted, descending,
                                              ascending, visited, result)

            return result

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
            for tul in self.users:
                if tul.user == user:
                    return True
            return False

    return Task
