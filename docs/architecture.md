# Architecture

Tudor uses a three-layer architecture: **View → Logic → Persistence**.

## View Layer (`view/layer.py`)

Flask route handlers. Delegates all business logic to the logic layer. Supports pluggable template renderers and login sources to aid testability.

## Logic Layer (`logic/layer.py`)

Business logic: task hierarchy sorting (recursive depth-first traversal), filtering, pagination, file upload validation, complex queries (deadlines, dependencies). Holds a reference to the persistence layer (`self.pl`).

## Persistence Layer (`persistence/`)

**`SqlAlchemyPersistenceLayer`** (`persistence/sqlalchemy/`) is the only implementation — PostgreSQL in production, in-memory SQLite in most tests.

Plain domain classes (`Task`, `User`, `Tag`, `Comment`, `Attachment`, `Option`) live in `models/` and use **ID-based relationships** (not object references) to avoid circular dependencies. `persistence/sqlalchemy/` maps them to the ORM `Db*` classes via the helpers in `conversion.py`. `save()` is the primary way to persist changes.

## Base Model Classes (`models/`)

`TaskBase`, `UserBase`, `TagBase`, etc. define field constants, serialization (`to_dict()` / `from_dict()`) and display helpers. The ORM `Db*` classes in `persistence/sqlalchemy/models/` inherit from them.

## Key Relationships

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
- `tests/view_t/` — view/route handler tests

SQLAlchemy persistence-layer tests use `PersistenceLayerTestBase` (in `tests/persistence_t/sqlalchemy/util.py`) which sets up a PostgreSQL fixture and manages app context.

Logic-layer tests and other tests that need a working PL use `generate_test_app()` (in `tests/util.py`, wrapped by `generate_ll()` for logic tests): a real app on in-memory SQLite with foreign keys enabled, cached per process with the schema reset per test. An autouse fixture in `tests/conftest.py` pops the app context afterward. View-layer tests mostly use `Mock(spec=SqlAlchemyPersistenceLayer)`.

## Active Refactoring

The persistence layer is being actively refactored toward ID-based relationships (replacing ORM object references) with a new `save()` method pattern. New code should follow this paradigm rather than the older ORM relationship-loading approach.

Each PL write (`save()`, `delete()`, the association setters) commits on its own. When one operation makes several writes, wrap them in `with self.pl.transaction():` so they commit together or roll back together; blocks nest, and `save()` still assigns ids inside a block.
