#!/bin/bash

SOURCES=tudor,conversions,logic,models,view,persistence,collections_util,\
logging_util

coverage run --source=$SOURCES --branch -m unittest discover -s tests -p '*.py' -t . "$@" && \
    coverage html && \
    csslint --exclude-list=static/bootstrap.min.css,static/bootstrap.css static/
