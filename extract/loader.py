"""Shared loader that writes raw API responses to bronze."""

import os
from datetime import UTC, datetime

import psycopg
from psycopg.types.json import Jsonb

INSERT_SQL = """
    insert into bronze.raw_payload (source, endpoint, run_id, fetched_at, payload)
    values (%s, %s, %s, %s, %s)
"""


def get_run_id() -> str:
    """Return the GitHub Actions run ID, or a timestamped ID for local runs."""
    return os.environ.get("GITHUB_RUN_ID") or f"local-{datetime.now(UTC):%Y%m%dT%H%M%SZ}"


def load_raw(source: str, endpoint: str, payload: dict | list, fetched_at: datetime) -> None:
    """Insert one raw payload. An empty payload raises, so gaps show up as failed runs."""
    if not payload:
        raise ValueError(f"Empty payload from {source}/{endpoint}")
    if fetched_at.tzinfo is None:
        raise ValueError("fetched_at must be timezone aware")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    with psycopg.connect(database_url) as conn:
        conn.execute(INSERT_SQL, (source, endpoint, get_run_id(), fetched_at, Jsonb(payload)))
