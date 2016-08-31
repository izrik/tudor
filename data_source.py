#!/usr/bin/env python

from flask.ext.sqlalchemy import SQLAlchemy
from models.task import generate_task_class
from models.tag import generate_tag_class
from models.task_tag_link import generate_task_tag_link_class
from models.note import generate_note_class
from models.attachment import generate_attachment_class
from models.user import generate_user_class
from models.option import generate_option_class
from models.task_user_link import generate_task_user_link_class


class SqlAlchemyDataSource(object):
    def __init__(self, db_uri, app):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.db = SQLAlchemy(self.app)

        db = self.db

        Tag = generate_tag_class(db)
        TaskTagLink = generate_task_tag_link_class(db)
        Task = generate_task_class(db, Tag, TaskTagLink)
        Note = generate_note_class(db)
        Attachment = generate_attachment_class(db)
        User = generate_user_class(db, app.bcrypt)
        Option = generate_option_class(db)
        TaskUserLink = generate_task_user_link_class(db)

        db.Task = Task
        db.Tag = Tag
        db.TaskTagLink = TaskTagLink
        db.Note = Note
        db.Attachment = Attachment
        db.User = User
        db.Option = Option
        db.TaskUserLink = TaskUserLink

        self.Task = Task
        self.Tag = Tag
        self.TaskTagLink = TaskTagLink
        self.Note = Note
        self.Attachment = Attachment
        self.User = User
        self.Option = Option
        self.TaskUserLink = TaskUserLink
