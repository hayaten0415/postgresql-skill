# Changelog

## 1.2.1 — 2026-07-05

Accuracy and design fixes from external review:

- Replace unsourced speed-multiplier claims ("100-1000x faster" etc.) in
  impactDescription with mechanism-based descriptions across 16 rules;
  fix the 5-10x / 100x+ inconsistency inside security-rls-performance
- data-pagination: correct the O(1) claim (index seek is O(log n) — the
  point is cost no longer grows with page depth), replace the
  computed-offset cursor example with a last-seen-value cursor, and
  document the no-arbitrary-page-jump trade-off
- query-missing-indexes: sequential scans grow linearly, not
  "exponentially"; remove fabricated EXPLAIN cost numbers
- conn-pooling: replace the spindle-era sizing formula with a CPU-core
  starting point plus load-test guidance
- SKILL.md: single severity system — per-rule impact drives scrutiny and
  report order; the category table is navigation only. Selective rule
  reading instead of whole-category reads; compact coverage footer
  allowed for small diffs
- README: state explicitly that check_skill.py is a structure lint only
  and trigger_cases.yaml is a manual spec, not an executed test

## 1.2.0 — 2026-07-05

Initial release, developed iteratively in one day (earlier internal
versions 1.0.0–1.1.1 consolidated here): 36 review rules across 6
categories, derived from supabase/agent-skills (MIT) and generalized for
plain PostgreSQL, extended with original review rules grounded in
the official PostgreSQL documentation. Review procedure with per-category
coverage footer, structure lint, and trigger routing cases.
