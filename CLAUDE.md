# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About Tudor

Tudor is a task management web application built with Flask and SQLAlchemy. It supports hierarchical tasks, user permissions, tags, notes, attachments, deadlines, and task dependencies.

## Commands

```bash
# Run all tests with coverage + CSS linting
./run_tests_with_coverage.sh

# Run all tests (no coverage)
pytest tests/

# Run all tests in parallel (significantly faster)
pytest tests/ -n auto

# Run a specific test file
pytest tests/test_conversions.py -v

# Run a specific test class or method
pytest tests/test_main.py::MainFunctionTests::test_main -v

# Run tests matching a pattern
pytest tests/ -k "test_pager" -v

# Run locally
python3 tudor.py

# Run via Docker
./run_docker.sh

# CSS linting
csslint --exclude-list=static/bootstrap.min.css,static/bootstrap.css static/
```

## Configuration

The app is configured via environment variables with `TUDOR_` prefix:
- `TUDOR_DB_URI` — database connection string
- `TUDOR_DEBUG`, `TUDOR_HOST`, `TUDOR_PORT`
- `TUDOR_UPLOAD_FOLDER`, `TUDOR_ALLOWED_EXTENSIONS`
- `TUDOR_SECRET_KEY`

## Architecture at a Glance

Three-layer design: **View → Logic → Persistence**

```
view/layer.py          Flask routes, delegates to logic layer
        ↓
logic/layer.py         Business logic, hierarchy, filtering, pagination
        ↓
persistence/sqlalchemy SQLAlchemy ORM, PostgreSQL in prod, SQLite in tests
        ↓
models/                Domain classes with ID-based relationships
```

See [docs/architecture.md](docs/architecture.md) for the full breakdown.

## Code Style

- 4-space indentation
- `snake_case` for variables/functions
- Follow existing patterns in each layer

## Development Workflow

1. Create a branch from `master` (use hyphens, not slashes: `feature-my-feature`)
2. Implement the change
3. Run tests: `pytest tests/ -n auto`
4. Commit with a clear message
5. Push and open a PR against `master`
6. Address review feedback, then merge

## Further Documentation

- [docs/architecture.md](docs/architecture.md) — full component breakdown, data flow, test structure, active refactoring notes
- [RELEASING.md](RELEASING.md) — release process and versioning
