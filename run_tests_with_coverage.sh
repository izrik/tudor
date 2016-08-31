#!/bin/bash

coverage run --source=tudor,conversions,logic_layer,data_source,models ./run_tests.py
coverage html
