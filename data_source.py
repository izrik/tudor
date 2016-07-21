#!/usr/bin/env python

from dateutil.parser import parse as dparse
from flask.ext.sqlalchemy import SQLAlchemy

from conversions import str_from_datetime


class SqlAlchemyDataSource(object):
    def __init__(self, db_uri, app):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.db = SQLAlchemy(self.app)

        db = self.db

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

                siblings = app.Task.query.filter(Task.parent_id == None)

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
            def load(roots=None, max_depth=0, include_done=False,
                     include_deleted=False, exclude_undeadlined=False):

                query = app.Task.query

                if not include_done:
                    query = query.filter_by(is_done=False)

                if not include_deleted:
                    query = query.filter_by(is_deleted=False)

                if exclude_undeadlined:
                    query = query.filter(Task.deadline.isnot(None))

                if roots is None:
                    query = query.filter(Task.parent_id.is_(None))
                else:
                    if not hasattr(roots, '__iter__'):
                        roots = [roots]
                    query = query.filter(Task.id.in_(roots))

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

                        query = app.Task.query
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
                                  exclude_undeadlined=False, tags=None):

                query = app.Task.query

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

        class Tag(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            value = db.Column(db.String(100), nullable=False, unique=True)
            description = db.Column(db.String(4000), nullable=True)

            def __init__(self, value, description=None):
                self.value = value
                self.description = description

            def to_dict(self):
                return {
                    'id': self.id,
                    'value': self.value,
                    'description': self.description,
                }

        class TaskTagLink(db.Model):
            task_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                                primary_key=True)
            tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'),
                               primary_key=True)

            tag = db.relationship('Tag',
                                  backref=db.backref('tasks', lazy='dynamic'))

            @property
            def value(self):
                return self.tag.value

            task = db.relationship('Task',
                                   backref=db.backref('tags', lazy='dynamic'))

            def __init__(self, task_id, tag_id):
                self.task_id = task_id
                self.tag_id = tag_id

        class Note(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            content = db.Column(db.String(4000))
            timestamp = db.Column(db.DateTime)

            task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
            task = db.relationship('Task',
                                   backref=db.backref('notes', lazy='dynamic',
                                                      order_by=timestamp))

            def __init__(self, content, timestamp=None):
                self.content = content
                if timestamp is None:
                    timestamp = datetime.datetime.utcnow()
                if isinstance(timestamp, basestring):
                    timestamp = dparse(timestamp)
                self.timestamp = timestamp

            def to_dict(self):
                return {
                    'id': self.id,
                    'content': self.content,
                    'timestamp': str_from_datetime(self.timestamp),
                    'task_id': self.task_id
                }

        class Attachment(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            timestamp = db.Column(db.DateTime, nullable=False)
            path = db.Column(db.String(1000), nullable=False)
            filename = db.Column(db.String(100), nullable=False)
            description = db.Column(db.String(100), nullable=False, default='')

            task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
            task = db.relationship('Task',
                                   backref=db.backref('attachments',
                                                      lazy='dynamic',
                                                      order_by=timestamp))

            def __init__(self, path, description=None, timestamp=None,
                         filename=None):
                if description is None:
                    description = ''
                if timestamp is None:
                    timestamp = datetime.datetime.utcnow()
                if isinstance(timestamp, basestring):
                    timestamp = dparse(timestamp)
                if filename is None:
                    filename = os.path.basename(path)
                self.timestamp = timestamp
                self.path = path
                self.filename = filename
                self.description = description

            def to_dict(self):
                return {
                    'id': self.id,
                    'timestamp': str_from_datetime(self.timestamp),
                    'path': self.path,
                    'filename': self.filename,
                    'description': self.description,
                    'task_id': self.task_id
                }

        class User(db.Model):
            email = db.Column(db.String(100), primary_key=True, nullable=False)
            hashed_password = db.Column(db.String(100), nullable=False)
            is_admin = db.Column(db.Boolean, nullable=False, default=False)
            authenticated = True

            def __init__(self, email, hashed_password=None, is_admin=False):
                if hashed_password is None:
                    digits = '0123456789abcdef'
                    key = ''.join((random.choice(digits) for x in xrange(48)))
                    hashed_password = app.bcrypt.generate_password_hash(key)

                self.email = email
                self.hashed_password = hashed_password
                self.is_admin = is_admin

            def to_dict(self):
                return {
                    'email': self.email,
                    'hashed_password': self.hashed_password,
                    'is_admin': self.is_admin
                }

            def is_active(self):
                return True

            def get_id(self):
                return self.email

            def is_authenticated(self):
                return self.authenticated

            def is_anonymous(self):
                return False

        class View(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            roots = db.Column(db.String(100), nullable=False)

            def __init__(self, name, roots):
                self.name = name
                self.roots = roots

            def to_dict(self):
                return {
                    'id': self.id,
                    'name': self.name,
                    'roots': self.roots
                }

        class Option(db.Model):
            key = db.Column(db.String(100), primary_key=True)
            value = db.Column(db.String(100), nullable=True)

            def __init__(self, key, value):
                self.key = key
                self.value = value

            def to_dict(self):
                return {
                    'key': self.key,
                    'value': self.value
                }

        db.Task = Task
        db.Tag = Tag
        db.TaskTagLink = TaskTagLink
        db.Note = Note
        db.Attachment = Attachment
        db.User = User
        db.View = View
        db.Option = Option

        self.Task = Task
        self.Tag = Tag
        self.TaskTagLink = TaskTagLink
        self.Note = Note
        self.Attachment = Attachment
        self.User = User
        self.View = View
        self.Option = Option
