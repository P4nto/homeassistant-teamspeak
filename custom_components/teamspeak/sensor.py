"""Sensor platform for the Teamspeak 3 Server integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ICON
from .coordinator import TeamspeakConfigEntry
from .entity import TeamspeakEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeamspeakConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities([TeamspeakSensor(entry.runtime_data)])


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
