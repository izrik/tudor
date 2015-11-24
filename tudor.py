#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request, flash
from flask import make_response, Markup
import flask
import argparse
from flask.ext.sqlalchemy import SQLAlchemy
from os import environ
import datetime
import os.path
from werkzeug import secure_filename
import random
from flask.ext.login import LoginManager, login_user, login_required
from flask.ext.login import logout_user
from flask.ext.bcrypt import Bcrypt
import re
import itertools
import gfm
import markdown
import dateutil.parser
from dateutil.parser import parse as dparse


DEFAULT_TUDOR_DEBUG = False
DEFAULT_TUDOR_PORT = 8304
DEFAULT_TUDOR_DB_URI = 'sqlite:////tmp/test.db'
DEFAULT_TUDOR_UPLOAD_FOLDER = '/tmp/tudor/uploads'
DEFAULT_TUDOR_ALLOWED_EXTENSIONS = 'txt,pdf,png,jpg,jpeg,gif'
DEFAULT_TUDOR_SECRET_KEY = None


def bool_from_str(s):
    if isinstance(s, basestring):
        s = s.lower()
    if s in ['true', 't', '1', 'y']:
        return True
    if s in ['false', 'f', '0', 'n']:
        return False
    return bool(s)


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

print('TUDOR_DEBUG: {}'.format(TUDOR_DEBUG))
print('TUDOR_PORT: {}'.format(TUDOR_PORT))
print('TUDOR_DB_URI: {}'.format(TUDOR_DB_URI))
print('TUDOR_UPLOAD_FOLDER: {}'.format(TUDOR_UPLOAD_FOLDER))
print('TUDOR_ALLOWED_EXTENSIONS: {}'.format(TUDOR_ALLOWED_EXTENSIONS))


def generate_app(db_uri=DEFAULT_TUDOR_DB_URI,
                 upload_folder=DEFAULT_TUDOR_UPLOAD_FOLDER,
                 secret_key=DEFAULT_TUDOR_SECRET_KEY,
                 allowed_extensions=DEFAULT_TUDOR_ALLOWED_EXTENSIONS):

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.secret_key = secret_key
    ALLOWED_EXTENSIONS = set(ext for ext in re.split('[\s,]+',
                                                     allowed_extensions)
                             if ext is not None and ext != '')
    db = SQLAlchemy(app)
    app.db = db

    login_manager = LoginManager()
    login_manager.init_app(app)
    app.login_manager = login_manager

    bcrypt = Bcrypt(app)
    app.bcrypt = bcrypt

    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        summary = db.Column(db.String(100))
        description = db.Column(db.String(4000))
        is_done = db.Column(db.Boolean)
        is_deleted = db.Column(db.Boolean)
        order_num = db.Column(db.Integer, nullable=False, default=0)
        deadline = db.Column(db.DateTime)

        parent_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                              nullable=True)
        parent = db.relationship('Task', remote_side=[id],
                                 backref=db.backref('children',
                                                    lazy='dynamic'))

        depth = 0

        def __init__(self, summary, description='', is_done=False,
                     is_deleted=False, deadline=None):
            self.summary = summary
            self.description = description
            self.is_done = is_done
            self.is_deleted = is_deleted
            if isinstance(deadline, str):
                deadline = dparse(deadline)
            self.deadline = deadline

        def get_siblings(self, include_deleted=True, descending=False,
                         ascending=False):
            if self.parent_id is not None:
                return self.parent.get_children(include_deleted, descending,
                                                ascending)

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

        def get_all_descendants(self, include_deleted=True, descending=False,
                                ascending=False, visited=None, result=None):
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

            query = Task.query

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
            self.timestamp = timestamp

    class Attachment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.DateTime, nullable=False)
        path = db.Column(db.String(1000), nullable=False)
        filename = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(100), nullable=False, default='')

        task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
        task = db.relationship('Task', backref=db.backref('attachments',
                                                          lazy='dynamic',
                                                          order_by=timestamp))

        def __init__(self, path, description=None, timestamp=None,
                     filename=None):
            if description is None:
                description = ''
            if timestamp is None:
                timestamp = datetime.datetime.utcnow()
            if filename is None:
                filename = os.path.basename(path)
            self.timestamp = timestamp
            self.path = path
            self.filename = filename
            self.description = description

    class User(db.Model):
        email = db.Column(db.String(100), primary_key=True, nullable=False)
        hashed_password = db.Column(db.String(100), nullable=False)
        authenticated = True

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

    class Option(db.Model):
        key = db.Column(db.String(100), primary_key=True)
        value = db.Column(db.String(100), nullable=True)

        def __init__(self, key, value):
            self.key = key
            self.value = value

    class Options(object):
        @staticmethod
        def get(key, default_value=None):
            option = Option.query.get(key)
            if option is None:
                return default_value
            return option.value

        @staticmethod
        def get_title():
            return Options.get('title', 'Tudor')

    app.Task = Task
    app.Note = Note
    app.Attachment = Attachment
    app.User = User
    app.View = View
    app.Option = Option

    def save_task(task):
        db.session.add(task)
        db.session.commit()

    def purge_tasks(tasks):
        for task in tasks:
            db.session.delete(task)
        db.session.commit()

    def purge_task_from_db(task):
        db.session.delete(task)
        db.session.commit()

    def get_roots_str():
        roots = request.args.get('roots') or request.cookies.get('roots')
        return roots

    def flatten(lst):
        gen = (x if isinstance(x, list) else [x] for x in lst)
        flattened = itertools.chain.from_iterable(gen)
        return list(flattened)

    def get_root_ids_from_str(roots):
        root_ids = roots.split(',')
        for i in xrange(len(root_ids)):
            m = re.match(r'(\d+)\*', root_ids[i])
            if m:
                id = m.group(1)
                task = Task.query.get(id)
                root_ids[i] = map(lambda c: c.id, task.children)
        if root_ids:
            root_ids = flatten(root_ids)
            return root_ids
        return None

    def get_tasks_and_all_descendants_from_tasks(tasks):
        visited = set()
        result = []
        for task in tasks:
            task.get_all_descendants(visited=visited, result=result)
        return result

    @app.context_processor
    def setup_options():
        return {'opts': Options}

    @app.route('/new_loader')
    @login_required
    def new_loader_page():

        kwargs = {}

        roots = request.args.get('roots')
        if roots is not None:
            kwargs['roots'] = roots.split(',')

        max_depth = request.args.get('max_depth')
        if max_depth is not None:
            kwargs['max_depth'] = int(max_depth)
        else:
            kwargs['max_depth'] = None

        include_done = request.args.get('include_done')
        if include_done is not None:
            kwargs['include_done'] = bool_from_str(include_done)

        include_deleted = request.args.get('include_deleted')
        if include_deleted is not None:
            kwargs['include_deleted'] = bool_from_str(include_deleted)

        exclude_undeadlined = request.args.get('exclude_undeadlined')
        if exclude_undeadlined is not None:
            kwargs['exclude_undeadlined'] = bool_from_str(exclude_undeadlined)

        tasks = Task.load(**kwargs)

        return render_template('new_loader.t.html', tasks=tasks,
                               cycle=itertools.cycle)

    @app.route('/new_loader/task_with_children/<int:id>')
    @login_required
    def new_loader_task_with_children(id):
        task = Task.query.get(id)
        if task is None:
            return '', 404
        descendants = Task.load(roots=task.id, max_depth=None,
                                include_done=True, include_deleted=True)
        return render_template('new_loader_task_with_children.t.html',
                               task=task, descendants=descendants)

    @app.route('/')
    @login_required
    def index():
        show_deleted = request.cookies.get('show_deleted')
        roots = get_roots_str()
        tasks = None
        if roots is not None:
            root_ids = get_root_ids_from_str(roots)
            if root_ids:
                tasks = Task.query.filter(Task.id.in_(root_ids))

        if tasks is None:
            tasks = Task.query.filter(Task.parent_id == None)
        if not show_deleted:
            tasks = tasks.filter_by(is_deleted=False)
        tasks = tasks.order_by(Task.order_num.desc())
        tasks = tasks.all()

        all_tasks = get_tasks_and_all_descendants_from_tasks(tasks)
        deadline_tasks = [t for t in all_tasks if t.deadline is not None and
                          not t.is_done]
        deadline_tasks = sorted(deadline_tasks, key=lambda task: task.deadline)

        resp = make_response(render_template('index.t.html', tasks=tasks,
                                             show_deleted=show_deleted,
                                             roots=roots, views=View.query,
                                             cycle=itertools.cycle,
                                             all_tasks=all_tasks,
                                             deadline_tasks=deadline_tasks))
        if roots:
            resp.set_cookie('roots', roots)
        return resp

    @app.route('/task/new', methods=['POST'])
    @login_required
    def new_task():
        summary = request.form['summary']
        task = Task(summary)

        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']
            if parent_id is None or parent_id == '':
                task.parent_id = None
            elif Task.query.filter_by(id=parent_id).count() > 0:
                task.parent_id = parent_id
        else:
            task.parent_id = None

        if 'next_url' in request.form:
            next_url = request.form['next_url']
        else:
            next_url = url_for('index')

        save_task(task)
        return redirect(next_url)

    @app.route('/task/<int:id>/mark_done')
    @login_required
    def task_done(id):
        task = Task.query.filter_by(id=id).first()
        if not task:
            return 404
        task.is_done = True
        save_task(task)
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/mark_undone')
    @login_required
    def task_undo(id):
        task = Task.query.filter_by(id=id).first()
        if not task:
            return 404
        task.is_done = False
        save_task(task)
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/delete')
    @login_required
    def delete_task(id):
        task = Task.query.filter_by(id=id).first()
        if not task:
            return 404
        task.is_deleted = True
        save_task(task)
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/undelete')
    @login_required
    def undelete_task(id):
        task = Task.query.filter_by(id=id).first()
        if not task:
            return 404
        task.is_deleted = False
        save_task(task)
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/purge')
    @login_required
    def purge_task(id):
        task = Task.query.filter_by(id=id, is_deleted=True).first()
        if not task:
            return 404
        purge_task_from_db(task)
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/purge_all')
    @login_required
    def purge_deleted_tasks():
        are_you_sure = request.args.get('are_you_sure')
        if are_you_sure:
            deleted_tasks = Task.query.filter_by(is_deleted=True)
            purge_tasks(deleted_tasks)
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('purge.t.html')

    @app.route('/task/<int:id>')
    @login_required
    def view_task(id):
        task = Task.query.filter_by(id=id).first()
        if task is None:
            return (('No task found for the id "%s"' % id), 404)
        return render_template('task.t.html', task=task)

    @app.route('/note/new', methods=['POST'])
    @login_required
    def new_note():
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        task = Task.query.filter_by(id=task_id).first()
        if task is None:
            return (('No task found for the id "%s"' % task_id), 404)
        content = request.form['content']
        note = Note(content)
        note.task = task

        save_task(note)

        return redirect(url_for('view_task', id=task_id))

    @app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(id):
        task = Task.query.filter_by(id=id).first()

        def render_get_response():
            return render_template("edit_task.t.html", task=task)

        if request.method == 'GET':
            return render_get_response()

        if 'summary' not in request.form or 'description' not in request.form:
            return render_get_response()

        task.summary = request.form['summary']
        task.description = request.form['description']
        deadline = request.form['deadline']
        if deadline:
            task.deadline = dparse(deadline)
        else:
            task.deadline = None

        task.is_done = ('is_done' in request.form and
                        not not request.form['is_done'])
        task.is_deleted = ('is_deleted' in request.form and
                           not not request.form['is_deleted'])

        if 'order_num' in request.form:
            task.order_num = request.form['order_num']
        else:
            task.order_num = 0

        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']
            if parent_id is None or parent_id == '':
                task.parent_id = None
            elif Task.query.filter_by(id=parent_id).count() > 0:
                task.parent_id = parent_id
        else:
            task.parent_id = None

        save_task(task)

        return redirect(url_for('view_task', id=task.id))

    def allowed_file(filename):
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1]
        return (ext in allowed_extensions)

    @app.route('/attachment/new', methods=['POST'])
    @login_required
    def new_attachment():
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        task = Task.query.filter_by(id=task_id).first()
        if task is None:
            return (('No task found for the task_id "%s"' % task_id), 404)
        f = request.files['filename']
        if f is None or not f or not allowed_file(f.filename):
            return 'Invalid file', 400
        path = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], path))
        if 'description' in request.form:
            description = request.form['description']
        else:
            description = ''

        att = Attachment(path, description)
        att.task = task

        save_task(att)

        return redirect(url_for('view_task', id=task_id))

    @app.route('/attachment/<int:aid>', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/<path:x>')
    @login_required
    def get_attachment(aid, x):
        att = Attachment.query.filter_by(id=aid).first()
        if att is None:
            return (('No attachment found for the id "%s"' % aid), 404)

        return flask.send_from_directory(upload_folder, att.path)

    def reorder_tasks(tasks):
        tasks = list(tasks)
        N = len(tasks)
        for i in xrange(N):
            tasks[i].order_num = 2 * (N - i)
            db.session.add(tasks[i])

    @app.route('/task/<int:id>/up')
    @login_required
    def move_task_up(id):
        task = Task.query.get(id)
        show_deleted = request.cookies.get('show_deleted')
        siblings = task.get_siblings(show_deleted)
        higher_siblings = siblings.filter(Task.order_num >= task.order_num)
        higher_siblings = higher_siblings.filter(Task.id != task.id)
        next_task = higher_siblings.order_by(Task.order_num.asc()).first()

        if next_task:
            if task.order_num == next_task.order_num:
                reorder_tasks(task.get_siblings(descending=True))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num = new_order_num, task.order_num

            db.session.add(task)
            db.session.add(next_task)
            db.session.commit()

        return redirect(url_for('index'))

    @app.route('/task/<int:id>/down')
    @login_required
    def move_task_down(id):
        task = Task.query.get(id)
        show_deleted = request.cookies.get('show_deleted')
        siblings = task.get_siblings(show_deleted)
        lower_siblings = siblings.filter(Task.order_num <= task.order_num)
        lower_siblings = lower_siblings.filter(Task.id != task.id)
        next_task = lower_siblings.order_by(Task.order_num.desc()).first()

        if next_task:
            if task.order_num == next_task.order_num:
                reorder_tasks(task.get_siblings(descending=True))
            new_order_num = next_task.order_num
            task.order_num, next_task.order_num = new_order_num, task.order_num

            db.session.add(task)
            db.session.add(next_task)
            db.session.commit()

        return redirect(url_for('index'))

    @app.route('/task/<int:id>/right')
    @login_required
    def move_task_right(id):
        task = Task.query.get(id)
        show_deleted = request.cookies.get('show_deleted')
        siblings = task.get_siblings(show_deleted)
        higher_siblings = siblings.filter(Task.order_num >= task.order_num)
        higher_siblings = higher_siblings.filter(Task.id != task.id)
        next_task = higher_siblings.order_by(Task.order_num.asc()).first()

        if next_task:
            if next_task.children.count() > 0:
                reorder_tasks(next_task.get_children(descending=True))
                children = next_task.get_children(ascending=True)
                next_sibling = children.first()
                new_order_num = next_sibling.order_num - 1
            else:
                new_order_num = 0
            prev_parent = task.parent
            task.parent = next_task
            task.order_num = new_order_num

            if prev_parent:
                db.session.add(prev_parent)
            db.session.add(task)
            db.session.add(next_task)
            db.session.commit()

        return redirect(url_for('index'))

    @app.route('/task/<int:id>/left')
    @login_required
    def move_task_left(id):
        task = Task.query.get(id)
        show_deleted = request.cookies.get('show_deleted')

        if task.parent:
            reorder_tasks(task.parent.get_siblings(descending=True))

            prev_parent = task.parent
            task.parent = task.parent.parent
            task.order_num = prev_parent.order_num - 1

            db.session.add(prev_parent)
            if task.parent is not None:
                db.session.add(task.parent)
            db.session.add(task)
            db.session.commit()

        return redirect(url_for('index'))

    @login_manager.user_loader
    def load_user(userid):
        return User.query.get(userid)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.t.html')
        email = request.form['email']
        password = request.form['password']
        user = User.query.get(email)

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

    @app.route('/users')
    @login_required
    def list_users():
        return render_template('list_users.t.html', users=User.query,
                               cycle=itertools.cycle)

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

    @app.route('/view/new', methods=['POST'])
    @login_required
    def new_view():
        if 'view_name' not in request.form or 'view_roots' not in request.form:
            return redirect(url_for('index'))

        name = request.form['view_name']
        roots = request.form['view_roots']
        view = View(name, roots)

        db.session.add(view)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/view/<int:id>')
    @login_required
    def set_view(id):
        view = View.query.get(id)
        if view is None:
            return (('No view found for the id "%s"' % id), 404)
        return redirect(url_for('set_roots', roots=view.roots))

    @app.route('/options', methods=['GET', 'POST'])
    @login_required
    def view_options():
        if request.method == 'GET' or 'key' not in request.form:
            return render_template('options.t.html', options=Option.query)

        key = request.form['key']
        value = ''
        if 'value' in request.form:
            value = request.form['value']

        option = Option.query.get(key)
        if option is not None:
            option.value = value
        else:
            option = Option(key, value)

        db.session.add(option)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('view_options'))

    @app.route('/option/<path:key>/delete')
    @login_required
    def delete_option(key):
        option = Option.query.get(key)
        if option is not None:
            db.session.delete(option)
            db.session.commit()

        return redirect(request.args.get('next') or url_for('view_options'))

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
        app.db.create_all()
    elif args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
    elif args.hash_password is not None:
        print(app.bcrypt.generate_password_hash(args.hash_password))
    else:
        app.run(debug=TUDOR_DEBUG, port=TUDOR_PORT)
