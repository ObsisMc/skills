# Template: docs/testing.md

The testing policy an agent consults when deciding *whether* to write a test, *at which tier*, and *how*. Keep it under ~150 lines. Commands live in the root `AGENTS.md`; this file owns the judgment.

---

```markdown
# Testing

How this repository tests, tier by tier, and the rules that keep a green suite meaningful. Commands: [AGENTS.md](../AGENTS.md#commands).

## Tiers

| Tier | Runs | Proves | Location |
| --- | --- | --- | --- |
| Unit | `<<unit command>>` — every push, fast | One module's contract in isolation | `<<tests/unit/ or beside the code>>` |
| Integration | `<<integration command>>` — every PR | Modules compose through the real wiring (real DB/fs/queue where cheap) | `<<tests/integration/>>` |
| End-to-end | `<<e2e command>>` — every PR or nightly | The product does the thing through its real entry point (<<CLI / HTTP / UI>>) | `<<tests/e2e/>>` |
| <<Snapshot / contract / perf, if the repo has them>> | | | |

Coverage gate: `<<coverage command>>` fails under **<<N>>%** on <<changed files / the project>>. Coverage proves lines ran, not that behavior is right — it is necessary, never sufficient. An uncovered line is often dead code to delete, not a test to bolt on.

## What must have a test

- **Any behavior change** — a test that fails on the old code and passes on the new. If you cannot make it fail first, you have not tested the change.
- **Any bug fix** — the regression test reproduces the original defect through the entry point where it was observed, not a hand-built object that happens to hit the same line.
- **Any new public surface** listed in a module README.
- **Anything a decision record promises** ("callers can rely on X") — the promise gets a test that pins it.

## What must not have a test

- Statically defined values, constants, enum contents, config defaults — the compiler or a single existence check covers them.
- Tests that mirror the implementation (assert that `f` calls `g`); they break on every refactor and catch nothing.
- Negative tests for logic that was removed.
- Reversible, low-impact changes where the test would only restate the diff. Say so in the PR's Evidence section instead.

## Mocks

Mock only the expensive or nondeterministic boundary — network, clock, external process, third-party API — and keep everything downstream real. A hand-rolled stand-in for your own module proves the bridge moves bytes, not that the module works.

- Never mock the module under test's own dependencies inside the repo when the real one runs in under a second.
- A mock returns what the real thing returns, including its failure shapes. Cover the failure path or the mock is lying.
- `<<repo-specific: fixtures location, the one approved fake for X>>`

## Verify the world, not the self-report

An assertion re-reads the file, re-queries the DB, or re-runs the command. Grepping the subject's own log or return message for "success" lets an implementation that claims success without doing the work pass. Assert untouched files are byte-identical when the change should not touch them.

## Test the real entry path

The test exercises the shipped artifact or the real registration path — the CLI binary, the router with the handler mounted, the plugin loaded through the loader — not a function pulled out and called directly. A helper test can pass while nothing in production ever calls the helper.

## Ownership and isolation

Tests run concurrently. Every test owns what it acquires — temp dirs, ports, DB rows, env vars, child processes — and releases it in teardown, including on failure. A test that passes only when run alone is a defect in the test, not the runner.

## Flaky tests

Fix them when you meet them: find the cause, repair it, verify the behavior. Do not:

- add a retry, a longer timeout, or a sleep;
- weaken the assertion or widen the mock;
- mark it skipped without an issue link and an owner.

A retry hides a race; the race ships.

## Snapshot and expected-output tests <<delete if none>>

Regenerate only when the model or product output intentionally changed; review every diff in the regenerated file as you would code. CI runs in replay mode and never writes expected outputs.

## Running subsets

```sh
<<run one module>>
<<run one test by name>>
<<run only what changed, if the repo has such a script>>
```

Run the subset matching your change before committing. The full matrix is CI's job; running it locally for a one-module change is not diligence, it is waiting.
```

---

## Notes for the generator

- Fill the tier table from what actually exists. Do not invent an e2e tier the repo does not have; write "None yet — see decision <<…>> or Known limitations" and let the user decide.
- Coverage threshold and scope come from the interview.
- The sections *What must / must not have a test*, *Mocks*, *Verify the world*, *Real entry path*, *Flaky* are the ones that change agent behavior; keep them even in a small repo. Trim the rest to fit.
- If the repo already has a testing doc, link it from here and add only the missing judgment sections rather than duplicating commands.
