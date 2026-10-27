"""Base entity for the Teamspeak 3 Server integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER
from .coordinator import TeamspeakDataUpdateCoordinator


class TeamspeakEntity(CoordinatorEntity[TeamspeakDataUpdateCoordinator]):
    """Base entity for a TeamSpeak 3 Server."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TeamspeakDataUpdateCoordinator,
        unique_id_suffix: str | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        unique_id = coordinator.config_entry.entry_id
        if unique_id_suffix:
            unique_id = f"{unique_id}_{unique_id_suffix}"
        self._attr_unique_id = unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        serverinfo = self.coordinator.data["serverinfo"]
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=serverinfo.get("name")
            or self.coordinator.config_entry.data[CONF_HOST],
            manufacturer=MANUFACTURER,
            model="TeamSpeak 3 Server",
            sw_version=serverinfo.get("version"),
            entry_type=DeviceEntryType.SERVICE,
        )
