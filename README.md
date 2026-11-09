# GTA VI Market & Sentiment Study

How Grand Theft Auto VI announcements, trailers, leaks, delays and launch relate to Take-Two and Sony stock moves and to public attention.

**Status:** Work in progress. Collecting YouTube statistics since 6 Nov 2026 and daily stock prices since 7 Nov 2026 (with history back to 2021). See the [one-pager](docs/one-pager.md).

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
