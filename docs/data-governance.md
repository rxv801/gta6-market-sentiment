# Data governance

Status: v1.0 · Owner: Rex · Last updated: 7 Nov 2026

This covers what data the project collects, what each source's terms allow, how personal data is handled, and where secrets live. It's short on purpose, but every collector has to follow it.

The first release leaves out Reddit and sentiment, so no post or comment text is collected yet. Those rules apply once that work starts.

## Sources and terms

I've summarised each source's terms as I understand them. This isn't legal advice. The items marked "verify" need a proper read of the current terms before the collector ships, and the result goes in the collector's PR.

| Source | What we collect | What the terms mean for us | Verify |
|---|---|---|---|
| YouTube Data API v3 | View, like and comment counts for official videos; comment text for sentiment | Free quota of 10,000 units a day, which is plenty. Data fetched with an API key is Non-Authorized Data, so statistics can't be stored for more than 30 days (policies III.E.4). Derived metrics aren't allowed either (III.E.4.h), so daily deltas are no way around this. Audited developers with an analytics use case can apply to keep statistics and derived metrics for up to 36 months (III.L). Comment text stays on the 30-day rule either way. | Checked 7 Nov 2026. See "YouTube retention" below. |
| Reddit Data API | Posts and comment counts from r/GTA6, r/GTA, r/PS5; comment text for sentiment | Non-commercial use with OAuth. Rate limited. Content that users delete should be removed from our copy too. | Current access rules for new apps, and the deletion requirement. |
| Twitch Helix | Viewer and stream counts for the GTA VI category | Public aggregate data. App access token only, no user login. | Terms not read in detail yet. Twitch had no GTA VI category on 7 Nov 2026, so nothing is collected yet. |
| yfinance (Yahoo Finance) | Daily prices and volume | Unofficial library. Yahoo's terms are for personal use, so the raw price table is not republished. | Nothing. Publish returns, charts and results only. |
| Google Trends | Search interest for three terms | No official API. Values are relative (0 to 100). Charts get a "Source: Google Trends" credit. | Nothing. |
| Publisher reports | Unit sales and rankings | Public press releases, entered by hand with a link to each one. | Nothing. |

The rule that follows from all of this: the public site and repo only ever show aggregates, statistics and charts. Raw API responses stay in the private warehouse.

## Personal data

Reddit and YouTube comments come with usernames, and the comment text itself can identify people. The project doesn't need to know who said anything, so:

- Usernames and channel IDs are replaced with a salted SHA-256 hash at ingestion. The salt is a secret, so hashes can't be reversed by guessing names.
- Comment text is stored in bronze only so the sentiment model can score it. It is never printed in logs or notebooks, never shown on the site, and never committed to git.
- Reddit comment text is deleted 90 days after it has been scored. YouTube comment text is deleted within 30 days of being fetched, as its terms require, so it has to be scored inside that window. Whether YouTube scores can be kept depends on the 36-month permission.
- The 200 hand-labelled samples are stored in the warehouse, not in the repo.

## Spoilers

The spoiler policy is in ADR-003. In short: spoiler-flagged posts are dropped at ingestion, a keyword blocklist catches the rest, and after launch only numeric metrics are collected.

## Secrets

- Locally, keys live in `.env`, which git ignores. `.env.example` lists the names with no values.
- In GitHub Actions, keys are repository secrets.
- A copy of every key is kept in my password manager. Nowhere else: not in chat, notes or screenshots.
- The pre-commit hook blocks private keys from being committed, once installed with `make install`. It doesn't recognise API keys, so check diffs before committing. If a key ever does get committed, I rotate it straight away. Deleting the commit isn't enough, because the repo is public.

## Database roles

Each part of the pipeline gets the least access it needs. Only `collector` exists so far. The others get created when the warehouse and dashboard are built.

| Role | Used by | Can do |
|---|---|---|
| `collector` | GitHub Actions collectors | Insert into `bronze` only. No reads, updates or deletes. |
| `transformer` | dbt, sentiment scoring | Read `bronze`; insert sentiment scores into `bronze`; delete expired comment text; create and write `silver` and `gold` |
| `reader` | Dashboard | Read `gold` only |
| `postgres` (owner) | Me, for admin and migrations | Everything. Used only by the setup scripts in `scripts/`, never by a collector. |

Supabase's auto-generated public API (the `anon` key) gets no access to these schemas.

## Retention and backups

- Bronze raw data is kept for the life of the project, except comment text (see above) and YouTube statistics (see below).
- Supabase's free tier has no backups. The plan is a weekly dump to storage outside Supabase (OPS-7), which isn't set up yet.
- If a source's terms require deleting data, the deletion is done in bronze and the downstream models are rebuilt.

## YouTube retention

The collector keeps a daily history of views, likes and comment counts, which the 30-day limit doesn't allow unless the 36-month permission is granted. The first row was saved on 6 Nov 2026, so it reaches 30 days on 6 Dec 2026.

Before that date, one of these has to be true:

- The permission has been granted, and history is kept for up to 36 months.
- Rows older than 30 days are deleted, and YouTube is used as a short-term measure only.
