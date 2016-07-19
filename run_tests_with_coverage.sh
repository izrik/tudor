#!/bin/bash

coverage run --source=tudor ./run_tests.py
coverage html
