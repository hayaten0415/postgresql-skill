---
title: Enable Row Level Security for Multi-Tenant Data
impact: CRITICAL
impactDescription: Database-enforced tenant isolation, prevent data leaks
tags: rls, row-level-security, multi-tenant, security
---

## Enable Row Level Security for Multi-Tenant Data

Row Level Security (RLS) enforces data access at the database level, ensuring users only see their own data.

**Incorrect (application-level filtering only):**

```sql
-- Relying only on application to filter
select * from orders where user_id = $current_user_id;

-- Bug or bypass means all data is exposed!
select * from orders;  -- Returns ALL orders
```

**Correct (database-enforced RLS):**

```sql
-- Enable RLS on the table
alter table orders enable row level security;

-- Create policy for users to see only their orders
create policy orders_user_policy on orders
  for all
  using (user_id = current_setting('app.current_user_id')::bigint);

-- Force RLS even for table owners
alter table orders force row level security;

-- Set user context and query
set app.current_user_id = '123';
select * from orders;  -- Only returns orders for user 123
```

Scope policies to specific roles where possible:

```sql
-- Applies only to the application role, not owners or migration roles
create policy orders_user_policy on orders
  for all
  to app_user
  using (user_id = (select current_setting('app.current_user_id')::bigint));
```

On managed platforms the caller's identity often comes from a platform function
instead of a session setting (e.g. Supabase's `auth.uid()`); the policy patterns
are the same.

Reference: [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
