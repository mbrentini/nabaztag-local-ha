"""Constants for Nabaztag Local."""

from datetime import timedelta

DOMAIN = "nabaztag_local"
CONF_URL = "url"
CONF_TOKEN = "api_token"
CONF_MAC = "mac"
CONF_WEATHER_ENTITY = "weather_entity"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
WEATHER_CHECK_MINUTE = 0

PLATFORMS = ["binary_sensor", "sensor", "light", "switch", "number", "select", "button"]

WEATHER_OPTIONS = ["sun", "cloudy", "smog", "rain", "snow", "storm"]
NOSE_OPTIONS = ["Aucun", "Clignotement", "Double clignotement"]
JINGLES = [
    "acquired", "ack", "abort", "ministop", "ears", "rfid_ok",
    "start_record", "end_record", "start_interactive", "end_interactive",
    "previous", "next",
]
EAR_MIN = 0
EAR_MAX = 16
