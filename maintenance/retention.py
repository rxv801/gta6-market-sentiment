"""Delete YouTube rows older than the retention limit.

YouTube's Developer Policies (III.E.4) allow API-key statistics to be kept for 30 days. If YouTube grants
the Section III.L permission, the limit becomes 36 months: set the YOUTUBE_RETENTION_DAYS repository
variable to 1095. Comment text always stays on the 30-day rule, and is handled when comments are collected.

Usage:
    uv run python -m maintenance.retention
"""

import os

import psycopg

DEFAULT_KEEP_DAYS = 30
MAX_KEEP_DAYS = 1095  # 36 months, only with the III.L permission


def keep_days_from(value: str | None) -> int:
    """Parse the retention setting. Anything unclear falls back to the strict 30-day rule."""
    if not value:
        return DEFAULT_KEEP_DAYS
    days = int(value)
    if not 1 <= days <= MAX_KEEP_DAYS:
        raise ValueError(f"YOUTUBE_RETENTION_DAYS must be between 1 and {MAX_KEEP_DAYS}, got {days}")
    return days


def main() -> None:
    keep_days = keep_days_from(os.environ.get("YOUTUBE_RETENTION_DAYS"))
    with psycopg.connect(os.environ["JANITOR_DATABASE_URL"]) as conn:
        deleted = conn.execute("select ops.purge_youtube(%s)", (keep_days,)).fetchone()[0]
    print(f"Kept YouTube rows from the last {keep_days} days; deleted {deleted} older rows.")


if __name__ == "__main__":
    main()
