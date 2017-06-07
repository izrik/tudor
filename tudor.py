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
from view_layer import ViewLayer
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

        @staticmethod
        def get_author():
            return Options.get('author', 'the author')

        @staticmethod
        def get_user():
            return current_user

    app.Task = ds.Task
    app.Tag = ds.Tag
    app.Note = ds.Note
    app.Attachment = ds.Attachment
    app.User = ds.User
    app.Option = ds.Option

    ll = LogicLayer(ds, upload_folder, allowed_extensions)
    app.ll = ll
    app._convert_task_to_tag = ll._convert_task_to_tag

    vl = ViewLayer(ll, db, app, upload_folder)
    app.vl = vl

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

    def get_form_or_arg(name):
        if name in request.form:
            return request.form[name]
        return request.args.get(name)

    # View Functions

    @app.route('/')
    @login_required
    def index():
        return vl.index(request, current_user)

    @app.route('/hierarchy')
    @login_required
    def hierarchy():
        return vl.hierarchy(request, current_user)

    @app.route('/deadlines')
    @login_required
    def deadlines():
        return vl.deadlines(request, current_user)

    @app.route('/task/new', methods=['GET'])
    @login_required
    def get_new_task():
        return vl.task_new_get(request, current_user)

    @app.route('/task/new', methods=['POST'])
    @login_required
    def new_task():
        return vl.task_new_post(request, current_user)

    @app.route('/task/<int:id>/mark_done')
    @login_required
    def task_done(id):
        return vl.task_mark_done(request, current_user, id)

    @app.route('/task/<int:id>/mark_undone')
    @login_required
    def task_undo(id):
        return vl.task_mark_undone(request, current_user, id)

    @app.route('/task/<int:id>/delete')
    @login_required
    def delete_task(id):
        return vl.task_delete(request, current_user, id)

    @app.route('/task/<int:id>/undelete')
    @login_required
    def undelete_task(id):
        return vl.task_undelete(request, current_user, id)

    @app.route('/task/<int:id>/purge')
    @login_required
    @admin_required
    def purge_task(id):
        return vl.task_purge(request, current_user, id)

    @app.route('/purge_all')
    @login_required
    @admin_required
    def purge_deleted_tasks():
        return vl.purge_all(request, current_user)

    @app.route('/task/<int:id>')
    @login_required
    def view_task(id):
        return vl.task(request, current_user, id)

    @app.route('/task/<int:id>/hierarchy')
    @login_required
    def view_task_hierarchy(id):
        return vl.task_hierarchy(request, current_user, id)

    @app.route('/note/new', methods=['POST'])
    @login_required
    def new_note():
        return vl.note_new_post(request, current_user)

    @app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(id):
        return vl.task_edit(request, current_user, id)

    @app.route('/attachment/new', methods=['POST'])
    @login_required
    def new_attachment():
        return vl.attachment_new(request, current_user)

    @app.route('/attachment/<int:aid>', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/<path:x>')
    @login_required
    def get_attachment(aid, x):
        return vl.attachment(request, current_user, aid, x)

    @app.route('/task/<int:id>/up')
    @login_required
    def move_task_up(id):
        return vl.task_up(request, current_user, id)

    @app.route('/task/<int:id>/top')
    @login_required
    def move_task_to_top(id):
        return vl.task_top(request, current_user, id)

    @app.route('/task/<int:id>/down')
    @login_required
    def move_task_down(id):
        return vl.task_down(request, current_user, id)

    @app.route('/task/<int:id>/bottom')
    @login_required
    def move_task_to_bottom(id):
        return vl.task_bottom(request, current_user, id)

    @app.route('/long_order_change', methods=['POST'])
    @login_required
    def long_order_change():
        return vl.long_order_change(request, current_user)

    @app.route('/task/<int:id>/add_tag', methods=['GET', 'POST'])
    @login_required
    def add_tag_to_task(id):
        return vl.task_add_tag(request, current_user, id)

    @app.route('/task/<int:id>/delete_tag', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/<tag_id>', methods=['GET', 'POST'])
    @login_required
    def delete_tag_from_task(id, tag_id):
        return vl.task_delete_tag(request, current_user, id, tag_id)

    @app.route('/task/<int:task_id>/authorize_user', methods=['GET', 'POST'])
    @login_required
    def authorize_user_for_task(task_id):
        return vl.task_authorize_user(request, current_user, task_id)

    @app.route('/task/<int:task_id>/pick_user')
    def pick_user_to_authorize(task_id):
        return vl.task_pick_user(request, current_user, task_id)

    @app.route('/task/<int:task_id>/authorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    @login_required
    def authorize_picked_user_for_task(task_id, user_id):
        return vl.task_authorize_user_user(request, current_user, task_id,
                                           user_id)

    @app.route('/task/<int:task_id>/deauthorize_user', methods=['GET', 'POST'],
               defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/',
               methods=['GET', 'POST'], defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    def deauthorize_user_for_task(task_id, user_id):
        return vl.task_deauthorize_user(request, current_user, task_id,
                                        user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return vl.login(request, current_user)

    @app.route('/logout')
    def logout():
        return vl.logout(request, current_user)

    @app.route('/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def list_users():
        return vl.users(request, current_user)

    @app.route('/users/<int:user_id>', methods=['GET'])
    @login_required
    def view_user(user_id):
        return vl.users_user_get(request, current_user, user_id)

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
        ll.do_reset_order_nums(current_user)
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
            tasks = ll.get_task_crud_data(current_user)
            return render_template('task_crud.t.html', tasks=tasks,
                                   cycle=itertools.cycle)

        crud_data = {}
        for key in request.form.keys():
            if re.match(r'task_\d+_(summary|deadline|is_done|is_deleted|'
                        r'order_num|duration|cost|parent_id)', key):
                crud_data[key] = request.form[key]

        ll.do_submit_task_crud(crud_data, current_user)
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

            tag = ll._convert_task_to_tag(id, current_user)

            return redirect(
                request.args.get('next') or url_for('view_tag', id=tag.id))

        task = ll.get_task(id, current_user)
        return render_template('convert_task_to_tag.t.html',
                               task_id=task.id,
                               tag_value=task.summary,
                               tag_description=task.description,
                               cycle=itertools.cycle,
                               tasks=task.children)

    @app.route('/search', methods=['GET', 'POST'],
               defaults={'search_query': None})
    @app.route('/search/', methods=['GET', 'POST'],
               defaults={'search_query': None})
    @app.route('/search/<query>', methods=['GET'])
    @login_required
    def search(search_query):
        if search_query is None and request.method == 'POST':
            search_query = request.form['query']

        results = ll.search(search_query, current_user)

        return render_template('search.t.html', query=search_query,
                               results=results)

    @app.route('/task/<int:task_id>/add_dependee', methods=['GET', 'POST'],
               defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/add_dependee/', methods=['GET', 'POST'],
               defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/add_dependee/<int:dependee_id>',
               methods=['GET', 'POST'])
    @login_required
    def add_dependee_to_task(task_id, dependee_id):
        if dependee_id is None or dependee_id == '':
            dependee_id = get_form_or_arg('dependee_id')
        if dependee_id is None or dependee_id == '':
            return (redirect(request.args.get('next') or
                             request.args.get('next_url') or
                             url_for('view_task', id=task_id)))

        ll.do_add_dependee_to_task(task_id, dependee_id, current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/remove_dependee',
               methods=['GET', 'POST'], defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/remove_dependee/',
               methods=['GET', 'POST'], defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/remove_dependee/<int:dependee_id>',
               methods=['GET', 'POST'])
    def remove_dependee_from_task(task_id, dependee_id):
        if dependee_id is None:
            dependee_id = get_form_or_arg('dependee_id')

        ll.do_remove_dependee_from_task(task_id, dependee_id, current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/add_dependant', methods=['GET', 'POST'],
               defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/add_dependant/', methods=['GET', 'POST'],
               defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/add_dependant/<int:dependant_id>',
               methods=['GET', 'POST'])
    @login_required
    def add_dependant_to_task(task_id, dependant_id):
        if dependant_id is None or dependant_id == '':
            dependant_id = get_form_or_arg('dependant_id')
        if dependant_id is None or dependant_id == '':
            return (redirect(request.args.get('next') or
                             request.args.get('next_url') or
                             url_for('view_task', id=task_id)))

        ll.do_add_dependant_to_task(task_id, dependant_id, current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/remove_dependant',
               methods=['GET', 'POST'], defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/remove_dependant/',
               methods=['GET', 'POST'], defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/remove_dependant/<int:dependant_id>',
               methods=['GET', 'POST'])
    def remove_dependant_from_task(task_id, dependant_id):
        if dependant_id is None:
            dependant_id = get_form_or_arg('dependant_id')

        ll.do_remove_dependant_from_task(task_id, dependant_id, current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/add_prioritize_before',
               methods=['GET', 'POST'],
               defaults={'prioritize_before_id': None})
    @app.route('/task/<int:task_id>/add_prioritize_before/',
               methods=['GET', 'POST'],
               defaults={'prioritize_before_id': None})
    @app.route(
        '/task/<int:task_id>/add_prioritize_before/<int:prioritize_before_id>',
        methods=['GET', 'POST'])
    @login_required
    def add_prioritize_before_to_task(task_id, prioritize_before_id):
        if prioritize_before_id is None or prioritize_before_id == '':
            prioritize_before_id = get_form_or_arg('prioritize_before_id')
        if prioritize_before_id is None or prioritize_before_id == '':
            return (redirect(request.args.get('next') or
                             request.args.get('next_url') or
                             url_for('view_task', id=task_id)))

        ll.do_add_prioritize_before_to_task(task_id, prioritize_before_id,
                                            current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/remove_prioritize_before',
               methods=['GET', 'POST'],
               defaults={'prioritize_before_id': None})
    @app.route('/task/<int:task_id>/remove_prioritize_before/',
               methods=['GET', 'POST'],
               defaults={'prioritize_before_id': None})
    @app.route(
        '/task/<int:task_id>/remove_prioritize_before/'
        '<int:prioritize_before_id>',
        methods=['GET', 'POST'])
    def remove_prioritize_before_from_task(task_id, prioritize_before_id):
        if prioritize_before_id is None:
            prioritize_before_id = get_form_or_arg('prioritize_before_id')

        ll.do_remove_prioritize_before_from_task(task_id, prioritize_before_id,
                                                 current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/add_prioritize_after',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route('/task/<int:task_id>/add_prioritize_after/',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route(
        '/task/<int:task_id>/add_prioritize_after/<int:prioritize_after_id>',
        methods=['GET', 'POST'])
    @login_required
    def add_prioritize_after_to_task(task_id, prioritize_after_id):
        if prioritize_after_id is None or prioritize_after_id == '':
            prioritize_after_id = get_form_or_arg('prioritize_after_id')
        if prioritize_after_id is None or prioritize_after_id == '':
            return (redirect(request.args.get('next') or
                             request.args.get('next_url') or
                             url_for('view_task', id=task_id)))

        ll.do_add_prioritize_after_to_task(task_id, prioritize_after_id,
                                           current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

    @app.route('/task/<int:task_id>/remove_prioritize_after',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route('/task/<int:task_id>/remove_prioritize_after/',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route(
        '/task/<int:task_id>/remove_prioritize_after/'
        '<int:prioritize_after_id>',
        methods=['GET', 'POST'])
    def remove_prioritize_after_from_task(task_id, prioritize_after_id):
        if prioritize_after_id is None:
            prioritize_after_id = get_form_or_arg('prioritize_after_id')

        ll.do_remove_prioritize_after_from_task(task_id, prioritize_after_id,
                                                current_user)
        db.session.commit()

        return (redirect(
            request.args.get('next') or
            request.args.get('next_url') or
            url_for('view_task', id=task_id)))

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
