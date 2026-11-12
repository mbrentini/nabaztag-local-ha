"""Jingle and diagnostic buttons."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, JINGLES
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [NabaztagJingle(coordinator, name) for name in JINGLES]
        + [NabaztagStateButton(coordinator), NabaztagPersonalityButton(coordinator), NabaztagPreviewJingle(coordinator), NabaztagEarWiggle(coordinator), NabaztagWeatherRefresh(coordinator)]
    )


class NabaztagJingle(NabaztagEntity, ButtonEntity):
    _attr_icon = "mdi:music-note"

    def __init__(self, coordinator, jingle: str) -> None:
        super().__init__(coordinator, f"jingle_{jingle}")
        self._jingle = jingle
        self._attr_name = f"Jingle {jingle.replace('_', ' ')}"

    async def async_press(self) -> None:
        await self.coordinator.client.jingle(self._jingle)


class NabaztagStateButton(NabaztagEntity, ButtonEntity):
    _attr_name = "Interroger l'état du lapin"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "query_state")

    async def async_press(self) -> None:
        await self.coordinator.client.state()


class NabaztagPersonalityButton(NabaztagEntity, ButtonEntity):
    _attr_name = "Comportement spontané"
    _attr_icon = "mdi:creation"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "personality")

    async def async_press(self) -> None:
        await self.coordinator.client.personality()


class NabaztagPreviewJingle(NabaztagEntity, ButtonEntity):
    _attr_name = "Jouer le jingle sélectionné"
    _attr_icon = "mdi:play-circle-outline"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "preview_jingle")

    async def async_press(self) -> None:
        await self.coordinator.client.jingle(self.coordinator.selected_jingle)


class NabaztagEarWiggle(NabaztagEntity, ButtonEntity):
    _attr_name = "Faire frétiller les oreilles"
    _attr_icon = "mdi:rabbit-variant"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "wiggle_ears")

    async def async_press(self) -> None:
        await self.coordinator.client.ear_wiggle()


class NabaztagWeatherRefresh(NabaztagEntity, ButtonEntity):
    """Push the selected Home Assistant weather condition right now."""

    _attr_name = "Synchroniser la météo"
    _attr_icon = "mdi:weather-partly-cloudy"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "weather_refresh")

    async def async_press(self) -> None:
        from .weather_sync import weather_icon

        source = self.coordinator.weather_entity
        if not source:
            raise HomeAssistantError("Choisir d'abord une source météo")
        state = self.hass.states.get(source)
        icon = weather_icon(state.state) if state else None
        if icon is None:
            raise HomeAssistantError("La source météo n'a pas de condition actuelle exploitable")
        await self.coordinator.client.weather(icon)
        self.coordinator.weather_icon = icon
        self.coordinator.async_update_listeners()
