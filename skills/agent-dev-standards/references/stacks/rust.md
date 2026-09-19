# Stack: Rust

Detect: `Cargo.toml`. Workspace: `[workspace] members` — modules are the member crates. Task runner: `justfile` or `cargo xtask` if present; `cargo make` rarely. No `typecheck` job — `cargo check`/`clippy` owns it.

## Tools

| Role | Tool | Notes |
| --- | --- | --- |
| Format | `cargo fmt --all -- --check` | `rustfmt.toml` if present; do not add one just to change defaults |
| Lint | `cargo clippy --all-targets --all-features -- -D warnings` | Respect existing `[lints]` tables / `clippy.toml`; `-D warnings` only if the tree is already clean, otherwise note the count and let the user decide |
| Test | `cargo test` / `cargo nextest run` if `.config/nextest.toml` exists | |
| Coverage | `cargo llvm-cov` (`cargo-llvm-cov`) | `cargo tarpaulin` if already used |
| Docs | `cargo doc --no-deps` with `RUSTDOCFLAGS="-D warnings"` | Broken intra-doc links fail — counts as a docs gate |

## Commands

```sh
cargo build                                            # build
cargo fmt --all -- --check                             # format — fix: cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo test -p <<crate>>                                # test subset
cargo llvm-cov --workspace --fail-under-lines <<N>>    # coverage gate
RUSTDOCFLAGS="-D warnings" cargo doc --no-deps         # rustdoc links
bash checks/check docs
```

Note in AGENTS.md: "Cargo commands can be slow under the build lock; do not kill them" (codex learned this the hard way).

## `check` wiring

```just
check group="all":
    bash checks/check {{group}}
```
Or an `xtask` subcommand that shells out to `checks/check`. Never add `make` for this.

## CI setup steps

```yaml
      - uses: dtolnay/rust-toolchain@stable        # or the pinned channel from rust-toolchain.toml
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
```

`test` job: `cargo llvm-cov --workspace --lcov --output-path lcov.info --fail-under-lines <<N>>` after `cargo install cargo-llvm-cov` (or `taiki-e/install-action@cargo-llvm-cov`). Matrix over `ubuntu/windows/macos` when the crate touches the filesystem, processes, or is a CLI.

## Hooks

`.githooks/pre-commit`:

```sh
#!/usr/bin/env bash
set -euo pipefail
git diff --cached --name-only --diff-filter=ACM -- '*.rs' | grep -q . || exit 0
cargo fmt --all -- --check || { echo "fix: cargo fmt --all"; exit 1; }
```
Clippy is too slow for a hook; it stays in CI. `.githooks/commit-msg`: `exec bash checks/verify-commit-convention.sh --file "$1"`. Install line in CONTRIBUTING setup: `git config core.hooksPath .githooks`.

## Language-specific rules (≤ 3)

- No `unwrap()`/`expect()` outside tests, `main`, and `const` contexts; propagate with `?` and a typed error (`thiserror` in libraries, `anyhow` in binaries — state which the repo uses).
- Public items have a doc comment stating what the signature cannot; `#![warn(missing_docs)]` in library crates.
- `match` exhaustive; avoid wildcard arms on enums the crate owns.
- Newtypes for ids and units (`UserId(u64)`), never bare `u64`/`String` across module boundaries.
- Modules target < 500 lines excluding tests; split at ~800 (`mod.rs` stays orchestration).

## Module detection

Workspace members; in a single crate, top-level `src/*/mod.rs` (or `src/<name>.rs` + `src/<name>/`) directories. `target/` is never a module.
