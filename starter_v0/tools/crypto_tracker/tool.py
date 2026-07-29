from __future__ import annotations

from typing import Any


def crypto_tracker(symbol: str = "") -> dict[str, Any]:
    return {
        "tool": "crypto_tracker",
        "symbol": symbol,
        "price": "unknown",
        "currency": "USD",
    }
