# Stack: TypeScript / JavaScript

Detect: `package.json`. Package manager by lockfile: `pnpm-lock.yaml` → pnpm; `bun.lock`/`bun.lockb` → bun; `yarn.lock` → yarn; `package-lock.json` → npm. Also honor `packageManager` in `package.json`. **Never switch the package manager.** Monorepo: `pnpm-workspace.yaml`, `workspaces` field, `turbo.json`, `nx.json` — modules are then the workspace packages.

## Tools — use what exists, add only when nothing does

| Role | Existing tool wins | Default when absent |
| --- | --- | --- |
| Format | `prettier`, `oxfmt`, `biome format`, `dprint` | `prettier` |
| Lint | `eslint`, `oxlint`, `biome lint` | `eslint` (flat config) — or `biome` if the user prefers one tool for both |
| Typecheck | `tsc --noEmit` (`tsconfig.json`), `tsgo` | `tsc --noEmit` |
| Test | `vitest`, `jest`, `bun test`, `node --test`, `mocha` | `vitest` |
| Coverage | `vitest --coverage` (`@vitest/coverage-v8`), `jest --coverage`, `c8` | `@vitest/coverage-v8` |

Biome replaces both prettier and eslint; do not run it beside them.

## Commands

```sh
pnpm install --frozen-lockfile              # install
pnpm prettier --check .                     # format — fix: pnpm prettier --write .
pnpm eslint .                               # lint   — fix: pnpm eslint --fix .
pnpm tsc --noEmit                           # typecheck (monorepo: pnpm -r exec tsc --noEmit, or tsc -b)
pnpm vitest run <path>                      # test subset
pnpm vitest run --coverage                  # coverage; thresholds in vitest.config.ts
bash checks/check docs
```

Prefer the repo's own `package.json` scripts (`pnpm test`, `pnpm lint`) in AGENTS.md when they exist and do the same thing — one home.

Coverage threshold lives in config, not the command:

```ts
// vitest.config.ts
test: { coverage: { provider: "v8", thresholds: { lines: <<N>>, branches: <<N-10>> }, include: ["src/**"] } }
```

## `check` entry point wiring

```json
"scripts": {
  "check": "bash checks/check",
  "check:docs": "bash checks/check docs"
}
```

Then `pnpm check docs` / `pnpm check all`. In a monorepo put it in the root `package.json` only.

## CI setup steps

```yaml
      - uses: pnpm/action-setup@v4          # drop for npm/yarn/bun
      - uses: actions/setup-node@v4
        with:
          node-version-file: ".nvmrc"       # or package.json engines / node-version: "22"
          cache: pnpm
      - run: pnpm install --frozen-lockfile
```

Bun: `oven-sh/setup-bun@v2` and `bun install --frozen-lockfile`.

`test` job body: `pnpm vitest run --coverage` (thresholds fail the run). Add `windows-latest` to the matrix only if the project ships a CLI or touches paths/processes.

## Hooks

`.githooks/pre-commit` (zero-dependency) runs the formatter and linter on staged files:

```sh
#!/usr/bin/env bash
set -euo pipefail
files=$(git diff --cached --name-only --diff-filter=ACM -- '*.ts' '*.tsx' '*.js' '*.mjs' '*.json' '*.md')
[[ -z "$files" ]] && exit 0
pnpm prettier --check $files || { echo "fix: pnpm prettier --write <files>"; exit 1; }
pnpm eslint $(printf '%s\n' $files | grep -E '\.(ts|tsx|js|mjs)$' || true)
```
`.githooks/commit-msg`: `exec bash checks/verify-commit-convention.sh --file "$1"`.

Install: `"prepare": "git config core.hooksPath .githooks"` in `package.json` scripts — runs on every `pnpm install`, so nobody has to remember.

If the repo already uses husky + lint-staged or lefthook, add the `commit-msg` step there instead of introducing `.githooks`. With husky and commitlint present, keep commitlint and point `commit-types.txt` at the same type list (or delete `commit-types.txt` and let commitlint be the home — one home per fact).

## Language-specific rules worth adding to engineering-standards.md (≤ 3)

- ESM only; `.ts` extensions in relative imports if the toolchain requires them (note which).
- No `any`; `unknown` + narrowing. `as` casts need an adjacent reason.
- No default exports except where the framework demands (state which).
- `readonly` / `as const` for data that must not change; exhaustive `switch` with a `never` check.
- Zod/valibot (or the repo's schema lib) at every untrusted boundary; nothing else validates.

## Module detection

Monorepo: each workspace package. Single package: each directory directly under `src/` that has an `index.ts` or more than ~3 files. Generated directories (`dist/`, `src/generated/`, `*.gen.ts`) go under Boundaries → Never edit, not into `modules.txt`.
