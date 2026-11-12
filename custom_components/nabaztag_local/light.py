"""RGB control for the five Nabaztag LEDs."""

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NabaztagEntity

# Keep the original "belly" unique ID for the bottom LED so existing
# installations update the existing entity instead of creating a duplicate.
LEDS = (
    ("bottom", "LED basse", "belly"),
    ("left", "LED gauche", "led_left"),
    ("middle", "LED centrale", "led_middle"),
    ("right", "LED droite", "led_right"),
    ("top", "LED haute", "led_top"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [NabaztagLed(coordinator, led, name, unique_id) for led, name, unique_id in LEDS]
    )


class NabaztagLed(NabaztagEntity, LightEntity):
    """One independently controllable RGB LED."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(self, coordinator, led: str, name: str, unique_id: str) -> None:
        super().__init__(coordinator, unique_id)
        self._led = led
        self._attr_name = name
        self._attr_is_on = False
        self._attr_rgb_color = (0, 0, 0)

    async def async_turn_on(self, **kwargs) -> None:
        rgb = kwargs.get("rgb_color", self._attr_rgb_color)
        self._attr_rgb_color = tuple(max(0, min(255, int(value))) for value in rgb)
        self._attr_is_on = True
        await self.coordinator.client.led(self._led, self._attr_rgb_color)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_rgb_color = (0, 0, 0)
        self._attr_is_on = False
        await self.coordinator.client.led(self._led, (0, 0, 0))
        self.async_write_ha_state()
