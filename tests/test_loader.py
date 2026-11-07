from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from extract import loader

FETCHED_AT = datetime(2026, 11, 6, tzinfo=UTC)


def test_run_id_uses_github_run_id(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "12345")
    assert loader.get_run_id() == "12345"


def test_run_id_falls_back_to_local(monkeypatch):
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    assert loader.get_run_id().startswith("local-")


@pytest.mark.parametrize("payload", [{}, []])
def test_empty_payload_raises(payload):
    with pytest.raises(ValueError, match="Empty payload"):
        loader.load_raw("youtube", "videos.list", payload, FETCHED_AT)


def test_naive_timestamp_raises():
    with pytest.raises(ValueError, match="timezone aware"):
        loader.load_raw("youtube", "videos.list", {"a": 1}, datetime(2026, 11, 6))  # noqa: DTZ001


def test_missing_database_url_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        loader.load_raw("youtube", "videos.list", {"a": 1}, FETCHED_AT)


def test_load_raw_inserts_one_row(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("GITHUB_RUN_ID", "99")
    conn = MagicMock()
    with patch.object(loader.psycopg, "connect") as connect:
        connect.return_value.__enter__.return_value = conn
        loader.load_raw("twitch", "streams", {"viewers": 10}, FETCHED_AT)

    params = conn.execute.call_args.args[1]
    assert params[:4] == ("twitch", "streams", "99", FETCHED_AT)
    assert params[4].obj == {"viewers": 10}
