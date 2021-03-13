#!/bin/bash

VERSION=$1
shift
if [[ -z "$VERSION" ]]; then
  VERSION=$(git describe --tags | sed 's/^v//' )
fi
if [[ -z "$VERSION" ]]; then
  echo "Error: Could not determine the version string." >&2
  exit 1
fi

echo "Running version $VERSION..."

docker run --rm -it "$@" "tudor:$VERSION"
