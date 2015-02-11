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
    return render_template('index.t.html', tasks=tasks)


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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    app.run(debug=args.debug)
