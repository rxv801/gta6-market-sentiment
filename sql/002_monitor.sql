-- Monitoring: a login that can see when each source last loaded, and nothing else. Safe to re-run.

create schema if not exists ops;

-- Returns one row per source. Runs with the owner's rights, so the monitor role never reads bronze itself.
create or replace function ops.source_freshness()
returns table (source text, last_fetched_at timestamptz, rows_last_24h bigint)
language sql
stable
security definer
set search_path = pg_catalog, pg_temp
as $$
    select p.source,
           max(p.fetched_at),
           count(*) filter (where p.fetched_at > now() - interval '24 hours')
    from bronze.raw_payload p
    group by p.source
$$;

-- The password is set separately by scripts/provision_role.py.
do $$
begin
    if not exists (select from pg_roles where rolname = 'monitor') then
        create role monitor login noinherit;
    end if;
end
$$;

revoke all on schema ops from public, anon, authenticated, service_role;
revoke all on function ops.source_freshness() from public, anon, authenticated, service_role;
grant usage on schema ops to monitor;
grant execute on function ops.source_freshness() to monitor;
