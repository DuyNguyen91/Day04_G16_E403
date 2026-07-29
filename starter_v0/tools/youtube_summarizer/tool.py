from __future__ import annotations

from typing import Any


def youtube_summarizer(url: str = "") -> dict[str, Any]:
    return {
        "tool": "youtube_summarizer",
        "url": url,
        "summary": f"Stub summary for YouTube video: {url or 'unknown URL'}",
        "source": "youtube",
    }
