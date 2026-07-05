# postgres-review

A Claude Code skill that reviews SQL queries, schema definitions, and migrations
against PostgreSQL best practices. It reports high-confidence findings —
performance traps, silent-wrong-result bugs, migration lock hazards, RLS issues —
each backed by a rule file with incorrect/correct SQL examples.

## Contents

- `SKILL.md` — the review procedure Claude follows
- `references/` — one rule per file, named `<category>-<topic>.md`, with impact
  level (CRITICAL / HIGH / MEDIUM-HIGH) in the frontmatter

Categories: query performance, connection management, security & RLS, schema
design, concurrency & locking, data access patterns.

## Install

Symlink into your personal skills directory:

```sh
ln -s /path/to/postgresql-skill ~/.claude/skills/postgres-review
```

Then ask Claude Code to review a migration, schema, or query diff.

## Attribution

Rule catalog derived from
[supabase/agent-skills](https://github.com/supabase/agent-skills)
(`supabase-postgres-best-practices`, MIT), generalized for plain PostgreSQL and
extended with additional review-focused rules. MIT licensed.
