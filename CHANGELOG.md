# Changelog

All notable changes to Tudor are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Comments have an author** (closes #155). The author's email address is
  shown next to each comment on the task page, and whoever posts a comment
  is recorded as its author.
- **A security policy** (closes #165). [SECURITY.md](SECURITY.md) says where to
  report a vulnerability — GitHub's private vulnerability reporting rather than
  a public issue — what's in scope, and what a reporter can expect. The CI
  workflow's token is also now scoped to `contents: read`, which is all it
  needs.

### Changed

- **Only the author of a comment can edit it** (closes #155). Until now any
  user authorized on the task could change anyone's comment. The Edit link
  now appears only on your own comments, and the edit page refuses anyone
  else. Admins can still edit any comment, which is also how the comments
  that pre-date this change — they have no author and are shown as
  "unknown" — can be edited at all. The database gains a `comment.author_id`
  column; upgrading applies it automatically at start-up, as with any other
  schema change.
- **Schema migrations are numbered with a plain counter** (closes #162).
  The scripts in `persistence/migrations/` were named like release
  versions, `v0.17.sql`, and were applied by counting upwards from the
  version the database was on — which meant the series could never leave
  `0.x`, and that every gap in it was announced on start-up as a missing
  script. They are now named for their place in a sequence that has no
  upper bound, `0018-add-comment-author.sql`, and the ones a database
  hasn't seen yet are applied in order. Nothing is needed from an
  operator: the version a database already carries is still understood,
  and is rewritten under the clearer name `__schema_version__` the next
  time it migrates.

### Fixed

- **Attachment borders align with child tasks** (#173), leaving space between
  the attachments section and the info panel.

- **Setting up a brand-new database works** (#162). `--create-db` against
  an empty database failed, because the schema version was read, and the
  migration attempted, before the tables it needed existed. The tables
  are now created first, and a database created that way is recorded as
  being at the current schema version rather than having every migration
  script replayed against it.

- **Creating or cloning a task with a tag on it works again** (#157).
  Saving the new-task form with anything in the Tags field, or cloning a
  task whose children carry tags, failed with an Internal Server Error
  (`'Task' object has no attribute 'is_user_authorized'`): the newly
  created task was handed to the tag code as a plain domain object,
  which carries no list of authorized users for the permission check to
  read. The task is now looked up in the database first.
- **Attaching a file with a long name works** (#161, closes #158). The
  attachment table stored the name in a `varchar(100)`, so a longer name
  — one copied from a browser's suggested download name, say — failed the
  upload with an Internal Server Error and no file attached. The name and
  the path are now unbounded `text`, which costs Postgres nothing, and a
  name too long for the file system itself is trimmed to 255 characters
  with its extension kept rather than failing. Upgrading runs a migration
  that widens the two columns.

## [v1.0] - 2026-10-16

Task lists get easier to work through: every task table sorts by clicking
a column header, the tags page paginates and sorts, search results come
back in the same table as everywhere else, and a task's tags are links on
its own page. Underneath, an operation that writes several rows now
commits as a unit instead of leaving half of itself behind when something
fails part way.

The version number leaves the `0.x` series, which records that Tudor has
been running in production for years rather than any break in
compatibility. Upgrading from v0.16 is like any other upgrade: pull the
new image, and there is nothing else to do.

### Added

- **Sortable task tables** (#145, closes #143). The ID, Summary,
  Deadline, Done?, Deleted?, Order #, Expected Duration, Expected Cost
  and Parent ID headers are links on the index, task, tag and deadlines
  pages; clicking one sorts by that column, clicking it again flips the
  direction, and an arrow marks the current sort. The sort runs in the
  database, so it covers the whole list rather than just the page in
  front of you, and the paging links keep it. Ties are broken by id so
  paging is stable. The hierarchy views keep plain headers, since sorting
  would break the indentation.
- **A task's tags on the task page** (#144, closes #142). They appear as
  chips between the summary and the description, each linking to its
  tag's page. A task with no tags gets no row.
- **A task count on the tags page** (#141, closes #140). Done and deleted
  tasks are counted, and a private task only if the current user can see
  it, so the number matches the list you get by clicking through and
  doesn't give away the existence of someone else's private tasks.
- **Pagination, sorting and descriptions on the tags page** (#139, closes
  #138). `/tags` shows 20 tags per page, overridable with `per_page` and
  navigable with `page` the way the other lists are; the ID and Value
  headers sort the list (`sort=name|id`, `order=asc|desc`, Value
  ascending by default); and a new Description column shows the first 100
  characters of each tag's description.
- **Line breaks inside markdown table cells** (#122). A literal `\n` in a
  description or comment renders as a line break, which a GFM table cell
  otherwise has no way to express.
- This changelog (#150), with the releases back to v0.1 reconstructed
  from the GitHub release notes and the git history.
- **Restructured agent docs** (#149, closes #148). `CLAUDE.md` is a thin
  entry point — commands, configuration, an architecture sketch and the
  development workflow — with the full component breakdown, data flow and
  test structure in `docs/architecture.md`. `AGENTS.md` is a symlink to
  `CLAUDE.md`, so an agent that looks for either finds the same guidance,
  and the README gained a quick start.

### Changed

- **Search results are shown as a task table** (#147, closes #146) — the
  same table as the index and deadlines pages, instead of an unstyled
  list. The page has a title and a heading now too.
- The copyright line in the page footer reads 2017-2026 (#137).

### Fixed

- **An operation that writes several rows no longer leaves part of its
  work behind** (#134). Every persistence write committed on its own, so
  a failure part way through could leave a task with no authorized user,
  an orphaned tag, a half-converted task, a partial purge or a partly
  cloned subtree. Creating a task, adding a tag to a task, converting a
  task to a tag, purging deleted tasks and cloning a subtree now commit
  together or roll back together.
- **Moving a task up or down updates the last-updated date of the
  siblings it moved past** (#135). The update never ran: the tasks to
  update were read from a generator that had already been consumed.

## [v0.16] - 2026-04-16

A container fix: the image serves again under Python 3.12.

### Fixed

- **The container starts under Python 3.12** (#118). gunicorn 20.1.0
  imports `pkg_resources`, which Python 3.12 no longer provides, so
  startup failed with `No module named pkg_resources`. gunicorn is now
  25.3.0, which doesn't need it; v0.15 had worked around the same error
  by adding `setuptools` to the requirements.

### Changed

- The version and revision build arguments are applied at the end of the
  Dockerfile instead of the beginning, so building a new version reuses
  the cached dependency and source layers. The image also carries a
  summary, description and maintainer label.

## [v0.15] - 2026-04-16

Schema migration becomes safe to retry, and applies every script it
should have applied in v0.14.

### Fixed

- **Every migration script that ships with a release is applied** (#116).
  The migration ran up to the app's own `__version__`, but the script
  filenames don't track release numbers — v0.14 shipped `v0.14.sql`,
  `v0.15.sql` and `v0.16.sql` — so upgrading to v0.14 applied the first
  and skipped the other two, leaving a database without the
  notes-to-comments rename the code expected. The target is now the
  highest-numbered script in `persistence/migrations/`, so a release that
  bumps the version without changing the schema no longer looks like a
  pending migration either.
- **A failed migration can be retried** (#116). `__version__` was written
  once at the end of the run, so a failure part way through left the
  database recorded at its old version and the next startup re-ran the
  scripts that had already succeeded. Each script's changes and its
  version bump are now committed together.
- **`v0.14.sql` widens the right table** (#116). It referred to
  `comment`, but the rename from `note` happens in the next script, so
  the migration failed on a v0.13 database.
- **gunicorn starts on Python 3.12** (#116): `setuptools` is now a
  requirement, so the `pkg_resources` gunicorn imports is present. v0.16
  replaces this with a gunicorn that doesn't need it.

### Changed

- The test suite runs in parallel under `pytest-xdist` (#117), down from
  about 187 seconds to about 59, and pytest is upgraded to 9.0.3.

## [v0.14] - 2026-04-06

Notes are renamed to comments and become editable, and the text fields
lose their length limits. The schema changes ship as migration scripts,
but migrating an existing database to this version needs the fixes in
v0.15.

### Added

- **Comments can be edited** (#113). Each comment has a
  `date_last_updated`, set when it is changed, and an "Edited" label
  appears on the ones that have been. `POST /comment/<id>/edit` is the
  new route.
- **A GitHub Actions workflow** runs the tests with coverage and the CSS
  lint on every push to `master` and every pull request.
- `run_local.sh`, for running the app against a local database without
  building an image.

### Changed

- **Notes are now comments** (#112) — in the UI, in the route
  (`POST /note/new` is now `POST /comment/new`), in the export, and in
  the database, where the `note` table is renamed. The export format
  version goes to 2 for the renamed fields; a version 1 export still
  imports.
- **Task descriptions and tag, comment and attachment text are unlimited
  in length** (#111). They were `varchar` columns with fixed limits; they
  are now `text`.
- Dependencies are upgraded to their current versions, targeting Python
  3.12 (#114).

### Fixed

- Import and export bugs around the renamed fields (#112).
- Raw SQL is wrapped in `text()`, which SQLAlchemy 2.0 requires, so
  migrations run instead of raising.

## [v0.13] - 2025-11-30

Two small additions to the task pages, a startup fix, and the move to
SQLAlchemy 2.0.

### Added

- **A `+ Task` link in the navigation bar** (#109), so a new task can be
  started from any page.
- **Cloning a task clones its children** (#105). The Clone button
  previously copied only the task it was on; it now reproduces the whole
  subtree.

### Changed

- Tudor runs on SQLAlchemy 2.0 (#106). Queries, pagination and the
  deprecated `datetime.utcnow()` were updated for it. Little else
  changes, though tasks that tie on the column a list is sorted by are no
  longer ordered by id after it, so their relative order — and the page a
  tied task lands on — is up to the database.
- The test suite runs against PostgreSQL rather than SQLite (#107), so it
  exercises the database Tudor is actually deployed on.

### Fixed

- **The app starts when the database needs migrating.** The schema version
  check and the automatic migration ran outside a Flask application
  context and raised `RuntimeError` instead of upgrading the database.

## [v0.12] - 2025-09-23

A tag with one change to a development script. Nothing in the
application or the image changed, and there is no GitHub release for it.

### Changed

- `run_docker.sh` connects to a different local database, with a
  username and password instead of the bare `postgres` user.

## [v0.11] - 2025-09-23

The running container can say which version and revision it is. There is
no GitHub release for this tag.

### Added

- **The image knows its own version and revision.** `build_docker.sh`
  passes `VERSION` and `REVISION` as build arguments; the Dockerfile
  writes `__version__.py` into the image and sets `TUDOR_REVISION`, and
  labels the image with the version. Outside a git checkout the revision
  is read from `TUDOR_REVISION` rather than reported as `unknown`.

### Changed

- `__version__` is no longer hard-coded in `tudor.py`, so a build no
  longer has to edit the source to set it.
- `run_docker.sh` passes default `TUDOR_PORT`, `TUDOR_SECRET_KEY` and
  `TUDOR_DB_URI` values, the last pointing at a PostgreSQL on the host,
  so it starts without extra arguments.
- `build_docker.sh` prints the `docker push` command for the image it
  built.

## [v0.10] - 2025-07-03

Upgrading no longer means running SQL by hand, tasks record when they
were created and last changed, a task can be cloned, and the error pages
are Tudor's own. There is no GitHub release for this tag.

### Added

- **Automatic database schema migration.** On startup Tudor compares the
  schema version recorded in the database against the scripts in
  `persistence/migrations/` and applies the ones that are missing.
- **`date_created` and `date_last_updated` on tasks** (#99), set when a
  task is created and whenever it changes, and shown on the task page.
  The migration script fills both in for existing tasks.
- **Cloning a task** (#104). A Clone button on the task page opens the
  new-task form with the fields of an existing task filled in.
- **404 and 401 pages** (#103), in Tudor's own layout, with a login form
  on the 401 page, instead of Flask's default error output.
- `run_docker.sh` publishes the container's port, overridable with
  `PORT`.

### Changed

- Dependencies are upgraded, Werkzeug and Flask-Login among them (#100,
  #102).

## [v0.9] - 2023-06-29

A new layout for the task page, and an upgrade to Python 3.11.

### Changed

- **The task page is rebuilt to a more responsive layout.** Breadcrumbs
  show the task's ancestors, the summary leads the page, the task's
  fields and the display options sit in an info panel beside the
  description, child tasks follow the description, and notes and
  attachments are collapsible rows. The layout uses Bootstrap's grid, so
  it reflows on a narrow screen, and task tables are a consistent width.
- **Attachment uploads no longer check the file extension.** The
  allowed-extensions check is disabled, so `TUDOR_ALLOWED_EXTENSIONS` and
  `--allowed-extensions` have no effect on what can be uploaded; any file
  with a name is accepted.
- Markdown is rendered by `pycmarkgfm` instead of `py-gfm`.
- The image runs Python 3.11, and SQLAlchemy, Flask, Werkzeug,
  Flask-Login and GitPython are upgraded with it.

## [v0.8] - 2022-08-25

### Fixed

- **A failure while fetching an attachment is logged.** The exception was
  swallowed, leaving nothing to diagnose a download that didn't work.

## [v0.7] - 2021-03-12

Case-insensitive search, and import/export errors that say what went
wrong.

### Changed

- **Search is case-insensitive.** Searching for `Email` now also matches
  `email` in a summary or description.
- MySQL and MariaDB are no longer referenced anywhere; PostgreSQL is the
  only supported database.

### Fixed

- **Importing data that contains attachments works.** The imported task
  was assigned to the JSON dict rather than to the attachment it
  described, which raised an `AttributeError` part way through the
  import.
- **An import says which record failed and why.** Errors were caught in
  one block around the whole import and reported without the exception
  that caused them; they are now handled per record and include it. JSON
  decoding is handled correctly too.

## [v0.6] - 2020-11-13

PostgreSQL becomes the primary supported database, and configuration
stops fighting with its own defaults.

### Added

- **`TUDOR_DB_OPTIONS` and `TUDOR_DB_OPTIONS_FILE`**, taking `key=value`
  pairs separated by whitespace and passing them to the ORM as engine
  options. TLS parameters go here, which is what an encrypted connection
  to PostgreSQL needs.
- The image installs `psycopg2`, replacing `pg8000`.

### Fixed

- **A file-based setting is no longer overridden by a default.**
  `TUDOR_DB_URI` and `TUDOR_SECRET_KEY` had defaults, and those defaults
  counted as values, so `TUDOR_DB_URI_FILE` and `TUDOR_SECRET_KEY_FILE`
  were ignored. The fallback to a default now happens only after the
  file, environment and command-line sources have been resolved, and the
  same applies to the other settings, debug mode among them.
- **The database URI and secret key are printed at startup only in debug
  mode**, instead of appearing in the logs of every deployment.

## [v0.5] - 2020-09-24

Credentials can be read from files instead of the environment.

### Added

- **`TUDOR_SECRET_KEY_FILE` and `TUDOR_DB_URI_FILE`**, which read the
  secret key and the database URI from a file rather than an environment
  variable or a command-line argument — easier to keep out of a process
  list or an image.
- Clearer messages when a configuration value is missing or unreadable.

### Changed

- Command-line arguments fall back to the corresponding `TUDOR_*`
  environment variable when they are not given.

## [v0.4] - 2020-08-27

Import and export from the command line.

### Added

- **`--export-db` and `--import-db`**, which write every record — tasks,
  tags, notes, attachment records (not the files themselves), users and
  options — to stdout as JSON, and read the same back in. The web UI
  already did this; now a backup or a transfer can be scripted.
- A `format_version` field in the exported data, so a later format can be
  told from this one.
- The image installs the `pg8000` PostgreSQL driver by default.

### Changed

- Diagnostic output goes to stderr, leaving stdout for the exported data
  alone.

## [v0.3] - 2020-07-02

### Fixed

- **Logging in with an `Authorization` header no longer risks a crash.**
  The decoded credentials were bytes and were split against a string,
  which raises on Python 3. Not a security hole, but a potential 500.

### Added

- `build_docker.sh` and `run_docker.sh`, for building and running the
  image.
- `RELEASING.md`, describing how a release is cut.
- Startup prints the version number alongside the revision.

## [v0.2] - 2019-10-01

Python 3, and an image a seventh of the size.

### Changed

- **Tudor runs on Python 3.7** instead of Python 2.7, with every
  dependency updated to a version that supports it.
- **The container image is 131 MB**, down from over 900 MB, on an Alpine
  base.

### Added

- **`--create-user`**, which creates a user from the command line, given
  an email address and a hashed password, and optionally makes them an
  admin.

## [v0.1] - 2018-05-17

First versioned release. The tag sits on the merge that containerized the
app (#70); the code itself goes back to 2015, and this section describes
what it could do by the time it was given a version number.

### Added

- Tasks with a summary, a markdown description, a deadline, an expected
  duration and cost, done and deleted flags, and an order number that
  can be changed by moving a task up, down, to the top or to the bottom
  of its list. Tasks nest, so a task can be the parent of others.
- A flat list, a hierarchical view and a deadline view of the tasks, all
  paginated, with done and deleted tasks shown or hidden.
- Tags, notes and file attachments on a task; a tag page listing the
  tasks that carry it; converting a task into a tag; and search across
  summaries and descriptions.
- Dependencies between tasks, and prioritization of one task before or
  after another.
- Users with a login, per-task authorization, public and private tasks,
  and an admin flag.
- Import and export of the whole database as JSON through the web UI, and
  options stored in the database.
- Command-line operations: `--create-db`, `--create-secret-key`,
  `--hash-password`, `--make-public` and `--make-private` (optionally
  with `--descendants`), and `--test-db-conn`.
- Configuration from `TUDOR_*` environment variables or command-line
  arguments: the database URI, the host and port, the upload folder and
  allowed extensions, the secret key, and debug mode.
- A Dockerfile that runs the app under gunicorn, creating the database
  schema on startup if it isn't there.

[Unreleased]: https://github.com/izrik/tudor/compare/v1.0...HEAD
[v1.0]: https://github.com/izrik/tudor/compare/v0.16...v1.0
[v0.16]: https://github.com/izrik/tudor/compare/v0.15...v0.16
[v0.15]: https://github.com/izrik/tudor/compare/v0.14...v0.15
[v0.14]: https://github.com/izrik/tudor/compare/v0.13...v0.14
[v0.13]: https://github.com/izrik/tudor/compare/v0.12...v0.13
[v0.12]: https://github.com/izrik/tudor/compare/v0.11...v0.12
[v0.11]: https://github.com/izrik/tudor/compare/v0.10...v0.11
[v0.10]: https://github.com/izrik/tudor/compare/v0.9...v0.10
[v0.9]: https://github.com/izrik/tudor/compare/v0.8...v0.9
[v0.8]: https://github.com/izrik/tudor/compare/v0.7...v0.8
[v0.7]: https://github.com/izrik/tudor/compare/v0.6...v0.7
[v0.6]: https://github.com/izrik/tudor/compare/v0.5...v0.6
[v0.5]: https://github.com/izrik/tudor/compare/v0.4...v0.5
[v0.4]: https://github.com/izrik/tudor/compare/v0.3...v0.4
[v0.3]: https://github.com/izrik/tudor/compare/v0.2...v0.3
[v0.2]: https://github.com/izrik/tudor/compare/v0.1...v0.2
[v0.1]: https://github.com/izrik/tudor/releases/tag/v0.1
