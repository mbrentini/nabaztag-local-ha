"""Diagnostic sensors."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagCount(coordinator), NabaztagAddress(coordinator)])


class NabaztagCount(NabaztagEntity, SensorEntity):
    _attr_name = "Nombre de lapins connectés"
    _attr_icon = "mdi:rabbit"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "connected_count")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.connected_rabbits)


class NabaztagAddress(NabaztagEntity, SensorEntity):
    _attr_name = "Adresse du serveur"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "server_address")

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("server_address")
