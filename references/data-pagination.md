---
title: Use Cursor-Based Pagination Instead of OFFSET
impact: MEDIUM-HIGH
impactDescription: page depth stops affecting cost — OFFSET reads and discards every skipped row
tags: pagination, cursor, keyset, offset, performance
---

## Use Cursor-Based Pagination Instead of OFFSET

`offset` pagination reads and discards all skipped rows, so cost grows linearly
with page depth. Keyset (cursor) pagination seeks the index directly to the last
row the client saw, so every page costs roughly the same regardless of depth.

**Incorrect (OFFSET pagination):**

```sql
-- Page 1: reads 20 rows
select * from products order by id limit 20 offset 0;

-- Deep page: reads and discards 199,980 rows to return 20
select * from products order by id limit 20 offset 199980;
```

**Correct (cursor/keyset pagination):**

```sql
-- First page
select * from products order by id limit 20;
-- Application remembers the id of the last row it served

-- Next page: seek past the remembered value via the index
select * from products
where id > $last_seen_id
order by id
limit 20;
```

For multi-column sorting, the cursor must include every sort column, with a
unique column (e.g. `id`) last as a tie-breaker, and a matching composite index:

```sql
select * from products
where (created_at, id) > ($last_created_at, $last_id)
order by created_at, id
limit 20;
```

Trade-off: keyset pagination only supports next/previous from a page you have
already seen — there is no way to jump to "page 500" without counting rows, so
numbered page links need `offset` (cap the depth) or a precomputed mapping.
Deep OFFSET pages have a second defect anyway: rows inserted or deleted between
requests shift the pages, so users see duplicates or gaps — a cursor is stable.

Reference: [LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html)
