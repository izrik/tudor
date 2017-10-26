#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,models,view_layer,persistence_layer,collections_util,logging_util --branch -m unittest discover -s tests -p '*.py' -t . "$@" && \
coverage html
