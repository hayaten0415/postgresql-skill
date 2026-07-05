---
title: Store Timestamps as timestamptz, Not timestamp
impact: HIGH
impactDescription: silently shifted times across time zones — wrong data with no error
tags: timestamptz, time-zones, data-types, correctness
---

## Store Timestamps as timestamptz, Not timestamp

A `timestamp` (without time zone) column stores bare wall-clock digits: any time
zone offset in the input is silently discarded, and the same column value means a
different instant to every client. `timestamptz` stores the absolute instant
(normalized to UTC internally) and converts on display — same 8 bytes, no storage
cost.

**Incorrect (offset silently thrown away):**

```sql
create table events (
  id        bigint generated always as identity primary key,
  starts_at timestamp        -- bare wall-clock, no zone
);

-- The +09 offset is dropped without error: stored as "10:00:00".
-- A client in UTC reads it as 10:00 UTC — nine hours off
insert into events (starts_at)
values ('2026-07-05 10:00:00+09');
```

**Correct (absolute instant, rendered per zone):**

```sql
create table events (
  id        bigint generated always as identity primary key,
  starts_at timestamptz      -- absolute instant, stored as UTC
);

insert into events (starts_at)
values ('2026-07-05 10:00:00+09');   -- offset honored: 01:00:00 UTC

-- Convert at the edge, per user/zone
select starts_at at time zone 'Asia/Tokyo' from events;
```

Comparing or mixing the two types implicitly converts through the session's
`TimeZone` setting, so the same query returns different results depending on who
runs it — a common source of "works locally, wrong in production." Reserve plain
`timestamp` for genuinely zone-less wall-clock values (e.g. recurring local
opening hours, paired with a separate zone column); for "when did this happen"
data, always use `timestamptz`.

Reference: [Date/Time Types](https://www.postgresql.org/docs/current/datatype-datetime.html)
