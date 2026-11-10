# Twitch has no GTA VI category

Date: 7 Nov 2026 · Status: open · Data lost: no Twitch data until the category exists

## What happened
The first run of the Twitch poller (#75) failed with `Twitch has no category named 'Grand Theft Auto VI'`.

## Impact
No Twitch viewer or stream counts for GTA VI before launch. This can't be backfilled, because Twitch only reports live numbers.

## Cause
Twitch had no GTA VI category. Ten exact names (including "GTA 6", "GTA VI" and "Grand Theft Auto 6") and eight broader searches found none on 7 Nov 2026. The credentials worked.

## Fix
Poller disabled to stop failing runs. Re-enable at preload on 12 Nov and check the category name (#21).

## Follow-up
A 30-minute poller needs a trigger outside GitHub's scheduler, because scheduled runs start hours late (see the other incident).
