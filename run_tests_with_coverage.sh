#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,data_source ./run_tests.py
coverage html
