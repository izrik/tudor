#!/bin/bash

VERSION=$1
if [[ -z "$VERSION" ]]; then
  VERSION=$(git describe --tags | sed 's/^v//' )
fi
if [[ -z "$VERSION" ]]; then
  echo "Error: Could not determine the version string." >&2
  exit 1
fi

REVISION="$(git describe --dirty --always --abbrev=40)"

echo "Building version $VERSION..."
echo "  Revision: $REVISION"
docker build \
  -t tudor:latest \
  --build-arg VERSION="$VERSION" \
  --build-arg REVISION="$REVISION" \
  .

docker tag tudor:latest "tudor:$VERSION"
docker tag tudor:latest "izrik/tudor:$VERSION"
echo "To push, use: docker push izrik/tudor:$VERSION"
