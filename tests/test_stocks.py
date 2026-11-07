from datetime import date

import pandas as pd
import pytest

from extract import stocks


def table(days=("2026-11-05", "2026-11-06"), close=100.0):
    index = pd.DatetimeIndex(days, tz="America/New_York")
    return pd.DataFrame(
        {
            "Open": 99.0,
            "High": 101.0,
            "Low": 98.0,
            "Close": close,
            "Adj Close": 95.0,
            "Volume": 1000,
            "Dividends": 0.0,
            "Stock Splits": 0.0,
        },
        index=index,
    )


def fake_ticker(tables):
    class Ticker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, start, interval, auto_adjust):
            assert auto_adjust is False
            assert interval == "1d"
            return tables(self.symbol)

    return Ticker


def test_bars_keep_both_closes_and_exchange_date(monkeypatch):
    monkeypatch.setattr(stocks.yf, "Ticker", fake_ticker(lambda _: table()))
    bars = stocks.fetch_bars("TTWO", date(2026, 11, 1))
    assert bars[0] == {
        "date": "2026-11-05",
        "open": 99.0,
        "high": 101.0,
        "low": 98.0,
        "close": 100.0,
        "adj_close": 95.0,
        "volume": 1000.0,
    }


def test_nan_becomes_none(monkeypatch):
    monkeypatch.setattr(stocks.yf, "Ticker", fake_ticker(lambda _: table(close=float("nan"))))
    assert stocks.fetch_bars("TTWO", date(2026, 11, 1))[0]["close"] is None


def test_empty_response_raises(monkeypatch):
    monkeypatch.setattr(stocks.yf, "Ticker", fake_ticker(lambda _: pd.DataFrame()))
    with pytest.raises(RuntimeError, match="no prices for TTWO"):
        stocks.fetch_bars("TTWO", date(2026, 11, 1))


def test_one_bad_ticker_does_not_lose_the_others(monkeypatch):
    saved = []
    monkeypatch.setattr(stocks.yf, "Ticker", fake_ticker(lambda s: pd.DataFrame() if s == "SONY" else table()))
    monkeypatch.setattr(stocks, "load_raw", lambda source, endpoint, payload, fetched_at: saved.append(payload))
    assert stocks.collect(date(2026, 11, 1)) == ["SONY"]
    assert [p["ticker"] for p in saved] == ["TTWO", "6758.T", "^GSPC", "^NDX"]


def test_failed_ticker_fails_the_run(monkeypatch):
    monkeypatch.setattr(stocks, "collect", lambda start: ["SONY"])
    monkeypatch.setattr("sys.argv", ["stocks"])
    with pytest.raises(RuntimeError, match="SONY"):
        stocks.main()


@pytest.mark.parametrize(("args", "expected"), [(["--backfill"], date(2021, 1, 1)), ([], None)])
def test_start_date_depends_on_mode(monkeypatch, args, expected):
    seen = []
    monkeypatch.setattr(stocks, "collect", lambda start: seen.append(start) or [])
    monkeypatch.setattr("sys.argv", ["stocks", *args])
    stocks.main()
    if expected:
        assert seen == [expected]
    else:
        assert (date.today() - seen[0]).days in {9, 10, 11}
