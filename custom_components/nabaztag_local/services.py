"""Home Assistant services."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SPEAK_SCHEMA = vol.Schema({
    vol.Required("text"): cv.string,
    vol.Optional("voice", default="fr"): cv.string,
    vol.Optional("speed", default=160): vol.All(vol.Coerce(int), vol.Range(min=80, max=300)),
    vol.Optional("pitch", default=50): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register domain services once."""

    async def handle_speak(call: ServiceCall) -> None:
        coordinators = list(hass.data.get(DOMAIN, {}).values())
        if not coordinators:
            raise vol.Invalid("Aucune instance Nabaztag Local n'est chargée")
        await coordinators[0].client.say(
            call.data["text"],
            voice=call.data["voice"],
            speed=call.data["speed"],
            pitch=call.data["pitch"],
        )

    if not hass.services.has_service(DOMAIN, "speak"):
        hass.services.async_register(DOMAIN, "speak", handle_speak, schema=SPEAK_SCHEMA)
