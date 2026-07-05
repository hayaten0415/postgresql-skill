# Changelog

## 1.1.1 — 2026-07-05

- Add `tests/check_skill.py`: validates frontmatter keys, impact enum,
  filename prefixes, Incorrect/Correct/Reference structure, H2==title
- Add `tests/trigger_cases.yaml`: routing cases vs. a generation skill,
  including the slow-query boundary case (routed to review)
- Document the partitioned-table CREATE INDEX CONCURRENTLY sequence
  (per-partition CIC → ON ONLY parent → ATTACH) with cross-references
  between schema-migration-locks and schema-partitioning

## 1.1.0 — 2026-07-05

- Add `schema-migration-locks` (CRITICAL): CREATE INDEX CONCURRENTLY,
  NOT VALID / VALIDATE two-step, lock_timeout, table-rewrite traps
- Restore `data-batch-inserts` as MEDIUM-HIGH (write-side N+1)
- Remove Supabase-specific `auth.uid()` from RLS rules; use neutral
  `current_setting()` examples with a note for managed platforms
- Review procedure: mandatory per-category coverage footer; suggest
  EXPLAIN verification for CRITICAL findings
- Description: explicit review-trigger phrases; "not for writing new SQL"
- Add README

## 1.0.0 — 2026-07-05

- Initial release: 32 review rules across 6 impact-prioritized categories,
  derived from supabase/agent-skills (MIT) plus additional original review rules
