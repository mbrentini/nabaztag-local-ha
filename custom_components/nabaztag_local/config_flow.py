"""Config flow for Nabaztag Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import NabaztagApiError, NabaztagClient
from .const import CONF_URL, DOMAIN


class NabaztagLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure the local server with its URL."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            if not url.startswith(("http://", "https://")):
                errors[CONF_URL] = "invalid_url"
            else:
                client = NabaztagClient(async_get_clientsession(self.hass), url)
                try:
                    status = await client.status()
                except NabaztagApiError:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(url.lower())
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Nabaztag ({url.split('//', 1)[-1]})",
                        data={CONF_URL: url},
                    )

        schema = vol.Schema({
            vol.Required(CONF_URL, default="http://homeassistant.local:8099"): TextSelector(
                TextSelectorConfig(type=TextSelectorType.URL)
            )
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
