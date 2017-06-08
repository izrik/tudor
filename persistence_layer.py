
from flask_sqlalchemy import SQLAlchemy
from models.task import generate_task_class
from models.tag import generate_tag_class
from models.note import generate_note_class
from models.attachment import generate_attachment_class
from models.user import generate_user_class
from models.option import generate_option_class


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

    @property
    def task_query(self):
        return self.Task.query

    def get_task(self, task_id):
        return self.task_query.get(task_id)

    def get_tasks(self, is_done=UNSPECIFIED, is_deleted=UNSPECIFIED,
                  parent_id=UNSPECIFIED, users_contains=UNSPECIFIED):
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

        return query

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
