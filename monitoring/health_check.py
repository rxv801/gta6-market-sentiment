"""Fail if any collector has gone quiet, so a missed scheduled run sends a GitHub failure email.

GitHub emails when a run fails, but not when a scheduled run never starts. This check catches that by
looking at when each source last loaded. It reads only load times, never payloads.

Usage:
    uv run python -m monitoring.health_check
"""

import os
from datetime import UTC, datetime, timedelta

import psycopg

# Longest normal gap between loads, with room for GitHub starting runs up to 7 hours late.
MAX_AGE = {
    "youtube": timedelta(hours=30),  # twice a day
    "yfinance": timedelta(hours=80),  # weeknights, so Friday to Monday is the longest gap
    # Add "twitch" when the poller is re-enabled (#21).
}


def find_problems(freshness: dict[str, datetime], now: datetime) -> list[str]:
    problems = []
    for source, max_age in MAX_AGE.items():
        last = freshness.get(source)
        if last is None:
            problems.append(f"{source}: no rows at all")
        elif now - last > max_age:
            problems.append(f"{source}: last loaded {now - last} ago, limit {max_age}")
    return problems


def main() -> None:
    with psycopg.connect(os.environ["MONITOR_DATABASE_URL"]) as conn:
        rows = conn.execute("select source, last_fetched_at, rows_last_24h from ops.source_freshness()").fetchall()

    now = datetime.now(UTC)
    for source, last, recent in sorted(rows):
        print(f"{source}: last loaded {last:%Y-%m-%d %H:%M} UTC ({now - last} ago), {recent} rows in 24h")

    problems = find_problems({source: last for source, last, _ in rows}, now)
    if problems:
        raise SystemExit("Stale sources:\n" + "\n".join(problems))
    print("All sources fresh.")


if __name__ == "__main__":
    main()
