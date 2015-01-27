#!/usr/bin/env python2

from flask import Flask
import argparse

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    args = parser.parse_args()

    app.run()
