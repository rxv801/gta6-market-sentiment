# ADR-001: Core stack

Status: Accepted · Date: 2026-10-29

## Context

The project needs to collect data from five sources, model it in a warehouse, run a statistical analysis and a sentiment model, and publish results. It's also a portfolio piece, so the tools should be ones that data teams in industry actually use.

## Decision

- Python 3.12, managed with uv, for collectors, analysis and ML.
- PostgreSQL as the warehouse.
- dbt for modelling and testing, in a medallion layout (bronze, silver, gold).
- GitHub Actions for scheduling collectors and running CI.
- Airflow added in W11 for the batch side (dbt and scoring), to learn it on a working pipeline.
- Hugging Face Transformers with PyTorch for sentiment.
- ruff, pytest and pre-commit for code quality.

## Consequences

Every tool here is free and common in data job ads. The cost is that dbt, Airflow and Actions are three moving parts for a small project. Airflow is the most optional and is planned last, so it can be cut if time runs short.

## Alternatives considered

- **Snowflake or BigQuery** instead of Postgres. More "enterprise", but free tiers are time limited or need a card, and Postgres is plenty for this data size.
- **Poetry or pip** instead of uv. uv is faster and handles Python versions too.
- **Prefect or Dagster** instead of Airflow. Arguably nicer, but Airflow shows up far more often in job ads.
