#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,data_source,models,json_renderer ./run_tests.py "$@"
coverage html
