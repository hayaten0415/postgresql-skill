---
title: Avoid NOT IN with Nullable Subqueries
impact: CRITICAL
impactDescription: silently returns zero rows; also blocks anti-join optimization
tags: null-handling, subqueries, correctness, anti-join
---

## Avoid NOT IN with Nullable Subqueries

If a `not in (select ...)` subquery returns even one NULL, the whole predicate evaluates to unknown and the query silently returns zero rows. The planner also cannot turn `not in` into an anti-join, so even the "working" case degrades badly at scale.

**Incorrect (one NULL in the subquery empties the result):**

```sql
-- If any account has a NULL team_id, this returns 0 rows —
-- x not in (1, 2, null) is never true, only false or unknown
select u.email
from users u
where u.team_id not in (select team_id from archived_accounts);
```

**Correct (NOT EXISTS is null-safe and plans as an anti-join):**

```sql
-- NOT EXISTS treats non-matching rows correctly regardless of NULLs,
-- and the planner can use a hash anti-join
select u.email
from users u
where not exists (
  select from archived_accounts a
  where a.team_id = u.team_id
);
```

`not in` is safe with a literal list of non-null constants (`status not in ('void', 'draft')`). For subqueries, prefer `not exists`, or a `left join ... where b.id is null` anti-join. If you must keep `not in`, add `where team_id is not null` inside the subquery — but that still leaves the slower subplan.

Reference: [Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html)
