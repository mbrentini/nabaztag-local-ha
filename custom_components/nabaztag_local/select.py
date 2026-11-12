"""Weather and nose selectors."""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, JINGLES, NOSE_OPTIONS, WEATHER_OPTIONS
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagWeather(coordinator), NabaztagNose(coordinator), NabaztagJingleSelect(coordinator)])


class NabaztagWeather(NabaztagEntity, SelectEntity):
    _attr_name = "Icône météo du ventre"
    _attr_options = WEATHER_OPTIONS
    _attr_icon = "mdi:weather-partly-cloudy"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "weather")
        self._attr_current_option = "sun"

    @property
    def current_option(self) -> str:
        return self.coordinator.weather_icon

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.weather(option)
        self.coordinator.weather_icon = option
        self.coordinator.async_update_listeners()


class NabaztagNose(NabaztagEntity, SelectEntity):
    _attr_name = "Nez"
    _attr_options = NOSE_OPTIONS
    _attr_icon = "mdi:account-circle"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "nose")
        self._attr_current_option = NOSE_OPTIONS[0]

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.nose(NOSE_OPTIONS.index(option))
        self._attr_current_option = option
        self.async_write_ha_state()


class NabaztagJingleSelect(NabaztagEntity, SelectEntity):
    """Choose the jingle played by the 'Test du jingle' button."""

    _attr_name = "Jingle à jouer"
    _attr_options = JINGLES
    _attr_icon = "mdi:music-note"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "jingle_select")

    @property
    def current_option(self) -> str:
        return self.coordinator.selected_jingle

    async def async_select_option(self, option: str) -> None:
        self.coordinator.selected_jingle = option
        self.coordinator.async_update_listeners()
