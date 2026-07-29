from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def audit_sources(items: list[dict[str, Any]], min_sources: int = 2) -> dict[str, Any]:
    if min_sources < 1:
        raise ValueError("min_sources must be at least 1")

    issues: list[dict[str, Any]] = []
    domains: set[str] = set()
    for index, item in enumerate(items):
        item_issues: list[str] = []
        title = str(item.get("title") or "").strip()
        summary = str(item.get("summary") or "").strip()
        url = str(item.get("url") or "").strip()
        parsed = urlparse(url)

        if not title:
            item_issues.append("missing_title")
        if not summary:
            item_issues.append("missing_summary")
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            item_issues.append("invalid_url")
        else:
            domains.add(parsed.netloc.lower().removeprefix("www."))

        if item_issues:
            issues.append({"index": index, "issues": item_issues})

    source_count = len(domains)
    return {
        "tool": "source_audit",
        "item_count": len(items),
        "valid_item_count": len(items) - len(issues),
        "source_count": source_count,
        "sources": sorted(domains),
        "minimum_sources": min_sources,
        "issues": issues,
        "ready": bool(items) and not issues and source_count >= min_sources,
    }
