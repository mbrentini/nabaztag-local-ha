"""Config and options flows for Nabaztag Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlowWithReload
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import NabaztagApiError, NabaztagAuthError, NabaztagClient
from .const import CONF_MAC, CONF_TOKEN, CONF_URL, CONF_WEATHER_ENTITY, CONF_RADIO_URL, DOMAIN
from .identity import normalize_mac


class NabaztagLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure the local server with its URL."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip().rstrip("/")
            token = user_input.get(CONF_TOKEN, "").strip()
            mac = normalize_mac(user_input.get(CONF_MAC, ""))
            if not url.startswith(("http://", "https://")):
                errors[CONF_URL] = "invalid_url"
            elif mac and (len(mac) != 12 or any(char not in "0123456789abcdef" for char in mac)):
                errors[CONF_MAC] = "invalid_mac"
            else:
                client = NabaztagClient(async_get_clientsession(self.hass), url, token or None, mac or None)
                try:
                    status = await client.status()
                    # The root status may be public even when /api/* requires a token.
                    try:
                        await client.adoption()
                    except NabaztagApiError as err:
                        if isinstance(err, NabaztagAuthError):
                            raise
                        # Optional on older versions of the local server.
                except NabaztagAuthError:
                    errors["base"] = "invalid_auth"
                except NabaztagApiError:
                    errors["base"] = "cannot_connect"
                else:
                    bunnies = (status.get("bunnies") or {})
                    if not mac and len(bunnies) > 1:
                        errors[CONF_MAC] = "mac_required"
                    elif mac and bunnies and not any(
                        normalize_mac(known) == mac for known in bunnies
                    ):
                        errors[CONF_MAC] = "mac_not_found"
                    else:
                        selected_mac = mac or (
                            normalize_mac(next(iter(bunnies))) if len(bunnies) == 1 else ""
                        )
                        for existing in self._async_current_entries():
                            existing_mac = normalize_mac(existing.data.get(CONF_MAC))
                            running = self.hass.data.get(DOMAIN, {}).get(existing.entry_id)
                            if not existing_mac and running:
                                existing_bunnies = running.connected_rabbits
                                if len(existing_bunnies) == 1:
                                    existing_mac = normalize_mac(next(iter(existing_bunnies)))
                            if selected_mac and existing_mac == selected_mac:
                                errors["base"] = "already_configured"
                                break
                            if (
                                existing.data.get(CONF_URL, "").rstrip("/").lower() == url.lower()
                                and existing_mac == mac
                            ):
                                errors["base"] = "already_configured"
                                break
                        if not errors:
                            # MAC selection distinguishes rabbits on the same server.
                            # Keep the old URL-only unique ID for single-rabbit entries.
                            unique_id = f"{url.lower()}/{mac}" if mac else url.lower()
                            await self.async_set_unique_id(unique_id)
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

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Request a replacement API token when the server rejects it."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            client = NabaztagClient(
                async_get_clientsession(self.hass),
                entry.data[CONF_URL],
                token or None,
                entry.data.get(CONF_MAC) or None,
            )
            try:
                await client.adoption()
            except NabaztagAuthError:
                errors["base"] = "invalid_auth"
            except NabaztagApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, CONF_TOKEN: token}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return NabaztagOptionsFlow()


class NabaztagOptionsFlow(OptionsFlowWithReload):
    """Configure optional automatic weather display."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            radio_url = (user_input.get(CONF_RADIO_URL) or "").strip()
            if radio_url and not radio_url.lower().startswith(("http://", "https://")):
                return self._show_options_form(
                    errors={CONF_RADIO_URL: "invalid_radio_url"},
                    values=user_input,
                )
            options = dict(user_input)
            if radio_url:
                options[CONF_RADIO_URL] = radio_url
            else:
                options.pop(CONF_RADIO_URL, None)
            return self.async_create_entry(title="", data=options)
        return self._show_options_form()

    def _show_options_form(
        self, errors: dict[str, str] | None = None,
        values: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Offer weather and a stored radio URL in the same options dialog."""
        values = values or dict(self.config_entry.options)
        current_entity = values.get(CONF_WEATHER_ENTITY)
        selector_key = (
            vol.Optional(CONF_WEATHER_ENTITY, default=current_entity)
            if current_entity
            else vol.Optional(CONF_WEATHER_ENTITY)
        )
        schema = vol.Schema({
            selector_key: EntitySelector(EntitySelectorConfig(domain="weather")),
            vol.Optional(
                CONF_RADIO_URL, default=values.get(CONF_RADIO_URL, "")
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors or {})
