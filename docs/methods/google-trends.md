# Google Trends: daily series from 2021

Code: [`extract/trends.py`](../../extract/trends.py). Ticket: ING-6 (#27).

## The problem

Google Trends has no official API, so this uses the unofficial `pytrends` library. Two limits shape the method:

- Daily values only come back for windows of about nine months or less. Longer ranges come back weekly or monthly.
- Every window is scaled to its own peak of 100. A value of 50 in one window isn't comparable with 50 in another.

## Method

1. **Terms:** "GTA 6", "PS5 Pro" and "Take-Two", worldwide, each fetched on its own. Fetched together, Google scales them against the busiest term, and "Take-Two" comes back as 0 every day.
2. **Windows:** 180 days long, starting every 120 days from 1 Jan 2021, so neighbouring windows share 60 days. Each window is stored raw in bronze (`source = 'google_trends'`).
3. **Stitching:** windows are joined in date order. Each new window is multiplied by a factor so that its total over the shared days matches the series so far. Only days that are non-zero in both count. New days are added at the new scale.
4. **Rescaling:** the joined series is rescaled so its highest day is 100.
5. **Daily updates:** each run fetches the latest 180-day window, which overlaps the backfill and is stitched the same way. The newest day is often flagged `is_partial` by Google and should be dropped or treated with care.

## Check against real data

On 9 Nov 2026, "GTA 6" was stitched from four windows covering 1 Jun 2025 to 8 Nov 2026. That was compared with a separately fetched 180-day window (15 Nov 2025 to 13 May 2026) that crosses a stitch boundary:

| Measure | Result |
|---|---|
| Correlation | 0.98 |
| Mean absolute error | 1.6 points (on the 0–100 scale) |
| Largest error | 8.2 points |

## Limits

- **Sampling noise:** Google samples searches, so the same request can return slightly different values on different days. Errors of a few points are normal.
- **Low-volume terms:** a term with many zero days, like "Take-Two" on quiet days, has fewer shared days to stitch with and is noisier. Stitching fails loudly if two windows share no non-zero days.
- **Relative, not absolute:** values show change over time within one term. They don't show how many people searched, and terms can't be compared with each other.
- **Unofficial library:** Google can change or rate-limit the endpoint at any time. The collector backs off and retries, then fails the run so a gap is visible.

Charts using this data are credited "Source: Google Trends".
