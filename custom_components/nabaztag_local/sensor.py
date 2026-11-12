"""Diagnostic sensors."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NabaztagCount(coordinator),
        NabaztagAddress(coordinator),
        NabaztagMicPackets(coordinator),
        NabaztagLastRecording(coordinator),
    ])


class NabaztagCount(NabaztagEntity, SensorEntity):
    _attr_name = "Nombre de lapins connectés"
    _attr_icon = "mdi:rabbit"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "connected_count")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.connected_rabbits)


class NabaztagAddress(NabaztagEntity, SensorEntity):
    _attr_name = "Adresse du serveur"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "server_address")

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("server_address")


class NabaztagMicPackets(NabaztagEntity, SensorEntity):
    _attr_name = "Paquets microphone"
    _attr_icon = "mdi:microphone"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "mic_packets")

    @property
    def native_value(self) -> int:
        return int((self.coordinator.data or {}).get("mic_stream", {}).get("packets", 0))

    @property
    def extra_state_attributes(self):
        return (self.coordinator.data or {}).get("mic_stream", {})


class NabaztagLastRecording(NabaztagEntity, SensorEntity):
    _attr_name = "Dernier enregistrement vocal"
    _attr_icon = "mdi:waveform"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_recording")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("last_recording", {}).get("ts")

    @property
    def extra_state_attributes(self):
        data = (self.coordinator.data or {}).get("last_recording", {})
        return {
            **data,
            "pcm_download_url": f"{self.coordinator.client.base_url}/api/lastrecording?format=pcm",
            "adpcm_download_url": f"{self.coordinator.client.base_url}/api/lastrecording?format=adpcm",
        }
