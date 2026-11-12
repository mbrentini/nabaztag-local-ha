"""Config and options flows for Nabaztag Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import NabaztagApiError, NabaztagClient
from .const import CONF_MAC, CONF_TOKEN, CONF_URL, CONF_WEATHER_ENTITY, DOMAIN


class NabaztagLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure the local server with its URL."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            token = user_input.get(CONF_TOKEN, "").strip()
            if not url.startswith(("http://", "https://")):
                errors[CONF_URL] = "invalid_url"
            else:
                mac = user_input.get(CONF_MAC, "").strip().lower().replace(":", "")
                client = NabaztagClient(async_get_clientsession(self.hass), url, token or None, mac or None)
                try:
                    await client.status()
                except NabaztagApiError:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(url.lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Nabaztag ({url.split('//', 1)[-1]})",
                        data={CONF_URL: url, CONF_TOKEN: token, CONF_MAC: mac},
                    )

        schema = vol.Schema({
            vol.Required(CONF_URL, default="http://192.168.1.20:8099"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.URL)
            ),
            vol.Optional(CONF_TOKEN, default=""): TextSelector(),
            vol.Optional(CONF_MAC, default=""): TextSelector(),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return NabaztagOptionsFlow(config_entry)


class NabaztagOptionsFlow(OptionsFlow):
    """Configure optional automatic weather display."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_entity = self.config_entry.options.get(CONF_WEATHER_ENTITY)
        selector_key = (
            vol.Optional(CONF_WEATHER_ENTITY, default=current_entity)
            if current_entity
            else vol.Optional(CONF_WEATHER_ENTITY)
        )
        schema = vol.Schema({
            selector_key: EntitySelector(EntitySelectorConfig(domain="weather")),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
