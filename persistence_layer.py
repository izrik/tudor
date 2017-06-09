
import collections

from flask_sqlalchemy import SQLAlchemy
from models.task import generate_task_class
from models.tag import generate_tag_class
from models.note import generate_note_class
from models.attachment import generate_attachment_class
from models.user import generate_user_class
from models.option import generate_option_class


def is_iterable(x):
    return isinstance(x, collections.Iterable)


def as_iterable(x):
    if is_iterable(x):
        return x
    return (x,)


class PersistenceLayer(object):
    def __init__(self, app, db_uri, bcrypt):

        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.db = SQLAlchemy(self.app)

        db = self.db

        Tag = generate_tag_class(db)

        tags_tasks_table = db.Table(
            'tags_tasks',
            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'),
                      index=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      index=True))

        users_tasks_table = db.Table(
            'users_tasks',
            db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
                      index=True),
            db.Column('task_id', db.Integer, db.ForeignKey('task.id'),
                      index=True))

        task_dependencies_table = db.Table(
            'task_dependencies',
            db.Column('dependee_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True),
            db.Column('dependant_id', db.Integer, db.ForeignKey('task.id'),
                      primary_key=True))

        task_prioritize_table = db.Table(
            'task_prioritize',
            db.Column('prioritize_before_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True),
            db.Column('prioritize_after_id', db.Integer,
                      db.ForeignKey('task.id'), primary_key=True))

        Task = generate_task_class(self, tags_tasks_table, users_tasks_table,
                                   task_dependencies_table,
                                   task_prioritize_table)
        Note = generate_note_class(db)
        Attachment = generate_attachment_class(db)
        User = generate_user_class(db, bcrypt)
        Option = generate_option_class(db)

        self.Task = Task
        self.Tag = Tag
        self.Note = Note
        self.Attachment = Attachment
        self.User = User
        self.Option = Option

    def add(self, obj):
        self.db.session.add(obj)

    def delete(self, obj):
        self.db.session.delete(obj)

    def commit(self):
        self.db.session.commit()

    def create_all(self):
        self.db.create_all()

    UNSPECIFIED = object()

    ASCENDING = object()
    DESCENDING = object()

    TASK_ID = object()
    ORDER_NUM = object()

    def get_db_field_by_order_field(self, f):
        if f is self.ORDER_NUM:
            return self.Task.order_num
        if f is self.TASK_ID:
            return self.Task.id
        raise Exception('Unhandled order_by field: {}'.format(f))

    @property
    def task_query(self):
        return self.Task.query

    def get_task(self, task_id):
        return self.task_query.get(task_id)

    def _get_tasks_query(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                         parent_id=UNSPECIFIED, users_contains=UNSPECIFIED,
                         id_in=UNSPECIFIED, order_by=UNSPECIFIED,
                         limit=UNSPECIFIED):

        """order_by is a list of order directives. Each such directive is
         either a field (e.g. ORDER_NUM) or a sequence of field and direction
          (e.g. [ORDER_NUM, ASCENDING]). Default direction is ASCENDING if not
           specified."""

        query = self.task_query
        if is_done is not self.UNSPECIFIED:
            query = query.filter_by(is_done=is_done)
        if is_deleted is not self.UNSPECIFIED:
            query = query.filter_by(is_deleted=is_deleted)
        if parent_id is not self.UNSPECIFIED:
            if parent_id is None:
                query = query.filter(self.Task.parent_id.is_(None))
            else:
                query = query.filter_by(parent_id=parent_id)
        if users_contains is not self.UNSPECIFIED:
            query = query.filter(self.Task.users.contains(users_contains))

        if id_in is not self.UNSPECIFIED:
            # Using in_ on an empty set works but is expensive for some db
            # engines. In the case of an empty collection, just use a query
            # that always returns an empty set, without the performance
            # penalty.
            if id_in:
                query = query.filter(self.Task.id.in_(id_in))
            else:
                query = query.filter(False)

        if order_by is not self.UNSPECIFIED:
            if not is_iterable(order_by):
                db_field = self.get_db_field_by_order_field(order_by)
                query = query.order_by(db_field)
            else:
                for ordering in order_by:
                    direction = self.ASCENDING
                    if is_iterable(ordering):
                        order_field = ordering[0]
                        if len(ordering) > 1:
                            direction = ordering[1]
                    else:
                        order_field = ordering
                    db_field = self.get_db_field_by_order_field(order_field)
                    if direction is self.ASCENDING:
                        query = query.order_by(db_field.asc())
                    elif direction is self.DESCENDING:
                        query = query.order_by(db_field.desc())
                    else:
                        raise Exception(
                            'Unknown order_by direction: {}'.format(direction))

        if limit is not self.UNSPECIFIED:
            query = query.limit(limit)

        return query

    def get_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                  parent_id=UNSPECIFIED, users_contains=UNSPECIFIED,
                  id_in=UNSPECIFIED, order_by=UNSPECIFIED, limit=UNSPECIFIED):
        query = self._get_tasks_query(
            is_done=is_done, is_deleted=is_deleted, parent_id=parent_id,
            users_contains=users_contains, order_by=order_by, id_in=id_in,
            limit=limit)
        return (_ for _ in query)

    def count_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                    parent_id=UNSPECIFIED, users_contains=UNSPECIFIED,
                    id_in=UNSPECIFIED, order_by=UNSPECIFIED,
                    limit=UNSPECIFIED):
        return self._get_tasks_query(is_done=is_done, is_deleted=is_deleted,
                                     parent_id=parent_id,
                                     users_contains=users_contains,
                                     order_by=order_by, id_in=id_in,
                                     limit=limit).count()

    @property
    def tag_query(self):
        return self.Tag.query

    def get_tag(self, tag_id):
        return self.tag_query.get(tag_id)

    @property
    def note_query(self):
        return self.Note.query

    def get_note(self, note_id):
        return self.note_query.get(note_id)

    @property
    def attachment_query(self):
        return self.Attachment.query

    def get_attachment(self, attachment_id):
        return self.attachment_query.get(attachment_id)

    @property
    def user_query(self):
        return self.User.query

    def get_user(self, user_id):
        return self.user_query.get(user_id)

    @property
    def option_query(self):
        return self.Option.query

    def get_option(self, key):
        return self.option_query.get(key)
