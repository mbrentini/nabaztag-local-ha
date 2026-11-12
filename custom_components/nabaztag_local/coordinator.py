"""Polling coordinator for the local Nabaztag server."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NabaztagApiError, NabaztagClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

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

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.status()
        except NabaztagApiError as err:
            raise UpdateFailed(f"Impossible de lire l'état du serveur Nabaztag: {err}") from err

        # Adoption is a documented optional API extension. Keep the status
        # sensors working if an older server build does not expose it.
        try:
            data["adoption"] = await self.client.adoption()
        except NabaztagApiError as err:
            _LOGGER.debug("API adoption indisponible : %s", err)
            data["adoption"] = {}
        return data

    @property
    def connected_rabbits(self) -> dict[str, Any]:
        return (self.data or {}).get("bunnies", {}) or {}
