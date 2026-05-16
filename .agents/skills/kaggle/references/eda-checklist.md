# EDA on Kaggle

Since the data lives only on Kaggle (per the workflow assumption), EDA does too.
Create a separate exploration kernel — not the submission kernel — so you can iterate
freely without polluting the submission flow.

## Setting up the EDA kernel

Use a minimal `kernel-metadata.json`:

```json
{
  "id": "<your-username>/<comp>-eda",
  "title": "<comp> EDA",
  "code_file": "eda.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_internet": false,
  "competition_sources": ["<comp-slug>"]
}
```

Ensure the notebook itself contains `metadata.kernelspec` so Kaggle can resolve the
kernel when executing via papermill:

```json
{
    "metadata": {
        "kernelspec": {
            "name": "python3",
            "display_name": "Python 3",
            "language": "python"
        }
    }
}
```

If you already created a notebook without `kernelspec`, enforce it locally with:

```python
import nbformat

path = r"path\to\ipynb"
nb = nbformat.read(path, as_version=4)

nb["metadata"]["kernelspec"] = {
        "name": "python3",
        "display_name": "Python 3",
        "language": "python",
}

nbformat.write(nb, path)
```

**`enable_gpu: false`** is important. EDA is CPU work and GPU kernels eat quota fast.

## Persist insights as artifacts

Write findings to `/kaggle/working/` so they become downloadable artifacts after the
kernel commits. Cell outputs alone are easy to lose:

```python
train_df.describe().to_csv("/kaggle/working/train_describe.csv")
train_df["target"].value_counts().to_csv("/kaggle/working/target_dist.csv")
test_df.isna().sum().to_csv("/kaggle/working/test_nulls.csv")
```

## Kaggle-specific EDA checklist

In addition to general EDA, check these Kaggle-specific items:

### `sample_submission.csv` is the contract

This file defines what your final submission must look like — exact column names,
dtypes, ID format, row count. Inspect first and plan around it.

```python
base_dirs = [f"/kaggle/input/competitions/{COMP}", f"/kaggle/input/{COMP}"]
data_dir = next((p for p in base_dirs if os.path.isdir(p)), None)
if data_dir is None:
    raise FileNotFoundError(f"Competition data dir not found for {COMP}")

sample = pd.read_csv(f"{data_dir}/sample_submission.csv")
print(sample.shape)
print(sample.columns.tolist())
print(sample.dtypes)
print(sample.head())
```

If `sample_submission.csv` has 1.5M rows with float columns clipped to [0, 1], your
submission needs to match exactly — wrong count, wrong dtype, or wrong range = scoring
error.

### Train vs test ID overlap

For some tasks (especially time-series, recommender systems) the test set contains
IDs unseen during training. For others (e.g. transaction-level tabular) train and
test IDs overlap. The pattern dictates how to design validation:

```python
train_ids = set(train_df["id"])
test_ids = set(test_df["id"])
print(f"Overlap: {len(train_ids & test_ids)}")
print(f"Only in train: {len(train_ids - test_ids)}")
print(f"Only in test: {len(test_ids - train_ids)}")
```

### Train vs test distribution drift

Same columns can have very different distributions between train and test, signaling
distribution shift or that your CV won't match the leaderboard. Check the major
features:

```python
for col in numeric_features[:10]:
    print(f"{col}: train mean={train_df[col].mean():.3f}, "
          f"test mean={test_df[col].mean():.3f}")
```

Large gaps mean adversarial validation or careful CV-design will pay off.

### Target distribution

Drives whether you need stratification, log-transforms, sample weights, or class
balancing:

```python
# Classification
print(train_df["target"].value_counts(normalize=True))

# Regression
print(train_df["target"].describe())
train_df["target"].hist(bins=50)
```

### Missing values

Pattern matters more than count. Missingness that correlates with the target is a
real signal in tabular competitions:

```python
nulls = train_df.isna().sum()
print(nulls[nulls > 0].sort_values(ascending=False))

# Does missingness correlate with target?
for col in cols_with_nulls:
    rate_when_missing = train_df.loc[train_df[col].isna(), "target"].mean()
    rate_when_present = train_df.loc[train_df[col].notna(), "target"].mean()
    print(f"{col}: missing→{rate_when_missing:.3f}, present→{rate_when_present:.3f}")
```

### File size / shape sanity

Some competitions have hidden test sets far larger than train, which changes the
inference budget:

```python
import os
for f in os.listdir(f"/kaggle/input/{COMP}"):
    path = f"/kaggle/input/{COMP}/{f}"
    if os.path.isfile(path):
        size_mb = os.path.getsize(path) / 1e6
        print(f"{f}: {size_mb:.1f} MB")
```

## The point of EDA

The goal is **not** beautiful charts — it's to surface the two or three things about
this specific competition that you'll keep referring back to. Write those into the
SPEC.md.

## After pushing a kernel

1. **Wait for completion** — after `kaggle kernels push`, wait for the run to finish.
2. **Check logs** — if the log shows an error, analyze it, fix the notebook, and push
    again.
3. **Download outputs** — if there is no error, download artifacts from the Output
    tab (or via `kaggle kernels output`).
