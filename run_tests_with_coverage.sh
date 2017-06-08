#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,models,view_layer,persistence_layer ./run_tests.py "$@" && \
coverage html
