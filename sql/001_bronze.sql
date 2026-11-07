-- Bronze layer: raw API payloads, append only. Safe to re-run.

create schema if not exists bronze;

create table if not exists bronze.raw_payload (
    id          bigint generated always as identity primary key,
    source      text        not null,
    endpoint    text        not null,
    run_id      text        not null,
    fetched_at  timestamptz not null,
    loaded_at   timestamptz not null default now(),
    payload     jsonb       not null
);

create index if not exists raw_payload_source_fetched_at_idx
    on bronze.raw_payload (source, fetched_at);

-- The password is set separately by scripts/provision_collector.py.
do $$
begin
    if not exists (select from pg_roles where rolname = 'collector') then
        create role collector login noinherit;
    end if;
end
$$;

-- Insert only: no reads, updates or deletes.
revoke all on schema bronze from public, anon, authenticated, service_role;
revoke all on all tables in schema bronze from public, anon, authenticated, service_role;
grant usage on schema bronze to collector;
grant insert on bronze.raw_payload to collector;
