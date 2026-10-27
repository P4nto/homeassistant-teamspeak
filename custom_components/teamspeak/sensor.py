"""Sensor platform for the Teamspeak 3 Server integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ICON
from .coordinator import TeamspeakConfigEntry, TeamspeakDataUpdateCoordinator
from .entity import TeamspeakEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeamspeakConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            TeamspeakSensor(coordinator),
            TeamspeakClientsOnlineSensor(coordinator),
            TeamspeakUptimeSensor(coordinator),
        ]
    )


class TeamspeakSensor(TeamspeakEntity, SensorEntity):
    """Sensor showing the state of a TeamSpeak 3 Server."""

    _attr_icon = ICON
    _unrecorded_attributes = frozenset({"clients", "channels"})

    @property
    def native_value(self) -> str | None:
        """Return the server status."""
        return self.coordinator.data["serverinfo"].get("status")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the server details."""
        return dict(self.coordinator.data)


class TeamspeakClientsOnlineSensor(TeamspeakEntity, SensorEntity):
    """Sensor showing the number of active voice clients."""

    _attr_translation_key = "clients_online"
    _attr_icon = "mdi:account-multiple"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: TeamspeakDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "clients_online")

    @property
    def native_value(self) -> int | None:
        """Return the number of active clients."""
        return self.coordinator.data["serverinfo"].get("active_clients")


class TeamspeakUptimeSensor(TeamspeakEntity, SensorEntity):
    """Sensor showing the server uptime."""

    _attr_translation_key = "uptime"
    _attr_icon = "mdi:clock-outline"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: TeamspeakDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "uptime")

    @property
    def native_value(self) -> int | None:
        """Return the server uptime in seconds."""
        return self.coordinator.data["serverinfo"].get("uptime")
