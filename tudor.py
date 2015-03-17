#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request
import argparse
from flask.ext.sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('TUDOR_DB_URI',
                                                    'sqlite:////tmp/test.db')
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(100))
    is_done = db.Column(db.Boolean)
    is_deleted = db.Column(db.Boolean)

    def __init__(self, summary, is_done=False, is_deleted=False):
        self.summary = summary
        self.is_done = is_done
        self.is_deleted = is_deleted


def db_from_nondb(nondb):
    summary = nondb.summary if hasattr(nondb, 'summary') else ''
    is_done = nondb.is_done if hasattr(nondb, 'is_done') else False
    is_deleted = nondb.is_deleted if hasattr(nondb, 'is_deleted') else False
    dbtask = Task(summary, is_done, is_deleted)
    return dbtask


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--port', action='store', default=8304, type=int)
    parser.add_argument('--create-db', action='store_true')

    args = parser.parse_args()

    if args.create_db:
        db.create_all()
    else:
        app.run(debug=args.debug, port=args.port)
