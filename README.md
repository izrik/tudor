# tudor [![Build Status](https://travis-ci.org/izrik/tudor.svg)](https://travis-ci.org/izrik/tudor) [![Coverage Status](https://coveralls.io/repos/github/izrik/tudor/badge.svg)](https://coveralls.io/github/izrik/tudor)

A task manager web application built with Flask and SQLAlchemy.

## Quick Start

```bash
# Run locally
python3 tudor.py

# Run via Docker
./run_docker.sh

# Run tests
pytest tests/ -n auto
```

## Configuration

The app is configured via environment variables with `TUDOR_` prefix:
- `TUDOR_DB_URI` — database connection string (PostgreSQL or SQLite)
- `TUDOR_DEBUG`, `TUDOR_HOST`, `TUDOR_PORT` — server settings
- `TUDOR_SECRET_KEY` — Flask secret key

See [CLAUDE.md](CLAUDE.md) for the full list of environment variables.

## Documentation

- [CLAUDE.md](CLAUDE.md) — agent guidance, commands, and architecture overview
- [docs/architecture.md](docs/architecture.md) — detailed architecture and test structure
- [RELEASING.md](RELEASING.md) — release process
