---
title: Handle NULLs in Unique Constraints Used for Upserts
impact: MEDIUM-HIGH
impactDescription: silent duplicate rows instead of updates (data integrity corruption)
tags: unique-constraints, upsert, on-conflict, null-handling
---

## Handle NULLs in Unique Constraints Used for Upserts

By default, unique constraints treat NULLs as distinct from each other, so two rows that differ only by a NULL column both pass the constraint. An `insert ... on conflict` targeting that key never matches the existing row and keeps inserting duplicates instead of updating.

**Incorrect (nullable column in the conflict target silently duplicates):**

```sql
create table stock_levels (
  product_id  int not null,
  location_id int,          -- null means "default location"
  quantity    int not null,
  unique (product_id, location_id)
);

-- Each run with a null location INSERTS a new row instead of updating:
-- (1, null) is never "equal" to the existing (1, null)
insert into stock_levels (product_id, location_id, quantity)
values (1, null, 25)
on conflict (product_id, location_id)
do update set quantity = excluded.quantity;
```

**Correct (make NULLs compare equal, or eliminate them):**

```sql
-- PostgreSQL 15+: NULLS NOT DISTINCT makes (1, null) conflict with (1, null)
create table stock_levels (
  product_id  int not null,
  location_id int,
  quantity    int not null,
  unique nulls not distinct (product_id, location_id)
);

-- Better on any version: replace the NULL with a real sentinel value
-- and make the column not null
alter table stock_levels
  alter column location_id set default 0,
  alter column location_id set not null;
```

On PostgreSQL 14 and earlier, the alternative is a partial unique index (`create unique index ... (product_id) where location_id is null`) plus a second index for non-null rows — but `on conflict` cannot target two indexes at once, so restructuring the schema to avoid the NULL is usually the cleaner fix.

Reference: [Unique Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS)
