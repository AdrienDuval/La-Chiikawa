# TD 2 screenshots

Key evidence for the report (19/10/2026): one working result and, where useful, one error.

| Topic | File | Shows |
|---|---|---|
| Python project | `1-python-project/02-uv-init-project.png` | `uv init` creates the `chiikawa` package |
| Python project | `1-python-project/05-pytest-3-passed.png` | ✅ 3 tests pass on Python 3.12 |
| Code quality | `2-ruff/04-ruff-format-check-diff.png` | ❌ the formatter shows what it would change |
| Code quality | `2-ruff/06-all-local-checks-pass.png` | ✅ lint, format and tests all pass locally |
| CI | `3-ci/01-ci-run1-green.png` | ✅ first CI run: install, lint, format, tests |
| CI | `3-ci/03-ci-run2-red-broken-test.png` | ❌ a failing test blocks the build (broken on purpose) |
| Docker | `4-docker/01-docker-build-and-run.png` | ✅ image builds (cached layers) and runs locally |
| Docker | `4-docker/02-ci-checks-then-docker-green.png` | ✅ CI: `checks` then `docker` job, both green |
