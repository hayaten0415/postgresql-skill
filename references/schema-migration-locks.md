---
title: Avoid Long Locks in Migrations — CONCURRENTLY, NOT VALID, lock_timeout
impact: CRITICAL
impactDescription: production outage: DDL holds ACCESS EXCLUSIVE and blocks all reads and writes while it runs
tags: migrations, locking, create-index-concurrently, not-valid, lock-timeout
---

## Avoid Long Locks in Migrations — CONCURRENTLY, NOT VALID, lock_timeout

A plain `create index` blocks every write to the table for the entire build, and
most `alter table` forms take `ACCESS EXCLUSIVE`, blocking reads too. Worse, DDL
waiting for a lock queues *behind* any long-running transaction — and every other
query then queues behind the DDL, so even a "fast" migration can freeze
production for minutes.

**Incorrect (blocking DDL on a live table):**

```sql
-- blocks all writes to orders for the whole build (minutes on large tables)
create index orders_customer_id_idx on orders (customer_id);

-- scans every row to validate WHILE holding ACCESS EXCLUSIVE
alter table orders
  add constraint orders_total_positive check (total >= 0);

-- no lock_timeout: if a long transaction holds the table, this waits
-- indefinitely and every query behind it piles up
alter table orders alter column note set not null;
```

**Correct (non-blocking equivalents, fail fast on contention):**

```sql
-- fail fast instead of queueing the whole workload behind us; retry on failure
set lock_timeout = '5s';

-- builds without blocking writes (cannot run inside a transaction block)
create index concurrently orders_customer_id_idx on orders (customer_id);

-- 1) attach the constraint without scanning (brief lock only)
alter table orders
  add constraint orders_total_positive check (total >= 0) not valid;
-- 2) validate in a second step: takes only SHARE UPDATE EXCLUSIVE,
--    writes continue during the scan
alter table orders validate constraint orders_total_positive;

-- NOT NULL without a blocking full-table scan (PG 12+):
alter table orders
  add constraint orders_note_not_null check (note is not null) not valid;
alter table orders validate constraint orders_note_not_null;
alter table orders alter column note set not null;  -- uses the validated check, no scan
alter table orders drop constraint orders_note_not_null;
```

The same two-step `not valid` / `validate` pattern applies to foreign keys. Other
rewrite traps to flag in migration review: `alter column ... type` rewrites the
whole table under `ACCESS EXCLUSIVE` (add a new column and backfill in batches
instead), and `add column ... default` with a *volatile* default does too. If
`create index concurrently` fails it leaves an `INVALID` index behind — drop it
and retry. Wrap DDL in a retry loop honoring `lock_timeout` rather than raising
the timeout.

Reference: [ALTER TABLE — Notes on locking](https://www.postgresql.org/docs/current/sql-altertable.html) / [Building Indexes Concurrently](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY)
