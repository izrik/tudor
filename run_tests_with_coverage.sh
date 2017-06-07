#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,data_source,models,view_layer,persistence_layer ./run_tests.py "$@"
coverage html
