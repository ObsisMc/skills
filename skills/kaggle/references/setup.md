# Setup: Credentials and Data Access

How to set up the `kaggle` CLI and how to access competition data without downloading it.

## Credentials

**The agent must not perform authentication on behalf of the user.** Setting up Kaggle
credentials involves long-lived API tokens that can submit, download, and modify
content under the user's account. These are sensitive secrets — the user must run the
authentication command themselves, in their own shell, where they can see what's
happening and where the token ends up. The agent must not:

- Run `kaggle auth login` or any auth command in a tool call
- Move, copy, or `chmod` a `kaggle.json` / `access_token` file
- Read the contents of these files
- Write API keys into config files, env vars, or scripts

If `kaggle competitions list` fails with an auth error, **stop and instruct the user
to authenticate**. Do not try to fix it by running commands.

### What to tell the user

The modern flow uses browser-based OAuth via the official CLI:

```bash
kaggle auth login
```

This opens a browser, lets the user log in to Kaggle, and writes the token to
`~/.kaggle/access_token`. If the user is on a headless machine (no browser), they
can use:

```bash
kaggle auth login --no-launch-browser
```

which prints a URL to open elsewhere and paste back the resulting code.

After they've authenticated, ask them to confirm by running `kaggle competitions list`
themselves and reporting whether it worked. Only then continue with the workflow.

### Legacy `kaggle.json` flow (if the user already has one)

Older setups use a `kaggle.json` file at `~/.kaggle/kaggle.json` (or
`$KAGGLE_CONFIG_DIR/kaggle.json`). If the user already has this file working,
nothing needs to change. If they're setting up from scratch, prefer
`kaggle auth login`.

### Common setup issues to tell the user about

- **`kaggle: command not found` after `pip install kaggle`**: their Python scripts
  directory isn't on PATH. Tell them to check `~/.local/bin` (Linux/macOS) or
  `%PYTHON_HOME%\Scripts` (Windows) and add it to PATH.
- **Windows kaggle.json location**: `C:\Users\<username>\.kaggle\kaggle.json`.
- **Permission warnings on Linux/macOS**: harmless but noisy. The user can silence
  with `chmod 600 ~/.kaggle/kaggle.json` (this is a user action, not an agent action).

## Accept competition rules first

Before any data operation works on a specific competition, the user must accept the
competition rules in a browser. The CLI gives confusing errors otherwise — usually a
400 or generic auth failure. This trips up nearly every fresh setup.

## Essential CLI commands

```bash
# List competitions
kaggle competitions list

# Inspect a competition's files (sizes, names) — does not download
kaggle competitions files <comp-slug>

# Download only the sample submission (safe, small)
kaggle competitions download <comp-slug> -f sample_submission.csv

# Push a local kernel directory (must contain kernel-metadata.json + notebook)
kaggle kernels push -p ./solution/

# Pull a public kernel WITH its metadata (-m flag is critical)
kaggle kernels pull <owner>/<kernel> -p ./solution/ -m

# Submit
kaggle competitions submit <comp-slug> -f submission.csv -m "<message>"
kaggle competitions submit <comp-slug> -k <user>/<kernel> -v <version> -m "<msg>"

# Status
kaggle competitions submissions <comp-slug>
kaggle kernels status <user>/<kernel-slug>
```

## Getting Data: don't download

Default position: **don't download the training data locally.** Mount it inside a
kernel via `competition_sources` in `kernel-metadata.json` instead. The kernel will
see it at `/kaggle/input/<comp-slug>/`. This is faster, uses no local disk, and
matches the environment your real submission will run in.

Two narrow cases where local download makes sense:

1. **`sample_submission.csv` only** — usually a few KB to a few MB. Useful for
   designing the column schema, drafting the SPEC.md, or building a validation script
   offline:
   ```bash
   kaggle competitions download <comp-slug> -f sample_submission.csv
   ```

2. **Schema inspection without download** — `kaggle competitions files <comp-slug>`
   lists all data files with sizes, so you can see what you're dealing with before
   committing to anything.

If a teammate or user asks "should I download the data?", the answer is almost always
"no, push a kernel instead." Reach for `kaggle competitions download` only when
there's a concrete reason the kernel can't do the work.

## When `-k -v` matters on submit

For code competitions, the submission is the notebook itself running on Kaggle's
infrastructure. Submitting with just `-f submission.csv` creates an orphan submission
not properly linked to a kernel run. Always submit code-competition entries with:

```bash
kaggle competitions submit <comp> -k <user>/<kernel> -v <version> -m "<msg>"
```

where `<version>` is the specific kernel version that produced the submission. You
can find versions with `kaggle kernels status` after a successful commit.
