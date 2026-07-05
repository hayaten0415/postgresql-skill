---
title: Build Optional Filters Dynamically, Not with OR-IS-NULL Catch-Alls
impact: HIGH
impactDescription: full table scan despite indexes on every filter column
tags: dynamic-sql, prepared-statements, or-is-null, where-clause
---

## Build Optional Filters Dynamically, Not with OR-IS-NULL Catch-Alls

A single static statement that disables unused filters via
`(col = $1 or $1 is null)` looks clever, but the planner must produce one plan
that is safe for every parameter combination — the worst case where no filter
applies. Once a prepared statement switches to a generic plan (typically from the
sixth execution), no index can be used and every call scans the table.

**Incorrect (what's wrong):**

```sql
-- one statement for all filter combinations: generic plan cannot prune
-- the ORs, so indexes on customer_id and status are ignored
select id, customer_id, status, total
from orders
where (customer_id = $1 or $1 is null)
  and (status      = $2 or $2 is null);
```

**Correct (the fix):**

```sql
-- generate only the predicates actually supplied (query builder / ORM),
-- still using bind parameters
select id, customer_id, status, total
from orders
where customer_id = $1;

-- ...and a different statement when both filters are set
select id, customer_id, status, total
from orders
where customer_id = $1
  and status = $2;
```

Dynamic SQL with bind parameters is the right tool here: each variant gets its
own optimal plan, and plan caching still works per variant. If a static statement
truly cannot be avoided, `set plan_cache_mode = force_custom_plan` re-plans with
actual values on every execution — at the cost of losing plan reuse entirely.
Never fix this by interpolating literals; that trades a performance bug for a SQL
injection risk.

Reference: [PREPARE — generic vs. custom plans](https://www.postgresql.org/docs/current/sql-prepare.html)
