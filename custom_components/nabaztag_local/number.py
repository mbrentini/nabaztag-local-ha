"""Volume, physical ear positioning, speech tuning and ambient palette."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NabaztagVolume(coordinator),
        NabaztagEar(coordinator, "left"),
        NabaztagEar(coordinator, "right"),
        NabaztagEarDirection(coordinator),
        NabaztagPalette(coordinator),
        NabaztagSpeechSetting(coordinator, "speed", "Vitesse de parole", 80, 300),
        NabaztagSpeechSetting(coordinator, "pitch", "Hauteur de voix", 0, 99),
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
        level = round(value)
        await self.coordinator.client.volume(level)
        self._attr_native_value = level
        self.async_write_ha_state()


class NabaztagEar(NabaztagEntity, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_max_value = 16
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:ear-hearing"

    def __init__(self, coordinator, side: str) -> None:
        super().__init__(coordinator, f"ear_{side}")
        self._side = side
        self._attr_name = f"Position oreille {side}"

    @property
    def native_value(self) -> int:
        return self.coordinator.ear_positions[self._side]

    async def async_set_native_value(self, value: float) -> None:
        positions = dict(self.coordinator.ear_positions)
        positions[self._side] = round(value)
        await self.coordinator.client.ears(
            positions["left"], positions["right"], self.coordinator.ear_direction
        )
        self.coordinator.ear_positions = positions
        self.coordinator.async_update_listeners()


class NabaztagEarDirection(NabaztagEntity, NumberEntity):
    _attr_name = "Sens de rotation des oreilles"
    _attr_native_min_value = 0
    _attr_native_max_value = 1
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:rotate-3d-variant"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "ear_direction")

    @property
    def native_value(self) -> int:
        return self.coordinator.ear_direction

    async def async_set_native_value(self, value: float) -> None:
        direction = round(value)
        await self.coordinator.client.ears(
            self.coordinator.ear_positions["left"],
            self.coordinator.ear_positions["right"],
            direction,
        )
        self.coordinator.ear_direction = direction
        self.coordinator.async_update_listeners()


class NabaztagPalette(NabaztagEntity, NumberEntity):
    _attr_name = "Palette LED basse"
    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_native_value = 0
    _attr_icon = "mdi:palette"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "bottom_palette")

    async def async_set_native_value(self, value: float) -> None:
        index = round(value)
        await self.coordinator.client.bottom_led(index)
        self._attr_native_value = index
        self.async_write_ha_state()


class NabaztagSpeechSetting(NabaztagEntity, NumberEntity):
    """Default speech parameters used by the text.speak entity."""

    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:account-voice"

    def __init__(self, coordinator, parameter: str, name: str, minimum: int, maximum: int) -> None:
        super().__init__(coordinator, f"say_{parameter}")
        self._parameter = parameter
        self._attr_name = name
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum

    @property
    def native_value(self) -> int:
        return int(self.coordinator.say_options[self._parameter])

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.say_options[self._parameter] = round(value)
        self.coordinator.async_update_listeners()
