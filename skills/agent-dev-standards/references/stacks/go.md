# Stack: Go

Detect: `go.mod`. Multi-module: `go.work`. Modules for `modules.txt` are the top-level packages under `internal/`, `pkg/`, `cmd/` (one entry per package directory that has non-test `.go` files). Task runner: `Makefile` is common in Go repos — use it if present; else `justfile` or `mage`. No `typecheck` job — `go vet`/`go build` owns it.

## Tools

| Role | Tool | Notes |
| --- | --- | --- |
| Format | `gofmt -l .` (fails if it prints anything) or `gofumpt -l .` if the repo uses it; `goimports` for import grouping | Keep `gofumpt` only if already adopted |
| Lint | `golangci-lint run` with the repo's `.golangci.yml`; else `go vet ./... && staticcheck ./...` | Adding golangci-lint to a repo without it is an *ask first* dependency |
| Test | `go test ./...` with `-race` | |
| Coverage | `go test -coverprofile=cover.out ./...` then a threshold check | Go has no built-in fail-under; use the snippet below |

## Commands

```sh
go build ./...
test -z "$(gofmt -l .)"                         # format — fix: gofmt -w .
go vet ./... && golangci-lint run               # lint
go test -race ./<<pkg>>/...                     # test subset
go test -race -coverprofile=cover.out ./... && bash checks/verify-coverage-threshold.sh cover.out <<N>>
bash checks/check docs
```

Coverage threshold script (add to `checks/` as another verify script):

```sh
#!/usr/bin/env bash
# verify-coverage-threshold <profile> <min-percent>
set -euo pipefail
total=$(go tool cover -func="$1" | awk '/^total:/ {gsub("%","",$3); print $3}')
awk -v t="$total" -v m="$2" 'BEGIN { if (t+0 < m+0) { printf "coverage %.1f%% is below %s%%\n  fix: add tests for the uncovered paths (go tool cover -html=%s)\n", t, m, ARGV[1]; exit 1 } else printf "verify-coverage-threshold: ok (%.1f%% >= %s%%)\n", t, m }' "$1"
```

## `check` wiring

```make
.PHONY: check
check:
	bash checks/check $(or $(GROUP),all)
```
(`make check GROUP=docs`). Or a justfile recipe. Note the Makefile tab.

## CI setup steps

```yaml
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
```

`lint` job: `golangci/golangci-lint-action@v6` with the repo's version pin, or `go vet ./...` when no linter is adopted. `test` job: the coverage command above. Matrix over OS when the code touches the filesystem or processes.

## Hooks

`.githooks/pre-commit`:

```sh
#!/usr/bin/env bash
set -euo pipefail
files=$(git diff --cached --name-only --diff-filter=ACM -- '*.go')
[[ -z "$files" ]] && exit 0
bad=$(gofmt -l $files); [[ -z "$bad" ]] || { echo "unformatted: $bad"; echo "fix: gofmt -w $bad"; exit 1; }
go vet $(go list -f '{{.Dir}}' $(dirname $files | sort -u | sed 's|^|./|') 2>/dev/null) || true
```
`.githooks/commit-msg`: `exec bash checks/verify-commit-convention.sh --file "$1"`. Install: `git config core.hooksPath .githooks` in the setup target.

## Language-specific rules (≤ 3)

- `context.Context` is the first parameter of anything that does I/O; never stored in a struct.
- Errors are wrapped with `%w` and the operation that failed (`fmt.Errorf("open config %s: %w", path, err)`); checked with `errors.Is/As`, never string-matched.
- Accept interfaces, return structs; define interfaces where they are consumed, not where they are implemented.
- No `init()` with side effects; no package-level mutable state outside `main`.
- Table-driven tests with `t.Run`; `t.Parallel()` when the test owns its state.

## Module detection

Every directory under `internal/`, `pkg/`, `cmd/` containing non-`_test.go` files; skip `vendor/`, generated `*.pb.go` directories (list under Boundaries → Never edit).
