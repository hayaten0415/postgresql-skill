---
title: Avoid Leading-Wildcard LIKE — Use Trigram or Full-Text Indexes
impact: HIGH
impactDescription: b-tree useless: every '%term%' search is a full table scan
tags: like, pattern-matching, pg_trgm, full-text-search
---

## Avoid Leading-Wildcard LIKE — Use Trigram or Full-Text Indexes

A B-tree can only use the characters before the first wildcard to bound the scan.
`like 'term%'` narrows the scan; `like '%term'` or `like '%term%'` gives the index
nothing to anchor on, so every search scans the whole table.

**Incorrect (what's wrong):**

```sql
create index products_name_idx on products (name);

-- leading wildcard: no prefix to anchor the b-tree, sequential scan
select id, name
from products
where name like '%phone%';
```

**Correct (the fix):**

```sql
-- trigram index supports substring search, including ilike
create extension if not exists pg_trgm;
create index products_name_trgm_idx
    on products using gin (name gin_trgm_ops);

select id, name
from products
where name like '%phone%';
```

Even prefix-only patterns (`like 'term%'`) need care: a plain B-tree index serves
them only under the `C` collation — otherwise create the index with
`text_pattern_ops`. For searching whole words rather than arbitrary substrings,
full-text search (`tsvector` with a GIN index) scales better than trigrams. Keep
the anchored part of any pattern as long and selective as possible.

Reference: [pg_trgm — trigram matching](https://www.postgresql.org/docs/current/pgtrgm.html)
