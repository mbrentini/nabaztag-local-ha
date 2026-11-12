"""Diagnostic sensors."""

from datetime import UTC, datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
        NabaztagAdoption(coordinator),
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
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:waveform"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_recording")

    @property
    def native_value(self):
        timestamp = (self.coordinator.data or {}).get("last_recording", {}).get("ts", 0)
        return datetime.fromtimestamp(timestamp, UTC) if timestamp else None

    @property
    def extra_state_attributes(self):
        data = (self.coordinator.data or {}).get("last_recording", {})
        return {
            **data,
            "pcm_download_url": f"{self.coordinator.client.base_url}/api/lastrecording?format=pcm",
            "adpcm_download_url": f"{self.coordinator.client.base_url}/api/lastrecording?format=adpcm",
        }


class NabaztagAdoption(NabaztagEntity, SensorEntity):
    """Expose pending / confirmed Naboot adoption keys."""

    _attr_name = "Clés d'adoption"
    _attr_icon = "mdi:shield-key"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "adoption")

    @property
    def native_value(self) -> int:
        return len((self.coordinator.data or {}).get("adoption", {}).get("keys", []))

    @property
    def extra_state_attributes(self):
        return (self.coordinator.data or {}).get("adoption", {})
