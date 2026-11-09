from datetime import date, timedelta

import pandas as pd
import pytest
from pytrends.exceptions import TooManyRequestsError

from extract import trends


def window_payload(true_series: dict[str, float], start: date, end: date) -> dict:
    """What Google would return: the true series cut to the window and scaled to the window's own peak."""
    days = [d for d in true_series if start.isoformat() <= d <= end.isoformat()]
    peak = max(true_series[d] for d in days)
    points = [{"date": d, "value": round(100 * true_series[d] / peak), "is_partial": False} for d in days]
    return {"term": "x", "start": start.isoformat(), "end": end.isoformat(), "points": points}


def test_windows_overlap_and_reach_the_end():
    spans = trends.windows(date(2021, 1, 1), date(2021, 12, 31))
    assert spans[0][0] == date(2021, 1, 1)
    assert spans[-1][1] == date(2021, 12, 31)
    for (_, prev_end), (next_start, _) in zip(spans, spans[1:], strict=False):
        assert prev_end - next_start >= timedelta(days=59)


def test_short_range_is_one_window():
    assert trends.windows(date(2026, 1, 1), date(2026, 2, 1)) == [(date(2026, 1, 1), date(2026, 2, 1))]


def test_stitch_recovers_the_true_shape():
    start = date(2021, 1, 1)
    true_series = {
        (start + timedelta(days=i)).isoformat(): 10 + (i % 30) + (500 if i == 300 else 0) for i in range(400)
    }
    payloads = [window_payload(true_series, s, e) for s, e in trends.windows(start, start + timedelta(days=399))]
    stitched = trends.stitch(payloads)
    assert len(stitched) == 400
    assert max(stitched.values()) == 100
    peak_day = (start + timedelta(days=300)).isoformat()
    assert stitched[peak_day] == 100
    # A quiet day should sit at the same fraction of the peak as in the true series, within rounding.
    quiet_day = (start + timedelta(days=10)).isoformat()
    assert stitched[quiet_day] == pytest.approx(100 * true_series[quiet_day] / 510, abs=1.5)


def test_stitch_refuses_windows_with_no_shared_signal():
    first = {"start": "2021-01-01", "points": [{"date": "2021-01-01", "value": 5}]}
    second = {"start": "2021-01-02", "points": [{"date": "2021-01-02", "value": 7}]}
    with pytest.raises(ValueError, match="shares no non-zero days"):
        trends.stitch([first, second])


class FakeClient:
    def __init__(self, tables):
        self.tables = list(tables)
        self.timeframes = []

    def build_payload(self, terms, timeframe, geo):
        self.timeframes.append(timeframe)

    def interest_over_time(self):
        table = self.tables.pop(0)
        if isinstance(table, Exception):
            raise table
        return table


def table(term="GTA 6"):
    index = pd.DatetimeIndex(["2026-11-07", "2026-11-08"])
    return pd.DataFrame({term: [47, 50], "isPartial": [False, True]}, index=index)


def test_fetch_window_keeps_partial_flag():
    payload = trends.fetch_window(FakeClient([table()]), "GTA 6", date(2026, 11, 7), date(2026, 11, 8))
    assert payload["points"][-1] == {"date": "2026-11-08", "value": 50, "is_partial": True}
    assert payload["term"] == "GTA 6"


def test_empty_window_raises():
    with pytest.raises(RuntimeError, match="no data"):
        trends.fetch_window(FakeClient([pd.DataFrame()]), "GTA 6", date(2026, 1, 1), date(2026, 1, 2))


def test_rate_limit_is_retried(monkeypatch):
    monkeypatch.setattr(trends.time, "sleep", lambda _: None)
    error = TooManyRequestsError.from_response(type("R", (), {"status_code": 429, "reason": "Too Many"})())
    client = FakeClient([error, table()])
    assert trends.fetch_with_retry(client, "GTA 6", date(2026, 11, 7), date(2026, 11, 8))["term"] == "GTA 6"
