#!/usr/bin/env python2

from flask import Flask, render_template, redirect, url_for, request
import argparse
from itertools import count
import pickle

app = Flask(__name__)

get_next_task_id = count().next


class Task(object):
    def __init__(self, summary):
        self.id = get_next_task_id()
        self.summary = summary
        self.is_done = False
        self.is_deleted = False


tasks = [Task('do something'), Task('do another thing')]


def load_tasks():
    try:
        with open('tudor_tasks.p', 'rb') as f:
            global tasks, get_next_task_id
            tasks = pickle.load(f)
            max_id = max(tasks, key=lambda t: t.id).id
            get_next_task_id = count(max_id+1).next
    except:
        return tasks

load_tasks()


@app.route('/')
def index():
    show_deleted = request.args.get('show_deleted')
    return render_template('index.t.html', tasks=tasks,
                           show_deleted=show_deleted)


@app.route('/new', methods=['POST'])
def add_new():
    summary = request.form['summary']
    tasks.append(Task(summary))
    return redirect(url_for('index'))


@app.route('/done/<int:id>')
def task_done(id):
    found = [t for t in tasks if t.id == id][:1]
    if not found:
        return 404
    t = found[0]
    t.is_done = True
    return redirect(url_for('index'))


@app.route('/undo/<int:id>')
def task_undo(id):
    found = [t for t in tasks if t.id == id][:1]
    if not found:
        return 404
    t = found[0]
    t.is_done = False
    return redirect(url_for('index'))


@app.route('/save')
def save():
    with open('tudor_tasks.p', 'wb') as f:
        pickle.dump(tasks, f)
    return redirect(url_for('index'))


@app.route('/load')
def load():
    load_tasks()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_task(id):
    found = [t for t in tasks if t.id == id][:1]
    if not found:
        return 404
    t = found[0]
    t.is_deleted = True
    return redirect(url_for('index'))


@app.route('/undelete/<int:id>')
def undelete_task(id):
    found = [t for t in tasks if t.id == id][:1]
    if not found:
        return 404
    t = found[0]
    t.is_deleted = False
    return redirect(url_for('index'))


@app.route('/purge/<int:id>')
def purge_task(id):
    global tasks
    found = [t for t in tasks if t.id == id][:1]
    if not found:
        return 404
    tt = found[0]
    if not hasattr(tt, 'is_deleted'):
        tt.is_deleted = False
    if tt.is_deleted:
        tasks = [t for t in tasks if t != tt]
    return redirect(url_for('index'))


@app.route('/purge_all')
def purge_deleted_tasks():
    are_you_sure = request.args.get('are_you_sure')
    if are_you_sure:
        global tasks
        for t in tasks:
            if not hasattr(t, 'is_deleted'):
                t.is_deleted = False
        tasks = [t for t in tasks if not t.is_deleted]
        return redirect(url_for('index'))
    return render_template('purge.t.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--port', action='store', default=8304, type=int)

    args = parser.parse_args()

    app.run(debug=args.debug, port=args.port)
