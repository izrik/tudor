# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About Tudor

Tudor is a task management web application built with Flask and SQLAlchemy. It supports hierarchical tasks, user permissions, tags, notes, attachments, deadlines, and task dependencies.

## Commands

### Running Tests

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
```

### Running the Application

```bash
# Run locally
python3 tudor.py

# Run via Docker
./run_docker.sh

# Run with local PostgreSQL
./run_docker_local_pg.sh
```

### CSS Linting

```bash
csslint --exclude-list=static/bootstrap.min.css,static/bootstrap.css static/
```

### Configuration

The app is configured via environment variables with `TUDOR_` prefix:
- `TUDOR_DB_URI` — database connection string
- `TUDOR_DEBUG`, `TUDOR_HOST`, `TUDOR_PORT`
- `TUDOR_UPLOAD_FOLDER`, `TUDOR_ALLOWED_EXTENSIONS`
- `TUDOR_SECRET_KEY`

## Architecture

The app has three main layers: **View → Logic → Persistence**, each in its own directory.

### View Layer (`view/layer.py`)
Flask route handlers. Delegates all business logic to the logic layer. Supports pluggable template renderers and login sources to aid testability.

### Logic Layer (`logic/layer.py`)
Business logic: task hierarchy sorting (recursive depth-first traversal), filtering, pagination, file upload validation, complex queries (deadlines, dependencies). Holds a reference to the persistence layer (`self.pl`).

### Persistence Layer (`persistence/`)
Two implementations share the same interface:
- **`SqlAlchemyPersistenceLayer`** — database-backed (PostgreSQL or SQLite)
- **`InMemoryPersistenceLayer`** — in-memory storage used in tests

Domain model classes (`Task2`, `User2`, `Tag2`, `Note2`, `Attachment2`, `Option2`) live in `persistence/` and use **ID-based relationships** (not object references) to avoid circular dependencies. A `save()` method is the primary way to persist changes.

### Base Model Classes (`models/`)
`TaskBase`, `UserBase`, `TagBase`, etc. define field constants and serialization (`to_dict()` / `from_dict()`). The `*2` classes in `persistence/` are the concrete implementations.

### Key Relationships
- Tasks can have parent tasks (hierarchy)
- Tasks can depend on other tasks (dependees/dependants)
- Tasks can prioritize before/after other tasks
- Tags and users have many-to-many relationships with tasks
- Notes and attachments have one-to-many relationships with tasks

## Test Structure

Tests mirror the source structure:
- `tests/logic_t/` — logic layer tests
- `tests/models_t/` — domain model tests
- `tests/persistence_t/sqlalchemy/` — SQL persistence tests (require live PostgreSQL via `pytest-postgresql`)
- `tests/persistence_t/in_memory/` — in-memory persistence tests
- `tests/view_t/` — view/route handler tests

SQLAlchemy persistence tests use `PersistenceLayerTestBase` (in `tests/persistence_t/sqlalchemy/util.py`) which sets up a PostgreSQL fixture and manages app context.

## Active Refactoring

The persistence layer is being actively refactored toward ID-based relationships (replacing ORM object references) with a new `save()` method pattern. New code should follow this paradigm rather than the older ORM relationship-loading approach.