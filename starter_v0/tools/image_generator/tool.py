from __future__ import annotations

from typing import Any


def image_generator(prompt: str = "") -> dict[str, Any]:
    return {
        "tool": "image_generator",
        "prompt": prompt,
        "image_url": "",
    }
