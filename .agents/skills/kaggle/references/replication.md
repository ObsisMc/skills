# Replicating Top Notebooks

The fastest way to get a strong baseline is to clone a high-scoring public notebook,
verify it runs end-to-end on your account, then improve from there.

## Workflow

```bash
# 1. Pull WITH metadata — the -m flag carries dependency declarations
kaggle kernels pull <owner>/<kernel-slug> -p ./solution/ -m

# 2. Edit ./solution/kernel-metadata.json:
#    - Change "id" to <your-username>/<your-new-slug>
#    - Change "title" if you want
#    - DO NOT touch competition_sources / dataset_sources / kernel_sources

# 3. Push under your account
kaggle kernels push -p ./solution/

# 4. Monitor until it completes
kaggle kernels status <your-username>/<your-new-slug>
```

## What to change vs preserve

**Only change**:
- `id` (must be your username)
- `title` (optional)

**Preserve everything else**:
- All `*_sources` arrays (`competition_sources`, `dataset_sources`, `kernel_sources`)
- `enable_internet` (changing this can disqualify submissions in offline competitions)
- `enable_gpu` (unless you have a specific reason)
- `is_private` (keep `true` until you decide to publish)

## Common replication mistakes

1. **Forgetting `-m` on pull** → kernel-metadata.json missing → push tries to run
   without the original's datasets/models → ImportError or FileNotFoundError on Kaggle.

2. **Removing a `dataset_sources` entry that "looks unused"** — it's often a
   pip-vendored package source the notebook needs offline. Keep all entries.

3. **Flipping `enable_internet` from `false` to `true` because it's convenient** —
   this can disqualify submissions in offline competitions. Match the original.

4. **Editing the notebook before verifying it runs unchanged** — you lose the ability
   to tell whether a failure is from your edit or from the replication itself. Always
   push the unmodified clone first, confirm it produces a submission, then modify.

## When to delegate replication

If you're doing more than a trivial fork (combining notebooks, refactoring,
integrating into existing code), pull all the referenced notebooks first and read
them side by side before editing. Quick clones are fast; non-trivial adaptations
earn their time back by being deliberate.

For complex adaptations, consider delegating the integration work to a coding agent
(OpenCode, Claude Code, etc.) with the SPEC.md and the source notebooks as context,
rather than trying to do it inline.
