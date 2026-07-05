---
title: Filter Dates with Half-Open Ranges, Not Functions on the Column
impact: HIGH
impactDescription: index unusable plus boundary rows double-counted across periods
tags: dates, range, between, sargable, where-clause
---

## Filter Dates with Half-Open Ranges, Not Functions on the Column

Wrapping a timestamp column in `date_trunc`, `::date`, `to_char`, or `extract` to
select a day/month/quarter hides the column from a plain B-tree index. An explicit
half-open range condition expresses the same period, uses the index directly, and
assigns each instant to exactly one period.

**Incorrect (what's wrong):**

```sql
-- function on the column: index on sale_date cannot bound the scan
select sum(amount)
from sales
where date_trunc('day', sale_date) = date '2026-07-04';

-- BETWEEN is inclusive on both ends: a sale at exactly midnight on
-- 2026-07-05 lands in BOTH this period and the next one
select sum(amount)
from sales
where sale_date between '2026-07-04' and '2026-07-05';
```

**Correct (the fix):**

```sql
-- half-open range: plain index on sale_date bounds the scan exactly,
-- and consecutive periods tile without overlap
select sum(amount)
from sales
where sale_date >= date '2026-07-04'
  and sale_date <  date '2026-07-04' + interval '1 day';
```

`between` is fine for truly discrete values (`id between 1 and 100`), but
timestamps are effectively continuous — and the `between ... and '23:59:59'`
workaround silently drops rows in the final second. Prefer `>= start and < end`;
it matches how range types and partition bounds work in PostgreSQL. An expression
index on `date_trunc('day', sale_date)` is a fallback, but it locks every query
into that exact expression and one granularity; a range on the raw column works
for days, months, and quarters with a single index.

Reference: [Index Types — B-tree](https://www.postgresql.org/docs/current/indexes-types.html#INDEXES-TYPES-BTREE)
