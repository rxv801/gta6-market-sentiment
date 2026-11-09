-- Retention: a login that can delete expired YouTube rows, and nothing else. Safe to re-run.
-- YouTube Developer Policies III.E.4: API-key statistics may be kept 30 days, or 36 months under the III.L permission.

create schema if not exists ops;

-- Deletes YouTube rows fetched before the cutoff and returns how many went.
-- Runs with the owner's rights, so the janitor role can't read or delete anything else.
create or replace function ops.purge_youtube(keep_days integer)
returns bigint
language plpgsql
volatile
security definer
set search_path = pg_catalog, pg_temp
as $$
declare
    deleted bigint;
begin
    if keep_days < 1 or keep_days > 1095 then
        raise exception 'keep_days must be between 1 and 1095, got %', keep_days;
    end if;
    delete from bronze.raw_payload
    where source = 'youtube'
      and fetched_at < now() - make_interval(days => keep_days);
    get diagnostics deleted = row_count;
    return deleted;
end
$$;

-- The password is set separately by scripts/provision_role.py.
do $$
begin
    if not exists (select from pg_roles where rolname = 'janitor') then
        create role janitor login noinherit;
    end if;
end
$$;

revoke all on function ops.purge_youtube(integer) from public, anon, authenticated, service_role;
grant usage on schema ops to janitor;
grant execute on function ops.purge_youtube(integer) to janitor;
