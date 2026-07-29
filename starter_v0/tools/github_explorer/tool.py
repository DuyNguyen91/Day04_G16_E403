from __future__ import annotations

from typing import Any


def github_explorer(query: str = "", language: str = "") -> dict[str, Any]:
    return {
        "tool": "github_explorer",
        "query": query,
        "language": language,
        "items": [],
    }
