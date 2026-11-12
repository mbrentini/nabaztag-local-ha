"""Native Home Assistant event entities for rabbit physical interactions."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NabaztagEntity
from .identity import event_for_rabbit

EVENT_TYPES = {
    "button": ["click", "double_click"],
    "rfid": ["scanned"],
    "ears": ["moved"],
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagInput(coordinator, kind) for kind in EVENT_TYPES])


class NabaztagInput(NabaztagEntity, EventEntity):
    """Capture an event without triggering for a different configured rabbit."""

    def __init__(self, coordinator, kind: str) -> None:
        super().__init__(coordinator, f"event_{kind}")
        self._kind = kind
        self._attr_event_types = EVENT_TYPES[kind]
        self._attr_name = {
            "button": "Bouton physique",
            "rfid": "Tag RFID",
            "ears": "Oreilles déplacées manuellement",
        }[kind]

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self.hass.bus.async_listen("nabaztag_event", self._on_event))

    def _on_event(self, event: Event) -> None:
        data = event.data
        if data.get("type") != self._kind:
            return
        if not event_for_rabbit(
            data, self.coordinator.client.mac, len(self.hass.data.get(DOMAIN, {}))
        ):
            return
        if self._kind == "button":
            event_type = data.get("action", "")
        elif self._kind == "rfid":
            event_type = "scanned"
        else:
            event_type = "moved"
        if event_type not in self._attr_event_types:
            return
        self._trigger_event(event_type, dict(data))
        self.async_write_ha_state()
