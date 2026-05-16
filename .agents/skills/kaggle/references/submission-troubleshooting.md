# Submission Troubleshooting

Diagnosing failed submissions: 400 errors at upload, Scoring Errors after upload, and
distinguishing CSV competitions from code/model competitions.

## 400 / Bad Request on `submit`

Work through these in order — roughly ranked by how often each is the cause:

### 1. Haven't accepted competition rules

The CLI gives a misleading error if you haven't clicked "I Understand and Accept" on
the competition page in a browser. This blocks downloads **and** submissions silently
from the CLI's perspective. **Check this first** — it's the most common cause.

### 2. Slug typo

`kaggle competitions submit titanic-2024` is not the same as `titanic`. Check the
exact slug in the competition URL (the part after `/competitions/`).

### 3. Wrong file format

Some competitions want the CSV zipped; others want the raw CSV; a few want a tarball.
Read the "Submission" or "Evaluation" tab on the competition page.

### 4. CSV header / column order / quoting

The grader is picky. Diff the first lines of your `submission.csv` against
`sample_submission.csv`:

```bash
head -3 submission.csv sample_submission.csv
```

### 5. Submission limit hit

Most competitions cap submissions per day. Check
`kaggle competitions submissions <comp>` — if your last several attempts are all today,
you're rate-limited.

## Zipped submissions

When a competition wants a zip, the failure mode is almost always **zipping the wrong
files** — zipping a folder that contains `__notebook__.ipynb`, `.ipynb_checkpoints`,
or extra CSVs from intermediate steps.

Zip only the submission file:

```python
import zipfile
with zipfile.ZipFile("submission.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("submission.csv", arcname="submission.csv")
```

## "Submission Scoring Error" after upload

The submission got through but Kaggle's grader couldn't score it. Almost always one of:

- **Row count mismatch** — your submission doesn't cover every test ID, or covers extras
- **ID column wrong** — string vs int, leading zeros stripped (`"00123"` → `123`),
  or sorted differently from `sample_submission.csv`
- **NaN, inf, or wrong dtype** in a prediction column
- **For multi-class:** probabilities don't sum to 1, or a class column is missing
- **Filename column has the file extension twice** (e.g. `audio_001.ogg.ogg`)

Before re-submitting, run the assertion block in `validation.md` against the actual
CSV that was submitted. Don't skip validation — every failed submission burns a daily
slot.

## Competition types: CSV vs code vs model

| Type | What you submit | How to recognize |
|------|-----------------|------------------|
| **CSV / answer submission** | A CSV with predictions | Most tabular & most image/audio competitions |
| **Code submission** | A notebook that Kaggle runs against the hidden test set | "Code Competition" badge; test data is hidden during run |
| **Model submission** | Model weights / adapter files (e.g. LoRA) | The competition page explicitly describes a model upload format |

Quick way to confirm: scan the top 2-3 public notebooks.
- If they all end with `submission.to_csv("submission.csv", index=False)` and nothing
  else → **CSV competition**.
- If they save model checkpoints to `/kaggle/working/` and the description talks
  about inference being run by Kaggle → **code competition**.
- If you see explicit model artifact uploads (LoRA adapters, weight files as the
  final output) → **model competition**.

## When you can't tell which competition type

Check the competition's "Submission" page for the exact format. When in doubt, use
the form most public notebooks use — top notebook authors have already debugged this.
