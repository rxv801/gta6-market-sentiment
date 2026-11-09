"""Save Google Trends daily search interest for each tracked term.

Google only returns daily values for windows of about nine months or less, and scales every window to its
own peak of 100. So the backfill fetches overlapping 180-day windows and stores each one raw in bronze.
`stitch` joins them into one daily series: each window is scaled to match the one before it on the days
they share, then the whole series is rescaled to a peak of 100. The method is in docs/methods/google-trends.md.

Each term is fetched on its own. Fetched together, Google scales them against the busiest term, which
pushes small terms like "Take-Two" to 0.

Usage:
    uv run python -m extract.trends              # latest window only
    uv run python -m extract.trends --backfill   # every window since 2021
"""

import argparse
import time
from datetime import UTC, date, datetime, timedelta

from pytrends.exceptions import TooManyRequestsError
from pytrends.request import TrendReq

from extract.loader import load_raw

TERMS = ["GTA 6", "PS5 Pro", "Take-Two"]
BACKFILL_START = date(2021, 1, 1)
WINDOW_DAYS = 180
STEP_DAYS = 120  # 60 days of overlap between windows
PAUSE_SECONDS = 8
RETRY_WAITS = (60, 180, 600)


def windows(start: date, end: date) -> list[tuple[date, date]]:
    """Overlapping windows that cover start to end. The last one always ends on `end`."""
    spans = []
    window_start = start
    while True:
        window_end = min(window_start + timedelta(days=WINDOW_DAYS - 1), end)
        spans.append((window_start, window_end))
        if window_end >= end:
            return spans
        window_start += timedelta(days=STEP_DAYS)


def fetch_window(client: TrendReq, term: str, start: date, end: date) -> dict:
    """Return one window's daily values. Google returns an empty table for no data, so empty raises."""
    client.build_payload([term], timeframe=f"{start.isoformat()} {end.isoformat()}", geo="")
    table = client.interest_over_time()
    if table.empty:
        raise RuntimeError(f"Google Trends returned no data for {term!r} {start} to {end}")
    points = [
        {"date": day.date().isoformat(), "value": int(row[term]), "is_partial": bool(row["isPartial"])}
        for day, row in table.iterrows()
    ]
    return {"term": term, "geo": "worldwide", "start": start.isoformat(), "end": end.isoformat(), "points": points}


def fetch_with_retry(client: TrendReq, term: str, start: date, end: date) -> dict:
    """Google rate-limits hard. Back off and retry before giving up."""
    for wait in (*RETRY_WAITS, None):
        try:
            return fetch_window(client, term, start, end)
        except TooManyRequestsError:
            if wait is None:
                raise
            print(f"{term} {start}: rate limited, waiting {wait}s")
            time.sleep(wait)
    raise AssertionError("unreachable")


def stitch(window_payloads: list[dict]) -> dict[str, float]:
    """Join overlapping windows for one term into a single daily series with a peak of 100."""
    series: dict[str, float] = {}
    for payload in sorted(window_payloads, key=lambda p: p["start"]):
        values = {p["date"]: p["value"] for p in payload["points"]}
        if series:
            shared = [d for d in values if d in series and series[d] > 0 and values[d] > 0]
            if not shared:
                raise ValueError(f"Window starting {payload['start']} shares no non-zero days with the one before")
            factor = sum(series[d] for d in shared) / sum(values[d] for d in shared)
        else:
            factor = 1.0
        for day, value in values.items():
            if day not in series:
                series[day] = value * factor
    peak = max(series.values())
    return {day: round(100 * value / peak, 2) for day, value in sorted(series.items())} if peak else series


def collect(spans: list[tuple[date, date]]) -> list[str]:
    """Save every window it can and return the ones that failed, so one failure can't lose the rest."""
    client = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
    failed = []
    for term in TERMS:
        for start, end in spans:
            fetched_at = datetime.now(UTC)
            try:
                payload = fetch_with_retry(client, term, start, end)
            except Exception as error:
                print(f"{term} {start} to {end}: {error}")
                failed.append(f"{term} {start}")
                continue
            load_raw("google_trends", "interest_over_time", payload, fetched_at)
            print(f"{term}: saved {len(payload['points'])} days, {start} to {end}")
            time.sleep(PAUSE_SECONDS)
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backfill", action="store_true", help="fetch every window since 2021")
    args = parser.parse_args()

    today = datetime.now(UTC).date()
    start = BACKFILL_START if args.backfill else today - timedelta(days=WINDOW_DAYS - 1)
    failed = collect(windows(start, today))
    if failed:
        raise RuntimeError(f"No data saved for: {failed}")


if __name__ == "__main__":
    main()
