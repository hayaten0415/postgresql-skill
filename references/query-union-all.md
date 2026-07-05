---
title: Use UNION ALL When Duplicates Are Impossible or Acceptable
impact: MEDIUM-HIGH
impactDescription: needless sort/hash over the whole combined result, plus silently merged rows
tags: union, union-all, deduplication, sorting
---

## Use UNION ALL When Duplicates Are Impossible or Acceptable

`union` deduplicates: the entire combined result is sorted or hashed before a
single row is returned. When the branches cannot overlap — or duplicates are
fine — that work is pure waste, and it also silently merges rows that are
legitimately identical (two same-amount payments become one).

**Incorrect (dedup over disjoint branches):**

```sql
-- The literal 'invoice' / 'refund' column makes overlap impossible,
-- yet UNION still sorts/hashes everything to dedup — and would
-- collapse two identical refunds into one row
select id, amount, 'invoice' as source from invoices where customer_id = $1
union
select id, amount, 'refund'  as source from refunds  where customer_id = $1;
```

**Correct (append and stream):**

```sql
-- UNION ALL appends the branches with no dedup step:
-- rows stream out as each branch produces them
select id, amount, 'invoice' as source from invoices where customer_id = $1
union all
select id, amount, 'refund'  as source from refunds  where customer_id = $1;
```

In `EXPLAIN`, a `Unique`, `Sort`, or `HashAggregate` node sitting above the
`Append` is the cost of `union` — it also blocks streaming to the client until
dedup finishes. If deduplication is genuinely required, `union` is correct;
state that intent in a comment so reviewers don't "fix" it. Note that `union`
compares all selected columns, so adding a discriminator column (as above) often
removes the need for dedup entirely.

Reference: [Combining Queries (UNION, INTERSECT, EXCEPT)](https://www.postgresql.org/docs/current/queries-union.html)
