# Competition Memory

Each competition gets a persistent local knowledge base under `~/.kaggle_agent/<comp>/`.
The purpose is to avoid re-deriving rules, re-debugging known errors, and re-discovering
domain knowledge across sessions.

## Directory structure

```
~/.kaggle_agent/
└── <competition-slug>/
    ├── NOTES.md              # main memory file — always read at session start
    ├── experiments/
    │   └── log.md            # one entry per submission: method, score, conclusion
    └── <notebook-slug>/
        ├── kernel-metadata.json
        ├── <notebook>.ipynb
        └── output/
```

## NOTES.md — what goes in it

Create this file the first time you work on a competition. Update it during the
session whenever you learn something worth keeping. It has five sections:

```markdown
# <Competition Name>

## Rules & constraints
- Submission type: CSV / code / mixed (note the exact submit command)
- Evaluation metric: <metric name + link to definition>
- Submission quota: <N per day>
- External data allowed: yes / no
- Internet in kernel: yes / no
- GPU allowed: yes / no
- Deadline: <date>

## Domain knowledge
<!-- What you've learned about the problem domain that isn't obvious from the data.
     E.g. for a geology competition: what the features physically represent,
     known relationships between variables, domain-specific preprocessing norms. -->

## Pitfalls & fixes
<!-- Errors you hit and how you resolved them. Format:
     - [date] <what went wrong> → <fix> -->

## Current best
- Score: <value> (<public/private LB>)
- Method: <one-line description>
- Kernel: <notebook-slug> v<N>

## Ideas & next steps
<!-- Untried approaches, ranked roughly by expected gain -->
- [ ] <idea>
```

## experiments/log.md — what goes in it

One entry per submission, appended chronologically:

```markdown
## <date> — <short description>

- Kernel: <notebook-slug> v<N>
- Score: <public LB score>
- Method: <what this run did differently>
- Conclusion: <what you learned — did it help? why?>
```

## When to read and update

**At session start**: always read `NOTES.md` before doing anything. It tells you
where you left off, what the rules are, and what not to repeat.

**During the session**: update `NOTES.md` whenever you:
- Hit an error and fix it (add to Pitfalls)
- Learn something about the domain (add to Domain knowledge)
- Get a new best score (update Current best)
- Think of a new idea (add to Ideas)

**After each submission**: append an entry to `experiments/log.md`.

**At session end**: do a quick pass to make sure NOTES.md reflects the current state.
The next session's you will thank you.

## Initializing a new competition

When starting a competition for the first time:

```bash
COMP="<competition-slug>"
mkdir -p ~/.kaggle_agent/$COMP/experiments

# Download sample submission to understand the format
kaggle competitions download $COMP -f sample_submission.csv \
  -p ~/.kaggle_agent/$COMP/

# Create NOTES.md with the rules skeleton
# Fill in what you can from kaggle competitions files $COMP
# and the competition page
```

Then fill in the Rules & constraints section before writing any code.
