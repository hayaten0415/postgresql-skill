---
title: Keep Predicates Sargable — No Casts or Arithmetic on Columns
impact: HIGH
impactDescription: index silently skipped: transforming the column side forces a scan of every row
tags: sargable, type-cast, arithmetic, where-clause
---

## Keep Predicates Sargable — No Casts or Arithmetic on Columns

The planner can only use an index when the bare column sits alone on one side of
the comparison. Casting the column or doing math on it makes the predicate
non-sargable; move the conversion or arithmetic to the constant side, where it is
evaluated once instead of once per row.

**Incorrect (what's wrong):**

```sql
-- cast applied to the column: index on order_ref unusable
select * from orders where order_ref::int = 42;

-- arithmetic on the column: index on total_cents unusable
select * from orders where total_cents / 100 >= $1;
```

**Correct (the fix):**

```sql
-- convert the parameter instead; the column stays bare
select * from orders where order_ref = $1::text;

-- solve the equation for the column
select * from orders where total_cents >= $1 * 100;
```

Watch for the schema smell behind these casts: numbers stored in text columns.
Besides defeating indexes, `'042'` and `'42'` compare as different strings, and
one malformed row makes any query that casts the column error out. Store numbers
in numeric types and pass parameters with the correct type — drivers bind typed
values fine. If the computation genuinely cannot move to the constant side,
normalize it (constants on the right) and create an expression index on the
left-hand expression.

Reference: [Type Conversion](https://www.postgresql.org/docs/current/typeconv.html)
