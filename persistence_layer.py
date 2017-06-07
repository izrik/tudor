
from flask_sqlalchemy import SQLAlchemy
from models.task import generate_task_class
from models.tag import generate_tag_class
from models.note import generate_note_class
from models.attachment import generate_attachment_class
from models.user import generate_user_class
from models.option import generate_option_class


class PersistenceLayer(object):
    def __init__(self, app, db_uri):

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

        Task = generate_task_class(db, tags_tasks_table, users_tasks_table,
                                   task_dependencies_table,
                                   task_prioritize_table)
        Note = generate_note_class(db)
        Attachment = generate_attachment_class(db)
        User = generate_user_class(db, app.bcrypt)
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
