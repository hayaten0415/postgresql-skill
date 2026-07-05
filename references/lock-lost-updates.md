---
title: Prevent Lost Updates — Atomic UPDATE or Row Locks for Read-Modify-Write
impact: CRITICAL
impactDescription: concurrent writes silently overwrite each other (lost increments, wrong balances)
tags: lost-update, row-locks, for-update, read-committed, concurrency
---

## Prevent Lost Updates — Atomic UPDATE or Row Locks for Read-Modify-Write

Under the default `READ COMMITTED` isolation, a plain `select` takes no lock: two
transactions can read the same row, compute in the application, and write back —
the second commit silently overwrites the first. Any select-compute-update
sequence in application code is a lost update waiting for load.

**Incorrect (read-modify-write across statements, no lock):**

```sql
begin;
-- both transactions read balance = 100...
select balance from accounts where id = $1;
-- ...both compute 100 - 50 in the app and write 50:
-- one withdrawal disappears, no error raised
update accounts set balance = 50 where id = $1;
commit;
```

**Correct (make the statement atomic, or lock the row on read):**

```sql
-- best: one atomic statement — the UPDATE itself locks the row,
-- and the expression is evaluated against the current value
update accounts
set balance = balance - 50
where id = $1 and balance >= 50
returning balance;

-- when the app must inspect the value before deciding, lock on read
begin;
select balance from accounts where id = $1 for no key update;
-- concurrent writers now block until this transaction commits
update accounts set balance = $2 where id = $1;
commit;
```

An optimistic alternative that holds no lock: a version column with
`update ... where id = $1 and version = $expected`, retrying when zero rows
match. Running the transaction under `repeatable read` also detects the
conflict, but as a serialization error the application must catch and retry.
Pick one strategy per hot table and apply it consistently.

Reference: [Row-Level Locks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS)
