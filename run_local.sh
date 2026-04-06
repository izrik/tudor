#!/bin/bash

VERSION=$(git describe --tags 2>/dev/null | sed 's/^v//' | sed 's/-[0-9]*-g/+g/')
if [[ -z "$VERSION" ]]; then
  VERSION="0.0"
fi

echo "__version__ = '$VERSION'" > __version__.py

mkdir -p instance

python tudor.py --debug --db-uri "sqlite:///$PWD/instance/tudor.sqlite" --secret-key 7RJK2cdY3T2xKgt1 "$@"
