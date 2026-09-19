# Stack: Python

Detect: `pyproject.toml` / `setup.py` / `requirements*.txt`. Package manager by lockfile: `uv.lock` → uv; `poetry.lock` → poetry; `Pipfile.lock` → pipenv; else pip + venv. **Keep whatever the repo uses.** The commands below assume uv; substitute `poetry run` / plain venv activation otherwise.

## Tools — use what exists, add only when nothing does

| Role | Existing tool wins | Default when absent |
| --- | --- | --- |
| Format | `black` (+ `isort`), `ruff format`, `yapf` | `ruff format` |
| Lint | `ruff`, `flake8`, `pylint` | `ruff check` |
| Typecheck | `mypy`, `pyright` (look for `[tool.mypy]`, `pyrightconfig.json`) | `mypy` if the code has annotations; otherwise leave `typecheck` out and note it |
| Test | `pytest` (nearly always), `unittest` | `pytest` |
| Coverage | `pytest-cov` / `coverage` | `pytest-cov` |

Do not add ruff to a Black+flake8 repo "for consistency"; two formatters fight.

## Commands (fill AGENTS.md#commands; run every one in Step 4)

```sh
uv sync                                   # install; poetry install / pip install -e ".[dev]"
ruff format --check .                     # format check — fix: ruff format .
ruff check .                              # lint     — fix: ruff check --fix .
mypy src                                  # typecheck (or: pyright)
pytest tests/<module> -q                  # test subset
pytest -q --cov=src --cov-report=term-missing --cov-fail-under=<<N>>   # test + coverage gate
bash checks/check docs                    # docs gates
```

With Black/isort/flake8 instead: `black --check .`, `isort --check-only .`, `flake8`.

## `check` entry point wiring

Prefer an existing runner: a `justfile` recipe, `nox`/`tox` session, or `make check`. If none, `pyproject.toml` scripts do not run shell, so add a justfile only if the user agrees; otherwise document `bash checks/check <group>` directly (that is acceptable — the registry is `ls checks/`).

```just
check group="all":
    bash checks/check {{group}}
```

## CI setup steps

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "<<3.12 — from pyproject requires-python>>"
      - uses: astral-sh/setup-uv@v5      # drop for pip/poetry
      - run: uv sync --all-extras --dev  # or: pip install -e ".[dev]" / poetry install
```

`test` job body: `uv run pytest -q --cov=src --cov-report=xml --cov-fail-under=<<N>>`. Matrix over Python versions only if `requires-python` spans more than one minor and the repo tests them today.

## Hooks

`.githooks/` (zero-dependency; install via `git config core.hooksPath .githooks`, added to the setup step):

```sh
#!/usr/bin/env bash
# .githooks/pre-commit — staged Python files only
set -euo pipefail
files=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')
[[ -z "$files" ]] && exit 0
ruff format --check $files || { echo "fix: ruff format $files"; exit 1; }
ruff check $files
```
```sh
#!/usr/bin/env bash
# .githooks/commit-msg
exec bash checks/verify-commit-convention.sh --file "$1"
```

`pre-commit` framework (`.pre-commit-config.yaml`) when the repo already uses it:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <<pin>>
    hooks: [{ id: ruff-format }, { id: ruff, args: [--fix] }]
  - repo: local
    hooks:
      - id: commit-convention
        name: commit convention
        entry: bash checks/verify-commit-convention.sh --file
        language: system
        stages: [commit-msg]
```

## Language-specific rules worth adding to engineering-standards.md (pick ≤ 3 the survey shows are needed)

- `from __future__ import annotations` / explicit `Optional` policy per the repo's minimum Python.
- No bare `except:`; `except Exception` names the reason in a comment.
- Dataclasses / pydantic models are `frozen=True` unless mutation is the point.
- `pathlib` over `os.path`; no string path concatenation.
- Tests use fixtures for resources; no module-level state in tests.

## Module detection

Packages under `src/<pkg>/<sub>/` (src layout) or `<pkg>/<sub>/` — each directory with an `__init__.py` directly under the top package is a module candidate. Skip `__pycache__`, `tests/`, `migrations/` (list migrations as a protected path in Boundaries instead).
