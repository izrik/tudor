#!/bin/bash

SOURCES=tudor,conversions,logic.layer,models,view.layer,persistence.persistence_layer,\
collections_util,logging_util,persistence.in_memory_persistence_layer

coverage run --source=$SOURCES --branch -m unittest discover -s tests -p '*.py' -t . "$@" && \
    coverage html
