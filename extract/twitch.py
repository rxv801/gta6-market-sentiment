"""Save total live viewers and stream count for the GTA VI category on Twitch.

Twitch had no GTA VI category at preload, and its final name isn't known. So each run looks it up by
several names, then by search, and exits cleanly if it still isn't there. The poller can stay on the
schedule and starts saving the first run after the category appears.

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
GAME_NAMES = ["Grand Theft Auto VI", "Grand Theft Auto 6", "GTA VI", "GTA 6"]
SEARCH_QUERY = "Grand Theft Auto"
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


def normalise(name: str) -> str:
    """Lower case, letters and digits only, so "Grand Theft Auto: VI" matches "Grand Theft Auto VI"."""
    return "".join(ch for ch in name.lower() if ch.isalnum())


WANTED = {normalise(name) for name in GAME_NAMES}


def find_game(headers: dict) -> dict | None:
    """Return the GTA VI category as {"id", "name"}, or None if Twitch doesn't have one yet."""
    response = httpx.get(f"{API_URL}/games", params={"name": GAME_NAMES}, headers=headers, timeout=30)
    response.raise_for_status()
    candidates = response.json()["data"]
    if not candidates:
        response = httpx.get(
            f"{API_URL}/search/categories", params={"query": SEARCH_QUERY, "first": 100}, headers=headers, timeout=30
        )
        response.raise_for_status()
        candidates = response.json()["data"]
    for game in candidates:
        if normalise(game["name"]) in WANTED:
            return {"id": game["id"], "name": game["name"]}
    return None


def count_streams(game: dict, headers: dict) -> dict:
    """Page through live streams and return totals. Twitch can repeat a stream across pages, so count by ID."""
    viewers_by_stream = {}
    cursor = None
    truncated = True
    for _ in range(MAX_PAGES):
        params = {"game_id": game["id"], "first": PAGE_SIZE}
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
        "game_id": game["id"],
        "game_name": game["name"],
        "viewer_count": sum(viewers_by_stream.values()),
        "stream_count": len(viewers_by_stream),
        "truncated": truncated,
    }


def main() -> None:
    client_id = os.environ["TWITCH_CLIENT_ID"]
    token = get_token(client_id, os.environ["TWITCH_CLIENT_SECRET"])
    headers = {"Client-Id": client_id, "Authorization": f"Bearer {token}"}

    game = find_game(headers)
    if game is None:
        print(f"No GTA VI category on Twitch yet (tried {GAME_NAMES} and a search). Nothing saved.")
        return
    fetched_at = datetime.now(UTC)
    totals = count_streams(game, headers)
    load_raw("twitch", "streams", totals, fetched_at)
    print(f"Saved Twitch totals: {totals['viewer_count']} viewers, {totals['stream_count']} streams")


if __name__ == "__main__":
    main()
