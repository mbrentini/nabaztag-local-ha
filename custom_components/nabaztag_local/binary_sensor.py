"""Binary sensors."""

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .entity import NabaztagEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NabaztagOnline(coordinator)])


class NabaztagOnline(NabaztagEntity, BinarySensorEntity):
    _attr_name = "Lapin connecté"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:rabbit"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "online")

    @property
    def is_on(self) -> bool:
        rabbit = self.coordinator.rabbit
        return bool(rabbit.get("alive", rabbit.get("bound", False)))
