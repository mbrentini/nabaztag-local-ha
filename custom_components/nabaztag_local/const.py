"""Constants for Nabaztag Local."""

from datetime import timedelta

DOMAIN = "nabaztag_local"
CONF_URL = "url"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

PLATFORMS = ["binary_sensor", "sensor", "light", "switch", "number", "select", "button"]

WEATHER_OPTIONS = ["sun", "cloudy", "smog", "rain", "snow", "storm"]
JINGLES = [
    "acquired", "ack", "abort", "ministop", "ears", "rfid_ok",
    "start_record", "end_record", "start_interactive", "end_interactive",
    "previous", "next",
]
