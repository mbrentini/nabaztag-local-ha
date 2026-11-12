"""Speaker volume control."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagVolume(coordinator)])


class NabaztagVolume(NabaztagEntity, NumberEntity):
    _attr_name = "Volume"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = 80
    _attr_icon = "mdi:volume-high"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "volume")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.volume(round(value))
        self._attr_native_value = round(value)
        self.async_write_ha_state()
