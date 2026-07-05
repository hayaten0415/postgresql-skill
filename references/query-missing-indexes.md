---
title: Add Indexes on WHERE and JOIN Columns
impact: CRITICAL
impactDescription: index scan instead of a full sequential scan on every query
tags: indexes, performance, sequential-scan, query-optimization
---

## Add Indexes on WHERE and JOIN Columns

Queries filtering or joining on unindexed columns cause full table scans, whose cost grows linearly with table size — invisible at 10k rows, dominant at 100M.

**Incorrect (sequential scan on large table):**

```sql
-- No index on customer_id causes full table scan
select * from orders where customer_id = 123;

-- EXPLAIN shows a Seq Scan node: every row is read and tested
```

**Correct (index scan):**

```sql
-- Create index on frequently filtered column
create index orders_customer_id_idx on orders (customer_id);

select * from orders where customer_id = 123;

-- EXPLAIN now shows an Index Scan using orders_customer_id_idx:
-- only matching rows are read
```

For JOIN columns, always index the foreign key side:

```sql
-- Index the referencing column
create index orders_customer_id_idx on orders (customer_id);

select c.name, o.total
from customers c
join orders o on o.customer_id = c.id;
```

Reference: [Indexes](https://www.postgresql.org/docs/current/indexes.html)
