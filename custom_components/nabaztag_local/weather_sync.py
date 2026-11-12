"""Map the current Home Assistant weather condition to Violet's six icons."""

from __future__ import annotations


def weather_icon(condition: str | None) -> str | None:
    """Return a supported /api/weather value or None for unknown conditions."""
    mapping = {
        "sunny": "sun",
        "clear-night": "sun",
        "partlycloudy": "cloudy",
        "cloudy": "cloudy",
        "windy": "cloudy",
        "windy-variant": "cloudy",
        "fog": "smog",
        "foggy": "smog",
        "snowy": "snow",
        "snowy-rainy": "snow",
        "lightning": "storm",
        "lightning-rainy": "storm",
        "hail": "storm",
        "rainy": "rain",
        "pouring": "rain",
    }
    return mapping.get((condition or "").lower())
