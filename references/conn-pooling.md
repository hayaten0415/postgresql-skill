---
title: Use Connection Pooling for All Applications
impact: CRITICAL
impactDescription: a small shared pool serves load that would otherwise exhaust connections and memory
tags: connection-pooling, pgbouncer, performance, scalability
---

## Use Connection Pooling for All Applications

Postgres connections are expensive (1-3MB RAM each). Without pooling, applications exhaust connections under load.

**Incorrect (new connection per request):**

```sql
-- Each request creates a new connection
-- Application code: db.connect() per request
-- Result: 500 concurrent users = 500 connections = crashed database

-- Check current connections
select count(*) from pg_stat_activity;  -- 487 connections!
```

**Correct (connection pooling):**

```sql
-- Use a pooler like PgBouncer between app and database
-- Application connects to pooler, pooler reuses a small pool to Postgres

-- Start with pool_size near the database server's CPU core count
-- (somewhat higher if queries spend time waiting on I/O or locks),
-- then tune under a realistic load test — bigger is not better
-- Example for 8 cores: pool_size = 8-16

-- Result: 500 concurrent users share ~10 actual connections
select count(*) from pg_stat_activity;  -- ~10 connections
```

Pool modes:

- **Transaction mode**: connection returned after each transaction (best for most apps)
- **Session mode**: connection held for entire session (needed for prepared statements, temp tables)

Reference: [Number Of Database Connections](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections)
