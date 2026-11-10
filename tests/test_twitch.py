import httpx

from extract import twitch

HEADERS = {"Client-Id": "id", "Authorization": "Bearer token"}


def response(json, status=200, url="https://example.test"):
    return httpx.Response(status, json=json, request=httpx.Request("GET", url))


def paged_get(pages):
    remaining = iter(pages)
    calls = []

    def _get(url, params, headers, timeout):
        calls.append(params)
        return response(next(remaining))

    _get.calls = calls
    return _get


def test_token_credentials_go_in_body_not_url(monkeypatch):
    seen = {}

    def _post(url, data, timeout):
        seen.update(url=url, data=data)
        return response({"access_token": "abc"})

    monkeypatch.setattr(twitch.httpx, "post", _post)
    assert twitch.get_token("id", "secret") == "abc"
    assert seen["data"]["client_secret"] == "secret"
    assert "secret" not in seen["url"]


GAME = {"id": "123", "name": "Grand Theft Auto VI"}


def test_missing_category_returns_none(monkeypatch):
    search_hits = [{"id": "32982", "name": "Grand Theft Auto V"}, {"id": "1", "name": "Grand Theft Auto: San Andreas"}]
    monkeypatch.setattr(twitch.httpx, "get", paged_get([{"data": []}, {"data": search_hits}]))
    assert twitch.find_game(HEADERS) is None


def test_exact_name_lookup_wins(monkeypatch):
    get = paged_get([{"data": [{"id": "9", "name": "GTA 6"}]}])
    monkeypatch.setattr(twitch.httpx, "get", get)
    assert twitch.find_game(HEADERS) == {"id": "9", "name": "GTA 6"}
    assert get.calls[0]["name"] == twitch.GAME_NAMES


def test_search_finds_category_with_odd_punctuation(monkeypatch):
    search_hits = [{"id": "32982", "name": "Grand Theft Auto V"}, {"id": "7", "name": "Grand Theft Auto: VI"}]
    monkeypatch.setattr(twitch.httpx, "get", paged_get([{"data": []}, {"data": search_hits}]))
    assert twitch.find_game(HEADERS) == {"id": "7", "name": "Grand Theft Auto: VI"}


def test_no_category_exits_cleanly_without_saving(monkeypatch):
    monkeypatch.setenv("TWITCH_CLIENT_ID", "id")
    monkeypatch.setenv("TWITCH_CLIENT_SECRET", "secret")
    monkeypatch.setattr(twitch, "get_token", lambda *_: "token")
    monkeypatch.setattr(twitch, "find_game", lambda _: None)
    saved = []
    monkeypatch.setattr(twitch, "load_raw", lambda *args: saved.append(args))
    twitch.main()
    assert saved == []


def test_counts_across_pages_and_dedupes(monkeypatch):
    get = paged_get(
        [
            {"data": [{"id": "1", "viewer_count": 10}, {"id": "2", "viewer_count": 5}], "pagination": {"cursor": "c"}},
            {"data": [{"id": "2", "viewer_count": 7}, {"id": "3", "viewer_count": 1}], "pagination": {}},
        ]
    )
    monkeypatch.setattr(twitch.httpx, "get", get)
    totals = twitch.count_streams(GAME, HEADERS)
    assert totals["viewer_count"] == 18
    assert totals["stream_count"] == 3
    assert totals["truncated"] is False
    assert get.calls[1]["after"] == "c"


def test_zero_streams_is_a_valid_result(monkeypatch):
    monkeypatch.setattr(twitch.httpx, "get", paged_get([{"data": [], "pagination": {}}]))
    totals = twitch.count_streams(GAME, HEADERS)
    assert totals["viewer_count"] == 0
    assert totals["stream_count"] == 0
    assert totals["truncated"] is False


def test_page_limit_marks_result_truncated(monkeypatch):
    monkeypatch.setattr(twitch, "MAX_PAGES", 2)
    page = {"data": [{"id": "1", "viewer_count": 1}], "pagination": {"cursor": "c"}}
    monkeypatch.setattr(twitch.httpx, "get", paged_get([page, page]))
    assert twitch.count_streams(GAME, HEADERS)["truncated"] is True


def test_payload_keeps_no_titles_or_usernames(monkeypatch):
    stream = {"id": "1", "viewer_count": 3, "title": "spoiler text", "user_name": "someone"}
    monkeypatch.setattr(twitch.httpx, "get", paged_get([{"data": [stream], "pagination": {}}]))
    totals = twitch.count_streams(GAME, HEADERS)
    assert "spoiler text" not in str(totals)
    assert "someone" not in str(totals)
