"""Polling coordinator for the local Nabaztag server."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NabaztagApiError, NabaztagAuthError, NabaztagClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .identity import rabbit_status

_LOGGER = logging.getLogger(__name__)


class NabaztagCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch server, rabbit connection and adoption state."""

    def __init__(self, hass: HomeAssistant, client: NabaztagClient) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        self.ear_positions = {"left": 8, "right": 8}
        self.ear_direction = 0
        self.say_options = {"voice": "fr", "speed": 160, "pitch": 50, "wait": False}
        self.selected_jingle = "ears"
        self.weather_icon = "sun"
        self.last_rfid = None
        self.last_button = None
        self.last_ears = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.status()
        except NabaztagApiError as err:
            raise UpdateFailed(f"Impossible de lire l'état du serveur Nabaztag: {err}") from err

        # Adoption is a documented optional API extension. Keep the status
        # sensors working if an older server build does not expose it.
        try:
            data["adoption"] = await self.client.adoption()
        except NabaztagAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except NabaztagApiError as err:
            _LOGGER.debug("API adoption indisponible : %s", err)
            data["adoption"] = {}
        return data

    @property
    def connected_rabbits(self) -> dict[str, Any]:
        return (self.data or {}).get("bunnies", {}) or {}

    @property
    def rabbit(self) -> dict[str, Any]:
        """Status of the chosen rabbit, if any; never another rabbit's status."""
        return rabbit_status(self.data or {}, self.client.mac)

    def handle_event(self, event_data: dict[str, Any]) -> None:
        """Remember input data so automations and dashboard sensors can use it."""
        kind = event_data.get("type")
        if kind == "rfid":
            self.last_rfid = str(event_data.get("tag", "")) or None
        elif kind == "button":
            self.last_button = event_data.get("action")
        elif kind == "ears":
            self.last_ears = {
                "left": event_data.get("left"),
                "right": event_data.get("right"),
            }
            for side in ("left", "right"):
                if isinstance(event_data.get(side), int):
                    self.ear_positions[side] = event_data[side]
        else:
            return
        self.async_update_listeners()
