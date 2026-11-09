# Scheduled runs start hours late

Date: 7 Nov 2026 · Status: resolved with workarounds · Data lost: no

## What happened
No scheduled run fired for the first day after the collectors were added. From 7 Nov, scheduled runs fired but started 4h 40m to 6h 48m after their cron time.

## Impact
None so far. YouTube and stocks were also run by hand on 6 and 7 Nov, so every day has a reading.

## Cause
GitHub Actions doesn't guarantee start times for scheduled workflows. The delay is on GitHub's side. Repo settings were checked and are correct.

## Fix
- YouTube runs twice a day, so one late or skipped run still leaves a daily reading.
- Stocks re-fetches the last 10 days on every run, so a missed run fills itself in.
- Every row stores its real collection time.
- A health check now fails if a source goes quiet (#34).

## Follow-up
Twitch needs an outside trigger before it is re-enabled (#21).
