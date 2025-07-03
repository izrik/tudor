#!/usr/bin/env python3
import argparse
import base64
import random
import sys
import traceback
from functools import wraps
from os import environ

from datetime import datetime
from flask import Flask, request
from flask import Markup
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import pycmarkgfm

from conversions import bool_from_str, int_from_str
from logic.layer import LogicLayer
from persistence.migration import auto_migrate
from persistence.sqlalchemy.layer import SqlAlchemyPersistenceLayer
from view.layer import ViewLayer

__version__ = '0.9'
try:
    import git

    try:
        __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                                  always=True, abbrev=40)
    except git.InvalidGitRepositoryError:
        __revision__ = 'unknown'
except ImportError:
    __revision__ = 'unknown'

DEFAULT_TUDOR_DEBUG = False
DEFAULT_TUDOR_HOST = '127.0.0.1'
DEFAULT_TUDOR_PORT = 8304
DEFAULT_TUDOR_DB_URI = 'sqlite:////tmp/test.db'
DEFAULT_TUDOR_UPLOAD_FOLDER = '/tmp/tudor/uploads'
DEFAULT_TUDOR_ALLOWED_EXTENSIONS = 'txt,pdf,png,jpg,jpeg,gif'
DEFAULT_TUDOR_SECRET_KEY = None


class Config(object):
    def __init__(self,
                 debug=None,
                 host=None,
                 port=None,
                 db_uri=None,
                 db_uri_file=None,
                 db_options=None,
                 db_options_file=None,
                 upload_folder=None,
                 allowed_extensions=None,
                 secret_key=None,
                 secret_key_file=None,
                 args=None):
        self.DEBUG = debug
        self.HOST = host
        self.PORT = port
        self.DB_URI = db_uri
        self.DB_URI_FILE = db_uri_file
        self.DB_OPTIONS = db_options
        self.DB_OPTIONS_FILE = db_options_file
        self.UPLOAD_FOLDER = upload_folder
        self.ALLOWED_EXTENSIONS = allowed_extensions  # TODO: remove this
        self.SECRET_KEY = secret_key
        self.SECRET_KEY_FILE = secret_key_file
        self.args = args

    def __repr__(self):
        return f'Config({str(self)})'

    def __str__(self):
        return (f'DEBUG: {self.DEBUG}, '
                f'HOST: {self.HOST}, '
                f'PORT: {self.PORT}, '
                f'DB_URI: {self.DB_URI}, '
                f'DB_URI_FILE: {self.DB_URI_FILE}, '
                f'DB_OPTIONS: {self.DB_OPTIONS}, '
                f'DB_OPTIONS_FILE: {self.DB_OPTIONS_FILE}, '
                f'UPLOAD_FOLDER: {self.UPLOAD_FOLDER}, '
                f'ALLOWED_EXTENSIONS: {self.ALLOWED_EXTENSIONS}, '
                f'SECRET_KEY: {self.SECRET_KEY}, '
                f'SECRET_KEY_FILE: {self.SECRET_KEY_FILE}, '
                f'args: {self.args}')

    @staticmethod
    def from_environ():
        debug = environ.get('TUDOR_DEBUG')
        if debug is not None:
            debug = bool_from_str(debug)
        return Config(
            debug=debug,
            host=environ.get('TUDOR_HOST'),
            port=int_from_str(environ.get('TUDOR_PORT')),
            db_uri=environ.get('TUDOR_DB_URI'),
            db_uri_file=environ.get('TUDOR_DB_URI_FILE'),
            db_options=environ.get('TUDOR_DB_OPTIONS'),
            db_options_file=environ.get('TUDOR_DB_OPTIONS_FILE'),
            upload_folder=environ.get('TUDOR_UPLOAD_FOLDER'),
            allowed_extensions=environ.get('TUDOR_ALLOWED_EXTENSIONS'),
            secret_key=environ.get('TUDOR_SECRET_KEY'),
            secret_key_file=environ.get('TUDOR_SECRET_KEY_FILE'))

    @staticmethod
    def from_defaults():
        return Config(
            debug=DEFAULT_TUDOR_DEBUG,
            host=DEFAULT_TUDOR_HOST,
            port=DEFAULT_TUDOR_PORT,
            db_uri=DEFAULT_TUDOR_DB_URI,
            upload_folder=DEFAULT_TUDOR_UPLOAD_FOLDER,
            allowed_extensions=DEFAULT_TUDOR_ALLOWED_EXTENSIONS,
            secret_key=DEFAULT_TUDOR_SECRET_KEY)

    @classmethod
    def combine(cls, first, second):
        if first is None:
            return second
        if second is None:
            return first

        def ifn(a, b):
            if a is not None:
                return a
            return b

        return Config(
            debug=ifn(first.DEBUG, second.DEBUG),
            host=ifn(first.HOST, second.HOST),
            port=ifn(first.PORT, second.PORT),
            db_uri=ifn(first.DB_URI, second.DB_URI),
            db_uri_file=ifn(first.DB_URI_FILE, second.DB_URI_FILE),
            db_options=ifn(first.DB_OPTIONS, second.DB_OPTIONS),
            db_options_file=ifn(first.DB_OPTIONS_FILE,
                                second.DB_OPTIONS_FILE),
            upload_folder=ifn(first.UPLOAD_FOLDER, second.UPLOAD_FOLDER),
            allowed_extensions=ifn(first.ALLOWED_EXTENSIONS,
                                   second.ALLOWED_EXTENSIONS),
            secret_key=ifn(first.SECRET_KEY, second.SECRET_KEY),
            secret_key_file=ifn(first.SECRET_KEY_FILE,
                                second.SECRET_KEY_FILE),
            args=ifn(first.args, second.args))


class ConfigError(Exception):
    pass


def get_config_from_command_line(argv, defaults=None):
    if defaults is None:
        defaults = Config.from_environ()

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--host', action='store')
    parser.add_argument('--port', action='store', type=int)
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--db-uri', action='store')
    parser.add_argument('--db-uri-file', action='store', default=None)
    parser.add_argument('--db-options', action='store')
    parser.add_argument('--db-options-file', action='store', default=None)
    parser.add_argument('--upload-folder', action='store')
    parser.add_argument('--allowed-extensions', action='store')
    parser.add_argument('--secret-key', action='store')
    parser.add_argument('--secret-key-file', action='store')
    parser.add_argument('--create-secret-key', action='store_true')
    parser.add_argument('--hash-password', action='store')
    parser.add_argument('--make-public', metavar='TASK_ID', action='store',
                        help='Make a given task public, viewable by anyone.',
                        type=int)
    parser.add_argument('--make-private', metavar='TASK_ID', action='store',
                        help='Make a given task private, viewable only by '
                             'authorized users of that task who are logged '
                             'in.',
                        type=int)
    parser.add_argument('--descendants', action='store_true',
                        help='When performing an operation on a given task, '
                             'also traverse all descendants and perform the '
                             'operation on them as well.')
    parser.add_argument('--test-db-conn', action='store_true',
                        help='Try to make a connection to the database. '
                             'Useful for diagnosing connection problems.')
    parser.add_argument('--create-user', action='store', nargs='*',
                        help='Create a user in the database. Can optionally '
                             'be made an admin.')
    parser.add_argument('--export-db', action='store_true',
                        help='Export the contents of the database in json '
                             'format to stdout.')
    parser.add_argument('--import-db', action='store_true',
                        help='Read json formatted items from stdin and '
                             'insert them into the database. Reverse of '
                             '"import".')

    args = parser.parse_args(args=argv)

    arg_config = Config(
        debug=args.debug if args.debug else None,
        host=args.host,
        port=args.port,
        db_uri=args.db_uri,
        db_uri_file=args.db_uri_file,
        db_options=args.db_options,
        db_options_file=args.db_options_file,
        upload_folder=args.upload_folder,
        secret_key=args.secret_key,
        secret_key_file=args.secret_key_file,
        allowed_extensions=args.allowed_extensions,
        args=args)

    config = Config.combine(arg_config, defaults)

    return config


def split_db_options(db_options):
    if db_options is None or db_options == '':
        return {}
    import re
    rv = {}
    for opt in re.split(r'\s+', db_options):
        opt = opt.strip()
        if not opt:
            continue
        k, v = opt.split('=', maxsplit=1)
        rv[k.strip()] = v.strip()
    return rv


def generate_app(db_uri=None,
                 db_options=None,
                 upload_folder=None,
                 secret_key=None,
                 allowed_extensions=None,
                 ll=None, vl=None, pl=None, flask_configs=None,
                 disable_admin_check=False):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if flask_configs:
        for k, v in flask_configs.items():
            app.config[k] = v
    app.secret_key = secret_key
    # ALLOWED_EXTENSIONS = set(ext for ext in re.split('[\s,]+',
    #                                                  allowed_extensions)
    #                          if ext is not None and ext != '')

    login_manager = LoginManager()
    login_manager.init_app(app)
    app.login_manager = login_manager
    login_manager.login_view = 'login'

    bcrypt = Bcrypt(app)
    app.bcrypt = bcrypt

    if pl is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

        opts = split_db_options(db_options)
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = opts

        db = SQLAlchemy(app)
        pl = SqlAlchemyPersistenceLayer(db)
    app.pl = pl

    class Options(object):
        @staticmethod
        def get(key, default_value=None):
            option = pl.get_option(key)
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
        def get_version():
            return __version__

        @staticmethod
        def get_author():
            return Options.get('author', 'the author')

        @staticmethod
        def get_user():
            if current_user is None:
                return pl.get_guest_user()

            try:
                user_id = current_user.id
                return pl.get_user(user_id)
            except AttributeError:
                return pl.get_guest_user()

    app.Options = Options

    if ll is None:
        ll = LogicLayer(upload_folder, allowed_extensions, pl)
    app.ll = ll

    if vl is None:
        vl = ViewLayer(ll, app.bcrypt)
    app.vl = vl

    # Flask setup functions

    @login_manager.user_loader
    def load_user(userid):
        return pl.get_user_by_email(userid)

    @login_manager.request_loader
    def load_user_with_basic_auth(request):
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            api_key = base64.b64decode(api_key).decode('utf-8')
            email, password = api_key.split(':', 1)
            user = pl.get_user_by_email(email)

            if user is None:
                return None
            if user.hashed_password is None or user.hashed_password == '':
                return None
            if not bcrypt.check_password_hash(user.hashed_password, password):
                return None

            return user

    def admin_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not disable_admin_check and not current_user.is_admin:
                return ('You are not authorized to view this page', 403)
            return func(*args, **kwargs)

        return decorated_view

    @app.context_processor
    def setup_options():
        return {'opts': Options}

    # Error pages

    @app.errorhandler(404)
    def handle_not_found(e):
        from flask import render_template
        return render_template('error_404_not_found.html'), 404

    @app.errorhandler(401)
    def handle_not_found(e):
        from flask import render_template
        return render_template('error_401_unauthorized.html'), 401

    # View Functions

    @login_required
    def index():
        return vl.index(request, Options.get_user())

    @login_required
    def hierarchy():
        return vl.hierarchy(request, Options.get_user())

    @login_required
    def deadlines():
        return vl.deadlines(request, Options.get_user())

    @login_required
    def get_new_task():
        return vl.task_new_get(request, Options.get_user())

    @login_required
    def new_task():
        return vl.task_new_post(request, Options.get_user())

    @login_required
    def task_done(id):
        return vl.task_mark_done(request, Options.get_user(), id)

    @login_required
    def task_undo(id):
        return vl.task_mark_undone(request, Options.get_user(), id)

    @login_required
    def delete_task(id):
        return vl.task_delete(request, Options.get_user(), id)

    @login_required
    def undelete_task(id):
        return vl.task_undelete(request, Options.get_user(), id)

    @login_required
    @admin_required
    def purge_task(id):
        return vl.task_purge(request, Options.get_user(), id)

    @login_required
    @admin_required
    def purge_deleted_tasks():
        return vl.purge_all(request, Options.get_user())

    def view_task(id):
        return vl.task(request, Options.get_user(), id)

    def clone_task(id):
        return vl.task_clone(request, Options.get_user(), id)

    def view_task_hierarchy(id):
        return vl.task_hierarchy(request, Options.get_user(), id)

    @login_required
    def new_note():
        return vl.note_new_post(request, Options.get_user())

    @login_required
    def edit_task(id):
        return vl.task_edit(request, Options.get_user(), id)

    @login_required
    def new_attachment():
        return vl.attachment_new(request, Options.get_user(),
                                 timestamp=datetime.utcnow())

    @login_required
    def get_attachment(aid, x):
        return vl.attachment(request, Options.get_user(), aid, x)

    @login_required
    def move_task_up(id):
        return vl.task_up(request, Options.get_user(), id)

    @login_required
    def move_task_to_top(id):
        return vl.task_top(request, Options.get_user(), id)

    @login_required
    def move_task_down(id):
        return vl.task_down(request, Options.get_user(), id)

    @login_required
    def move_task_to_bottom(id):
        return vl.task_bottom(request, Options.get_user(), id)

    @login_required
    def long_order_change():
        return vl.long_order_change(request, Options.get_user())

    @login_required
    def add_tag_to_task(id):
        return vl.task_add_tag(request, Options.get_user(), id)

    @login_required
    def delete_tag_from_task(id, tag_id):
        return vl.task_delete_tag(request, Options.get_user(), id, tag_id)

    @login_required
    def authorize_user_for_task(task_id):
        return vl.task_authorize_user(request, Options.get_user(), task_id)

    @login_required
    def pick_user_to_authorize(task_id):
        return vl.task_pick_user(request, Options.get_user(), task_id)

    @login_required
    def authorize_picked_user_for_task(task_id, user_id):
        return vl.task_authorize_user_user(request, Options.get_user(),
                                           task_id, user_id)

    @login_required
    def deauthorize_user_for_task(task_id, user_id):
        return vl.task_deauthorize_user(request, Options.get_user(), task_id,
                                        user_id)

    def login():
        return vl.login(request, Options.get_user())

    def logout():
        return vl.logout(request, Options.get_user())

    @login_required
    @admin_required
    def list_users():
        return vl.users(request, Options.get_user())

    @login_required
    def view_user(user_id):
        return vl.users_user_get(request, Options.get_user(), user_id)

    @login_required
    def show_hide_deleted():
        return vl.show_hide_deleted(request, Options.get_user())

    @login_required
    def show_hide_done():
        return vl.show_hide_done(request, Options.get_user())

    @login_required
    @admin_required
    def view_options():
        return vl.options(request, Options.get_user())

    @login_required
    @admin_required
    def delete_option(key):
        return vl.option_delete(request, Options.get_user(), key)

    @login_required
    def reset_order_nums():
        return vl.reset_order_nums(request, Options.get_user())

    @login_required
    @admin_required
    def export_data():
        return vl.export(request, Options.get_user())

    @login_required
    @admin_required
    def import_data():
        return vl.import_(request, Options.get_user())

    @login_required
    @admin_required
    def task_crud():
        return vl.task_crud(request, Options.get_user())

    @login_required
    def list_tags():
        return vl.tags(request, Options.get_user())

    @login_required
    def view_tag(id):
        return vl.tags_id_get(request, Options.get_user(), id)

    @login_required
    def edit_tag(id):
        return vl.tags_id_edit(request, Options.get_user(), id)

    @login_required
    def convert_task_to_tag(id):
        return vl.task_id_convert_to_tag(request, Options.get_user(), id)

    @login_required
    def search(search_query):
        return vl.search(request, Options.get_user(), search_query)

    @login_required
    def add_dependee_to_task(task_id, dependee_id):
        return vl.task_id_add_dependee(request, Options.get_user(), task_id,
                                       dependee_id)

    @login_required
    def remove_dependee_from_task(task_id, dependee_id):
        return vl.task_id_remove_dependee(request, Options.get_user(), task_id,
                                          dependee_id)

    @login_required
    def add_dependant_to_task(task_id, dependant_id):
        return vl.task_id_add_dependant(request, Options.get_user(), task_id,
                                        dependant_id)

    @login_required
    def remove_dependant_from_task(task_id, dependant_id):
        return vl.task_id_remove_dependant(request, Options.get_user(),
                                           task_id, dependant_id)

    @login_required
    def add_prioritize_before_to_task(task_id, prioritize_before_id):
        return vl.task_id_add_prioritize_before(request, Options.get_user(),
                                                task_id, prioritize_before_id)

    @login_required
    def remove_prioritize_before_from_task(task_id, prioritize_before_id):
        return vl.task_id_remove_prioritize_before(request, Options.get_user(),
                                                   task_id,
                                                   prioritize_before_id)

    @login_required
    def add_prioritize_after_to_task(task_id, prioritize_after_id):
        return vl.task_id_add_prioritize_after(request, Options.get_user(),
                                               task_id, prioritize_after_id)

    @login_required
    def remove_prioritize_after_from_task(task_id, prioritize_after_id):
        return vl.task_id_remove_prioritize_after(request, Options.get_user(),
                                                  task_id, prioritize_after_id)

    @app.template_filter(name='gfm')
    def render_gfm(s):
        output = pycmarkgfm.gfm_to_html(s)
        moutput = Markup(output)
        return moutput

    app.add_url_rule('/', None, index)
    app.add_url_rule('/hierarchy', None, hierarchy)
    app.add_url_rule('/deadlines', None, deadlines)
    app.add_url_rule('/task/new', None, get_new_task, methods=['GET'])
    app.add_url_rule('/task/new', None, new_task, methods=['POST'])
    app.add_url_rule('/task/<int:id>/mark_done', None, task_done)
    app.add_url_rule('/task/<int:id>/mark_undone', None, task_undo)
    app.add_url_rule('/task/<int:id>/delete', None, delete_task)
    app.add_url_rule('/task/<int:id>/undelete', None, undelete_task)
    app.add_url_rule('/task/<int:id>/purge', None, purge_task)
    app.add_url_rule('/purge_all', None, purge_deleted_tasks)
    app.add_url_rule('/task/<int:id>', None, view_task)
    app.add_url_rule('/task/<int:id>/hierarchy', None, view_task_hierarchy)
    app.add_url_rule('/note/new', None, new_note, methods=['POST'])
    app.add_url_rule('/task/<int:id>/edit', None, edit_task,
                     methods=['GET', 'POST'])
    app.add_url_rule('/attachment/new', None, new_attachment,
                     methods=['POST'])
    app.add_url_rule('/attachment/<int:aid>', None, get_attachment,
                     defaults={'x': 'x'})
    app.add_url_rule('/attachment/<int:aid>/', None, get_attachment,
                     defaults={'x': 'x'})
    app.add_url_rule('/attachment/<int:aid>/<path:x>', None, get_attachment)
    app.add_url_rule('/task/<int:id>/up', None, move_task_up)
    app.add_url_rule('/task/<int:id>/top', None, move_task_to_top)
    app.add_url_rule('/task/<int:id>/down', None, move_task_down)
    app.add_url_rule('/task/<int:id>/bottom', None, move_task_to_bottom)
    app.add_url_rule('/long_order_change', None, long_order_change,
                     methods=['POST'])
    app.add_url_rule('/task/<int:id>/add_tag', None, add_tag_to_task,
                     methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:id>/delete_tag', None, delete_tag_from_task,
                     methods=['GET', 'POST'], defaults={'tag_id': None})
    app.add_url_rule('/task/<int:id>/delete_tag/', None, delete_tag_from_task,
                     methods=['GET', 'POST'], defaults={'tag_id': None})
    app.add_url_rule('/task/<int:id>/delete_tag/<tag_id>', None,
                     delete_tag_from_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/authorize_user', None,
                     authorize_user_for_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/pick_user', None,
                     pick_user_to_authorize)
    app.add_url_rule('/task/<int:task_id>/authorize_user/<int:user_id>', None,
                     authorize_picked_user_for_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/deauthorize_user', None,
                     deauthorize_user_for_task, methods=['GET', 'POST'],
                     defaults={'user_id': None})
    app.add_url_rule('/task/<int:task_id>/deauthorize_user/', None,
                     deauthorize_user_for_task, methods=['GET', 'POST'],
                     defaults={'user_id': None})
    app.add_url_rule('/task/<int:task_id>/deauthorize_user/<int:user_id>',
                     None, deauthorize_user_for_task, methods=['GET', 'POST'])
    app.add_url_rule('/login', None, login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', None, logout)
    app.add_url_rule('/users', None, list_users, methods=['GET', 'POST'])
    app.add_url_rule('/users/<int:user_id>', None, view_user, methods=['GET'])
    app.add_url_rule('/show_hide_deleted', None, show_hide_deleted)
    app.add_url_rule('/show_hide_done', None, show_hide_done)
    app.add_url_rule('/options', None, view_options, methods=['GET', 'POST'])
    app.add_url_rule('/option/<path:key>/delete', None, delete_option)
    app.add_url_rule('/reset_order_nums', None, reset_order_nums)
    app.add_url_rule('/export', None, export_data, methods=['GET', 'POST'])
    app.add_url_rule('/import', None, import_data, methods=['GET', 'POST'])
    app.add_url_rule('/task_crud', None, task_crud, methods=['GET', 'POST'])
    app.add_url_rule('/tags', None, list_tags)
    app.add_url_rule('/tags/', None, list_tags)
    app.add_url_rule('/tags/<int:id>', None, view_tag)
    app.add_url_rule('/tags/<int:id>/edit', None, edit_tag,
                     methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:id>/convert_to_tag', None,
                     convert_task_to_tag)
    app.add_url_rule('/search', None, search, methods=['GET', 'POST'],
                     defaults={'search_query': None})
    app.add_url_rule('/search/', None, search, methods=['GET', 'POST'],
                     defaults={'search_query': None})
    app.add_url_rule('/search/<search_query>', None, search, methods=['GET'])
    app.add_url_rule('/task/<int:task_id>/add_dependee', None,
                     add_dependee_to_task, methods=['GET', 'POST'],
                     defaults={'dependee_id': None})
    app.add_url_rule('/task/<int:task_id>/add_dependee/', None,
                     add_dependee_to_task, methods=['GET', 'POST'],
                     defaults={'dependee_id': None})
    app.add_url_rule('/task/<int:task_id>/add_dependee/<int:dependee_id>',
                     None, add_dependee_to_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/remove_dependee', None,
                     remove_dependee_from_task, methods=['GET', 'POST'],
                     defaults={'dependee_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_dependee/', None,
                     remove_dependee_from_task, methods=['GET', 'POST'],
                     defaults={'dependee_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_dependee/<int:dependee_id>',
                     None, remove_dependee_from_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/add_dependant', None,
                     add_dependant_to_task, methods=['GET', 'POST'],
                     defaults={'dependant_id': None})
    app.add_url_rule('/task/<int:task_id>/add_dependant/', None,
                     add_dependant_to_task, methods=['GET', 'POST'],
                     defaults={'dependant_id': None})
    app.add_url_rule('/task/<int:task_id>/add_dependant/<int:dependant_id>',
                     None, add_dependant_to_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/remove_dependant', None,
                     remove_dependant_from_task, methods=['GET', 'POST'],
                     defaults={'dependant_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_dependant/', None,
                     remove_dependant_from_task, methods=['GET', 'POST'],
                     defaults={'dependant_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_dependant/<int:dependant_id>',
                     None, remove_dependant_from_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/add_prioritize_before', None,
                     add_prioritize_before_to_task, methods=['GET', 'POST'],
                     defaults={'prioritize_before_id': None})
    app.add_url_rule('/task/<int:task_id>/add_prioritize_before/', None,
                     add_prioritize_before_to_task, methods=['GET', 'POST'],
                     defaults={'prioritize_before_id': None})
    app.add_url_rule(
        '/task/<int:task_id>/add_prioritize_before/<int:prioritize_before_id>',
        None, add_prioritize_before_to_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/remove_prioritize_before', None,
                     remove_prioritize_before_from_task,
                     methods=['GET', 'POST'],
                     defaults={'prioritize_before_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_prioritize_before/', None,
                     remove_prioritize_before_from_task,
                     methods=['GET', 'POST'],
                     defaults={'prioritize_before_id': None})
    app.add_url_rule(
        '/task/<int:task_id>/remove_prioritize_before/'
        '<int:prioritize_before_id>',
        None, remove_prioritize_before_from_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/add_prioritize_after', None,
                     add_prioritize_after_to_task, methods=['GET', 'POST'],
                     defaults={'prioritize_after_id': None})
    app.add_url_rule('/task/<int:task_id>/add_prioritize_after/', None,
                     add_prioritize_after_to_task, methods=['GET', 'POST'],
                     defaults={'prioritize_after_id': None})
    app.add_url_rule(
        '/task/<int:task_id>/add_prioritize_after/<int:prioritize_after_id>',
        None, add_prioritize_after_to_task, methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:task_id>/remove_prioritize_after', None,
                     remove_prioritize_after_from_task,
                     methods=['GET', 'POST'],
                     defaults={'prioritize_after_id': None})
    app.add_url_rule('/task/<int:task_id>/remove_prioritize_after/', None,
                     remove_prioritize_after_from_task,
                     methods=['GET', 'POST'],
                     defaults={'prioritize_after_id': None})
    app.add_url_rule(
        '/task/<int:task_id>/remove_prioritize_after/'
        '<int:prioritize_after_id>', None, remove_prioritize_after_from_task,
        methods=['GET', 'POST'])
    app.add_url_rule('/task/<int:id>/clone', None, clone_task)

    return app


def default_printer(*args):
    print(args)


def make_task_public(pl, task_id, printer=default_printer, descendants=False):
    task = pl.get_task(task_id)
    if not task:
        printer('No task found by the id "{}"'.format(task_id))
    else:
        if descendants:
            def recurse(task):
                task.is_public = True
                printer(
                    'Made task {}, "{}", public'.format(task.id, task.summary))
                for child in task.children:
                    recurse(child)

            recurse(task)
        else:
            task.is_public = True
            printer('Made task {}, "{}", public'.format(task.id, task.summary))
        pl.commit()


def make_task_private(pl, task_id, printer=default_printer,
                      descendants=False):
    task = pl.get_task(task_id)
    if not task:
        printer('No task found by the id "{}"'.format(task_id))
    else:
        if descendants:
            def recurse(task):
                task.is_public = False
                printer(
                    'Made task {}, "{}", private'.format(task.id,
                                                         task.summary))
                for child in task.children:
                    recurse(child)

            recurse(task)
        else:
            task.is_public = False
            printer('Made task {}, "{}", private'.format(task.id,
                                                         task.summary))
        pl.commit()


def test_db_conn(pl, debug):
    try:
        count = pl.count_tasks()
    except Exception as e:
        print('Caught {}: "{}"'.format(type(e).__name__, e))
        if debug:
            print(traceback.format_exc())
    else:
        print('Test was successful. There are {} '
              'tasks in the DB.'.format(count))


def create_user(pl, email, hashed_password, is_admin=False):
    user = pl.create_user(email=email, hashed_password=hashed_password,
                          is_admin=is_admin)
    pl.add(user)
    pl.commit()


def get_db_uri(db_uri, db_uri_file):
    if db_uri is None and db_uri_file is not None:
        try:
            with open(db_uri_file) as f:
                return f.read()
        except FileNotFoundError:
            raise ConfigError(
                f'Could not find uri file "{db_uri_file}".')
        except PermissionError:
            raise ConfigError(
                f'Permission error when opening uri file '
                f'"{db_uri_file}".')
        except Exception as e:
            raise ConfigError(
                f'Error opening uri file "{db_uri_file}": {e}')
    return db_uri


def get_db_options(db_options, db_options_file):
    if db_options is None and db_options_file is not None:
        try:
            with open(db_options_file) as f:
                return f.read()
        except FileNotFoundError:
            raise ConfigError(
                f'Could not find db options file "{db_options_file}".')
        except PermissionError:
            raise ConfigError(
                f'Permission error when opening db options file '
                f'"{db_options_file}".')
        except Exception as e:
            raise ConfigError(
                f'Error opening db options file "{db_options_file}": {e}')
    return db_options


def get_secret_key(secret_key, secret_key_file):
    if secret_key is None and secret_key_file is not None:
        try:
            with open(secret_key_file) as f:
                return f.read()
        except FileNotFoundError:
            raise ConfigError(
                f'Could not find secret key file '
                f'"{secret_key_file}".')
        except PermissionError:
            raise ConfigError(
                f'Permission error when opening secret key file '
                f'"{secret_key_file}".')
        except Exception as e:
            raise ConfigError(
                f'Error opening secret key file '
                f'"{secret_key_file}": {e}')
    return secret_key


def main(argv):
    import os
    arg_config = get_config_from_command_line(argv)

    arg_config.DB_URI = get_db_uri(arg_config.DB_URI, arg_config.DB_URI_FILE)
    arg_config.DB_OPTIONS = get_db_options(arg_config.DB_OPTIONS,
                                           arg_config.DB_OPTIONS_FILE)
    arg_config.SECRET_KEY = get_secret_key(arg_config.SECRET_KEY,
                                           arg_config.SECRET_KEY_FILE)

    arg_config = Config.combine(arg_config, Config.from_defaults())

    print(f'__version__: {__version__}', file=sys.stderr)
    print(f'__revision__: {__revision__}', file=sys.stderr)
    print(f'getcwd(): {os.getcwd()}', file=sys.stderr)
    print(f'DEBUG: {arg_config.DEBUG}', file=sys.stderr)
    print(f'HOST: {arg_config.HOST}', file=sys.stderr)
    print(f'PORT: {arg_config.PORT}', file=sys.stderr)
    print(f'UPLOAD_FOLDER: {arg_config.UPLOAD_FOLDER}', file=sys.stderr)
    # TODO: remove this
    print(f'ALLOWED_EXTENSIONS: {arg_config.ALLOWED_EXTENSIONS}',
          file=sys.stderr)
    if arg_config.DEBUG:
        print(f'DB_URI: {arg_config.DB_URI}', file=sys.stderr)
        print(f'DB_OPTIONS: {arg_config.DB_OPTIONS}', file=sys.stderr)
        print(f'SECRET_KEY: {arg_config.SECRET_KEY}', file=sys.stderr)

    app = generate_app(db_uri=arg_config.DB_URI,
                       db_options=arg_config.DB_OPTIONS,
                       upload_folder=arg_config.UPLOAD_FOLDER,
                       secret_key=arg_config.SECRET_KEY,
                       allowed_extensions=arg_config.ALLOWED_EXTENSIONS)

    print('Checking database schema version')
    from packaging.version import parse
    current = app.pl.get_schema_version()
    if current:
        current = current.value
    if not current:
        current = '0.0'
    current = parse(parse(current).base_version)
    desired = parse(parse(__version__).base_version)
    if current < desired:
        print(f'Wrong DB schema version. Expected {desired.public} but got '
              f'{current.public}. Will auto-migrate.')
        auto_migrate(app.pl, desired.public)
        print('Migration complete.')
    else:
        print('Database schema version is up-to-date.')

    args = arg_config.args

    if args.create_db:
        print('Setting up the database')
        app.pl.create_all()
    elif args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in range(48)))
        print(key)
    elif args.hash_password is not None:
        print(app.bcrypt.generate_password_hash(args.hash_password).decode())
    elif args.make_public is not None:
        make_task_public(app.pl, args.make_public,
                         descendants=args.descendants)
    elif args.make_private is not None:
        make_task_private(app.pl, args.make_private,
                          descendants=args.descendants)
    elif args.test_db_conn:
        test_db_conn(app.pl, args.debug)
    elif args.create_user:
        email = args.create_user[0]
        hashed_password = args.create_user[1]
        is_admin = False
        if len(args.create_user) > 2 and bool_from_str(args.create_user[2]):
            is_admin = True
        create_user(app.pl, email=email, hashed_password=hashed_password,
                    is_admin=is_admin)
    elif args.export_db:
        with app.app_context():
            types_to_export = ('tasks', 'tags', 'notes', 'attachments',
                               'users', 'options')
            result = app.ll.do_export_data(types_to_export)
            import json
            print(json.dumps(result))
    elif args.import_db:
        with app.app_context():
            import json
            data = json.load(sys.stdin)
            app.ll.do_import_data(data)
            print('Finished')
    else:
        app.run(debug=arg_config.DEBUG, host=arg_config.HOST,
                port=arg_config.PORT)


if __name__ == '__main__':
    main(sys.argv[1:])
