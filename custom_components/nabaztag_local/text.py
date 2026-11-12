"""Editable action text fields for local speech, audio and Violet programs."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            NabaztagActionText(coordinator, "say_text", "Dire un texte", "say"),
            NabaztagActionText(coordinator, "say_voice", "Voix de synthèse", "voice"),
            NabaztagActionText(coordinator, "play_url", "Lire une URL audio", "play"),
            NabaztagActionText(coordinator, "choreography", "Envoyer une chorégraphie", "choreography"),
            NabaztagActionText(coordinator, "program", "Envoyer un programme", "program"),
            NabaztagActionText(coordinator, "raw_packet", "Envoyer un paquet Base64", "raw"),
            NabaztagActionText(coordinator, "ambient_packet", "Envoyer un paquet Ambient", "ambient"),
        ]
    )


class NabaztagActionText(NabaztagEntity, TextEntity):
    """Sending a text value immediately runs the corresponding API command.

    Values are stored only in the Home Assistant entity state, not on the server.
    For payloads longer than HA text fields, use the matching service action.
    """

    _attr_mode = TextMode.TEXT
    _attr_native_min = 0
    _attr_native_max = 255
    _attr_native_value = ""

    def __init__(self, coordinator, unique_key: str, name: str, command: str) -> None:
        super().__init__(coordinator, unique_key)
        self._attr_name = name
        self._command = command
        if command == "voice":
            self._attr_native_value = coordinator.say_options["voice"]
        if command == "play":
            self._attr_pattern = r"https?://.+"

    async def async_set_value(self, value: str) -> None:
        """Run a command when the user submits the field."""
        client = self.coordinator.client
        if self._command == "say":
            await client.say(value, **self.coordinator.say_options)
        elif self._command == "voice":
            self.coordinator.say_options["voice"] = value
        elif self._command == "play":
            await client.play(value)
        elif self._command == "choreography":
            await client.choreography(value)
        elif self._command == "program":
            await client.program(value)
        elif self._command == "raw":
            await client.raw(value)
        elif self._command == "ambient":
            try:
                pairs = [part.strip().split("=", 1) for part in value.split(",") if part.strip()]
                services = [int(pair[0]) for pair in pairs]
                values = [int(pair[1]) for pair in pairs]
                if not pairs or any(len(pair) != 2 for pair in pairs):
                    raise ValueError("Expected service=value")
            except (ValueError, IndexError) as err:
                raise HomeAssistantError(
                    "Saisir service=valeur,service=valeur (ex. 8=1,9=2)"
                ) from err
            await client.ambient(services, values)
        self._attr_native_value = value
        self.async_write_ha_state()
