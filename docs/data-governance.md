# Data governance

Status: v1.0 · Owner: Rex · Last updated: 29 Oct 2026

This covers what data the project collects, what each source's terms allow, how personal data is handled, and where secrets live. It's short on purpose, but every collector has to follow it.

## Sources and terms

I've summarised each source's terms as I understand them. The items marked "verify" need a proper read of the current terms before the collector ships, and the result goes in the collector's PR.

| Source | What we collect | What the terms mean for us | Verify |
|---|---|---|---|
| YouTube Data API v3 | View, like and comment counts for official videos; comment text for sentiment | Free quota of 10,000 units a day, which is plenty. The developer policies limit how long some API data can be stored without refreshing it. | Whether keeping a daily history of public view counts is allowed, and for how long. If it isn't, store only derived daily deltas. |
| Reddit Data API | Posts and comment counts from r/GTA6, r/GTA, r/PS5; comment text for sentiment | Non-commercial use with OAuth. Rate limited. Content that users delete should be removed from our copy too. | Current access rules for new apps, and the deletion requirement. |
| Twitch Helix | Viewer and stream counts for the GTA VI category | Public aggregate data. App access token only, no user login. | Nothing major. |
| yfinance (Yahoo Finance) | Daily prices and volume | Unofficial library. Yahoo's terms are for personal use, so the raw price table is not republished. | Nothing. Publish returns, charts and results only. |
| Google Trends | Search interest for three terms | No official API. Values are relative (0 to 100). Charts get a "Source: Google Trends" credit. | Nothing. |
| Publisher reports | Unit sales and rankings | Public press releases, entered by hand with a link to each one. | Nothing. |

The rule that follows from all of this: the public site and repo only ever show aggregates, statistics and charts. Raw API responses stay in the private warehouse.

## Personal data

Reddit and YouTube comments come with usernames, and the comment text itself can identify people. The project doesn't need to know who said anything, so:

- Usernames and channel IDs are replaced with a salted SHA-256 hash at ingestion. The salt is a secret, so hashes can't be reversed by guessing names.
- Comment text is stored in bronze only so the sentiment model can score it. It is never printed in logs or notebooks, never shown on the site, and never committed to git.
- Comment text is deleted 90 days after it has been scored. Scores and daily aggregates are kept.
- The 200 hand-labelled samples are stored in the warehouse, not in the repo.

## Spoilers

The spoiler policy is in ADR-003. In short: spoiler-flagged posts are dropped at ingestion, a keyword blocklist catches the rest, and after launch only numeric metrics are collected.

## Secrets

- Locally, keys live in `.env`, which git ignores. `.env.example` lists the names with no values.
- In GitHub Actions, keys are repository secrets.
- A copy of every key is kept in my password manager. Nowhere else: not in chat, notes or screenshots.
- The pre-commit hook blocks private keys from being committed. If a key ever does get committed, I rotate it straight away. Deleting the commit isn't enough, because the repo is public.

## Database roles

Each part of the pipeline gets the least access it needs.

| Role | Used by | Can do |
|---|---|---|
| `collector` | GitHub Actions collectors | Insert into `bronze` only. No reads, updates or deletes. |
| `transformer` | dbt, sentiment scoring | Read `bronze`; create and write `silver` and `gold` |
| `reader` | Dashboard | Read `gold` only |
| `postgres` (owner) | Me, for admin and migrations | Everything. Never used by code. |

Supabase's auto-generated public API (the `anon` key) gets no access to these schemas.

## Retention and backups

- Bronze raw data is kept for the life of the project, except comment text (see above).
- Supabase's free tier has no backups, so a weekly dump goes to storage outside Supabase (OPS-7).
- If a source's terms require deleting data, the deletion is done in bronze and the downstream models are rebuilt.
