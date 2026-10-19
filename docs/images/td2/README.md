# TD 2 screenshots

Evidence for the report, in the order things happened (19/10/2026).

## 1. Python project (uv + pytest)
| File | Shows | Use in the report for |
|---|---|---|
| `1-python-project/01-uv-not-on-path-troubleshooting.png` | `uv` not found until PATH is refreshed | Troubleshooting / setup notes |
| `1-python-project/02-uv-init-project.png` | `uv init` creates the `chiikawa` package | Project setup |
| `1-python-project/03-uv-run-and-add-pytest.png` | `.venv` created, pytest added, `uv.lock` written | Reproducible environment |
| `1-python-project/04-canonical-url-manual-check.png` | `canonical_url` removes tracking parameters | First function (deduplication) |
| `1-python-project/05-pytest-3-passed.png` | 3 tests pass on Python 3.12 | First tests |
| `1-python-project/06-first-push.png` | Project pushed to GitHub | Version control |

## 2. Code quality (ruff)
| File | Shows | Use in the report for |
|---|---|---|
| `2-ruff/01-ruff-check-finds-I001.png` | ruff finds an import-order problem | Linting catches issues |
| `2-ruff/02-ruff-check-fix.png` | `ruff check --fix` repairs it | Automatic fixes |
| `2-ruff/03-ruff-format-has-no-fix-flag.png` | `format` has no `--fix` flag | Troubleshooting |
| `2-ruff/04-ruff-format-check-diff.png` | What the formatter would change | Consistent style |
| `2-ruff/05-ruff-format-applied.png` | Files reformatted | Consistent style |
| `2-ruff/06-all-local-checks-pass.png` | Lint, format and tests all pass locally | Checks before pushing |
| `2-ruff/07-ruff-commit-push.png` | ruff setup pushed | Version control |

## 3. Continuous integration (GitHub Actions)
| File | Shows | Use in the report for |
|---|---|---|
| `3-ci/01-ci-run1-green.png` | First CI run green: install, lint, format, tests | CI works |
| `3-ci/02-ci-annotations-node20-ubuntu.png` | Warnings: old Node.js in setup-uv, `ubuntu-latest` will change | Why we pin versions |
| `3-ci/03-ci-run2-red-broken-test.png` | Run broken on purpose: a failing test blocks the build | CI protects `main` |
| `3-ci/04-ci-red-format-step.png` | Badly formatted code also blocks the build; later steps skipped | CI protects code quality |
