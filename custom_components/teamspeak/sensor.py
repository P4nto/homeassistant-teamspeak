"""Sensor platform for the Teamspeak 3 Server integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import ICON
from .coordinator import TeamspeakConfigEntry, TeamspeakDataUpdateCoordinator
from .entity import TeamspeakEntity

PARALLEL_UPDATES = 0

_UPTIME_LABELS = {
    "de": (
        ("Tag", "Tage"),
        ("Stunde", "Stunden"),
        ("Minute", "Minuten"),
    ),
    "en": (
        ("day", "days"),
        ("hour", "hours"),
        ("minute", "minutes"),
    ),
}


def _format_uptime(seconds: int, language: str) -> str:
    """Format uptime seconds as days, hours and minutes."""
    days, remainder = divmod(max(seconds, 0), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    labels = _UPTIME_LABELS["de" if language.lower().startswith("de") else "en"]

    parts = [
        f"{value} {singular if value == 1 else plural}"
        for value, (singular, plural) in zip(
            (days, hours, minutes), labels, strict=True
        )
        if value
    ]
    if not parts:
        return f"0 {labels[2][1]}"
    return ", ".join(parts)


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

    def __init__(self, coordinator: TeamspeakDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "uptime")

    @property
    def native_value(self) -> str | None:
        """Return the server uptime in days, hours and minutes."""
        uptime = self.coordinator.data["serverinfo"].get("uptime")
        if uptime is None:
            return None
        return _format_uptime(uptime, self.hass.config.language)
