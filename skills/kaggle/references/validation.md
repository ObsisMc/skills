# Validation: Smoke-Test Commit

Most "Submission Scoring Error" failures are format problems, not modeling problems:
wrong columns, wrong row count, mismatched IDs, NaNs, out-of-range probabilities.
These are cheap to catch and expensive to ignore — every failed submission burns a
slot from the daily quota and tells you almost nothing about what went wrong.

Since all heavy work runs on Kaggle, validation runs there too via a **smoke-test
commit**.

## The pattern

Add a flag at the top of the submission notebook that limits inference to a handful
of test items. Run "Save & Run All" (commit mode). Check the resulting
`submission.csv` looks structurally right. Then flip the flag and do the real run.

```python
SMOKE_TEST = True   # flip to False for the real submission run

COMP = "<competition-slug>"
submission = pd.read_csv(f"/kaggle/input/{COMP}/sample_submission.csv")

TEST_DIR = Path(f"/kaggle/input/{COMP}/test")
test_files = sorted(TEST_DIR.glob("*.ogg"))
if SMOKE_TEST:
    test_files = test_files[:10]   # tiny slice — proves the path works end-to-end

if test_files:
    preds = model_predict(test_files)
    # write predictions back into `submission` keyed by ID
    ...
else:
    # No hidden test mounted (interactive run mode) — write a valid placeholder
    submission.iloc[:, 1:] = 0.0

submission.to_csv("submission.csv", index=False)
```

## Assertions (always run them)

After writing `submission.csv`, validate against `sample_submission.csv`:

```python
sample = pd.read_csv(f"/kaggle/input/{COMP}/sample_submission.csv")

assert list(submission.columns) == list(sample.columns), \
    f"Column mismatch:\n  sub:    {list(submission.columns)}\n  sample: {list(sample.columns)}"
assert len(submission) == len(sample), \
    f"Row count: {len(submission)} vs expected {len(sample)}"
assert set(submission.iloc[:, 0]) == set(sample.iloc[:, 0]), \
    "ID column doesn't match sample"
assert not submission.isna().any().any(), \
    f"Found NaNs:\n{submission.isna().sum()[submission.isna().sum() > 0]}"

# For probability columns, sanity-check ranges
prob_cols = submission.columns[1:]
assert (submission[prob_cols] >= 0).all().all() and (submission[prob_cols] <= 1).all().all(), \
    "Probabilities out of [0, 1]"

print(f"OK — {len(submission)} rows, {len(submission.columns)} columns, no NaNs")
print(submission.head())
```

These assertions catch the overwhelming majority of "Submission Scoring Error" cases
before they cost a submission slot.

## Why smoke-test commit, not interactive Run

| | Interactive Run | Smoke-test Commit |
|---|---|---|
| Hidden test set mounted? | No | Yes |
| Can verify real submission path? | No | Yes |
| Produces a `submission.csv` Kaggle considers valid? | No | Yes |
| Costs a submission slot? | No | Yes (one) |

A smoke-test commit costs one submission slot, but catches format bugs that would
otherwise cost a slot **and** several hours of wasted GPU time. The trade is
overwhelmingly worth it.

## After the smoke test passes

1. Flip `SMOKE_TEST = False`
2. Commit again (this is the real submission run)
3. Use `kaggle competitions submit -k <user>/<kernel> -v <version>` with the new
   version number
4. Monitor with `kaggle competitions submissions <comp>`

## Keep assertions in the production notebook

The assertion block is worth keeping in the notebook permanently, not just during
smoke testing. Format bugs can sneak back in after a "tiny" edit; the assertions are
your tripwire. They're cheap to run on a full submission.
