# ADR-003: Spoiler policy

Status: Accepted · Date: 2026-10-29

## Context

I don't want the game spoiled for me, and readers of the site shouldn't get spoiled either. After launch, Reddit and YouTube comments will be full of story details.

## Decision

- Reddit posts flagged as spoilers are dropped at ingestion, before anything is written to the database.
- A keyword blocklist (story terms, character names once known, "ending", "final mission" and so on) drops matching posts and comments at ingestion too.
- No collector, notebook, log line or test output ever prints raw post or comment text. Only counts and aggregates.
- After launch, only numeric metrics are collected from Twitch and YouTube: viewers, views, likes, counts. No achievement lists and no wiki scraping.
- The dashboard shows aggregate sentiment only, never quotes.
- Hand-labelling for the sentiment model uses pre-launch comments only.

## Consequences

The sentiment data after launch will be thinner than it could be, because spoiler-heavy discussion is dropped. That's a real bias, and the write-up will say so.

The blocklist will miss things. Since text is never displayed anywhere, a missed spoiler only affects the scores, not what anyone sees.

## Alternatives considered

- Collecting everything and filtering later. Simpler, but it means spoiler text sits in the database and could leak into logs during debugging.
