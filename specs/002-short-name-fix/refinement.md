---
branch: "002-short-name-fix"
created: "2026-03-29"
---

## [001] Fix unhashable list used as cache key

**Date**: 2026-03-29
**Type**: bug
**File(s)**: test1.py

### What was wrong

Line 5: `key = numbers` used the input list directly as a dict key. Python lists are unhashable, so `_cache[key]` raises `TypeError: unhashable type: 'list'` at runtime.

### What was changed

Changed `key = numbers` → `key = tuple(numbers)` so the cache key is an immutable, hashable tuple.

### Why

Dict keys must be hashable. Tuples are the canonical way to make a list hashable for this purpose. The cache now works correctly for any input list.

### Other observations

- The function silently returns `0` for empty input rather than raising an error — may or may not be intentional.
