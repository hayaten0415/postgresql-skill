---
title: Partition Large Tables for Better Performance
impact: MEDIUM-HIGH
impactDescription: 5-20x faster queries and maintenance on large tables
tags: partitioning, large-tables, time-series, performance
---

## Partition Large Tables for Better Performance

Partitioning splits a large table into smaller pieces, improving query performance and maintenance operations.

**Incorrect (single large table):**

```sql
create table events (
  id bigint generated always as identity,
  created_at timestamptz,
  data jsonb
);

-- 500M rows, queries scan everything
select * from events where created_at > '2024-01-01';  -- Slow
vacuum events;  -- Takes hours, locks table
```

**Correct (partitioned by time range):**

```sql
create table events (
  id bigint generated always as identity,
  created_at timestamptz not null,
  data jsonb
) partition by range (created_at);

-- Create partitions for each month
create table events_2024_01 partition of events
  for values from ('2024-01-01') to ('2024-02-01');

create table events_2024_02 partition of events
  for values from ('2024-02-01') to ('2024-03-01');

-- Queries only scan relevant partitions
select * from events where created_at > '2024-01-15';  -- Only scans events_2024_01+

-- Drop old data instantly
drop table events_2023_01;  -- Instant vs DELETE taking hours
```

When to partition:

- Tables > 100M rows
- Time-series data with date-based queries
- Need to efficiently drop old data

Adding an index to an already-partitioned live table needs a special sequence —
`create index concurrently` does not work on the parent (see
`schema-migration-locks.md`):

```sql
-- 1. build on each partition without blocking writes
create index concurrently events_2024_01_created_idx on events_2024_01 (created_at);
-- 2. create an invalid parent index without touching partitions
create index events_created_idx on only events (created_at);
-- 3. attach each partition index; parent becomes valid when all are attached
alter index events_created_idx attach partition events_2024_01_created_idx;
```

Reference: [Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
