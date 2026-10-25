"""Custom integration to integrate a TeamSpeak 3 Server with Home Assistant."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import TeamspeakConfigEntry, TeamspeakDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: TeamspeakConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    coordinator = TeamspeakDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TeamspeakConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator = entry.runtime_data
        await coordinator.async_shutdown()
        await coordinator.async_close()
    return unloaded
