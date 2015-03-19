#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request
import argparse
from flask.ext.sqlalchemy import SQLAlchemy
from os import environ
import datetime


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


args = None
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=TUDOR_DEBUG)
    parser.add_argument('--port', action='store', default=TUDOR_PORT, type=int)
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--db-uri', action='store', default=TUDOR_DB_URI)

    args = parser.parse_args()

    TUDOR_DEBUG = args.debug
    TUDOR_PORT = args.port
    TUDOR_DB_URI = args.db_uri

print('TUDOR_DEBUG: {}'.format(TUDOR_DEBUG))
print('TUDOR_PORT: {}'.format(TUDOR_PORT))
print('TUDOR_DB_URI: {}'.format(TUDOR_DB_URI))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = TUDOR_DB_URI
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(100))
    description = db.Column(db.String(4000))
    is_done = db.Column(db.Boolean)
    is_deleted = db.Column(db.Boolean)

    def __init__(self, summary, description='', is_done=False, is_deleted=False):
        self.summary = summary
        self.description = description
        self.is_done = is_done
        self.is_deleted = is_deleted


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4000))
    timestamp = db.Column(db.DateTime)

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    task = db.relationship('Task', backref=db.backref('notes', lazy='dynamic'))

    def __init__(self, content, timestamp=None):
        self.content = content
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()
        self.timestamp = timestamp


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
    if show_deleted:
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(is_deleted=False).all()
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

    def render_get_response(x=''):
        return render_template("edit_task.t.html", task=task, x=x)

    if request.method == 'GET':
        return render_get_response()

    if 'summary' not in request.form or 'description' not in request.form:
        return render_get_response()

    task.summary = request.form['summary']
    task.description = request.form['description']
    task.is_done = 'is_done' in request.form and not not request.form['is_done']
    task.is_deleted = ('is_deleted' in request.form and
                       not not request.form['is_deleted'])

    save_task(task)

    return redirect(url_for('view_task', id=task.id))


if __name__ == '__main__':
    if args.create_db:
        db.create_all()
    else:
        app.run(debug=TUDOR_DEBUG, port=TUDOR_PORT)
