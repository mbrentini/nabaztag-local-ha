"""Belly weather icon selector."""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, WEATHER_OPTIONS
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagWeather(coordinator)])


class NabaztagWeather(NabaztagEntity, SelectEntity):
    _attr_name = "Icône météo du ventre"
    _attr_options = WEATHER_OPTIONS
    _attr_icon = "mdi:weather-partly-cloudy"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "weather")
        self._attr_current_option = "sun"

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.weather(option)
        self._attr_current_option = option
        self.async_write_ha_state()
