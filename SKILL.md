---
name: postgres-review
description: Review SQL queries, schema definitions, and migrations against PostgreSQL best practices. Use this skill when asked to review database-related code — "review this migration", "このスキーマをレビュー", "check this query", or a diff touching SQL files, migrations, or ORM schema definitions — to find performance, security, and correctness issues. Not for writing new SQL from scratch; use a generation skill for that.
license: MIT
metadata:
  version: "1.1.0"
  derived-from: https://github.com/supabase/agent-skills (supabase-postgres-best-practices, MIT)
  abstract: PostgreSQL code-review skill backed by performance rules across 6 categories, prioritized by impact from critical (query performance, connection management) to medium (data access patterns). Each rule includes incorrect vs. correct SQL examples used to detect and fix violations.
---

# PostgreSQL Review

Review database-related changes against a curated set of PostgreSQL best-practice rules. Each rule file in `references/` contains the rationale, an incorrect example, a correct example, and the expected performance impact — use them as the review criteria.

## When to Apply

Run this review when the change under review touches:
- SQL files, migrations (raw SQL or ORM-generated)
- Schema definitions (tables, indexes, constraints, partitions)
- Query code (raw SQL in application code, ORM query builders)
- Database configuration (connection pooling, timeouts, roles, RLS policies)

## Review Procedure

1. **Scope the change.** Identify what the diff or target files touch: new tables, new queries, index changes, RLS policies, connection setup, etc. If no target was given, review the pending diff (`git diff` / staged changes); otherwise review the files or SQL the user pointed at.

2. **Select applicable rule categories.** Map what the change touches to categories by filename prefix, highest priority first:

   | Priority | Category | Impact | Prefix | Applies when the change involves |
   |----------|----------|--------|--------|----------------------------------|
   | 1 | Query Performance | CRITICAL | `query-` | SELECT/JOIN/WHERE, indexes |
   | 2 | Connection Management | CRITICAL | `conn-` | pool config, client setup, serverless |
   | 3 | Security & RLS | CRITICAL | `security-` | RLS policies, GRANT/REVOKE, roles |
   | 4 | Schema Design | HIGH | `schema-` | CREATE/ALTER TABLE, types, constraints |
   | 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` | transactions, UPDATE contention, queues |
   | 6 | Data Access Patterns | MEDIUM-HIGH | `data-` | loops issuing queries, bulk writes, pagination |

3. **Read the matching rule files** in `references/` (e.g. a new foreign key → `schema-foreign-key-indexes.md`; a query in a loop → `data-n-plus-one.md`). Read every rule in an applicable category, not just the obvious one — adjacent rules often catch subtler issues.

4. **Check the change against each rule.** A finding must match the rule's "Incorrect" pattern in substance, not just superficially. Do not report speculative issues on code the diff doesn't touch.

5. **Report findings**, ordered by the rule's impact level. For each finding include:
   - **Location** — `file:line`
   - **Rule** — the rule title and its file (e.g. `references/query-missing-indexes.md`)
   - **Impact** — the rule's impact level and expected cost (e.g. "CRITICAL — 100-1000x slower on large tables")
   - **Problem** — what in the change violates the rule, in one or two sentences
   - **Fix** — concrete corrected SQL/code, adapted from the rule's "Correct" example to the actual change

   If nothing violates the rules, say so explicitly rather than inventing low-value findings. For CRITICAL findings, suggest verifying with `explain (analyze, buffers)` against realistic data when practical.

6. **End with a coverage footer.** After the findings, list every category from the table in step 2 with exactly one status: `N findings`, `checked — no findings`, or `N/A (reason it does not apply to this change)`. This makes "reviewed and clean" distinguishable from "not reviewed" — never silently skip a category.

## Notes

- Rules are review criteria, not laws: if the change has a stated reason to deviate (e.g. OFFSET pagination on a small bounded table), note the trade-off instead of flagging it.
- Prefer few high-confidence findings over exhaustive nitpicks. CRITICAL/HIGH categories deserve the most scrutiny.
