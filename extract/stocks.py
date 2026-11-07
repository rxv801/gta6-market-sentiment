"""Save daily prices for Take-Two, Sony and the market indexes.

The daily run re-fetches the last 10 days, so a missed run fills itself in. Bronze is append-only, so the
same date can appear more than once. Staging keeps the latest fetched row for each ticker and date, which
also picks up later corrections from Yahoo.

Usage:
    uv run python -m extract.stocks              # last 10 days
    uv run python -m extract.stocks --backfill   # everything since 2021
"""

import argparse
import math
from datetime import UTC, date, datetime, timedelta

import yfinance as yf

from extract.loader import load_raw

TICKERS = ["TTWO", "SONY", "6758.T", "^GSPC", "^NDX"]
BACKFILL_START = date(2021, 1, 1)
DAILY_LOOKBACK_DAYS = 10
COLUMNS = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}


def fetch_bars(ticker: str, start: date) -> list[dict]:
    """Return daily bars for a ticker. yfinance returns an empty table on failure, so empty raises."""
    history = yf.Ticker(ticker).history(start=start.isoformat(), interval="1d", auto_adjust=False)
    if history.empty:
        raise RuntimeError(f"Yahoo returned no prices for {ticker}")

    bars = []
    for trading_day, row in history.iterrows():
        values = {name: row[column] for column, name in COLUMNS.items()}
        # Yahoo can leave gaps as NaN, which Postgres jsonb rejects.
        bars.append(
            {
                "date": trading_day.date().isoformat(),
                **{name: None if math.isnan(value) else float(value) for name, value in values.items()},
            }
        )
    return bars


def collect(start: date) -> list[str]:
    """Save every ticker it can and return the ones that failed, so one bad ticker can't lose the others."""
    failed = []
    for ticker in TICKERS:
        fetched_at = datetime.now(UTC)
        try:
            bars = fetch_bars(ticker, start)
        except Exception as error:
            print(f"{ticker}: {error}")
            failed.append(ticker)
            continue
        load_raw("yfinance", "history", {"ticker": ticker, "start": start.isoformat(), "bars": bars}, fetched_at)
        print(f"{ticker}: saved {len(bars)} bars, {bars[0]['date']} to {bars[-1]['date']}")
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backfill", action="store_true", help="fetch everything since 2021")
    args = parser.parse_args()

    start = BACKFILL_START if args.backfill else datetime.now(UTC).date() - timedelta(days=DAILY_LOOKBACK_DAYS)
    failed = collect(start)
    if failed:
        raise RuntimeError(f"No prices saved for: {failed}")


if __name__ == "__main__":
    main()
