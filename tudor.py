#!/usr/bin/env python2
import traceback

import sys
from flask import Flask, request
from flask import Markup
import argparse
from os import environ
import random
from flask.ext.login import LoginManager, login_required, current_user
from flask.ext.bcrypt import Bcrypt
import re
import markdown
from functools import wraps
import git
from flask_sqlalchemy import SQLAlchemy

from conversions import bool_from_str, int_from_str
from logic_layer import LogicLayer
from models.user import GuestUser
from view_layer import ViewLayer
from persistence_layer import PersistenceLayer
import base64

try:
    __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                              always=True, abbrev=40)
except git.InvalidGitRepositoryError:
    __revision__ = 'unknown'


DEFAULT_TUDOR_DEBUG = False
DEFAULT_TUDOR_HOST = '127.0.0.1'
DEFAULT_TUDOR_PORT = 8304
DEFAULT_TUDOR_DB_URI = 'sqlite:////tmp/test.db'
DEFAULT_TUDOR_UPLOAD_FOLDER = '/tmp/tudor/uploads'
DEFAULT_TUDOR_ALLOWED_EXTENSIONS = 'txt,pdf,png,jpg,jpeg,gif'
DEFAULT_TUDOR_SECRET_KEY = None


class Config(object):
    def __init__(self, debug=DEFAULT_TUDOR_DEBUG, host=DEFAULT_TUDOR_HOST,
                 port=DEFAULT_TUDOR_PORT, db_uri=DEFAULT_TUDOR_DB_URI,
                 upload_folder=DEFAULT_TUDOR_UPLOAD_FOLDER,
                 allowed_extensions=DEFAULT_TUDOR_ALLOWED_EXTENSIONS,
                 secret_key=DEFAULT_TUDOR_SECRET_KEY, args=None):
        self.DEBUG = debug
        self.HOST = host
        self.PORT = port
        self.DB_URI = db_uri
        self.UPLOAD_FOLDER = upload_folder
        self.ALLOWED_EXTENSIONS = allowed_extensions
        self.SECRET_KEY = secret_key
        self.args = args

    @staticmethod
    def from_environ():
        return Config(
            debug=bool_from_str(
                environ.get('TUDOR_DEBUG', DEFAULT_TUDOR_DEBUG)),
            host=environ.get('TUDOR_HOST', DEFAULT_TUDOR_HOST),
            port=int_from_str(environ.get('TUDOR_PORT', DEFAULT_TUDOR_PORT),
                              DEFAULT_TUDOR_PORT),
            db_uri=environ.get('TUDOR_DB_URI', DEFAULT_TUDOR_DB_URI),
            upload_folder=environ.get('TUDOR_UPLOAD_FOLDER',
                                      DEFAULT_TUDOR_UPLOAD_FOLDER),
            allowed_extensions=environ.get('TUDOR_ALLOWED_EXTENSIONS',
                                           DEFAULT_TUDOR_ALLOWED_EXTENSIONS),
            secret_key=environ.get('TUDOR_SECRET_KEY'))


def get_config_from_command_line(args, defaults):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        default=defaults.DEBUG)
    parser.add_argument('--host', action='store', default=defaults.HOST)
    parser.add_argument('--port', action='store', default=defaults.PORT,
                        type=int)
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--db-uri', action='store', default=defaults.DB_URI)
    parser.add_argument('--upload-folder', action='store',
                        default=defaults.UPLOAD_FOLDER)
    parser.add_argument('--allowed-extensions', action='store',
                        default=defaults.ALLOWED_EXTENSIONS)
    parser.add_argument('--secret-key', action='store',
                        default=defaults.SECRET_KEY)
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

    args2 = parser.parse_args(args=args)

    return Config(
        debug=args2.debug,
        host=args2.host,
        port=args2.port,
        db_uri=args2.db_uri,
        upload_folder=args2.upload_folder,
        secret_key=args2.secret_key,
        allowed_extensions=args2.allowed_extensions,
        args=args2)


def generate_app(db_uri=DEFAULT_TUDOR_DB_URI,
                 upload_folder=DEFAULT_TUDOR_UPLOAD_FOLDER,
                 secret_key=DEFAULT_TUDOR_SECRET_KEY,
                 allowed_extensions=DEFAULT_TUDOR_ALLOWED_EXTENSIONS,
                 ll=None, vl=None, pl=None, flask_configs=None,
                 disable_admin_check=False):

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if flask_configs:
        for k, v in flask_configs.iteritems():
            app.config[k] = v
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

    if pl is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        db = SQLAlchemy(app)
        pl = PersistenceLayer(db)
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
        def get_author():
            return Options.get('author', 'the author')

        @staticmethod
        def get_user():
            if current_user is None:
                return GuestUser()

            try:
                user_id = current_user.id
                return pl.get_user(user_id)
            except AttributeError:
                return GuestUser()

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
            api_key = base64.b64decode(api_key)
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

    # View utility functions

    def get_form_or_arg(name):
        if name in request.form:
            return request.form[name]
        return request.args.get(name)

    # View Functions

    @app.route('/')
    @login_required
    def index():
        return vl.index(request, Options.get_user())

    @app.route('/hierarchy')
    @login_required
    def hierarchy():
        return vl.hierarchy(request, Options.get_user())

    @app.route('/deadlines')
    @login_required
    def deadlines():
        return vl.deadlines(request, Options.get_user())

    @app.route('/task/new', methods=['GET'])
    @login_required
    def get_new_task():
        return vl.task_new_get(request, Options.get_user())

    @app.route('/task/new', methods=['POST'])
    @login_required
    def new_task():
        return vl.task_new_post(request, Options.get_user())

    @app.route('/task/<int:id>/mark_done')
    @login_required
    def task_done(id):
        return vl.task_mark_done(request, Options.get_user(), id)

    @app.route('/task/<int:id>/mark_undone')
    @login_required
    def task_undo(id):
        return vl.task_mark_undone(request, Options.get_user(), id)

    @app.route('/task/<int:id>/delete')
    @login_required
    def delete_task(id):
        return vl.task_delete(request, Options.get_user(), id)

    @app.route('/task/<int:id>/undelete')
    @login_required
    def undelete_task(id):
        return vl.task_undelete(request, Options.get_user(), id)

    @app.route('/task/<int:id>/purge')
    @login_required
    @admin_required
    def purge_task(id):
        return vl.task_purge(request, Options.get_user(), id)

    @app.route('/purge_all')
    @login_required
    @admin_required
    def purge_deleted_tasks():
        return vl.purge_all(request, Options.get_user())

    @app.route('/task/<int:id>')
    def view_task(id):
        return vl.task(request, Options.get_user(), id)

    @app.route('/task/<int:id>/hierarchy')
    def view_task_hierarchy(id):
        return vl.task_hierarchy(request, Options.get_user(), id)

    @app.route('/note/new', methods=['POST'])
    @login_required
    def new_note():
        return vl.note_new_post(request, Options.get_user())

    @app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(id):
        return vl.task_edit(request, Options.get_user(), id)

    @app.route('/attachment/new', methods=['POST'])
    @login_required
    def new_attachment():
        return vl.attachment_new(request, Options.get_user())

    @app.route('/attachment/<int:aid>', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/', defaults={'x': 'x'})
    @app.route('/attachment/<int:aid>/<path:x>')
    @login_required
    def get_attachment(aid, x):
        return vl.attachment(request, Options.get_user(), aid, x)

    @app.route('/task/<int:id>/up')
    @login_required
    def move_task_up(id):
        return vl.task_up(request, Options.get_user(), id)

    @app.route('/task/<int:id>/top')
    @login_required
    def move_task_to_top(id):
        return vl.task_top(request, Options.get_user(), id)

    @app.route('/task/<int:id>/down')
    @login_required
    def move_task_down(id):
        return vl.task_down(request, Options.get_user(), id)

    @app.route('/task/<int:id>/bottom')
    @login_required
    def move_task_to_bottom(id):
        return vl.task_bottom(request, Options.get_user(), id)

    @app.route('/long_order_change', methods=['POST'])
    @login_required
    def long_order_change():
        return vl.long_order_change(request, Options.get_user())

    @app.route('/task/<int:id>/add_tag', methods=['GET', 'POST'])
    @login_required
    def add_tag_to_task(id):
        return vl.task_add_tag(request, Options.get_user(), id)

    @app.route('/task/<int:id>/delete_tag', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/', methods=['GET', 'POST'],
               defaults={'tag_id': None})
    @app.route('/task/<int:id>/delete_tag/<tag_id>', methods=['GET', 'POST'])
    @login_required
    def delete_tag_from_task(id, tag_id):
        return vl.task_delete_tag(request, Options.get_user(), id, tag_id)

    @app.route('/task/<int:task_id>/authorize_user', methods=['GET', 'POST'])
    @login_required
    def authorize_user_for_task(task_id):
        return vl.task_authorize_user(request, Options.get_user(), task_id)

    @app.route('/task/<int:task_id>/pick_user')
    @login_required
    def pick_user_to_authorize(task_id):
        return vl.task_pick_user(request, Options.get_user(), task_id)

    @app.route('/task/<int:task_id>/authorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    @login_required
    def authorize_picked_user_for_task(task_id, user_id):
        return vl.task_authorize_user_user(request, Options.get_user(),
                                           task_id, user_id)

    @app.route('/task/<int:task_id>/deauthorize_user', methods=['GET', 'POST'],
               defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/',
               methods=['GET', 'POST'], defaults={'user_id': None})
    @app.route('/task/<int:task_id>/deauthorize_user/<int:user_id>',
               methods=['GET', 'POST'])
    @login_required
    def deauthorize_user_for_task(task_id, user_id):
        return vl.task_deauthorize_user(request, Options.get_user(), task_id,
                                        user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return vl.login(request, Options.get_user())

    @app.route('/logout')
    def logout():
        return vl.logout(request, Options.get_user())

    @app.route('/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def list_users():
        return vl.users(request, Options.get_user())

    @app.route('/users/<int:user_id>', methods=['GET'])
    @login_required
    def view_user(user_id):
        return vl.users_user_get(request, Options.get_user(), user_id)

    @app.route('/show_hide_deleted')
    @login_required
    def show_hide_deleted():
        return vl.show_hide_deleted(request, Options.get_user())

    @app.route('/show_hide_done')
    @login_required
    def show_hide_done():
        return vl.show_hide_done(request, Options.get_user())

    @app.route('/options', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def view_options():
        return vl.options(request, Options.get_user())

    @app.route('/option/<path:key>/delete')
    @login_required
    @admin_required
    def delete_option(key):
        return vl.option_delete(request, Options.get_user(), key)

    @app.route('/reset_order_nums')
    @login_required
    def reset_order_nums():
        return vl. reset_order_nums(request, Options.get_user())

    @app.route('/export', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def export_data():
        return vl.export(request, Options.get_user())

    @app.route('/import', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def import_data():
        return vl.import_(request, Options.get_user())

    @app.route('/task_crud', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def task_crud():
        return vl.task_crud(request, Options.get_user())

    @app.route('/tags')
    @app.route('/tags/')
    @login_required
    def list_tags():
        return vl.tags(request, Options.get_user())

    @app.route('/tags/<int:id>')
    @login_required
    def view_tag(id):
        return vl.tags_id_get(request, Options.get_user(), id)

    @app.route('/tags/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_tag(id):
        return vl.tags_id_edit(request, Options.get_user(), id)

    @app.route('/task/<int:id>/convert_to_tag')
    @login_required
    def convert_task_to_tag(id):
        return vl.task_id_convert_to_tag(request, Options.get_user(), id)

    @app.route('/search', methods=['GET', 'POST'],
               defaults={'search_query': None})
    @app.route('/search/', methods=['GET', 'POST'],
               defaults={'search_query': None})
    @app.route('/search/<search_query>', methods=['GET'])
    @login_required
    def search(search_query):
        return vl.search(request, Options.get_user(), search_query)

    @app.route('/task/<int:task_id>/add_dependee', methods=['GET', 'POST'],
               defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/add_dependee/', methods=['GET', 'POST'],
               defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/add_dependee/<int:dependee_id>',
               methods=['GET', 'POST'])
    @login_required
    def add_dependee_to_task(task_id, dependee_id):
        return vl.task_id_add_dependee(request, Options.get_user(), task_id,
                                       dependee_id)

    @app.route('/task/<int:task_id>/remove_dependee',
               methods=['GET', 'POST'], defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/remove_dependee/',
               methods=['GET', 'POST'], defaults={'dependee_id': None})
    @app.route('/task/<int:task_id>/remove_dependee/<int:dependee_id>',
               methods=['GET', 'POST'])
    @login_required
    def remove_dependee_from_task(task_id, dependee_id):
        return vl.task_id_remove_dependee(request, Options.get_user(), task_id,
                                          dependee_id)

    @app.route('/task/<int:task_id>/add_dependant', methods=['GET', 'POST'],
               defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/add_dependant/', methods=['GET', 'POST'],
               defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/add_dependant/<int:dependant_id>',
               methods=['GET', 'POST'])
    @login_required
    def add_dependant_to_task(task_id, dependant_id):
        return vl.task_id_add_dependant(request, Options.get_user(), task_id,
                                        dependant_id)

    @app.route('/task/<int:task_id>/remove_dependant',
               methods=['GET', 'POST'], defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/remove_dependant/',
               methods=['GET', 'POST'], defaults={'dependant_id': None})
    @app.route('/task/<int:task_id>/remove_dependant/<int:dependant_id>',
               methods=['GET', 'POST'])
    @login_required
    def remove_dependant_from_task(task_id, dependant_id):
        return vl.task_id_remove_dependant(request, Options.get_user(),
                                           task_id, dependant_id)

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
        return vl.task_id_add_prioritize_before(request, Options.get_user(),
                                                task_id, prioritize_before_id)

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
    @login_required
    def remove_prioritize_before_from_task(task_id, prioritize_before_id):
        return vl.task_id_remove_prioritize_before(request, Options.get_user(),
                                                   task_id,
                                                   prioritize_before_id)

    @app.route('/task/<int:task_id>/add_prioritize_after',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route('/task/<int:task_id>/add_prioritize_after/',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route(
        '/task/<int:task_id>/add_prioritize_after/<int:prioritize_after_id>',
        methods=['GET', 'POST'])
    @login_required
    def add_prioritize_after_to_task(task_id, prioritize_after_id):
        return vl.task_id_add_prioritize_after(request, Options.get_user(),
                                               task_id, prioritize_after_id)

    @app.route('/task/<int:task_id>/remove_prioritize_after',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route('/task/<int:task_id>/remove_prioritize_after/',
               methods=['GET', 'POST'], defaults={'prioritize_after_id': None})
    @app.route(
        '/task/<int:task_id>/remove_prioritize_after/'
        '<int:prioritize_after_id>',
        methods=['GET', 'POST'])
    @login_required
    def remove_prioritize_after_from_task(task_id, prioritize_after_id):
        return vl.task_id_remove_prioritize_after(request, Options.get_user(),
                                                  task_id, prioritize_after_id)

    @app.template_filter(name='gfm')
    def render_gfm(s):
        output = markdown.markdown(s, extensions=['gfm'])
        moutput = Markup(output)
        return moutput

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


if __name__ == '__main__':

    default_config = Config()

    env_config = Config.from_environ()

    arg_config = get_config_from_command_line(sys.argv[1:], env_config)

    print('__revision__: {}'.format(__revision__))
    print('DEBUG: {}'.format(arg_config.DEBUG))
    print('HOST: {}'.format(arg_config.HOST))
    print('PORT: {}'.format(arg_config.PORT))
    print('DB_URI: {}'.format(arg_config.DB_URI))
    print('UPLOAD_FOLDER: {}'.format(arg_config.UPLOAD_FOLDER))
    print('ALLOWED_EXTENSIONS: {}'.format(arg_config.ALLOWED_EXTENSIONS))

    app = generate_app(db_uri=arg_config.DB_URI,
                       upload_folder=arg_config.UPLOAD_FOLDER,
                       secret_key=arg_config.SECRET_KEY,
                       allowed_extensions=arg_config.ALLOWED_EXTENSIONS)

    args = arg_config.args

    if args.create_db:
        print('Setting up the database')
        app.pl.create_all()
    elif args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
    elif args.hash_password is not None:
        print(app.bcrypt.generate_password_hash(args.hash_password))
    elif args.make_public is not None:
        make_task_public(app.pl, args.make_public, descendants=args.descendants)
    elif args.make_private is not None:
        make_task_private(app.pl, args.make_private, descendants=args.descendants)
    elif args.test_db_conn:
        test_db_conn(app.pl, args.debug)
    else:
        app.run(debug=arg_config.DEBUG, host=arg_config.HOST,
                port=arg_config.PORT)
