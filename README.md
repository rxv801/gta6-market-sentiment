# GTA VI Market & Sentiment Study

How Grand Theft Auto VI announcements, trailers, leaks, delays and launch relate to Take-Two and Sony stock moves and to public attention.

[Privacy policy](PRIVACY.md) · [Terms of use](TERMS.md)

**Status:** Work in progress. Collecting YouTube statistics since 6 Nov 2026 and daily stock prices since 7 Nov 2026 (with history back to 2021). See the [one-pager](docs/one-pager.md).

## Data sources

<a href="https://www.youtube.com/@RockstarGames"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/youtube-logo-dark-bg.png"><img src="docs/assets/youtube-logo-light-bg.png" alt="YouTube" width="120"></picture></a>

YouTube view, like and comment counts come from the YouTube Data API, so YouTube is their source. Any figure calculated from them, such as daily change or sentiment, is this project's own calculation. Daily stock prices come from Yahoo Finance via yfinance. Google Trends and Twitch are planned.

This project uses YouTube API Services. By using it you agree to the [YouTube Terms of Service](https://www.youtube.com/t/terms). See the [privacy policy](PRIVACY.md) and [terms of use](TERMS.md).

## Repository layout

| Path | Contents |
|---|---|
| `extract/` | One collector module per data source |
| `dags/` | Airflow DAGs |
| `dbt/` | dbt project: staging, intermediate and mart models, seeds, tests |
| `ml/` | Sentiment scoring and evaluation |
| `dashboard/` | Dashboard app and screenshots |
| `docs/` | One-pager, design doc, ADRs, backlog |
| `scripts/` | One-off project tooling (GitHub and database setup) |
| `sql/` | Database schema |
| `tests/` | pytest tests |

## Getting started

Requires [uv](https://docs.astral.sh/uv/).

```bash
make install        # create the virtualenv and install pre-commit hooks
cp .env.example .env  # then fill in your keys
make lint test
```
