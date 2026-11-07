"""Save total live viewers and stream count for the GTA VI category on Twitch.

Stores aggregates only. Stream titles and usernames are never kept, because titles
can contain spoilers and usernames are personal data.

Usage:
    uv run python -m extract.twitch
"""

import os
from datetime import UTC, datetime

import httpx

from extract.loader import load_raw

TOKEN_URL = "https://id.twitch.tv/oauth2/token"  # noqa: S105
API_URL = "https://api.twitch.tv/helix"
GAME_NAME = "Grand Theft Auto VI"
PAGE_SIZE = 100
MAX_PAGES = 100


def get_token(client_id: str, client_secret: str) -> str:
    """Get an app access token. Credentials go in the form body so they stay out of error messages."""
    response = httpx.post(
        TOKEN_URL,
        data={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_game_id(headers: dict) -> str:
    response = httpx.get(f"{API_URL}/games", params={"name": GAME_NAME}, headers=headers, timeout=30)
    response.raise_for_status()
    games = response.json()["data"]
    if not games:
        raise RuntimeError(f"Twitch has no category named {GAME_NAME!r}")
    return games[0]["id"]


def count_streams(game_id: str, headers: dict) -> dict:
    """Page through live streams and return totals. Twitch can repeat a stream across pages, so count by ID."""
    viewers_by_stream = {}
    cursor = None
    truncated = True
    for _ in range(MAX_PAGES):
        params = {"game_id": game_id, "first": PAGE_SIZE}
        if cursor:
            params["after"] = cursor
        response = httpx.get(f"{API_URL}/streams", params=params, headers=headers, timeout=30)
        response.raise_for_status()
        body = response.json()
        for stream in body["data"]:
            viewers_by_stream[stream["id"]] = stream["viewer_count"]
        cursor = body.get("pagination", {}).get("cursor")
        if not cursor or not body["data"]:
            truncated = False
            break
    return {
        "game_id": game_id,
        "game_name": GAME_NAME,
        "viewer_count": sum(viewers_by_stream.values()),
        "stream_count": len(viewers_by_stream),
        "truncated": truncated,
    }


def main() -> None:
    client_id = os.environ["TWITCH_CLIENT_ID"]
    token = get_token(client_id, os.environ["TWITCH_CLIENT_SECRET"])
    headers = {"Client-Id": client_id, "Authorization": f"Bearer {token}"}

    fetched_at = datetime.now(UTC)
    totals = count_streams(get_game_id(headers), headers)
    load_raw("twitch", "streams", totals, fetched_at)
    print(f"Saved Twitch totals: {totals['viewer_count']} viewers, {totals['stream_count']} streams")


if __name__ == "__main__":
    main()
