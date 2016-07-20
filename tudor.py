#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request, flash
from flask import make_response, Markup, jsonify, json
import flask
import argparse
from flask.ext.sqlalchemy import SQLAlchemy
from os import environ
import datetime
import os.path
from werkzeug import secure_filename
import random
from flask.ext.login import LoginManager, login_user, login_required
from flask.ext.login import logout_user, current_user
from flask.ext.bcrypt import Bcrypt
import re
import itertools
import gfm
import markdown
import dateutil.parser
from dateutil.parser import parse as dparse
from functools import wraps
import git
import os
from decimal import Decimal
import werkzeug.exceptions
from conversions import bool_from_str, int_from_str, str_from_datetime
from conversions import money_from_str
from logic_layer import LogicLayer

__revision__ = git.Repo('.').git.describe(tags=True, dirty=True, always=True,
                                          abbrev=40)


DEFAULT_TUDOR_DEBUG = False
DEFAULT_TUDOR_PORT = 8304
DEFAULT_TUDOR_DB_URI = 'sqlite:////tmp/test.db'
DEFAULT_TUDOR_UPLOAD_FOLDER = '/tmp/tudor/uploads'
DEFAULT_TUDOR_ALLOWED_EXTENSIONS = 'txt,pdf,png,jpg,jpeg,gif'
DEFAULT_TUDOR_SECRET_KEY = None


TUDOR_DEBUG = bool_from_str(environ.get('TUDOR_DEBUG', DEFAULT_TUDOR_DEBUG))
TUDOR_PORT = environ.get('TUDOR_PORT', DEFAULT_TUDOR_PORT)
try:
    TUDOR_PORT = int(TUDOR_PORT)
except:
    TUDOR_PORT = DEFAULT_TUDOR_PORT
TUDOR_DB_URI = environ.get('TUDOR_DB_URI', DEFAULT_TUDOR_DB_URI)
TUDOR_UPLOAD_FOLDER = environ.get('TUDOR_UPLOAD_FOLDER',
                                  DEFAULT_TUDOR_UPLOAD_FOLDER)
TUDOR_ALLOWED_EXTENSIONS = environ.get('TUDOR_ALLOWED_EXTENSIONS',
                                       DEFAULT_TUDOR_ALLOWED_EXTENSIONS)
TUDOR_SECRET_KEY = environ.get('TUDOR_SECRET_KEY')


args = None
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=TUDOR_DEBUG)
    parser.add_argument('--port', action='store', default=TUDOR_PORT, type=int)
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--db-uri', action='store', default=TUDOR_DB_URI)
    parser.add_argument('--upload-folder', action='store',
                        default=TUDOR_UPLOAD_FOLDER)
    parser.add_argument('--allowed-extensions', action='store',
                        default=TUDOR_ALLOWED_EXTENSIONS)
    parser.add_argument('--secret-key', action='store',
                        default=TUDOR_SECRET_KEY)
    parser.add_argument('--create-secret-key', action='store_true')
    parser.add_argument('--hash-password', action='store')

    args = parser.parse_args()

    TUDOR_DEBUG = args.debug
    TUDOR_PORT = args.port
    TUDOR_DB_URI = args.db_uri
    TUDOR_UPLOAD_FOLDER = args.upload_folder
    TUDOR_SECRET_KEY = args.secret_key
    TUDOR_ALLOWED_EXTENSIONS = args.allowed_extensions

print('__revision__: {}'.format(__revision__))
print('TUDOR_DEBUG: {}'.format(TUDOR_DEBUG))
print('TUDOR_PORT: {}'.format(TUDOR_PORT))
print('TUDOR_DB_URI: {}'.format(TUDOR_DB_URI))
print('TUDOR_UPLOAD_FOLDER: {}'.format(TUDOR_UPLOAD_FOLDER))
print('TUDOR_ALLOWED_EXTENSIONS: {}'.format(TUDOR_ALLOWED_EXTENSIONS))


def create_sqlalchemy_ds_factory(db_uri=DEFAULT_TUDOR_DB_URI):
    def ds_factory(_app):
        ds = SqlAlchemyDataSource(db_uri, _app)
        return ds
    return ds_factory


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


def generate_app(db_uri=DEFAULT_TUDOR_DB_URI, ds_factory=None,
                 upload_folder=DEFAULT_TUDOR_UPLOAD_FOLDER,
                 secret_key=DEFAULT_TUDOR_SECRET_KEY,
                 allowed_extensions=DEFAULT_TUDOR_ALLOWED_EXTENSIONS):

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.secret_key = secret_key
    ALLOWED_EXTENSIONS = set(ext for ext in re.split('[\s,]+',
                                                     allowed_extensions)
                             if ext is not None and ext != '')

    login_manager = LoginManager()
    login_manager.init_app(app)
    app.login_manager = login_manager

    bcrypt = Bcrypt(app)
    app.bcrypt = bcrypt

    if ds_factory is None:
        ds_factory = create_sqlalchemy_ds_factory(db_uri)

    ds = ds_factory(app)
    db = ds.db
    app.ds = ds

    class Options(object):
        @staticmethod
        def get(key, default_value=None):
            option = app.Option.query.get(key)
            if option is None:
                return default_value
            return option.value

        @staticmethod
        def get_title():
            return Options.get('title', 'Tudor')

        @staticmethod
        def get_revision():
            return __revision__

    app.Task = ds.Task
    app.Tag = ds.Tag
    app.TaskTagLink = ds.TaskTagLink
    app.Note = ds.Note
    app.Attachment = ds.Attachment
    app.User = ds.User
    app.View = ds.View
    app.Option = ds.Option

    ll = LogicLayer(ds, upload_folder, allowed_extensions)
    app.ll = ll
    app._convert_task_to_tag = ll._convert_task_to_tag

    # Flask setup functions

    @login_manager.user_loader
    def load_user(userid):
        return app.User.query.get(userid)

    def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_admin:
                return ('You are not authorized to view this page', 403)
            return func(*args, **kwargs)
        return decorated_view

    @app.context_processor
    def setup_options():
        return {'opts': Options}

    # View utility functions

    def get_form_or_arg(self, name):
        if name in request.form:
            return request.form[name]
        return request.args.get(name)

    # View Functions

    @app.route('/')
    @login_required
    def index():
        show_deleted = request.cookies.get('show_deleted')
        show_done = request.cookies.get('show_done')
        roots = request.args.get('roots') or request.cookies.get('roots')

        tags = request.args.get('tags') or request.cookies.get('tags')

        data = ll.get_index_data(show_deleted, show_done, roots, tags)

        resp = make_response(
            render_template('index.t.html',
                            tasks=data['tasks'],
                            show_deleted=data['show_deleted'],
                            show_done=data['show_done'],
                            roots=data['roots'],
                            views=data['views'],
                            cycle=itertools.cycle,
                            all_tasks=data['all_tasks'],
                            deadline_tasks=data['deadline_tasks'],
                            user=current_user,
                            tasks_h=data['tasks_h'],
                            tags=data['all_tags']))
        if roots:
            resp.set_cookie('roots', roots)
        return resp

    @app.route('/task/new', methods=['POST'])
    @login_required
    def new_task():
        summary = request.form['summary']

        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']
        else:
            parent_id = None

        task = ll.create_new_task(summary, parent_id)

        db.session.add(task)
        db.session.commit()

        if 'next_url' in request.form:
            next_url = request.form['next_url']
        else:
            next_url = url_for('index')

        return redirect(next_url)

    @app.route('/task/<int:id>/mark_done')
    @login_required
    def task_done(id):
        task = ll.task_set_done(id)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/mark_undone')
    @login_required
    def task_undo(id):
        task = ll.task_unset_done(id)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/delete')
    @login_required
    def delete_task(id):
        task = ll.task_set_deleted(id)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/undelete')
    @login_required
    def undelete_task(id):
        task = ll.task_unset_deleted(id)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/purge')
    @login_required
    @admin_required
    def purge_task(id):
        task = app.Task.query.filter_by(id=id, is_deleted=True).first()
        if not task:
            return 404
        db.session.delete(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/purge_all')
    @login_required
    @admin_required
    def purge_deleted_tasks():
        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:
            deleted_tasks = app.Task.query.filter_by(is_deleted=True)
            for task in deleted_tasks:
                db.session.delete(task)
            db.session.commit()
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('purge.t.html')

    @app.route('/task/<int:id>')
    @login_required
    def view_task(id):
        data = ll.get_task_data(id)

        return render_template('task.t.html', task=data['task'],
                               descendants=data['descendants'],
                               cycle=itertools.cycle)

    @app.route('/note/new', methods=['POST'])
    @login_required
    def new_note():
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        content = request.form['content']

        note = ll.create_new_note(task_id, content)

        db.session.add(note)
        db.session.commit()

        return redirect(url_for('view_task', id=task_id))

    @app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(id):

        def render_get_response():
            data = ll.get_edit_task_data(id)
            return render_template("edit_task.t.html", task=data['task'],
                                   tag_list=data['tag_list'])

        if request.method == 'GET':
            return render_get_response()

        if 'summary' not in request.form or 'description' not in request.form:
            return render_get_response()

        summary = request.form['summary']
        description = request.form['description']
        deadline = request.form['deadline']

        is_done = ('is_done' in request.form and
                   not not request.form['is_done'])
        is_deleted = ('is_deleted' in request.form and
                      not not request.form['is_deleted'])

        order_num = None
        if 'order_num' in request.form:
            order_num = request.form['order_num']

        parent_id = None
        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']

        tags = request.form['tags']

        duration = int_from_str(request.form['expected_duration_minutes'])

        expected_cost = money_from_str(request.form['expected_cost'])

        task = ll.set_task(id, summary, description, deadline, is_done,
                           is_deleted, order_num, duration, expected_cost,
                           parent_id, tags)

        db.session.add(task)
        db.session.commit()

        return redirect(url_for('view_task', id=task.id))

    @app.route('/attachment/new', methods=['POST'])
    @login_required
    def new_attachment():
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']

        f = request.files['filename']
        if f is None or not f or not ll.allowed_file(f.filename):
            return 'Invalid file', 400

        if 'description' in request.form:
            description = request.form['description']
        else:
            description = ''

        att = ll.create_new_attachment(task_id, f, description)

        db.session.add(att)
        db.session.commit()

        return redirect(url_for('view_task', id=task_id))

    @app.route('/attachment/<int:aid>', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/<path:x>')
    @login_required
    def get_attachment(aid, x):
        att = app.Attachment.query.filter_by(id=aid).first()
        if att is None:
            return (('No attachment found for the id "%s"' % aid), 404)

        return flask.send_from_directory(upload_folder, att.path)

    @app.route('/task/<int:id>/up')
    @login_required
    def move_task_up(id):
        show_deleted = request.cookies.get('show_deleted')
        ll.do_move_task_up(id, show_deleted)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/top')
    @login_required
    def move_task_to_top(id):
        ll.do_move_task_to_top(id)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/down')
    @login_required
    def move_task_down(id):
        show_deleted = request.cookies.get('show_deleted')
        ll.do_move_task_down(id, show_deleted)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/bottom')
    @login_required
    def move_task_to_bottom(id):
        ll.do_move_task_to_bottom(id)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/long_order_change', methods=['POST'])
    @login_required
    def long_order_change():

        task_to_move_id = get_form_or_arg('long_order_task_to_move')
        if task_to_move_id is None:
            redirect(request.args.get('next') or url_for('index'))

        target_id = get_form_or_arg('long_order_target')
        if target_id is None:
            redirect(request.args.get('next') or url_for('index'))

        ll.do_long_order_change(task_to_move_id, target_id)

        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/add_tag', methods=['GET', 'POST'])
    @login_required
    def add_tag_to_task(id):

        value = get_form_or_arg('value')
        if value is None or value == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=id)))

        ll.do_add_tag_to_task(id, value)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=id)))

    @app.route('/task/<int:id>/delete_tag', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/<tag_id>', methods=['GET', 'POST'])
    @login_required
    def delete_tag_from_task(id, tag_id):

        if tag_id is None:
            tag_id = get_form_or_arg('tag_id')

        ll.do_delete_tag_from_task(id, tag_id)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=id)))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.t.html')
        email = request.form['email']
        password = request.form['password']
        user = app.User.query.get(email)

        if (user is None or
                not bcrypt.check_password_hash(user.hashed_password,
                                               password)):
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    login_manager.login_view = 'login'

    @app.route('/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def list_users():

        if request.method == 'GET':
            return render_template('list_users.t.html', users=app.User.query,
                                   cycle=itertools.cycle)

        email = request.form['email']
        is_admin = False
        if 'is_admin' in request.form:
            is_admin = bool_from_str(request.form['is_admin'])

        ll.do_add_new_user(email, is_admin)
        db.session.commit()

        return redirect(url_for('list_users'))

    @app.route('/clear_roots')
    @login_required
    def clear_roots():
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('roots', '', expires=0)
        return resp

    @app.route('/set_roots')
    @login_required
    def set_roots():
        roots = request.args.get('roots')
        resp = make_response(redirect(url_for('index')))
        if roots is not None and roots != '':
            resp.set_cookie('roots', roots)
        else:
            resp.set_cookie('roots', '', expires=0)
        return resp

    @app.route('/show_hide_deleted')
    @login_required
    def show_hide_deleted():
        show_deleted = request.args.get('show_deleted')
        resp = make_response(redirect(url_for('index')))
        if show_deleted and show_deleted != '0':
            resp.set_cookie('show_deleted', '1')
        else:
            resp.set_cookie('show_deleted', '')
        return resp

    @app.route('/show_hide_done')
    @login_required
    def show_hide_done():
        show_done = request.args.get('show_done')
        resp = make_response(redirect(url_for('index')))
        if show_done and show_done != '0':
            resp.set_cookie('show_done', '1')
        else:
            resp.set_cookie('show_done', '')
        return resp

    @app.route('/view/new', methods=['POST'])
    @login_required
    def new_view():
        if 'view_name' not in request.form or 'view_roots' not in request.form:
            return redirect(url_for('index'))

        name = request.form['view_name']
        roots = request.form['view_roots']
        ll.do_add_new_view(name, roots)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/view/<int:id>')
    @login_required
    def set_view(id):
        view = app.View.query.get(id)
        if view is None:
            return (('No view found for the id "%s"' % id), 404)
        return redirect(url_for('set_roots', roots=view.roots))

    @app.route('/options', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def view_options():
        if request.method == 'GET' or 'key' not in request.form:
            data = ll.get_view_options_data()
            return render_template('options.t.html', options=data)

        key = request.form['key']
        value = ''
        if 'value' in request.form:
            value = request.form['value']

        ll.do_set_option(key, value)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('view_options'))

    @app.route('/option/<path:key>/delete')
    @login_required
    @admin_required
    def delete_option(key):
        ll.do_delete_option(key)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('view_options'))

    @app.route('/reset_order_nums')
    @login_required
    def reset_order_nums():
        ll.do_reset_order_nums()
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/export', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def export_data():
        if request.method == 'GET':
            return render_template('export.t.html', results=None)
        types_to_export = set(k for k in request.form.keys() if
                              k in request.form and request.form[k] == 'all')
        results = ll.do_export_data(types_to_export)
        return jsonify(results)

    @app.route('/import', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def import_data():
        if request.method == 'GET':
            return render_template('import.t.html')

        f = request.files['file']
        if f is None or not f:
            r = request.form['raw']
            src = json.loads(r)
        else:
            src = json.load(f)

        ll.do_import_data(src)
        db.session.commit()

        return redirect(url_for('index'))

    @app.route('/task_crud', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def task_crud():

        if request.method == 'GET':
            tasks = ll.get_task_crud_data()
            return render_template('task_crud.t.html', tasks=tasks,
                                   cycle=itertools.cycle)

        crud_data = {}
        for key in request.form.keys():
            if re.match(r'task_\d+_(summary|deadline|is_done|is_deleted|'
                        r'order_num|duration|cost|parent_id)', key):
                crud_data[key] = request.form[key]

        ll.do_submit_task_crud(crud_data)
        db.session.commit()

        return redirect(url_for('task_crud'))

    @app.route('/tags')
    @app.route('/tags/')
    @login_required
    def list_tags():
        tags = ll.get_tags()
        return render_template('list_tags.t.html', tags=tags,
                               cycle=itertools.cycle)

    @app.route('/tags/<int:id>')
    @login_required
    def view_tag(id):
        data = ll.get_tag_data(id)
        return render_template('tag.t.html', tag=data['tag'],
                               tasks=data['tasks'], cycle=itertools.cycle)

    @app.route('/tags/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_tag(id):

        def render_get_response():
            tag = ll.get_tag(id)
            return render_template("edit_tag.t.html", tag=tag)

        if request.method == 'GET':
            return render_get_response()

        if 'value' not in request.form or 'description' not in request.form:
            return render_get_response()
        value = request.form['value']
        description = request.form['description']
        ll.do_edit_tag(id, value, description)
        db.session.commit()

        return redirect(url_for('view_tag', id=id))

    @app.route('/task/<int:id>/convert_to_tag')
    @login_required
    def convert_task_to_tag(id):

        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:

            tag = ll._convert_task_to_tag(id)

            return redirect(
                request.args.get('next') or url_for('view_tag', id=tag.id))

        task = ll.get_task(id)
        return render_template('convert_task_to_tag.t.html',
                               task_id=task.id,
                               tag_value=task.summary,
                               tag_description=task.description,
                               cycle=itertools.cycle,
                               tasks=task.children)

    @app.template_filter(name='gfm')
    def render_gfm(s):
        output = markdown.markdown(s, extensions=['gfm'])
        moutput = Markup(output)
        return moutput

    return app

if __name__ == '__main__':
    app = generate_app(db_uri=TUDOR_DB_URI, upload_folder=TUDOR_UPLOAD_FOLDER,
                       secret_key=TUDOR_SECRET_KEY,
                       allowed_extensions=TUDOR_ALLOWED_EXTENSIONS)

    if args.create_db:
        print('Setting up the database')
        app.ds.db.create_all()
    elif args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
    elif args.hash_password is not None:
        print(app.bcrypt.generate_password_hash(args.hash_password))
    else:
        app.run(debug=TUDOR_DEBUG, port=TUDOR_PORT)
