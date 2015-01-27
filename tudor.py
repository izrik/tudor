#!/usr/bin/env python2

from flask import Flask, render_template
import argparse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.t.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    app.run(debug=args.debug)
