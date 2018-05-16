#!/bin/sh

python /opt/tudor/tudor.py --create-db
gunicorn -b $TUDOR_HOST:$TUDOR_PORT gtudor:app
