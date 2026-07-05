---
title: Lock Down SECURITY DEFINER Functions
impact: HIGH
impactDescription: privilege escalation and data leaks to any user who can call the function
tags: security-definer, search-path, privileges, functions
---

## Lock Down SECURITY DEFINER Functions

A `security definer` function runs with its owner's privileges, like setuid in Unix. Left with default execute rights (granted to PUBLIC) and no pinned `search_path`, it lets any user run privileged code — and lets attackers hijack unqualified object references by planting same-named objects in a schema that resolves first.

**Incorrect (world-executable, hijackable object resolution):**

```sql
-- Executable by every role (PUBLIC gets EXECUTE by default),
-- and "payroll" resolves via the caller's search_path — an attacker
-- can shadow it with their own table or function
create function monthly_payroll_total()
returns numeric as $$
  select sum(gross_pay) from payroll
  where pay_period = date_trunc('month', now())
$$ language sql security definer;
```

**Correct (pin the search path, revoke PUBLIC, grant narrowly — atomically):**

```sql
begin;

create function monthly_payroll_total()
returns numeric as $$
  select sum(gross_pay) from hr.payroll
  where pay_period = date_trunc('month', now())
$$ language sql
security definer
set search_path = pg_catalog, hr, pg_temp;  -- fixed, trusted resolution order

-- Close the PUBLIC grant before anyone can call it, then grant narrowly
revoke all on function monthly_payroll_total() from public;
grant execute on function monthly_payroll_total() to finance_role;

commit;
```

Keep `security definer` bodies minimal and single-purpose, schema-qualify object references, and never create them as a superuser when a lesser role suffices — the function inherits every privilege its owner has. `pg_temp` must come last in the pinned path so temporary objects cannot shadow real ones. Use the default `security invoker` unless the function genuinely needs elevated rights.

Reference: [Writing SECURITY DEFINER Functions Safely](https://www.postgresql.org/docs/current/sql-createfunction.html#SQL-CREATEFUNCTION-SECURITY)
