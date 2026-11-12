"""Weather and nose selectors."""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import CONF_WEATHER_ENTITY, DOMAIN, JINGLES, NOSE_OPTIONS, WEATHER_OPTIONS
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagWeather(coordinator), NabaztagNose(coordinator), NabaztagJingleSelect(coordinator), NabaztagWeatherSource(coordinator, entry)])


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


class NabaztagWeatherSource(NabaztagEntity, SelectEntity):
    """Select the Home Assistant weather entity directly on the device."""

    _attr_name = "Source météo Home Assistant"
    _attr_icon = "mdi:weather-cloudy"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, "weather_source")
        self._entry = entry

    @property
    def options(self) -> list[str]:
        """Available current-weather entities; refresh when HA adds new ones."""
        weather_entities = sorted(
            state.entity_id for state in self.hass.states.async_all("weather")
        )
        configured = self._entry.options.get(CONF_WEATHER_ENTITY)
        if configured and configured not in weather_entities:
            weather_entities.append(configured)
        return ["Désactivée", *weather_entities]

    @property
    def current_option(self) -> str:
        return self._entry.options.get(CONF_WEATHER_ENTITY) or "Désactivée"

    async def async_select_option(self, option: str) -> None:
        """Persist source and reload so weather listeners follow the selection."""
        weather_entity = None if option == "Désactivée" else option
        if weather_entity and not weather_entity.startswith("weather."):
            raise ValueError("Une entité météo Home Assistant est requise")
        if weather_entity == self._entry.options.get(CONF_WEATHER_ENTITY):
            return
        options = dict(self._entry.options)
        if weather_entity is None:
            options.pop(CONF_WEATHER_ENTITY, None)
        else:
            options[CONF_WEATHER_ENTITY] = weather_entity
        self.hass.config_entries.async_update_entry(self._entry, options=options)
        await self.hass.config_entries.async_reload(self._entry.entry_id)
