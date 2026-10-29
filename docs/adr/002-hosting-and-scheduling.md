# ADR-002: Hosted database and scheduling

Status: Accepted · Date: 2026-10-29

## Context

I work on this project on Wednesdays and Thursdays. Collectors have to run every day, and the Twitch poller every 30 minutes, whether or not my laptop is on. The data from before and during launch can't be collected again later.

## Decision

- The production database is Supabase Postgres on the free tier.
- Collectors run as scheduled GitHub Actions workflows and write directly to Supabase using a `collector` role that can only insert into bronze.
- Local Postgres in Docker is used only for dbt development and tests.

## Consequences

Collection keeps running while the laptop is closed, and Actions minutes are free because the repo is public.

Things to watch:

- The Supabase free tier has 500 MB of storage and no backups. Comment text is the largest thing we store, so it's deleted 90 days after scoring, and a weekly dump is kept outside Supabase (OPS-7).
- Supabase pauses free projects after a week without activity. Daily collector writes prevent that.
- Scheduled Actions can run late or skip. Rows store the real fetch time.

## Alternatives considered

- **Laptop cron and local Postgres.** Free and simple, but misses runs whenever the laptop sleeps.
- **A small VPS** (about $5 a month). Always on and could host Airflow, but it's a server to patch and pay for. Not worth it unless Actions proves unreliable.
- **Neon** instead of Supabase. Similar free tier. Supabase was picked for its dashboard and built-in roles, but either would work.
