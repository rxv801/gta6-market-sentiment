from datetime import UTC, datetime, timedelta

from monitoring.health_check import MAX_AGE, find_problems

NOW = datetime(2026, 11, 9, 12, tzinfo=UTC)


def test_fresh_sources_pass():
    assert find_problems({source: NOW - timedelta(hours=1) for source in MAX_AGE}, NOW) == []


def test_stale_source_fails():
    freshness = {source: NOW for source in MAX_AGE} | {"youtube": NOW - timedelta(hours=31)}
    assert [p.split(":")[0] for p in find_problems(freshness, NOW)] == ["youtube"]


def test_missing_source_fails():
    assert find_problems({"youtube": NOW}, NOW) == ["yfinance: no rows at all"]


def test_weekend_gap_for_stocks_is_allowed():
    assert find_problems({"youtube": NOW, "yfinance": NOW - timedelta(hours=70)}, NOW) == []
