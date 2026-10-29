# GTA VI Market & Sentiment Study

How Grand Theft Auto VI announcements, trailers, leaks, delays and launch relate to Take-Two and Sony stock moves and to public attention.

**Status:** Sprint 0 (kickoff). Work in progress. See the [project board](https://github.com/users/rxv801/projects/1) and the [one-pager](docs/one-pager.md).

## Repository layout

| Path | Contents |
|---|---|
| `extract/` | One collector module per data source |
| `dags/` | Airflow DAGs |
| `dbt/` | dbt project: staging, intermediate and mart models, seeds, tests |
| `ml/` | Sentiment scoring and evaluation |
| `dashboard/` | Dashboard app and screenshots |
| `docs/` | One-pager, design doc, ADRs, backlog |
| `scripts/` | One-off project tooling (GitHub setup) |
| `tests/` | pytest tests |

## Getting started

Requires [uv](https://docs.astral.sh/uv/).

```bash
make install        # create the virtualenv and install pre-commit hooks
cp .env.example .env  # then fill in your keys
make lint test
```
