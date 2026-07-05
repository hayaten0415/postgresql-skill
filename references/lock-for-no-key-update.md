---
title: Prefer FOR NO KEY UPDATE Over FOR UPDATE When Keys Don't Change
impact: MEDIUM-HIGH
impactDescription: hot parent rows serialize all child-table inserts behind the lock
tags: for-update, for-no-key-update, row-locks, foreign-keys, contention
---

## Prefer FOR NO KEY UPDATE Over FOR UPDATE When Keys Don't Change

Foreign key checks take a `for key share` lock on the referenced row, and
`for update` is the one row-lock mode that blocks it. Locking a parent row with
`select ... for update` therefore stalls every concurrent insert into child
tables referencing it — even though you only intend to update a non-key column.

**Incorrect (over-strong lock blocks child inserts):**

```sql
begin;
-- only status will change, but FOR UPDATE blocks the FOR KEY SHARE
-- taken by FK checks: every concurrent
--   insert into order_items (order_id, ...) values ($1, ...)
-- now waits until this transaction commits
select * from orders where id = $1 for update;

update orders set status = 'processing' where id = $1;
commit;
```

**Correct (weakest mode that still blocks writers):**

```sql
begin;
-- blocks concurrent UPDATE/DELETE on the row, but lets FK checks
-- (FOR KEY SHARE) proceed — child inserts continue unblocked
select * from orders where id = $1 for no key update;

update orders set status = 'processing' where id = $1;
commit;
```

This matches what a plain `update` of non-key columns acquires internally, so
the explicit lock is no stronger than the update it protects. Reserve
`for update` for when the transaction will `delete` the row or change key
columns (primary/unique keys referenced by FKs). For readers that only need the
row to not disappear, `for share` — or the still-weaker `for key share` — keeps
even more concurrency.

Reference: [Row-Level Locks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS)
