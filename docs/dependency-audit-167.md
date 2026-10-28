# Dependency vulnerability verification — #167

Verified 2026-10-28. The requested pins already landed in [#169](https://github.com/izrik/tudor/pull/169) (GitPython 3.2.1, after #121 moved it to 3.1.50) and [#170](https://github.com/izrik/tudor/pull/170) (Werkzeug 3.1.9). This report completes the triage and verification without unrelated dependency changes or suppressions.

## Decision and compatibility

Keep Werkzeug 3.1.9 and GitPython 3.2.1: these are the lowest versions clearing all reported findings. GitPython 3.1.60 leaves CVE-2026-114145 open, plus five additional advisories now reported against the original pin and fixed in 3.2.0. No advisories are deferred.

The issue calls 3.1.46 → 3.1.60 “minor” and → 3.2.1 “major”. Numerically these are patch and minor changes respectively; the table uses those conventional version-component classifications, without assuming API compatibility from numbering alone.

`rg -n '\bgit\b|GitPython' tests/` finds no direct calls. The only import is optional in `tudor.py`: `git.Repo('.').git.describe(tags=True, dirty=True, always=True, abbrev=40)` computes the revision string when the application is imported. Tests exercise application imports; no source changes are needed for 3.2.1. GitPython is declared directly in the test manifest, while Werkzeug is a direct runtime dependency.

The ecosystem template linked in #167 returned HTTP 404 through GitHub's API; the explicit rules reproduced in #167 were followed.

## Advisory triage

Severity and advisory links come from GitHub's advisory records (including fixed Dependabot alerts); minimum fixes and duplicate counts come from pip-audit 2.10.1 against the original pins. Each unique ID appears once below. “Rows” preserves duplicate entries in the audit output. All dependencies below are direct. Original versions are Werkzeug 3.1.8 and GitPython 3.1.46; final versions are 3.1.9 and 3.2.1 respectively.

| Package | Advisory | Severity | Original | Lowest fix | Change to lowest fix | Rows |
| --- | --- | --- | --- | --- | --- | --- |
| werkzeug | [PYSEC-2026-4312](https://github.com/advisories/GHSA-g6x2-hccm-hh4m) | medium | 3.1.8 | 3.1.9 | patch | 1 |
| gitpython | [PYSEC-2026-2160](https://github.com/advisories/GHSA-rpm5-65cw-6hj4) | high | 3.1.46 | 3.1.47 | patch | 2 |
| gitpython | [PYSEC-2026-2161](https://github.com/advisories/GHSA-x2qx-6953-8485) | high | 3.1.46 | 3.1.47 | patch | 2 |
| gitpython | [PYSEC-2026-2163](https://github.com/advisories/GHSA-v87r-6q3f-2j67) | high | 3.1.46 | 3.1.49 | patch | 2 |
| gitpython | [PYSEC-2026-3984](https://github.com/advisories/GHSA-g5vv-9gxw-82hx) | high | 3.1.46 | 3.1.60 | patch | 2 |
| gitpython | [PYSEC-2026-3980](https://github.com/advisories/GHSA-mv93-w799-cj2w) | high | 3.1.46 | 3.1.50 | patch | 1 |
| gitpython | [PYSEC-2026-3982](https://github.com/advisories/GHSA-239g-whfq-7xj9) | high | 3.1.46 | 3.1.60 | patch | 1 |
| gitpython | [PYSEC-2026-3981](https://github.com/advisories/GHSA-3rp5-jjmw-4wv2) | high | 3.1.46 | 3.1.53 | patch | 2 |
| gitpython | [PYSEC-2026-2162](https://github.com/advisories/GHSA-7545-fcxq-7j24) | high | 3.1.46 | 3.1.48 | patch | 1 |
| gitpython | [PYSEC-2026-3836](https://github.com/advisories/GHSA-2f96-g7mh-g2hx) | high | 3.1.46 | 3.1.51 | patch | 2 |
| gitpython | [PYSEC-2026-3995](https://github.com/advisories/GHSA-fjr4-x663-mwxc) | high | 3.1.46 | 3.1.54 | patch | 1 |
| gitpython | [PYSEC-2026-3951](https://github.com/advisories/GHSA-94p4-4cq8-9g67) | high | 3.1.46 | 3.1.55 | patch | 2 |
| gitpython | [PYSEC-2026-3783](https://github.com/advisories/GHSA-jm78-9fvv-mhgr) | high | 3.1.46 | 3.1.58 | patch | 2 |
| gitpython | [PYSEC-2026-3785](https://github.com/advisories/GHSA-7833-fr7j-v32q) | high | 3.1.46 | 3.1.59 | patch | 1 |
| gitpython | [PYSEC-2026-3786](https://github.com/advisories/GHSA-284h-m62q-gf8w) | critical | 3.1.46 | 3.1.59 | patch | 2 |
| gitpython | [PYSEC-2026-3787](https://github.com/advisories/GHSA-8mcc-hrx5-hvxc) | high | 3.1.46 | 3.1.59 | patch | 2 |
| gitpython | [PYSEC-2026-3788](https://github.com/advisories/GHSA-5xxx-qhh7-9287) | medium | 3.1.46 | 3.1.59 | patch | 2 |
| gitpython | [PYSEC-2026-3784](https://github.com/advisories/GHSA-hmq2-w58f-27jc) | high | 3.1.46 | 3.1.58 | patch | 1 |
| gitpython | [PYSEC-2026-3837](https://github.com/advisories/GHSA-3wxw-xv34-2frg) | medium | 3.1.46 | 3.1.59 | patch | 2 |
| gitpython | [PYSEC-2026-3840](https://github.com/advisories/GHSA-9rj7-rf2p-w77r) | high | 3.1.46 | 3.1.58 | patch | 1 |
| gitpython | [PYSEC-2026-3838](https://github.com/advisories/GHSA-4gmw-gg2m-w46p) | high | 3.1.46 | 3.1.58 | patch | 1 |
| gitpython | [PYSEC-2026-3839](https://github.com/advisories/GHSA-956x-8gvw-wg5v) | high | 3.1.46 | 3.1.51 | patch | 1 |
| gitpython | [PYSEC-2026-3841](https://github.com/advisories/GHSA-hh9p-6wh2-4mfc) | medium | 3.1.46 | 3.1.58 | patch | 1 |
| gitpython | [PYSEC-2026-3843](https://github.com/advisories/GHSA-wvpp-8hx9-p66j) | high | 3.1.46 | 3.1.58 | patch | 1 |
| gitpython | [PYSEC-2026-3949](https://github.com/advisories/GHSA-3f7w-8rr8-f37f) | high | 3.1.46 | 3.1.57 | patch | 1 |
| gitpython | [PYSEC-2026-3953](https://github.com/advisories/GHSA-r9mr-m37c-5fr3) | high | 3.1.46 | 3.1.54 | patch | 1 |
| gitpython | [PYSEC-2026-3952](https://github.com/advisories/GHSA-6p8h-3wgx-97gf) | high | 3.1.46 | 3.1.54 | patch | 1 |
| gitpython | [PYSEC-2026-3950](https://github.com/advisories/GHSA-p538-c434-8v24) | medium | 3.1.46 | 3.1.56 | patch | 1 |
| gitpython | [PYSEC-2026-3948](https://github.com/advisories/GHSA-539m-9xh6-q6rr) | medium | 3.1.46 | 3.1.57 | patch | 1 |
| gitpython | [CVE-2026-114145](https://github.com/advisories/GHSA-83vg-56qc-22m7) | high | 3.1.46 | 3.2.1 | minor | 1 |
| gitpython | [CVE-2026-110859](https://github.com/advisories/GHSA-23mf-xhv8-69c2) | high | 3.1.46 | 3.2.0 | minor | 1 |
| gitpython | [CVE-2026-110858](https://github.com/advisories/GHSA-f9j4-qggq-h239) | high | 3.1.46 | 3.2.0 | minor | 1 |
| gitpython | [CVE-2026-110856](https://github.com/advisories/GHSA-m64x-33q8-m5h7) | high | 3.1.46 | 3.2.0 | minor | 1 |
| gitpython | [CVE-2026-110857](https://github.com/advisories/GHSA-w8jc-g24h-crhw) | high | 3.1.46 | 3.2.0 | minor | 1 |
| gitpython | [CVE-2026-110855](https://github.com/advisories/GHSA-fx3j-rwgx-fr94) | medium | 3.1.46 | 3.2.0 | minor | 1 |

## Audit evidence

Exact command (pip-audit 2.10.1):

```sh
pip-audit -r requirements.txt -r dev-requirements.txt -r test_requirements.txt
```

The issue's 2026-10-24 baseline reported 42 findings. Rechecking on 2026-10-28 reports 47 findings against the original pins, including five subsequently reported CVEs. To reproduce the baseline without changing the checkout:

```sh
mkdir -p /tmp/tudor167-before
sed 's/Werkzeug==3.1.9/Werkzeug==3.1.8/' requirements.txt > /tmp/tudor167-before/requirements.txt
sed 's/GitPython==3.2.1/GitPython==3.1.46/' test_requirements.txt > /tmp/tudor167-before/test_requirements.txt
pip-audit -r /tmp/tudor167-before/requirements.txt -r dev-requirements.txt -r /tmp/tudor167-before/test_requirements.txt
```

Before (exit 1; tabular rendering of the captured JSON audit):

```text
Found 47 known vulnerabilities in 2 packages
Name Version ID Fix Versions
werkzeug 3.1.8 PYSEC-2026-4312 3.1.9
gitpython 3.1.46 PYSEC-2026-2160 3.1.47
gitpython 3.1.46 PYSEC-2026-2161 3.1.47
gitpython 3.1.46 PYSEC-2026-2163 3.1.49
gitpython 3.1.46 PYSEC-2026-3984 3.1.60
gitpython 3.1.46 PYSEC-2026-3980 3.1.50
gitpython 3.1.46 PYSEC-2026-3982 3.1.60
gitpython 3.1.46 PYSEC-2026-3981 3.1.53
gitpython 3.1.46 PYSEC-2026-2161 3.1.47
gitpython 3.1.46 PYSEC-2026-2160 3.1.47
gitpython 3.1.46 PYSEC-2026-2162 3.1.48
gitpython 3.1.46 PYSEC-2026-2163 3.1.49
gitpython 3.1.46 PYSEC-2026-3836 3.1.51
gitpython 3.1.46 PYSEC-2026-3995 3.1.54
gitpython 3.1.46 PYSEC-2026-3981 3.1.53
gitpython 3.1.46 PYSEC-2026-3951 3.1.55
gitpython 3.1.46 PYSEC-2026-3783 3.1.58
gitpython 3.1.46 PYSEC-2026-3984 3.1.60
gitpython 3.1.46 PYSEC-2026-3785 3.1.59
gitpython 3.1.46 PYSEC-2026-3786 3.1.59
gitpython 3.1.46 PYSEC-2026-3783 3.1.58
gitpython 3.1.46 PYSEC-2026-3787 3.1.59
gitpython 3.1.46 PYSEC-2026-3788 3.1.59
gitpython 3.1.46 PYSEC-2026-3784 3.1.58
gitpython 3.1.46 PYSEC-2026-3786 3.1.59
gitpython 3.1.46 PYSEC-2026-3787 3.1.59
gitpython 3.1.46 PYSEC-2026-3788 3.1.59
gitpython 3.1.46 PYSEC-2026-3837 3.1.59
gitpython 3.1.46 PYSEC-2026-3840 3.1.58
gitpython 3.1.46 PYSEC-2026-3836 3.1.51
gitpython 3.1.46 PYSEC-2026-3838 3.1.58
gitpython 3.1.46 PYSEC-2026-3839 3.1.51
gitpython 3.1.46 PYSEC-2026-3841 3.1.58
gitpython 3.1.46 PYSEC-2026-3837 3.1.59
gitpython 3.1.46 PYSEC-2026-3843 3.1.58
gitpython 3.1.46 PYSEC-2026-3949 3.1.57
gitpython 3.1.46 PYSEC-2026-3951 3.1.55
gitpython 3.1.46 PYSEC-2026-3953 3.1.54
gitpython 3.1.46 PYSEC-2026-3952 3.1.54
gitpython 3.1.46 PYSEC-2026-3950 3.1.56
gitpython 3.1.46 PYSEC-2026-3948 3.1.57
gitpython 3.1.46 CVE-2026-114145 3.2.1
gitpython 3.1.46 CVE-2026-110859 3.2.0
gitpython 3.1.46 CVE-2026-110858 3.2.0
gitpython 3.1.46 CVE-2026-110856 3.2.0
gitpython 3.1.46 CVE-2026-110857 3.2.0
gitpython 3.1.46 CVE-2026-110855 3.2.0
```

After, against the committed manifests (exit 0):

```text
No known vulnerabilities found
```

GitHub check, 2026-10-28:

```sh
gh api 'repos/izrik/tudor/dependabot/alerts?state=open&per_page=100' --jq 'length'
```

```text
0
```

No remaining advisories require follow-up issues. The deferred CI audit job and ecosystem status update remain follow-up work as described in #167.

## Validation environment

Installed all three manifests into a new Python 3.11.17 virtual environment; `pip check` reports no broken requirements. CI uses Python 3.12, so this local run does not replace that CI result. Installed csslint through npm outside the checkout.

This container initially lacked libpq and PostgreSQL executables. Supplied `psycopg[binary]==3.3.6` (matching the resolved psycopg version) in the temporary environment, and extracted Debian PostgreSQL 17.11 and its libraries outside the checkout. No manifest changes were made for this environment setup. The initial incomplete run was stopped after confirming missing `pg_config` setup errors, then the complete check was restarted with the explicit PostgreSQL executable:

```sh
export LD_LIBRARY_PATH=/tmp/tudor167-pg/root/usr/lib/x86_64-linux-gnu
./run_tests_with_coverage.sh --postgresql-exec=/tmp/tudor167-pg/root/usr/lib/postgresql/17/bin/pg_ctl
```

Application import with GitPython 3.2.1 successfully produced the checkout revision via `git describe`.

Full check result (exit 0):

```text
1568 passed, 1 skipped, 15 warnings in 986.95s (0:16:26)
Wrote HTML report to htmlcov/index.html
csslint: No errors in static/tudor.css.
```

Warnings include SQLAlchemy detached dynamic relationships; they did not fail the check. No tests were excluded to accommodate the dependency updates.
