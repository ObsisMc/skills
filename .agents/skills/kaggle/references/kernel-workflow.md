# Kernel Workflow

Pushing notebooks to Kaggle, understanding execution modes, and getting
`kernel-metadata.json` right.

## Run mode vs Commit mode (subtle but critical)

| Mode | When triggered | Hidden test set mounted? |
|------|----------------|--------------------------|
| Interactive / "Run" | Cell-by-cell on Kaggle, or a `kaggle kernels push` run | **No** — only public files exist |
| Commit / "Save & Run All" | The green button on Kaggle, or the run that scores a code submission | **Yes** — hidden test paths are populated |

This is the most common source of "my kernel works but submission.csv is empty/wrong"
confusion. A `kaggle kernels push` does **not** mount the hidden test set, so any code
path that depends on hidden test files being present will produce nothing.

### Defensive notebook structure

Write the notebook so it produces a valid `submission.csv` in both modes:

```python
import pandas as pd
from pathlib import Path

COMP = "<competition-slug>"
TEST_DIR = Path(f"/kaggle/input/{COMP}/test")
test_files = sorted(TEST_DIR.glob("*.ogg"))   # or *.png, *.parquet, etc.

if test_files:
    # Hidden test set is mounted — run real inference
    submission = run_inference(test_files)
else:
    # Interactive run mode — write a valid placeholder so the kernel still completes
    submission = pd.read_csv(f"/kaggle/input/{COMP}/sample_submission.csv")
    submission.iloc[:, 1:] = 0.0

submission.to_csv("submission.csv", index=False)
```

**Do not** silently fall back to training data when test data is missing. That hides
real bugs and produces submissions that look fine locally but score badly:

```python
# WRONG — masks the "no test data" state and runs on train data
test_files = sorted(TEST_DIR.glob("*.ogg"))
if not test_files:
    test_files = sorted((COMP_DIR / "train_soundscapes").glob("*.ogg"))[:10]
```

## Input data paths

Kaggle mounts competition data under `/kaggle/input/<competition-slug>/`. Some legacy
notebooks use `/kaggle/input/competitions/<slug>/`; if the obvious path doesn't exist,
list `/kaggle/input/` to confirm:

```python
from pathlib import Path
for p in Path("/kaggle/input").iterdir():
    print(p, list(p.iterdir())[:5])
```

Don't hardcode paths without verifying — the directory structure varies by competition.

## `kernel-metadata.json` checklist

When pushing a kernel, the metadata file controls everything about how it runs:

```json
{
  "id": "<your-username>/<kernel-slug>",
  "title": "Human-readable title",
  "code_file": "notebook.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_internet": false,
  "competition_sources": ["<competition-slug>"],
  "dataset_sources": ["<owner>/<dataset-slug>"],
  "kernel_sources": ["<owner>/<kernel-slug>"]
}
```

Field-by-field:

- **`id`** — `username/kernel-slug` format. Must match your account.
- **`is_private`** — defaults to `true`. Keep true unless explicitly publishing.
- **`enable_gpu`** — turn off for EDA kernels (saves quota); turn on for training/inference.
- **`enable_internet`** — **forbidden in many competitions**. Check the comp rules
  before flipping to `true`; the wrong setting can disqualify submissions.
- **`competition_sources`** — mounts the competition's data at `/kaggle/input/<slug>/`.
- **`dataset_sources`** — additional datasets (e.g. pretrained weights, pip-vendored
  packages). Preserve all entries when adapting someone else's kernel.
- **`kernel_sources`** — outputs from other kernels (e.g. cached features). Same:
  preserve when forking.

### Pushing

```bash
kaggle kernels push -p ./solution/      # ./solution must contain metadata + notebook
kaggle kernels status <user>/<kernel>   # poll until COMPLETE
```

If push fails with metadata errors, the fix is almost always in `kernel-metadata.json`
— check the `id` field matches your account, and that all `*_sources` slugs exist
and you have access to them.

## Polling for kernel completion

GPU notebooks take 30–90 minutes. Use a Monitor with a long interval rather than
short polling. Watch for all terminal states — not just success:

```bash
while true; do
  status=$(kaggle kernels status <user>/<kernel> 2>&1)
  echo "$(date '+%H:%M') $status"
  echo "$status" | grep -qE "COMPLETE|ERROR|canceledRunning|error|failed|cancelled" && break
  sleep 1800  # 30-minute intervals for GPU jobs; use 300 for CPU jobs
done
```

Typical runtimes by notebook type:
- CPU tabular (LightGBM, CatBoost CPU): 15–30 min
- GPU tabular (CatBoost GPU, XGBoost GPU): 20–45 min
- GPU deep learning (NN, RealMLP): 45–90 min
- Multi-model stacking chain: 60–120 min

After `COMPLETE`, download the output into the standard location:

```bash
# Following the ~/.kaggle_agent/<comp>/<notebook>/output/ convention
kaggle kernels output <user>/<kernel> -p ~/.kaggle_agent/<comp>/<notebook>/output/
ls ~/.kaggle_agent/<comp>/<notebook>/output/
```

## Polling for submission score

After submitting a CSV, the score is usually ready within 1–2 minutes but starts as
`PENDING`. Use the same pattern to wait for it:

```bash
while true; do
  result=$(kaggle competitions submissions <comp> 2>&1 | head -5)
  echo "$result"
  # Break when the latest submission is no longer PENDING
  echo "$result" | grep -q "PENDING" || break
  sleep 30
done
```

## Competition type: CSV vs Code

This affects which submit command to use and whether the hidden test set matters.

**How to tell which type you have:**

```bash
# Check the top public notebooks — what does their final output look like?
kaggle kernels list --competition <comp-slug> --sort-by scoreDescending --page-size 5
kaggle kernels pull <top-kernel> -p /tmp/inspect/ -m
# Read the last few cells — does it save submission.csv and stop, or does it save
# model weights / checkpoints for Kaggle to re-run?
```

| Signal | CSV competition | Code competition |
|--------|----------------|-----------------|
| Competition page badge | none | "Code Competition" badge |
| test.csv visible in competition files | yes | no (hidden) |
| Top notebooks end with | `submission.to_csv(...)` | saving model weights |
| Submit command | `-f submission.csv` | `-k <kernel> -v <version>` |
| Score appears | within ~2 min | after Kaggle re-runs your kernel |

**For CSV competitions** — download the kernel output and submit the file:

```bash
kaggle kernels output <user>/<kernel> -p ~/.kaggle_agent/<comp>/<notebook>/output/
kaggle competitions submit <comp> -f ~/.kaggle_agent/<comp>/<notebook>/output/submission.csv -m "description"
```

**For code competitions** — link the submission to a specific kernel version:

```bash
kaggle competitions submit <comp> -k <user>/<kernel> -v <version> -m "description"
```

Using `-k -v` on a CSV competition returns `400 Bad Request`. Using `-f` on a code
competition creates an orphan submission not linked to a kernel run. See
`submission-troubleshooting.md` for more.
