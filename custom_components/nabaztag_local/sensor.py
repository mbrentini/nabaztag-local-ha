"""Diagnostic sensors and the latest physical input data."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NabaztagCount(coordinator),
        NabaztagAddress(coordinator),
        NabaztagMicPackets(coordinator),
        NabaztagLastRecording(coordinator),
        NabaztagAdoption(coordinator),
        NabaztagResource(coordinator),
        NabaztagUptime(coordinator),
        NabaztagLastRx(coordinator),
        NabaztagLastRfid(coordinator),
        NabaztagLastButton(coordinator),
        NabaztagLastEars(coordinator),
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
        return dict((self.coordinator.data or {}).get("last_recording", {}))


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


class NabaztagResource(NabaztagEntity, SensorEntity):
    _attr_name = "État XMPP du lapin"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "rabbit_resource")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.rabbit.get("resource")


class NabaztagUptime(NabaztagEntity, SensorEntity):
    _attr_name = "Durée de connexion du lapin"
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "rabbit_uptime")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.rabbit.get("uptime")


class NabaztagLastRx(NabaztagEntity, SensorEntity):
    _attr_name = "Dernière réception XMPP"
    _attr_icon = "mdi:clock-outline"
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "rabbit_last_rx")

    @property
    def native_value(self) -> float | None:
        ago = self.coordinator.rabbit.get("last_rx_ago")
        return round(float(ago), 1) if ago is not None else None


class NabaztagLastRfid(NabaztagEntity, SensorEntity):
    _attr_name = "Dernier tag RFID"
    _attr_icon = "mdi:nfc-variant"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_rfid")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.last_rfid


class NabaztagLastButton(NabaztagEntity, SensorEntity):
    _attr_name = "Dernier appui bouton"
    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_button")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.last_button


class NabaztagLastEars(NabaztagEntity, SensorEntity):
    _attr_name = "Dernier déplacement manuel des oreilles"
    _attr_icon = "mdi:ear-hearing"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "last_ears")

    @property
    def native_value(self) -> str | None:
        ears = self.coordinator.last_ears
        return f"{ears['left']} / {ears['right']}" if ears else None

    @property
    def extra_state_attributes(self) -> dict:
        return dict(self.coordinator.last_ears or {})
