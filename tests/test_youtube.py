import httpx
import pytest

from extract import youtube

IDS = ["a", "b"]


def fake_get(status=200, items=None):
    calls = []

    def _get(url, params, headers, timeout):
        calls.append({"url": url, "params": params, "headers": headers})
        requested = params["id"].split(",")
        found = [{"id": i, "statistics": {"viewCount": "1"}} for i in requested] if items is None else items
        return httpx.Response(status, json={"items": found}, request=httpx.Request("GET", url))

    _get.calls = calls
    return _get


def test_fetch_returns_every_video(monkeypatch):
    monkeypatch.setattr(youtube.httpx, "get", fake_get())
    assert {item["id"] for item in youtube.fetch_stats("secret", IDS)["items"]} == set(IDS)


def test_long_list_is_split_into_requests(monkeypatch):
    get = fake_get()
    monkeypatch.setattr(youtube.httpx, "get", get)
    ids = [str(i) for i in range(51)]
    assert len(youtube.fetch_stats("secret", ids)["items"]) == 51
    assert len(get.calls) == 2


def test_key_is_sent_in_header_not_url(monkeypatch):
    get = fake_get()
    monkeypatch.setattr(youtube.httpx, "get", get)
    youtube.fetch_stats("secret", IDS)
    call = get.calls[0]
    assert call["headers"]["X-Goog-Api-Key"] == "secret"
    assert "secret" not in call["url"]
    assert "secret" not in str(call["params"])


def test_only_statistics_are_requested(monkeypatch):
    get = fake_get()
    monkeypatch.setattr(youtube.httpx, "get", get)
    youtube.fetch_stats("secret", IDS)
    assert get.calls[0]["params"]["part"] == "statistics"


def test_missing_video_raises(monkeypatch):
    monkeypatch.setattr(youtube.httpx, "get", fake_get(items=[{"id": "a"}]))
    with pytest.raises(RuntimeError, match="no stats for"):
        youtube.fetch_stats("secret", IDS)


def test_http_error_raises_without_leaking_key(monkeypatch):
    monkeypatch.setattr(youtube.httpx, "get", fake_get(status=403))
    with pytest.raises(httpx.HTTPStatusError) as err:
        youtube.fetch_stats("secret", IDS)
    assert "secret" not in str(err.value)


def test_real_config_lists_both_original_trailers():
    ids = youtube.load_video_ids()
    assert {"QdBZY2fkU-0", "VQRLujxTm3c"} <= set(ids)


def test_empty_config_raises(tmp_path):
    path = tmp_path / "videos.toml"
    path.write_text("")
    with pytest.raises(ValueError, match="No videos"):
        youtube.load_video_ids(path)


def test_duplicate_config_raises(tmp_path):
    path = tmp_path / "videos.toml"
    path.write_text('[[video]]\nid = "a"\n[[video]]\nid = "a"\n')
    with pytest.raises(ValueError, match="Duplicate"):
        youtube.load_video_ids(path)
