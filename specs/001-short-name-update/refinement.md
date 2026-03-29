---
branch: "001-short-name-update"
created: "2026-03-29"
---

## [001] Fix off-by-one in calculate_average

**Date**: 2026-03-29
**Type**: bug
**File(s)**: test.py

### What was wrong

Line 3: divisor was `len(numbers) - 1` instead of `len(numbers)`. For a 4-element list this divides by 3, returning a wrong result (33.33… instead of 25). For a 1-element list it raises `ZeroDivisionError`.

### What was changed

`return total / (len(numbers) - 1)` → `return total / len(numbers)`

### Why

Average = sum / count. The `- 1` has no mathematical basis here — it belongs in sample standard deviation (Bessel's correction), not mean calculation.

---

## [002] Fix cache key collision and mutable default argument in calculate_average

**Date**: 2026-03-29
**Type**: bug
**File(s)**: test.py

### What was wrong

Two bugs in the caching rewrite:

1. **Line 10**: `key = len(numbers)` — cache key is only the list length. Any two lists of equal length (e.g. `[1,2,3]` and `[10,20,30]`) map to the same key, so the second call returns the first call's result.

2. **Lines 9 & 16–22**: `_seen={}` mutable default argument is shared across all calls. After the first call populates `_seen`, subsequent calls check `if i in _seen` and reuse the first call's values by index — regardless of what `numbers` actually contains.

### What was changed

- Cache key changed from `len(numbers)` → `tuple(numbers)` (value-based identity).
- Removed `_seen` logic entirely; replaced with `sum(numbers)` (the `_seen` accumulation added no value and was the source of the cross-call contamination).
- Removed the duplicate dead `calculate_average` definition (lines 1–3 were shadowed by the redefinition on line 9).

### Why

`tuple(numbers)` is the minimal correct key: two lists with equal contents produce equal tuples, two lists with different contents do not. The `_seen` pattern was an attempt to memoize per-element work but was fundamentally broken — mutable defaults in Python persist for the lifetime of the function object, not the call.
