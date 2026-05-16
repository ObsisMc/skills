# SPEC.md Template

For non-trivial competition entries, write the plan before writing the code. A short
spec costs ~30 minutes and saves much more than that in misdirected work — especially
when delegating to a coding agent that can't ask clarifying questions about goals.

## Why a SPEC

- Forces explicit decisions on metric, evaluation strategy, time budget
- Becomes durable context for an agent to come back to, rather than re-deriving from
  competition page every time
- Captures the "why" of strategic choices so iteration doesn't re-litigate them

## Template

Save as `SPEC.md` in the competition's working directory:

```markdown
# Competition: <name>

## 1. Overview
- Task: <classification / regression / detection / generation / ...>
- Metric: <AUC / mAP / F1 / custom — link to the exact definition>
- Submission type: <CSV / notebook / model>
- Deadline: <date>
- Current top score: <value>
- Submission quota per day: <N>

## 2. Data
- Train size, test size, key files (from `kaggle competitions files <slug>`)
- Schema: input columns, target columns, ID column
- Train/test overlap: <yes / no / partial — from EDA>
- Distribution drift: <noted issues — from EDA>
- Missing values: <pattern summary — from EDA>

## 3. Top public approaches
- <kernel link>: <score>, <one-line strategy>
- <kernel link>: <score>, <one-line strategy>
- <kernel link>: <score>, <one-line strategy>

## 4. Plan
- Phase 1 (Day 1): reproduce strongest public baseline end-to-end, submit it
- Phase 2 (Days 2-N): high-ROI improvements — list them ranked by expected gain
  - [ ] <idea 1>
  - [ ] <idea 2>
- Phase 3 (final): tuning, ensembling, submission selection

## 5. Constraints
- Submission format and grader quirks
- Time/GPU limits (e.g. 9h GPU runtime in code competitions)
- Internet on/off
- External data allowed: <yes / no>

## 6. Targets
| Milestone | Target score | When |
|-----------|--------------|------|
| Baseline submitted | <value> | Day 1 |
| Beat median | <value> | Day 3 |
| Top 25% | <value> | Day N |

## 7. Open questions
- <things you don't know yet, to revisit>
```

## How to use the SPEC

- Treat it as a living document, but update it deliberately, not in passing
- When delegating to a coding agent, pass the SPEC as context — it answers most of
  what the agent would otherwise ask
- When the plan changes, change the SPEC first, then change the code
- The "Open questions" section is for things you'll resolve via EDA or experiments;
  don't pretend to have answered them
