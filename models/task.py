
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
                'tag_ids': [ttl.tag_id for ttl in self.tags]
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

        @staticmethod
        def load(root_task_id=None, max_depth=0, include_done=False,
                 include_deleted=False, exclude_undeadlined=False):

            query = Task.query

            if not include_done:
                query = query.filter_by(is_done=False)

            if not include_deleted:
                query = query.filter_by(is_deleted=False)

            if exclude_undeadlined:
                query = query.filter(Task.deadline.isnot(None))

            if root_task_id is None:
                query = query.filter(Task.parent_id.is_(None))
            else:
                query = query.filter_by(id=root_task_id)

            query = query.order_by(Task.id.asc())
            query = query.order_by(Task.order_num.desc())

            tasks = query.all()

            depth = 0
            for task in tasks:
                task.depth = depth

            if max_depth is None or max_depth > 0:

                buckets = [tasks]
                next_ids = map(lambda t: t.id, tasks)
                already_ids = set()
                already_ids.update(next_ids)

                while ((max_depth is None or depth < max_depth) and
                               len(next_ids) > 0):

                    depth += 1

                    query = Task.query
                    query = query.filter(Task.parent_id.in_(next_ids),
                                         Task.id.notin_(already_ids))
                    if not include_done:
                        query = query.filter_by(is_done=False)
                    if not include_deleted:
                        query = query.filter_by(is_deleted=False)
                    if exclude_undeadlined:
                        query = query.filter(Task.deadline.isnot(None))

                    children = query.all()

                    for child in children:
                        child.depth = depth

                    child_ids = set(map(lambda t: t.id, children))
                    next_ids = child_ids - already_ids
                    already_ids.update(child_ids)
                    buckets.append(children)
                tasks = list(
                    set([task for bucket in buckets for task in bucket]))

            return tasks

        @staticmethod
        def load_no_hierarchy(include_done=False, include_deleted=False,
                              exclude_undeadlined=False, tags=None,
                              query_post_op=None):

            query = Task.query

            if not include_done:
                query = query.filter_by(is_done=False)

            if not include_deleted:
                query = query.filter_by(is_deleted=False)

            if exclude_undeadlined:
                query = query.filter(Task.deadline.isnot(None))

            if tags is not None:
                if not hasattr(tags, '__iter__'):
                    tags = [tags]
                if len(tags) < 1:
                    tags = None

            if tags is not None:
                def get_tag_id(tag):
                    if tag is None:
                        return None
                    if tag == str(tag):
                        return Tag.query.filter_by(value=tag).all()[0].id
                    if isinstance(tag, Tag):
                        return tag.id
                    raise TypeError(
                        "Unknown type ('{}') of argument 'tag'".format(
                            type(tag)))

                tag_ids = map(get_tag_id, tags)
                query = query.join(TaskTagLink).filter(
                    TaskTagLink.tag_id.in_(tag_ids))

            if query_post_op:
                query = query_post_op(query)

            tasks = query.all()

            depth = 0
            for task in tasks:
                task.depth = depth

            return tasks

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
                if tul.user is user:
                    return True
            return False

    return Task
