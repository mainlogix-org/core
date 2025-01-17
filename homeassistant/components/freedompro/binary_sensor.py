"""Support for Freedompro binary_sensor."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

DEVICE_CLASS_MAP = {
    "smokeSensor": BinarySensorDeviceClass.SMOKE,
    "occupancySensor": BinarySensorDeviceClass.OCCUPANCY,
    "motionSensor": BinarySensorDeviceClass.MOTION,
    "contactSensor": BinarySensorDeviceClass.OPENING,
}

DEVICE_KEY_MAP = {
    "smokeSensor": "smokeDetected",
    "occupancySensor": "occupancyDetected",
    "motionSensor": "motionDetected",
    "contactSensor": "contactSensorState",
}

SUPPORTED_SENSORS = {"smokeSensor", "occupancySensor", "motionSensor", "contactSensor"}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Freedompro binary_sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        Device(device, coordinator)
        for device in coordinator.data
        if device["type"] in SUPPORTED_SENSORS
    )


class Device(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Freedompro binary_sensor."""

    def __init__(self, device, coordinator):
        """Initialize the Freedompro binary_sensor."""
        super().__init__(coordinator)
        self._attr_name = device["name"]
        self._attr_unique_id = device["uid"]
        self._type = device["type"]
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, self.unique_id),
            },
            manufacturer="Freedompro",
            model=device["type"],
            name=self.name,
        )
        self._attr_device_class = DEVICE_CLASS_MAP[device["type"]]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = next(
            (
                device
                for device in self.coordinator.data
                if device["uid"] == self.unique_id
            ),
            None,
        )
        if device is not None and "state" in device:
            state = device["state"]
            self._attr_is_on = state[DEVICE_KEY_MAP[self._type]]
        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
