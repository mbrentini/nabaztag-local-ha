"""Jingle buttons."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, JINGLES
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagJingle(coordinator, name) for name in JINGLES])


class NabaztagJingle(NabaztagEntity, ButtonEntity):
    _attr_icon = "mdi:music-note"

    def __init__(self, coordinator, jingle: str) -> None:
        super().__init__(coordinator, f"jingle_{jingle}")
        self._jingle = jingle
        self._attr_name = f"Jingle {jingle.replace('_', ' ')}"

    async def async_press(self) -> None:
        await self.coordinator.client.jingle(self._jingle)
