"""Tests for local Nabaztag weather mapping, independent of HA dependencies."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "custom_components/nabaztag_local/weather_sync.py"
SPEC = importlib.util.spec_from_file_location("weather_sync", MODULE)
assert SPEC is not None and SPEC.loader is not None
weather_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(weather_sync)


class WeatherMappingTests(unittest.TestCase):
    def test_documented_violet_icons(self):
        cases = {
            "sunny": "sun",
            "clear-night": "sun",
            "partlycloudy": "cloudy",
            "cloudy": "cloudy",
            "windy": "cloudy",
            "fog": "smog",
            "rainy": "rain",
            "pouring": "rain",
            "snowy": "snow",
            "snowy-rainy": "snow",
            "lightning": "storm",
            "lightning-rainy": "storm",
            "hail": "storm",
        }
        for condition, expected in cases.items():
            with self.subTest(condition=condition):
                self.assertEqual(weather_sync.weather_icon(condition), expected)

    def test_unavailable_is_not_sent_to_server(self):
        for condition in (None, "unknown", "unavailable", "exceptional"):
            self.assertIsNone(weather_sync.weather_icon(condition))


if __name__ == "__main__":
    unittest.main()
