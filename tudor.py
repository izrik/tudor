#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request, flash
import flask
import argparse
from flask.ext.sqlalchemy import SQLAlchemy
from os import environ
import datetime
import os.path
from werkzeug import secure_filename
from flask.ext.misaka import Misaka
import random
from flask.ext.login import LoginManager, login_user, login_required, logout_user


def bool_from_str(s):
    if isinstance(s, basestring):
        s = s.lower()
    if s in ['true', 't', '1', 'y']:
        return True
    if s in ['false', 'f', '0', 'n']:
        return False
    return bool(s)


TUDOR_DEBUG = bool_from_str(environ.get('TUDOR_DEBUG', False))
TUDOR_PORT = environ.get('TUDOR_PORT', 8304)
try:
    TUDOR_PORT = int(TUDOR_PORT)
except:
    TUDOR_PORT = 8304
TUDOR_DB_URI = environ.get('TUDOR_DB_URI', 'sqlite:////tmp/test.db')
TUDOR_UPLOAD_FOLDER = environ.get('TUDOR_UPLOAD_FOLDER', '/tmp/tudor/uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
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
    parser.add_argument('--secret-key', action='store',
                        default=TUDOR_SECRET_KEY)
    parser.add_argument('--create-secret-key', action='store_true')

    args = parser.parse_args()

    TUDOR_DEBUG = args.debug
    TUDOR_PORT = args.port
    TUDOR_DB_URI = args.db_uri
    TUDOR_UPLOAD_FOLDER = args.upload_folder
    TUDOR_SECRET_KEY = args.secret_key

print('TUDOR_DEBUG: {}'.format(TUDOR_DEBUG))
print('TUDOR_PORT: {}'.format(TUDOR_PORT))
print('TUDOR_DB_URI: {}'.format(TUDOR_DB_URI))
print('TUDOR_UPLOAD_FOLDER: {}'.format(TUDOR_UPLOAD_FOLDER))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = TUDOR_DB_URI
app.config['UPLOAD_FOLDER'] = TUDOR_UPLOAD_FOLDER
app.secret_key = TUDOR_SECRET_KEY
db = SQLAlchemy(app)
Misaka(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(100))
    description = db.Column(db.String(4000))
    is_done = db.Column(db.Boolean)
    is_deleted = db.Column(db.Boolean)
    order_num = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, summary, description='', is_done=False,
                 is_deleted=False):
        self.summary = summary
        self.description = description
        self.is_done = is_done
        self.is_deleted = is_deleted


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4000))
    timestamp = db.Column(db.DateTime)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship('Task', backref=db.backref('notes', lazy='dynamic',
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

    def __init__(self, path, description=None, timestamp=None, filename=None):
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
    password = db.Column(db.String(100), nullable=False)
    authenticated = True

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


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


@app.route('/')
def index():
    show_deleted = request.args.get('show_deleted')
    tasks = Task.query
    if not show_deleted:
        tasks = tasks.filter_by(is_deleted=False)
    tasks = tasks.order_by(Task.order_num.desc())
    tasks = tasks.all()
    return render_template('index.t.html', tasks=tasks,
                           show_deleted=show_deleted)


@app.route('/new', methods=['POST'])
def add_new():
    summary = request.form['summary']
    task = Task(summary)
    save_task(task)
    return redirect(url_for('index'))


@app.route('/done/<int:id>')
def task_done(id):
    task = Task.query.filter_by(id=id).first()
    if not task:
        return 404
    task.is_done = True
    save_task(task)
    return redirect(url_for('index'))


@app.route('/undo/<int:id>')
def task_undo(id):
    task = Task.query.filter_by(id=id).first()
    if not task:
        return 404
    task.is_done = False
    save_task(task)
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    if not task:
        return 404
    task.is_deleted = True
    save_task(task)
    return redirect(url_for('index'))


@app.route('/undelete/<int:id>')
def undelete_task(id):
    task = Task.query.filter_by(id=id).first()
    if not task:
        return 404
    task.is_deleted = False
    save_task(task)
    return redirect(url_for('index'))


@app.route('/purge/<int:id>')
def purge_task(id):
    global tasks
    task = Task.query.filter_by(id=id, is_deleted=True).first()
    if not task:
        return 404
    purge_task_from_db(task)
    return redirect(url_for('index'))


@app.route('/purge_all')
def purge_deleted_tasks():
    are_you_sure = request.args.get('are_you_sure')
    if are_you_sure:
        deleted_tasks = Task.query.filter_by(is_deleted=True)
        purge_tasks(deleted_tasks)
        return redirect(url_for('index'))
    return render_template('purge.t.html')


@app.route('/task/<int:id>')
def view_task(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        return (('No task found for the id "%s"' % id), 404)
    return render_template('task.t.html', task=task)


@app.route('/task/<int:id>/new_note', methods=['POST'])
def new_note(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        return (('No task found for the id "%s"' % id), 404)
    content = request.form['content']
    note = Note(content)
    note.task = task

    save_task(note)

    return redirect(url_for('view_task', id=id))


@app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
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
    task.is_done = ('is_done' in request.form and
                    not not request.form['is_done'])
    task.is_deleted = ('is_deleted' in request.form and
                       not not request.form['is_deleted'])

    save_task(task)

    return redirect(url_for('view_task', id=task.id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/task/<int:id>/new_attachment', methods=['POST'])
def new_attachment(id):
    task = Task.query.filter_by(id=id).first()
    if task is None:
        return (('No task found for the id "%s"' % id), 404)
    f = request.files['filename']
    if f is None or not f or not allowed_file(f.filename):
        return 400
    path = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], path))
    if 'description' in request.form:
        description = request.form['description']
    else:
        description = ''

    att = Attachment(path, description)
    att.task = task

    save_task(att)

    return redirect(url_for('view_task', id=id))


@app.route('/task/<int:id>/attachment/<int:aid>', defaults={'x': 'x'})
@app.route('/task/<int:id>/attachment/<int:aid>/', defaults={'x': 'x'})
@app.route('/task/<int:id>/attachment/<int:aid>/<path:x>')
def get_attachment(id, aid, x):
    att = Attachment.query.filter_by(id=aid).first()
    if att is None:
        return (('No attachment found for the id "%s"' % aid), 404)

    return flask.send_from_directory(TUDOR_UPLOAD_FOLDER, att.path)


@app.route('/task/<int:id>/up')
def move_task_up(id):
    task = Task.query.get(id)
    tasks = Task.query.filter(Task.order_num >= task.order_num)
    show_deleted = request.args.get('show_deleted')
    if not show_deleted:
        tasks = tasks.filter_by(is_deleted=False)
    tasks = tasks.order_by(Task.order_num.desc()).all()
    i = tasks.index(task)
    if i > 0:
        next_task = tasks[i - 1]
        if task.order_num == next_task.order_num:
            # re-calculate all order numbers
            tasks = Task.query.order_by(Task.order_num.desc()).all()
            N = len(tasks)
            for i in xrange(N):
                tasks[i].order_num = N - i
                db.session.add(tasks[i])
        a, b = next_task.order_num, task.order_num
        task.order_num, next_task.order_num = a, b
        db.session.add(task)
        db.session.add(next_task)
        db.session.commit()

    return redirect(url_for('index', show_deleted=show_deleted))


@app.route('/task/<int:id>/down')
def move_task_down(id):
    task = Task.query.get(id)
    tasks = Task.query.filter(Task.order_num <= task.order_num)
    show_deleted = request.args.get('show_deleted')
    if not show_deleted:
        tasks = tasks.filter_by(is_deleted=False)
    tasks = tasks.order_by(Task.order_num.desc()).all()
    i = tasks.index(task)
    if i + 1 < len(tasks):
        next_task = tasks[i + 1]
        if task.order_num == next_task.order_num:
            # re-calculate all order numbers
            tasks = Task.query.order_by(Task.order_num.desc()).all()
            N = len(tasks)
            for i in xrange(N):
                tasks[i].order_num = N - i
                db.session.add(tasks[i])
        a, b = next_task.order_num, task.order_num
        task.order_num, next_task.order_num = a, b
        db.session.add(task)
        db.session.add(next_task)
        db.session.commit()

    return redirect(url_for('index', show_deleted=show_deleted))


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.t.html')
    email = request.form['email']
    password = request.form['password']
    registered_user = User.query.filter_by(email=email,
                                           password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
login_manager.login_view = 'login'


if __name__ == '__main__':
    if args.create_db:
        db.create_all()
    elif args.create_secret_key:
        digits = ['0123456789abcdef']
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
    else:
        app.run(debug=TUDOR_DEBUG, port=TUDOR_PORT)
