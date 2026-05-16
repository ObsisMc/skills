# Common Traps

Recurring code-level bugs in Kaggle notebooks. Each section is a self-contained
failure mode + fix.

## Double file extension

Filename columns sometimes already include the extension. Concatenating naively gives
`audio_001.ogg.ogg`, which silently mismatches the test files:

```python
print(train_df["filename"].head())   # Always inspect first
# If it shows "1161364/iNat1216197.ogg", don't append ".ogg" again
```

**Fix**: inspect the raw values in any ID/filename column before assuming you need to
add an extension. If the column ends with `.ogg`/`.png`/`.parquet` already, leave it
alone.

## Silent `except Exception: continue`

Hides exactly the information you need to debug:

```python
# Bad
try:
    audio, sr = load_audio(file)
except Exception:
    continue

# Better
try:
    audio, sr = load_audio(file)
except Exception as e:
    print(f"Failed on {file}: {type(e).__name__}: {e}")
    continue
```

If a notebook runs for 90 minutes and produces a half-empty submission, the
diagnostic print is what tells you whether 5% of files failed for a known reason or
90% failed for an unknown one. Always log the failure mode, even if you're going to
ignore it.

## Falling back to training data when test data is missing

Documented in `kernel-workflow.md`, but worth re-flagging here: never silently
substitute training data for missing test data. It hides the "no test mounted" state
and produces submissions that look fine but score badly.

```python
# WRONG — masks the "no test data" state
test_files = sorted(TEST_DIR.glob("*.ogg"))
if not test_files:
    test_files = sorted((COMP_DIR / "train_soundscapes").glob("*.ogg"))[:10]

# CORRECT — write a valid placeholder submission instead
if not test_files:
    submission = pd.read_csv("sample_submission.csv")
    submission.iloc[:, 1:] = 0.0
    submission.to_csv("submission.csv", index=False)
```

## Oversimplified agents in game/RL competitions

In game-AI competitions, top solutions often implement substantially more feature
logic (opponent modeling, multi-step lookahead, hand-tuned heuristics on top of the
learned policy) than a clean RL baseline would suggest. A minimal "just train an RL
agent" approach typically scores far below the top of the leaderboard.

**Fix**: read the top solution write-ups (forum posts from past iterations of the
competition) before deciding how much complexity to commit to. Plan for the actual
feature set required, not the cleanest possible baseline.

## Trusting one early score

For all submissions, the public LB is a noisy estimate of the private LB (it's
measured on a subset). For code competitions specifically, see the queue behavior
section. Don't make irreversible choices (deleting a model, changing the whole
approach) based on a single score swing.

**Fix**: take at least two readings before reacting strongly to a score change. If
two submissions of essentially the same code give very different scores, the
variance is in the LB sampling, not your code.

## Forgetting `-m` on `kernel pull`

```bash
# Wrong — gets the source but not the metadata
kaggle kernels pull <owner>/<kernel> -p ./solution/

# Right — gets metadata too, so push will know about dataset/model dependencies
kaggle kernels pull <owner>/<kernel> -p ./solution/ -m
```

Without `-m`, your subsequent `kaggle kernels push` will fail because Kaggle doesn't
know to mount the original's `competition_sources`, `dataset_sources`, etc.

## Kernel title does not slugify to kernel id

If the kernel `title` does not resolve to the same slug as the `id`, `kaggle kernels push`
can fail with a 400 error when saving.

**Fix**: set `title` to the exact slug (or a title that slugifies to it). This is the
safest way to ensure the `id` and `title` agree.

## Hardcoding `/kaggle/input/<comp>/` paths

The path structure varies. Some competitions mount at `/kaggle/input/<slug>/`,
some at `/kaggle/input/competitions/<slug>/`. Always verify in early iterations:

```python
from pathlib import Path
for p in Path("/kaggle/input").iterdir():
    print(p)
```

Then derive paths from what's actually there.

## Changing `enable_internet` to `true` for convenience

Many competitions are offline-only — `enable_internet: true` will disqualify your
submission. When forking a kernel, preserve whatever `enable_internet` value the
original had unless you've explicitly verified the competition allows internet.

## Mistaking a blender notebook for a standalone model

High-scoring notebooks near the top of the leaderboard are often **blenders** — they
average pre-computed submission CSVs from other notebooks rather than training any
model. They look standalone but have hidden dependencies.

Signs a notebook is a blender:
- Title contains "Blend", "Blender", "Ensemble", or "Stacking"
- `dataset_sources` contains entries like `<owner>/submissions`, `<owner>/submission-files`,
  or `<owner>/<anything>-blend-inputs`
- The notebook code is mostly `shutil.copy(...)` or `pd.read_csv(path)[col].mean()`
- The kernel runs in under 2 minutes despite claiming a high score

**Fix**: before choosing a notebook to replicate, inspect its `kernel-metadata.json`
(pull with `-m` or just read from the Kaggle UI). If `kernel_sources` is non-empty or
`dataset_sources` contains submission files from other competitors, look for a more
independent alternative. Filter for notebooks where `kernel_sources` is empty and
`dataset_sources` only contains public external datasets.

## `id_no` field in kernel-metadata.json

When pulling a notebook with `kaggle kernels pull -m`, the metadata includes an
`id_no` field (numeric internal ID of the original notebook). When you push under your
own account, Kaggle ignores this field but it doesn't cause errors. You can safely
leave it in the JSON — no need to remove it.

## Kernel visible via URL but not in "Your Work" → Code

Notebooks pushed via `kaggle kernels push` sometimes take a few minutes to appear in
the Kaggle web UI under "Your Work → Code". The notebook is live and runnable
immediately; the UI index just lags. Access it directly via
`https://www.kaggle.com/code/<username>/<kernel-slug>` while waiting for the index to
update.
