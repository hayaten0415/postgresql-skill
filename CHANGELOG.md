# Changelog

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
