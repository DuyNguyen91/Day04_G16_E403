from __future__ import annotations

from typing import Any


def weather_forecast(location: str = "") -> dict[str, Any]:
    return {
        "tool": "weather_forecast",
        "location": location,
        "forecast": f"Stub forecast for {location or 'unknown location'}",
        "unit": "celsius",
    }
