#!/bin/bash

VERSION=$1
if [[ -z "$VERSION" ]]; then
  VERSION=$(git describe --tags | sed 's/^v//' )
fi
if [[ -z "$VERSION" ]]; then
  echo "Error: Could not determine the version string." >&2
  exit 1
fi

echo "Building version $VERSION..."
docker build -t tudor:latest .

docker tag tudor:latest "tudor:$VERSION"
docker tag tudor:latest "izrik/tudor:$VERSION"
