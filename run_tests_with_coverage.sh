#!/bin/bash

coverage run --source=tudor,conversions,logic_layer ./run_tests.py
coverage html
