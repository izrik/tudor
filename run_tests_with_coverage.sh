#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,data_source,models,render,api ./run_tests.py "$@"
coverage html
