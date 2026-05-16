# Replicating Top Notebooks

The fastest way to get a strong baseline is to clone a high-scoring public notebook,
verify it runs end-to-end on your account, then improve from there.

## Local directory convention

All competition work lives under `~/.kaggle_agent/`:

```
~/.kaggle_agent/
└── <competition-slug>/
    └── <notebook-slug>/          # one directory per distinct notebook
        ├── kernel-metadata.json
        ├── <notebook>.ipynb
        └── output/               # kaggle kernels output downloads go here
```

- **Different notebooks** for the same competition → separate `<notebook-slug>/` directories
- **Version updates** (re-push of the same notebook) → same directory, no new folder needed; the kernel id in metadata.json stays the same, only the version number increments on Kaggle's side

## Workflow

```bash
# 1. Pull WITH metadata — the -m flag carries dependency declarations
COMP="<competition-slug>"
NOTEBOOK="<notebook-slug>"
TARGET=~/.kaggle_agent/$COMP/$NOTEBOOK
mkdir -p $TARGET
kaggle kernels pull <owner>/<kernel-slug> -p $TARGET -m

# 2. Edit $TARGET/kernel-metadata.json:
#    - Change "id" to <your-username>/<your-new-slug>
#    - Change "title" if you want
#    - DO NOT touch competition_sources / dataset_sources / kernel_sources

# 3. Push under your account
kaggle kernels push -p $TARGET

# 4. Monitor until it completes
kaggle kernels status <your-username>/<your-new-slug>

# 5. Download output into the same directory
kaggle kernels output <your-username>/<your-new-slug> -p $TARGET/output/
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

## Choosing which notebook to replicate

Not every high-scoring notebook is easy to replicate. Before pulling, check the
`kernel_sources` and `dataset_sources` in `kernel-metadata.json`. They reveal the
notebook's actual dependency chain:

**Types of high-scoring notebooks (by complexity):**

| Type | What it is | Replication effort |
|------|------------|--------------------|
| **Standalone** | Only `competition_sources`, no `kernel_sources`, minimal `dataset_sources` | Lowest — pull, rename, push |
| **Blend/Ensemble** | Uses `dataset_sources` with pre-computed CSVs from others' models | Medium — need to replicate the source models first, or accept using their public predictions |
| **Stacking** | Multiple `kernel_sources` pointing to other kernels' OOF artifacts | High — chain of dependencies, each must run first |

**How to quickly assess before pulling:**

```bash
# 1. Pull metadata only to inspect, then decide
kaggle kernels pull <owner>/<kernel> -p /tmp/inspect/ -m
cat /tmp/inspect/kernel-metadata.json | python3 -c "
import json,sys; m=json.load(sys.stdin)
print('dataset_sources:', m.get('dataset_sources'))
print('kernel_sources:', m.get('kernel_sources'))
"
```

**Blender notebooks**: A notebook titled "Blender" or "Ensemble" with a `dataset_sources`
entry like `<owner>/submission-files` is NOT training a model — it's averaging
pre-computed CSVs. To replicate it you'd need the source submissions, which are often
private or belong to other competitors. Choose a standalone notebook instead unless
you explicitly want to blend.

**Practical rule**: For a quick baseline, prefer notebooks where `kernel_sources` is
empty and `dataset_sources` contains only public external data (e.g. historical
datasets from `aadigupta1601/...`), not submission CSVs from other competitors.

## Polling for completion with Monitor

For GPU notebooks that take 30+ minutes, use a Monitor with a long poll interval
rather than sleeping inline. The correct pattern:

```bash
# Start a Monitor — get notified when done, don't poll manually
while true; do
  status=$(kaggle kernels status <user>/<kernel> 2>&1)
  echo "$(date '+%H:%M') $status"
  echo "$status" | grep -qE "COMPLETE|ERROR|canceledRunning|error|failed|cancelled" && break
  sleep 1800  # 30-minute intervals for long GPU jobs
done
```

Typical runtimes by notebook type:
- CPU-only tabular (LightGBM, CatBoost): 15–30 min
- GPU tabular (CatBoost GPU, XGBoost GPU): 20–45 min  
- GPU deep learning (NN, RealMLP): 45–90 min
- Multi-model ensemble/stacking: 60–120 min

## Submitting after the kernel completes

For **CSV competitions** (most tabular competitions), the kernel produces
`submission.csv` in its output. Download it and submit directly — do **not** use
the `-k -v` kernel-link form, which is for code competitions:

```bash
# Download kernel output files
kaggle kernels output <user>/<kernel> -p ./output/

# Verify the submission file
head -3 ./output/submission.csv
wc -l ./output/submission.csv

# Submit the CSV directly
kaggle competitions submit <comp> -f ./output/submission.csv -m "description"

# Check score
kaggle competitions submissions <comp> | head -5
```

If `kaggle competitions submit ... -k <kernel> -v <version>` returns a 400 error
but the competition is a CSV competition (not a code competition), switch to the
`-f <file>` form instead.

## When to delegate replication

If you're doing more than a trivial fork (combining notebooks, refactoring,
integrating into existing code), pull all the referenced notebooks first and read
them side by side before editing. Quick clones are fast; non-trivial adaptations
earn their time back by being deliberate.

For complex adaptations, consider delegating the integration work to a coding agent
(OpenCode, Claude Code, etc.) with the SPEC.md and the source notebooks as context,
rather than trying to do it inline.
