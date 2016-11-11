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
from data_source import SqlAlchemyDataSource
import base64

try:
    __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                              always=True, abbrev=40)
except git.InvalidGitRepositoryError:
    __revision__ = 'unknown'


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
    login_manager.login_view = 'login'

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
            option = ds.Option.query.get(key)
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
    app.Option = ds.Option

    ll = LogicLayer(ds, upload_folder, allowed_extensions)
    app.ll = ll
    app._convert_task_to_tag = ll._convert_task_to_tag

    # Flask setup functions

    @login_manager.user_loader
    def load_user(userid):
        return app.User.query.filter_by(email=userid).first()

    @login_manager.request_loader
    def load_user_with_basic_auth(request):
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            api_key = base64.b64decode(api_key)
            email, password = api_key.split(':', 1)
            user = app.User.query.filter_by(email=email).first()

            if (user is None or
                    not bcrypt.check_password_hash(
                        user.hashed_password, password)):
                return None

            return user

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

    def get_form_or_arg(name, default=None):
        if name in request.form:
            return request.form[name]
        if name in request.args:
            return request.args.get(name)
        return default

    def get_accept_type():
        best = request.accept_mimetypes.best_match(['application/json',
                                                    'text/html'])
        if (best == 'text/html' and request.accept_mimetypes[best] >=
                request.accept_mimetypes['application/json']):
            return 'html'
        elif (best == 'application/json' and request.accept_mimetypes[best] >=
                request.accept_mimetypes['text/html']):
            return 'json'
        else:
            return None

    # View Functions

    @app.route('/')
    @login_required
    def index():
        accept = get_accept_type()
        if accept is None:
            return '', 406

        if accept == 'html':
            show_deleted = request.cookies.get('show_deleted')
            show_done = request.cookies.get('show_done')
            show_hierarchy = request.cookies.get('show_hierarchy', True)

            data = ll.get_index_data(show_deleted, show_done, show_hierarchy,
                                     current_user)

            resp = make_response(
                render_template('index.t.html',
                                show_deleted=data['show_deleted'],
                                show_done=data['show_done'],
                                show_hierarchy=data['show_hierarchy'],
                                cycle=itertools.cycle,
                                user=current_user,
                                tasks_h=data['tasks_h'],
                                tags=data['all_tags']))
        else:
            show_deleted = get_form_or_arg('show_deleted')
            show_done = get_form_or_arg('show_done')
            show_hierarchy = False

            data = ll.get_index_data(show_deleted, show_done, show_hierarchy,
                                     current_user)

            tasks = [
                {'summary': t.summary, 'href': url_for('view_task', id=t.id)}
                for t in data['tasks_h'] if t is not None]

            tags = [
                {'name': tag.value, 'href': url_for('view_tag', id=tag.id)}
                for tag in data['all_tags']]

            data = {
                'tasks': tasks,
                'tags': tags
            }

            resp = json.dumps(data), 200

        return resp

    @app.route('/deadlines')
    @login_required
    def deadlines():
        accept = get_accept_type()
        if accept is None:
            return '', 406

        data = ll.get_deadlines_data(current_user)

        if accept == 'html':
            return make_response(
                render_template(
                    'deadlines.t.html',
                    cycle=itertools.cycle,
                    deadline_tasks=data['deadline_tasks']))
        else:
            deadline_tasks = [{'deadline': task.deadline,
                               'summary': task.summary,
                               'href': url_for('view_task', id=task.id)} for
                              task in data['deadline_tasks']]
            return json.dumps(deadline_tasks), 200

    @app.route('/task/new', methods=['POST'])
    @login_required
    def new_task():
        summary = request.form['summary']

        if 'parent_id' in request.form:
            parent_id = request.form['parent_id']
        else:
            parent_id = None

        task, tul = ll.create_new_task(summary, parent_id, current_user)

        db.session.add(task)
        # TODO: extra commit in view
        db.session.commit()
        # TODO: modifying return value from logic layer in view
        tul.task_id = task.id
        db.session.add(tul)
        db.session.commit()

        if 'next_url' in request.form:
            next_url = request.form['next_url']
        else:
            next_url = url_for('index')

        return redirect(next_url)

    @app.route('/task/<int:id>/mark_done')
    @login_required
    def task_done(id):
        task = ll.task_set_done(id, current_user)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/mark_undone')
    @login_required
    def task_undo(id):
        task = ll.task_unset_done(id, current_user)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/delete')
    @login_required
    def delete_task(id):
        task = ll.task_set_deleted(id, current_user)
        db.session.add(task)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/undelete')
    @login_required
    def undelete_task(id):
        task = ll.task_unset_deleted(id, current_user)
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
        accept = get_accept_type()
        if accept is None:
            return '', 406

        if accept == 'html':
            show_deleted = request.cookies.get('show_deleted')
            show_done = request.cookies.get('show_done')
            show_hierarchy = request.cookies.get('show_hierarchy', True)
            data = ll.get_task_data(id, current_user,
                                    include_deleted=show_deleted,
                                    include_done=show_done,
                                    show_hierarchy=show_hierarchy)

            return render_template('task.t.html', task=data['task'],
                                   descendants=data['descendants'],
                                   cycle=itertools.cycle,
                                   show_deleted=show_deleted,
                                   show_done=show_done,
                                   show_hierarchy=show_hierarchy)
        else:
            show_deleted = get_form_or_arg('show_deleted')
            show_done = get_form_or_arg('show_done')
            show_hierarchy = False
            data = ll.get_task_data(id, current_user,
                                    include_deleted=show_deleted,
                                    include_done=show_done,
                                    show_hierarchy=show_hierarchy)
            task = data['task']
            data = {
                'id': task.id,
                'summary': task.summary,
                'description': task.description,
                'is_done': task.is_done,
                'is_deleted': task.is_deleted,
                'order_num': task.order_num,
                'deadline': str_from_datetime(task.deadline),
                'parent_id': task.parent_id,
                'expected_duration_minutes':
                    task.expected_duration_minutes,
                'expected_cost': task.get_expected_cost_for_export(),
                'tags': [url_for('view_tag', id=ttl.tag_id)
                         for ttl in task.tags],
                'users': [url_for('view_user', user_id=tul.user_id)
                          for tul in task.users]}
            return json.dumps(data), 200

    @app.route('/note/new', methods=['POST'])
    @login_required
    def new_note():
        if 'task_id' not in request.form:
            return ('No task_id specified', 400)
        task_id = request.form['task_id']
        content = request.form['content']

        note = ll.create_new_note(task_id, content, current_user)

        db.session.add(note)
        db.session.commit()

        return redirect(url_for('view_task', id=task_id))

    @app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(id):

        def render_get_response():
            data = ll.get_edit_task_data(id, current_user)
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

        duration = int_from_str(request.form['expected_duration_minutes'])

        expected_cost = money_from_str(request.form['expected_cost'])

        task = ll.set_task(id, current_user, summary, description, deadline,
                           is_done, is_deleted, order_num, duration,
                           expected_cost, parent_id)

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

        att = ll.create_new_attachment(task_id, f, description, current_user)

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
        ll.do_move_task_up(id, show_deleted, current_user)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/top')
    @login_required
    def move_task_to_top(id):
        ll.do_move_task_to_top(id, current_user)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/down')
    @login_required
    def move_task_down(id):
        show_deleted = request.cookies.get('show_deleted')
        ll.do_move_task_down(id, show_deleted, current_user)
        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/bottom')
    @login_required
    def move_task_to_bottom(id):
        ll.do_move_task_to_bottom(id, current_user)
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

        ll.do_long_order_change(task_to_move_id, target_id, current_user)

        db.session.commit()

        return redirect(request.args.get('next') or url_for('index'))

    @app.route('/task/<int:id>/add_tag', methods=['GET', 'POST'])
    @login_required
    def add_tag_to_task(id):

        value = get_form_or_arg('value')
        if value is None or value == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=id)))

        ll.do_add_tag_to_task(id, value, current_user)
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

        ll.do_delete_tag_from_task(id, tag_id, current_user)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=id)))

    @app.route('/task/<int:task_id>/authorize_user', methods=['GET', 'POST'])
    @login_required
    def authorize_user_for_task(task_id):

        email = get_form_or_arg('email')
        if email is None or email == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=task_id)))

        ll.do_authorize_user_for_task_by_email(task_id, email, current_user)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/pick_user')
    def pick_user_to_authorize(task_id):
        task = ll.get_task(task_id, current_user)
        users = ll.get_users()
        return render_template('pick_user.t.html', task=task, users=users,
                               cycle=itertools.cycle)

    @app.route('/task/<int:task_id>/authorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    @login_required
    def authorize_picked_user_for_task(task_id, user_id):
        if user_id is None or user_id == '':
            return (redirect(request.args.get('next') or
                             url_for('view_task', id=task_id)))

        ll.do_authorize_user_for_task_by_id(task_id, user_id, current_user)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/deauthorize_user', methods=['GET', 'POST'],
               defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/',
               methods=['GET', 'POST'], defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    def deauthorize_user_for_task(task_id, user_id):
        if user_id is None:
            user_id = get_form_or_arg('user_id')

        ll.do_deauthorize_user_for_task(task_id, user_id, current_user)
        db.session.commit()

        return (redirect(request.args.get('next') or
                         url_for('view_task', id=task_id)))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.t.html')
        email = request.form['email']
        password = request.form['password']
        user = app.User.query.filter_by(email=email).first()

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

    @app.route('/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def list_users():

        if request.method == 'GET':
            accept = get_accept_type()
            if accept is None:
                return '', 406

            users = ll.get_users()
            if accept == 'html':
                return render_template('list_users.t.html', users=users,
                                       cycle=itertools.cycle)
            else:
                data = [{'href': url_for('view_user', user_id=user.id),
                         'id': user.id,
                         'email': user.email}
                        for user in users]
                return json.dumps(data), 200

        email = request.form['email']
        is_admin = False
        if 'is_admin' in request.form:
            is_admin = bool_from_str(request.form['is_admin'])

        ll.do_add_new_user(email, is_admin)
        db.session.commit()

        return redirect(url_for('list_users'))

    @app.route('/users/<int:user_id>', methods=['GET'])
    @login_required
    def view_user(user_id):
        accept = get_accept_type()
        if accept is None:
            return '', 406
        user = ll.do_get_user_data(user_id, current_user)
        if accept == 'html':
            return render_template('view_user.t.html', user=user)
        else:
            data = {'id': user.id,
                    'email': user.email,
                    'is_admin': user.is_admin}
            return json.dumps(data), 200

    @app.route('/show_hide_deleted')
    @login_required
    def show_hide_deleted():
        show_deleted = request.args.get('show_deleted')
        resp = make_response(
            redirect(request.args.get('next') or url_for('index')))
        if show_deleted and show_deleted != '0':
            resp.set_cookie('show_deleted', '1')
        else:
            resp.set_cookie('show_deleted', '')
        return resp

    @app.route('/show_hide_done')
    @login_required
    def show_hide_done():
        show_done = request.args.get('show_done')
        resp = make_response(
            redirect(request.args.get('next') or url_for('index')))
        if show_done and show_done != '0':
            resp.set_cookie('show_done', '1')
        else:
            resp.set_cookie('show_done', '')
        return resp

    @app.route('/show_hide_hierarchy')
    @login_required
    def show_hide_hierarchy():
        show_hierarchy = request.args.get('show_hierarchy')
        resp = make_response(
            redirect(request.args.get('next') or url_for('index')))
        if show_hierarchy and show_hierarchy != '0':
            resp.set_cookie('show_hierarchy', '1')
        else:
            resp.set_cookie('show_hierarchy', '')
        return resp

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
        data = ll.get_tag_data(id, current_user)
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

        task = ll.get_task(id, current_user)
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
