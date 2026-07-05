---
title: Create Expression Indexes for Transformed Column Predicates
impact: HIGH
impactDescription: full table scan: index on the raw column is ignored when the query filters on an expression
tags: index, expression-index, functions, where-clause
---

## Create Expression Indexes for Transformed Column Predicates

To the planner, `lower(email)` and `email` are unrelated values, so a plain index on
`email` can never serve a `where lower(email) = ...` predicate. Any function or
expression wrapped around a column in a hot predicate needs its own expression index.

**Incorrect (what's wrong):**

```sql
create index users_email_idx on users (email);

-- case-insensitive lookup: the index above is never used, full scan every time
select id, name
from users
where lower(email) = lower($1);
```

**Correct (the fix):**

```sql
-- index the expression itself; the query must use the exact same expression
create index users_email_lower_idx on users (lower(email));

select id, name
from users
where lower(email) = lower($1);
```

Standardize on one canonical expression (e.g. always `lower`, never a mix of
`lower` and `upper`) so a single index serves every query — each extra index
slows every insert, update, and delete. Functions used in an index must be
`immutable`; anything depending on the clock or settings (e.g. computing an age
from `now()`) cannot be indexed — filter on the underlying column with a range
instead. Beware ORMs that add `lower()`/`upper()` implicitly for
case-insensitive matching. For emails specifically, `citext` is an alternative.

Reference: [Indexes on Expressions](https://www.postgresql.org/docs/current/indexes-expressional.html)
