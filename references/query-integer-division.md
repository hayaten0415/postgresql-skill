---
title: Cast Before Dividing Integers
impact: MEDIUM-HIGH
impactDescription: silently truncated results (percentages and ratios come out as 0)
tags: integer-division, casting, correctness, aggregates
---

## Cast Before Dividing Integers

Dividing two integers in PostgreSQL truncates toward zero, so `3 / 4` is `0`, not `0.75`. This bites hardest in ratio and percentage calculations built on `count(*)`, which returns `bigint` — the query runs fine and quietly reports 0%.

**Incorrect (integer division truncates before the multiply):**

```sql
-- count(*) is bigint, so failed / total is 0 for any ratio under 1,
-- and the result is always 0%
select
  count(*) filter (where status = 'failed')
  / count(*) * 100 as failure_pct
from deliveries;
```

**Correct (cast one operand so division happens in numeric):**

```sql
-- Casting either operand promotes the whole division
select
  round(
    count(*) filter (where status = 'failed')::numeric
    / count(*) * 100, 1
  ) as failure_pct
from deliveries;
```

Also guard denominators that can be zero: `total / nullif(denominator, 0)` returns NULL instead of raising a division-by-zero error, and `coalesce(..., 0)` can supply a fallback. Multiplying by `100.0` (a numeric literal) instead of `100` is another idiomatic way to force non-integer arithmetic — but only if the multiplication happens before the division.

Reference: [Mathematical Functions and Operators](https://www.postgresql.org/docs/current/functions-math.html)
