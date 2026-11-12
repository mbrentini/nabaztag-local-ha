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
        device_id = coordinator.client.base_url
        if coordinator.client.mac:
            device_id = f"{device_id}/{coordinator.client.mac}"
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{description}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"Nabaztag {coordinator.client.mac}" if coordinator.client.mac else "Nabaztag",
            manufacturer="Violet",
            model="Nabaztag / Nabaztag:tag (serveur local)",
            configuration_url=coordinator.client.base_url,
        )
