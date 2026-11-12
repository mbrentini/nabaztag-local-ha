"""Home Assistant services for advanced Nabaztag API functions."""

from __future__ import annotations

import re
from pathlib import Path

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SPEAK_SCHEMA = vol.Schema({
    vol.Required("text"): cv.string,
    vol.Optional("voice", default="fr"): cv.string,
    vol.Optional("speed", default=160): vol.All(vol.Coerce(int), vol.Range(min=80, max=300)),
    vol.Optional("pitch", default=50): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
    vol.Optional("wait", default=False): cv.boolean,
})
PLAY_SCHEMA = vol.Schema({
    vol.Required("url"): cv.string,
    vol.Optional("wait", default=False): cv.boolean,
})
EARS_SCHEMA = vol.Schema({
    vol.Required("left"): vol.All(vol.Coerce(int), vol.Range(min=0, max=16)),
    vol.Required("right"): vol.All(vol.Coerce(int), vol.Range(min=0, max=16)),
    vol.Optional("direction", default=0): vol.In([0, 1]),
})
LED_SCHEMA = vol.Schema({
    vol.Required("led"): vol.In(["bottom", "left", "middle", "right", "top"]),
    vol.Required("red"): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
    vol.Required("green"): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
    vol.Required("blue"): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
})
CHOREOGRAPHY_SCHEMA = vol.Schema({vol.Required("spec"): cv.string})
def _int_list(value):
    """Accept either a YAML list or a comma-separated list of integers."""
    if isinstance(value, str):
        return [int(item.strip()) for item in value.split(",") if item.strip()]
    return [int(item) for item in value]


AMBIENT_SCHEMA = vol.Schema({
    vol.Required("services"): _int_list,
    vol.Required("values"): _int_list,
})
RAW_SCHEMA = vol.Schema({vol.Required("packet_b64"): cv.string})
RECORDING_SCHEMA = vol.Schema({
    vol.Optional("format", default="pcm"): vol.In(["pcm", "adpcm"]),
    vol.Optional("filename", default="nabaztag-recording.wav"): cv.string,
})
ADOPTION_SCHEMA = vol.Schema({
    vol.Required("action"): vol.In(["confirm", "reject", "forget"]),
    vol.Required("mac"): cv.string,
    vol.Optional("fingerprint"): cv.string,
})
OTA_SCHEMA = vol.Schema({
    vol.Required("path"): cv.string,
    vol.Optional("name", default="firmware.signed.sim"): cv.string,
    vol.Optional("trigger", default=False): cv.boolean,
})


def _coordinator(hass: HomeAssistant, call: ServiceCall):
    """Select the exact device; never silently route to the first rabbit."""
    instances = hass.data.get(DOMAIN, {})
    device_id = call.data.get("device_id")
    if device_id:
        device = dr.async_get(hass).async_get(device_id)
        if device is None:
            raise HomeAssistantError("Appareil Nabaztag introuvable")
        matches = [
            coordinator
            for entry_id, coordinator in instances.items()
            if entry_id in device.config_entries
        ]
        if len(matches) == 1:
            return matches[0]
        raise HomeAssistantError("L'appareil sélectionné ne correspond pas à un seul Nabaztag Local")
    if len(instances) == 1:
        return next(iter(instances.values()))
    if not instances:
        raise HomeAssistantError("Aucune instance Nabaztag Local n'est chargée")
    raise HomeAssistantError("Plusieurs Nabaztag : choisir un appareil dans l'action")


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services once."""

    async def handle_speak(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.say(
            call.data["text"], voice=call.data["voice"], speed=call.data["speed"],
            pitch=call.data["pitch"], wait=call.data["wait"],
        )

    async def handle_play(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.play(call.data["url"], wait=call.data["wait"])

    async def handle_ears(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.ears(call.data["left"], call.data["right"], call.data["direction"])

    async def handle_led(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.led(
            call.data["led"], (call.data["red"], call.data["green"], call.data["blue"])
        )

    async def handle_choreography(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.choreography(call.data["spec"])

    async def handle_program(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.program(call.data["text"])

    async def handle_ambient(call: ServiceCall) -> None:
        if len(call.data["services"]) != len(call.data["values"]):
            raise vol.Invalid("services et values doivent avoir la même longueur")
        await _coordinator(hass, call).client.ambient(call.data["services"], call.data["values"])

    async def handle_raw(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.raw(call.data["packet_b64"])

    async def handle_recording(call: ServiceCall) -> None:
        filename = Path(call.data["filename"]).name
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", filename):
            raise vol.Invalid("Nom de fichier invalide")
        content = await _coordinator(hass, call).client.last_recording(call.data["format"])
        target = Path(hass.config.path("www", filename))
        await hass.async_add_executor_job(target.parent.mkdir, 0o755, True, True)
        await hass.async_add_executor_job(target.write_bytes, content)

    async def handle_adoption(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.adoption_action(
            call.data["action"], call.data["mac"], call.data.get("fingerprint")
        )

    async def handle_ota(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.stage_ota(
            call.data["path"], call.data["name"], call.data["trigger"]
        )

    async def handle_bottom_led(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.bottom_led(call.data["value"])

    async def handle_ear_wiggle(call: ServiceCall) -> None:
        await _coordinator(hass, call).client.ear_wiggle(call.data["left"], call.data["right"])

    services = {
        "say": (handle_speak, SPEAK_SCHEMA),
        "speak": (handle_speak, SPEAK_SCHEMA),
        "play": (handle_play, PLAY_SCHEMA),
        "move_ears": (handle_ears, EARS_SCHEMA),
        "set_led": (handle_led, LED_SCHEMA),
        "send_choreography": (handle_choreography, CHOREOGRAPHY_SCHEMA),
        "send_program": (handle_program, vol.Schema({vol.Required("text"): cv.string})),
        "send_ambient": (handle_ambient, AMBIENT_SCHEMA),
        "send_raw_packet": (handle_raw, RAW_SCHEMA),
        "download_recording": (handle_recording, RECORDING_SCHEMA),
        "adoption_action": (handle_adoption, ADOPTION_SCHEMA),
        "stage_ota": (handle_ota, OTA_SCHEMA),
        "set_bottom_led": (handle_bottom_led, vol.Schema({vol.Required("value"): vol.Coerce(int)})),
        "wiggle_ears": (handle_ear_wiggle, vol.Schema({
            vol.Optional("left", default=1): vol.Coerce(int),
            vol.Optional("right", default=1): vol.Coerce(int),
        })),
    }
    for name, (handler, schema) in services.items():
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(
                DOMAIN,
                name,
                handler,
                schema=schema.extend({vol.Optional("device_id"): cv.string}),
            )
