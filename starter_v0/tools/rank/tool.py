from __future__ import annotations

from typing import Any

from tools._shared import terms


def rank_items(
    items: list[dict[str, Any]] | None = None,
    query: str = "",
    top_k: int = 5,
) -> dict[str, Any]:
    """Rank research items by term overlap with query. Local, no network."""
    items = items or []
    query = (query or "").strip()
    if not query:
        return {
            "tool": "rank_items",
            "error": "missing_query",
            "message": "Provide a non-empty query to rank against.",
            "items": [],
            "scores": [],
            "item_count": 0,
        }

    try:
        top_k = max(1, int(top_k or 5))
    except (TypeError, ValueError):
        top_k = 5

    query_terms = terms(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        blob = " ".join(
            str(item.get(key) or "")
            for key in ("title", "summary", "source", "section")
        )
        item_terms = terms(blob)
        overlap = len(query_terms & item_terms)
        score = overlap / max(len(query_terms), 1)
        scored.append((score, item))

    scored.sort(key=lambda pair: (-pair[0], pair[1].get("title") or ""))
    top = scored[:top_k]
    ranked_items = [item for _, item in top]
    scores = [
        {"title": item.get("title"), "score": round(score, 4)}
        for score, item in top
    ]
    return {
        "tool": "rank_items",
        "query": query,
        "top_k": top_k,
        "items": ranked_items,
        "scores": scores,
        "item_count": len(ranked_items),
        "error": None,
        "message": None,
    }
