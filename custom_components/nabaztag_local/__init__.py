"""Nabaztag Local integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .api import NabaztagApiError, NabaztagClient
from .const import CONF_MAC, CONF_TOKEN, CONF_URL, CONF_WEATHER_ENTITY, DOMAIN, PLATFORMS
from .coordinator import NabaztagCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)
type NabaztagConfigEntry = ConfigEntry[NabaztagCoordinator]


def _weather_icon(condition: str) -> str | None:
    """Map Home Assistant weather conditions to Nabaztag belly icons."""
    condition = condition.lower()
    if condition in {"sunny", "clear-night"}:
        return "sun"
    if condition in {"partlycloudy", "cloudy", "windy", "windy-variant"}:
        return "cloudy"
    if condition in {"fog", "foggy"}:
        return "smog"
    if condition in {"snowy", "snowy-rainy"}:
        return "snow"
    if condition in {"lightning", "lightning-rainy", "hail"}:
        return "storm"
    if condition in {"rainy", "pouring"}:
        return "rain"
    return None


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration services."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: NabaztagConfigEntry) -> bool:
    client = NabaztagClient(
        async_get_clientsession(hass),
        entry.data[CONF_URL],
        entry.data.get(CONF_TOKEN) or None,
        entry.data.get(CONF_MAC) or None,
    )
    coordinator = NabaztagCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    weather_entity = entry.options.get(CONF_WEATHER_ENTITY)
    if weather_entity:
        async def update_weather(_now=None) -> None:
            state = hass.states.get(weather_entity)
            if state is None:
                _LOGGER.warning("Entité météo %s introuvable", weather_entity)
                return
            icon = _weather_icon(state.state)
            if icon is None:
                _LOGGER.debug("Condition météo non prise en charge : %s", state.state)
                return
            try:
                await client.weather(icon)
            except NabaztagApiError as err:
                _LOGGER.warning("Impossible de mettre à jour l'icône météo du Nabaztag : %s", err)

        await update_weather()
        cancel_weather = async_track_time_change(hass, update_weather, minute=0, second=0)
        entry.async_on_unload(cancel_weather)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: NabaztagConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
