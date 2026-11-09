.PHONY: install lint format test dbt-dev-db dbt-dev-sample dbt-build dbt-freshness

install:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

# dbt, dev target: local Postgres database gta6_dev
dbt-dev-db:
	createdb gta6_dev 2>/dev/null || true
	psql -d gta6_dev -f sql/001_bronze.sql

# Made-up rows shaped like real payloads, for local dev only
dbt-dev-sample:
	psql -d gta6_dev -v ON_ERROR_STOP=1 -f sql/dev/sample_bronze.sql

dbt-build:
	cd dbt && uv run --group dbt dbt build --profiles-dir .

dbt-freshness:
	cd dbt && uv run --group dbt dbt source freshness --profiles-dir .
