import httpx
import pytest

from spike import youtube_snapshot as snap

IDS = ["a", "b"]


def fake_get(status=200, json=None):
    def _get(url, params, headers, timeout):
        fake_get.calls.append({"url": url, "params": params, "headers": headers})
        return httpx.Response(status, json=json or {}, request=httpx.Request("GET", url))

    fake_get.calls = []
    return _get


def test_fetch_returns_payload(monkeypatch):
    payload = {"items": [{"id": "a", "statistics": {"viewCount": "1"}}, {"id": "b", "statistics": {}}]}
    monkeypatch.setattr(snap.httpx, "get", fake_get(json=payload))
    assert snap.fetch_stats("secret", IDS) == payload


def test_key_is_sent_in_header_not_url(monkeypatch):
    monkeypatch.setattr(snap.httpx, "get", fake_get(json={"items": [{"id": "a"}, {"id": "b"}]}))
    snap.fetch_stats("secret", IDS)
    call = fake_get.calls[0]
    assert call["headers"]["X-Goog-Api-Key"] == "secret"
    assert "secret" not in call["url"]
    assert "secret" not in str(call["params"])


def test_only_statistics_are_requested(monkeypatch):
    monkeypatch.setattr(snap.httpx, "get", fake_get(json={"items": [{"id": "a"}, {"id": "b"}]}))
    snap.fetch_stats("secret", IDS)
    assert fake_get.calls[0]["params"]["part"] == "statistics"


def test_missing_video_raises(monkeypatch):
    monkeypatch.setattr(snap.httpx, "get", fake_get(json={"items": [{"id": "a"}]}))
    with pytest.raises(RuntimeError, match="no stats for"):
        snap.fetch_stats("secret", IDS)


def test_http_error_raises_without_leaking_key(monkeypatch):
    monkeypatch.setattr(snap.httpx, "get", fake_get(status=403))
    with pytest.raises(httpx.HTTPStatusError) as err:
        snap.fetch_stats("secret", IDS)
    assert "secret" not in str(err.value)
