# Code-Competition Queue Behavior

**This applies only to code competitions** (where Kaggle re-runs your notebook
against the hidden test set), not to direct-CSV competitions.

## CSV competitions: deterministic, immediate

In a direct-CSV competition, the public LB score is computed against a fixed public
test subset and is deterministic — it appears within seconds and does not change.
**Do not apply the "wait 4 hours" rule here.** If a CSV submission's score is X, it's X.

## Code competitions: queue + delayed scoring

In a code competition, the flow is different:

```
submit → notebook enters queue → eventually runs on hidden test → score appears
```

A few things follow from this.

### Queue delays grow toward the deadline

As the deadline approaches, the queue gets congested. A submission that normally
runs in 30 minutes can sit for hours. Plan final submissions earlier than you think
you need to.

### Submissions before deadline are scored eventually

All submissions submitted **before** the deadline are scored eventually, even if they
finish executing after the deadline. This is the documented behavior on most code
competitions. Do not assume a slow queue costs you the submission. Double-check on
the specific competition's FAQ if it matters.

### The "4-hour heuristic"

The author of this skill has observed that for some code competitions, the score
visible immediately after a run completes is less reliable than the score visible
~4 hours later — possibly due to deferred re-grading or rolling updates. If major
strategy decisions hinge on a score, prefer waiting and re-checking before acting.

**Important caveats:**

- This is a heuristic from one author's experience, **not** documented Kaggle behavior
- Treat it as "don't burn the rest of your submission budget chasing a single score
  that just appeared"
- Do not generalize this to non-code competitions

## Practical implications

For code competitions:

- **Submit early.** Multiple times if the daily quota allows. Late submissions risk
  not finishing before users care about the score.
- **Don't make irreversible decisions on one early reading.** Delete a model, change
  the whole approach, etc. — wait for the score to settle, or take multiple readings.
- **Track which queue your submission is in.** Code competitions usually show a
  status (QUEUED → RUNNING → COMPLETE). If it's been QUEUED for hours during a
  non-deadline period, something is wrong; check the competition forum for outages.

For CSV competitions:

- The score is immediate and trustworthy. The public LB is a noisy estimate of the
  private LB (different test subsets), but the public LB number itself is fixed.

## Score swing causes

If a score moves between two reads, possible reasons (in rough order of likelihood):

1. **You submitted a different version and forgot** — check `kaggle competitions submissions <comp>`
2. **Code competition: queue re-ran your notebook** (rare but possible)
3. **Public LB recalculation by Kaggle** (very rare, usually announced)
4. **You're misreading the leaderboard** — public vs private, your team's best vs
   your latest, etc.

Rule out 1 and 4 before considering 2 or 3.
