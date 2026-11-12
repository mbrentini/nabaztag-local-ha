"""RGB belly light."""

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagBelly(coordinator)])


class NabaztagBelly(NabaztagEntity, LightEntity):
    _attr_name = "LED du ventre"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_is_on = False
    _attr_rgb_color = (0, 0, 0)

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "belly")

    async def async_turn_on(self, **kwargs) -> None:
        rgb = kwargs.get("rgb_color", (255, 255, 255))
        self._attr_rgb_color = tuple(max(0, min(255, int(v))) for v in rgb)
        self._attr_is_on = True
        await self.coordinator.client.led("bottom", self._attr_rgb_color)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_rgb_color = (0, 0, 0)
        self._attr_is_on = False
        await self.coordinator.client.led("bottom", (0, 0, 0))
        self.async_write_ha_state()
