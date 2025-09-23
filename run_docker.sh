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

PORT=${PORT:-8080}

docker run --rm -it \
  -p "$PORT:8080" \
  -e TUDOR_PORT="8080" \
  -e TUDOR_SECRET_KEY=7RJK2cdY3T2xKgt1 \
  -e TUDOR_DB_URI=postgresql://postgres@host.docker.internal:5432/tudor \
  "$@" \
  "tudor:$VERSION"
