import csv
from datetime import date, time
from pathlib import Path

import pytest

EVENTS = Path(__file__).parent.parent / "dbt" / "seeds" / "events.csv"
COLUMNS = [
    "event_id",
    "event_date_et",
    "announce_time_et",
    "market_status",
    "event_type",
    "description",
    "confounded",
    "confounder",
    "cluster",
    "verification",
    "source_url_1",
    "source_url_2",
    "notes",
]
MARKET_STATUS = {"pre_market", "intraday", "after_hours", "non_trading_day", "unknown"}
EVENT_TYPES = {"announcement", "leak", "trailer", "delay", "earnings_guidance", "commercial", "launch"}
VERIFICATION = {"verified", "partly", "unverified"}


def rows():
    with EVENTS.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        return list(reader)


EVENT_ROWS = rows()


def test_ids_are_unique_and_dates_are_in_order():
    assert len({r["event_id"] for r in EVENT_ROWS}) == len(EVENT_ROWS)
    dates = [date.fromisoformat(r["event_date_et"]) for r in EVENT_ROWS]
    assert dates == sorted(dates)


@pytest.mark.parametrize("row", EVENT_ROWS, ids=lambda r: r["event_id"])
def test_row_is_complete(row):
    assert row["market_status"] in MARKET_STATUS
    assert row["event_type"] in EVENT_TYPES
    assert row["verification"] in VERIFICATION
    assert row["confounded"] in {"true", "false"}
    assert row["description"]
    assert row["source_url_1"].startswith("https://")
    if row["source_url_2"]:
        assert row["source_url_2"].startswith("https://")
    if row["announce_time_et"]:
        time.fromisoformat(row["announce_time_et"])


@pytest.mark.parametrize("row", EVENT_ROWS, ids=lambda r: r["event_id"])
def test_confounded_events_say_why(row):
    assert bool(row["confounder"]) == (row["confounded"] == "true")


@pytest.mark.parametrize("row", EVENT_ROWS, ids=lambda r: r["event_id"])
def test_market_status_matches_time(row):
    if not row["announce_time_et"]:
        return
    t = time.fromisoformat(row["announce_time_et"])
    expected = "pre_market" if t < time(9, 30) else "intraday" if t < time(16) else "after_hours"
    if date.fromisoformat(row["event_date_et"]).weekday() < 5:
        assert row["market_status"] == expected
