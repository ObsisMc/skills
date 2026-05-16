---
name: agentic-data-science-competition
description: |
  Run Kaggle competitions end-to-end as an autonomous agent. Use when the user mentions
  Kaggle, a competition, leaderboard, submission.csv, kernel, notebook push/pull, kaggle
  CLI, a 400 error on submit, "submission scoring error", replicating a public solution,
  or any "I'm stuck on Kaggle" situation. Covers credential setup, data access without
  local downloads, EDA on Kaggle, top-notebook replication, smoke-test validation,
  submission troubleshooting, and code-competition queue behavior.
---

# Agentic Data Science Competition

Run Kaggle competitions end-to-end as an autonomous agent. This skill is a control plane
for the workflow; deeper material lives in `references/`.

---

## When to Use

Consult this skill whenever the user is working on a Kaggle competition or any task
involving the `kaggle` CLI. Typical triggers:

- "help me set up Kaggle / submit / push a kernel"
- "my submission returned 400 / Submission Scoring Error"
- "replicate this top notebook"
- "what should I do for this competition" (planning, EDA, strategy)
- "the leaderboard score doesn't match my local score"

---

## Core Mental Model

**Local is a control plane. Kaggle is a data plane.**

| Local does | Kaggle does |
|------------|-------------|
| `kaggle` CLI calls (push, pull, submit) | EDA |
| Edit `kernel-metadata.json` | Training |
| Read public notebook source | Inference |
| Plan strategy (SPEC.md) | Smoke-test the submission pipeline |
| Inspect `sample_submission.csv` (small) | Generate `submission.csv` |

**Do not download the full training set locally.** The kernel mounts it at
`/kaggle/input/<comp-slug>/`. If you reach for `kaggle competitions download <comp>`,
stop — push a kernel instead.

This shapes everything: validation, EDA, debugging all happen by pushing kernels and
reading their output, not by running data through a local Python environment.

---

## Quick Reference

```bash
# Smoke test — agent runs this to check if user is already authenticated
kaggle competitions list

# Inspect a competition without downloading
kaggle competitions files <comp-slug>             # list files + sizes
kaggle competitions download <comp> -f sample_submission.csv   # only allowed download

# Pull a public top notebook (the -m flag is what gets dependencies)
kaggle kernels pull <owner>/<kernel> -p ./solution/ -m

# Push a kernel
kaggle kernels push -p ./solution/
kaggle kernels status <user>/<kernel-slug>

# Submit
kaggle competitions submit <comp> -k <user>/<kernel> -v <ver> -m "<msg>"
kaggle competitions submissions <comp>            # check status
```

**The agent must not authenticate on the user's behalf.** If `kaggle competitions list`
fails with an auth error, tell the user to run `kaggle auth login` themselves. See
`references/setup.md` for details.

**Prerequisite for everything**: the user must accept the competition rules in a
browser before any data operation on that competition works. The CLI fails silently
otherwise.

---

## Procedure: Standard Competition Workflow

This is the rough sequence an agent should follow when handed a new competition.

1. **Load competition memory** — Read `~/.kaggle_agent/<comp>/NOTES.md` if it exists.
   It contains rules, past pitfalls, current best score, and domain knowledge from
   previous sessions. If it doesn't exist yet, create it now (template in
   `references/competition-memory.md`) and fill in the Rules section before proceeding.
2. **Setup check** — Run `kaggle competitions list` to verify the CLI is authenticated.
   **If it fails**, do not attempt to fix it. Stop and tell the user to run
   `kaggle auth login` themselves, then wait for confirmation. See `references/setup.md`.
2. **Inspect** — Run `kaggle competitions files <comp-slug>` and skim the competition
   page in browser. Note: submission format (CSV / notebook / model), evaluation
   metric, deadline, GPU/internet rules.
3. **Plan** — Draft a `SPEC.md` (template in `references/spec-template.md`). Identify
   2-3 top public notebooks to replicate or learn from.
4. **EDA on Kaggle** — Create a dedicated EDA kernel. Don't download data locally.
   Checklist in `references/eda-checklist.md`.
   If a notebook fails to run with papermill “No kernel name found”, fix the notebook
   metadata locally by adding `metadata.kernelspec` before pushing again (see snippet below).
5. **Replicate baseline** — `kaggle kernels pull <top-notebook> -p ./baseline/ -m`,
   change `id` and `title` in `kernel-metadata.json`, push, verify it runs. Details
   in `references/replication.md`.
   Ensure `title` slugifies to `id` before pushing, or the save can fail with a 400.
   **Before picking which notebook to replicate**, check `kernel_sources` and
   `dataset_sources` — blender notebooks with submission-CSV dependencies look
   standalone but require other competitors' outputs. Prefer notebooks where
   `kernel_sources` is empty and `dataset_sources` has only public external data.
6. **Poll for completion with Monitor** — GPU notebooks take 30–90 min. Use a Monitor
   with `sleep 1800` (30 min interval) rather than short polling. Terminal states to
   watch: `COMPLETE`, `ERROR`, `canceledRunning`, `failed`, `cancelled`.
7. **Smoke-test validate** — Add a `SMOKE_TEST` flag to the submission notebook,
   run a tiny slice via commit mode, check format with assertions. Full code in
   `references/validation.md`.
8. **Submit** — For CSV competitions, download kernel output with
   `kaggle kernels output <kernel> -p ./output/` and submit with
   `-f ./output/submission.csv`. The `-k -v` form is only for code competitions
   (where Kaggle re-runs your kernel against a hidden test set) — using it on a
   CSV competition returns 400.
9. **Verify score** — `kaggle competitions submissions <comp>` shows status and
   `publicScore` once grading is `COMPLETE`. Use a Monitor loop to detect when
   `PENDING` clears.
10. **Update memory** — After each submission, append to `experiments/log.md` and
    update `NOTES.md` (new pitfalls, domain insights, current best score, next ideas).
11. **Iterate** — Improve based on score. For score interpretation see
    `references/code-competition-queue.md`.

---

## Pitfalls

The recurring failure modes. Full details in `references/common-traps.md` and the
troubleshooting reference.

- **Agent tries to authenticate on the user's behalf** → security violation. Never
  run `kaggle auth login`, never move/chmod `kaggle.json`, never read or write the
  token file. Auth is the user's job. See `references/setup.md`.
- **Haven't accepted competition rules** → silent CLI failures
- **Wrong submission file format** → 400 error (see `references/submission-troubleshooting.md`)
- **CSV row/column/ID mismatch** → "Submission Scoring Error" after upload
- **Run mode vs Commit mode confusion** → kernel "works" but submission.csv missing
  the hidden test predictions (see `references/kernel-workflow.md`)
- **Pulling a kernel without `-m`** → metadata missing → push fails on dependencies
- **Kernel title does not slugify to kernel id** → `kaggle kernels push` fails with 400. Ensure `title` resolves to the `id` slug; safest is using the exact slug as the title or a title that slugifies to it.
- **Assuming a single input mount path** → some competitions mount under `/kaggle/input/competitions/<slug>/` instead of `/kaggle/input/<slug>/`. Always probe both before reading files.
- **Notebook missing `kernelspec` metadata** → Kaggle papermill fails with `ValueError: No kernel name found`. Ensure generated notebooks include `metadata.kernelspec` (name: `python3`, display_name: `Python 3`, language: `python`) before pushing.
- **Silent `except Exception: continue`** → submission half-empty, no diagnostics
- **Filename column with doubled extension** (`audio.ogg.ogg`) → ID mismatch
- **Trusting a single early score** in a code competition → see queue behavior
- **Choosing a blender as the "top notebook"** → looks standalone but depends on other competitors' pre-computed CSVs; fails or produces no predictions without those inputs. Check `kernel_sources` and `dataset_sources` before choosing. See `references/replication.md`.
- **Using `-k -v` submit form on a CSV competition** → 400 error. Only code competitions (hidden test set re-run by Kaggle) use `-k -v`. CSV competitions use `-f submission.csv`. See `references/submission-troubleshooting.md`.
- **Polling kernel status with short sleep intervals** → wastes API calls and generates noise. GPU notebooks take 30–90 min; use Monitor with 30-min intervals and watch for terminal states (`COMPLETE`, `ERROR`, `cancelled`).
- **Kernel not appearing in "Your Work → Code"** → normal; the UI index lags a few minutes after push. Access directly via URL `https://www.kaggle.com/code/<username>/<kernel-slug>`.

---

## Verification

A submission is "green" when:

- [ ] `kaggle competitions submissions <comp>` shows the new submission with a recent timestamp
- [ ] Status reached `COMPLETE` (not `PENDING` or an error)
- [ ] For code competitions: linked to the right kernel + version (not orphan)
- [ ] Score is in a plausible range vs. your previous submissions
- [ ] No `Submission Scoring Error`

If the score looks off, re-check the submitted CSV against `sample_submission.csv`
column-by-column. The CSV you actually submitted is the one to verify, not the one
you thought you submitted.

---

## References

Read these on demand. Each is independently readable; titles within them are stable
anchors so they can be sliced if needed.

| File | When to read |
|------|--------------|
| `references/setup.md` | First-time `kaggle` CLI setup; data access patterns |
| `references/kernel-workflow.md` | Pushing kernels, Run vs Commit, metadata, `/kaggle/input/` paths; **polling for kernel/submission completion**; **CSV vs code competition type判断** |
| `references/replication.md` | Cloning a public top notebook into your own kernel |
| `references/eda-checklist.md` | Exploring a new competition's data |
| `references/validation.md` | Smoke-test commit pattern + full assertion code |
| `references/submission-troubleshooting.md` | 400 errors, Scoring Errors, format issues |
| `references/code-competition-queue.md` | Score delays, queue behavior, the 4-hour heuristic |
| `references/spec-template.md` | The SPEC.md planning template |
| `references/competition-memory.md` | Per-competition memory structure (NOTES.md + experiments/log.md) |
| `references/common-traps.md` | Recurring code-level bugs (silent except, double extensions, etc.) |

---

## Why This Skill Exists

Most Kaggle pain isn't in modeling — it's in the gap between "my notebook scored X on
Kaggle" and "my submission shows X on the leaderboard". This skill is a checklist of
the things in that gap that have actually gone wrong in real competitions. Use it as a
first-pass diagnostic before deep-diving, and as a setup guide when starting fresh.
