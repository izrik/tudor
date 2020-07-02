#!/bin/bash

if [[ -z "$VERSION" ]]; then
  VERSION=latest
fi

docker run --rm -it "$@" tudor:$VERSION
