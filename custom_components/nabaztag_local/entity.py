"""Shared entity helpers."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NabaztagCoordinator


class NabaztagEntity(CoordinatorEntity[NabaztagCoordinator]):
    """Base entity for the configured local Nabaztag server."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NabaztagCoordinator, description: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{description}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.base_url)},
            name="Nabaztag",
            manufacturer="Violet",
            model="Nabaztag / Nabaztag:tag (serveur local)",
            configuration_url=coordinator.client.base_url,
        )
