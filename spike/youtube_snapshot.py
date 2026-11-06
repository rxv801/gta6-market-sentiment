"""Stopgap: save daily YouTube stats for the official trailers until ING-2 replaces this.

Stores numeric statistics only, with no comment text.

Usage:
    uv run python -m spike.youtube_snapshot
"""

import os
from datetime import UTC, datetime

import httpx

from extract.loader import load_raw

API_URL = "https://www.googleapis.com/youtube/v3/videos"
VIDEO_IDS = [
    "QdBZY2fkU-0",  # Trailer 1
    "VQRLujxTm3c",  # Trailer 2
]


def fetch_stats(api_key: str, video_ids: list[str]) -> dict:
    """Return the videos.list response, failing if any video is missing."""
    # The key goes in a header, not the URL, so it can't appear in error messages.
    response = httpx.get(
        API_URL,
        params={"part": "statistics", "id": ",".join(video_ids)},
        headers={"X-Goog-Api-Key": api_key},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    returned = {item["id"] for item in payload.get("items", [])}
    missing = set(video_ids) - returned
    if missing:
        raise RuntimeError(f"YouTube returned no stats for: {sorted(missing)}")
    return payload


def main() -> None:
    fetched_at = datetime.now(UTC)
    payload = fetch_stats(os.environ["YOUTUBE_API_KEY"], VIDEO_IDS)
    load_raw("youtube", "videos.list", payload, fetched_at)
    print(f"Saved stats for {len(VIDEO_IDS)} videos")


if __name__ == "__main__":
    main()
