"""Speaker volume and ear positioning controls."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NabaztagVolume(coordinator),
        NabaztagEar(coordinator, "left"),
        NabaztagEar(coordinator, "right"),
    ])


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


class NabaztagEar(NabaztagEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 16
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = 8
    _attr_icon = "mdi:ear-hearing"

    def __init__(self, coordinator, side: str) -> None:
        super().__init__(coordinator, f"ear_{side}")
        self._side = side
        self._attr_name = f"Position oreille {side}"

    async def async_set_native_value(self, value: float) -> None:
        left = round(value) if self._side == "left" else 8
        right = round(value) if self._side == "right" else 8
        await self.coordinator.client.ears(left, right)
        self._attr_native_value = round(value)
        self.async_write_ha_state()
