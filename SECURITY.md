# Security Policy

## Reporting a vulnerability

Please don't open a public issue for a security problem — that tells everyone
about it before there's a fix.

Instead, use one of these:

- **GitHub's private vulnerability reporting** — go to the
  [Security tab](https://github.com/izrik/tudor/security) and choose "Report a
  vulnerability". This is the preferred route: it's private, and the report and
  the discussion stay in one place.
- **A direct message to the maintainer**, [@izrik](https://github.com/izrik), if
  for some reason private reporting isn't available to you.

Include enough to reproduce it: what you did, what happened, and what you
expected. A proof of concept against a local instance is welcome.

## Scope

In scope:

- The code in this repository.
- The instances of Tudor we run.

Not in scope:

- Third-party dependencies. If the bug is in Flask, SQLAlchemy, or anything else
  in `requirements.txt`, please report it to that project; we'll pick up the fix
  when they release it. If a dependency has a published advisory that this repo
  hasn't acted on yet, an ordinary public issue is the right place for that.
- Anything you'd have to attack a running production system to find. Please
  don't test against instances you don't own — run Tudor locally instead
  (`./run_local.sh`, or see the [README](README.md)).

## What to expect

Tudor is maintained by one person in their spare time, so this section promises
only what one person can keep:

- An acknowledgement that the report arrived and was read.
- A fix, when the finding is real and the fix is affordable. If it isn't
  affordable, we'll say so rather than leave the report unanswered.
- Credit for the report, if you want it, in the
  [changelog](CHANGELOG.md) entry for the fix.

There is no bounty, and no committed response time — writing a number here that
nobody is on the hook for would be worse than saying nothing.

## Supported versions

Tudor ships from `master` and tags releases without maintaining release
branches, so the supported versions are **the latest release and `master`**.
Fixes land on `master` and go out in the next release; older tags don't get
backports.
