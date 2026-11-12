"""Sleep switch."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagSleep(coordinator)])


class NabaztagSleep(NabaztagEntity, SwitchEntity):
    _attr_name = "Sommeil"
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "sleep")
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.sleep(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.sleep(False)
        self._attr_is_on = False
        self.async_write_ha_state()
