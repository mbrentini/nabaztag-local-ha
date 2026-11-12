"""Polling coordinator for the local Nabaztag server."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NabaztagApiError, NabaztagClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class NabaztagCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch server and rabbit connection state."""

    def __init__(self, hass: HomeAssistant, client: NabaztagClient) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.status()
        except NabaztagApiError as err:
            raise UpdateFailed(f"Impossible de lire l'état du serveur Nabaztag: {err}") from err

    @property
    def connected_rabbits(self) -> dict[str, Any]:
        data = self.data or {}
        return data.get("bunnies", {}) or {}
