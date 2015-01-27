#!/usr/bin/env python2

from flask import Flask, render_template
import argparse

app = Flask(__name__)

task_id = 0
def get_next_task_id():
    global task_id
    next_task_id = task_id
    task_id += 1
    return next_task_id

class Task(object):
    def __init__(self, summary):
        self.id = get_next_task_id()
        self.summary = summary


tasks = [Task('do something'), Task('do another thing')]

@app.route('/')
def index():
    return render_template('index.t.html', tasks=tasks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    app.run(debug=args.debug)
