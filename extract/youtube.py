"""Save daily views, likes and comment counts for the videos listed in config.

Stores numeric statistics only, with no comment text.

Usage:
    uv run python -m extract.youtube
"""

import os
import tomllib
from datetime import UTC, datetime
from itertools import batched
from pathlib import Path

import httpx

from extract.loader import load_raw

API_URL = "https://www.googleapis.com/youtube/v3/videos"
CONFIG_PATH = Path(__file__).parent.parent / "config" / "youtube_videos.toml"
MAX_IDS_PER_REQUEST = 50


def load_video_ids(path: Path = CONFIG_PATH) -> list[str]:
    """Read tracked video IDs from config. A bad list raises, so it can't silently shrink the data."""
    with path.open("rb") as config:
        ids = [video["id"] for video in tomllib.load(config).get("video", [])]
    if not ids:
        raise ValueError(f"No videos listed in {path}")
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate video IDs in {path}")
    return ids


def fetch_stats(api_key: str, video_ids: list[str]) -> dict:
    """Return statistics for every video, failing if any video is missing."""
    items = []
    for chunk in batched(video_ids, MAX_IDS_PER_REQUEST):
        # The key goes in a header, not the URL, so it can't appear in error messages.
        response = httpx.get(
            API_URL,
            params={"part": "statistics", "id": ",".join(chunk)},
            headers={"X-Goog-Api-Key": api_key},
            timeout=30,
        )
        response.raise_for_status()
        items.extend(response.json().get("items", []))

    missing = set(video_ids) - {item["id"] for item in items}
    if missing:
        raise RuntimeError(f"YouTube returned no stats for: {sorted(missing)}")
    return {"items": items}


def main() -> None:
    video_ids = load_video_ids()
    fetched_at = datetime.now(UTC)
    load_raw("youtube", "videos.list", fetch_stats(os.environ["YOUTUBE_API_KEY"], video_ids), fetched_at)
    print(f"Saved stats for {len(video_ids)} videos")


if __name__ == "__main__":
    main()
