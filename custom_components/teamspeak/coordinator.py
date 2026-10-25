"""Data update coordinator for the Teamspeak 3 Server integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    TeamspeakApiClient,
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientError,
    TeamspeakData,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__package__)

SCAN_INTERVAL = timedelta(seconds=30)


class TeamspeakDataUpdateCoordinator(DataUpdateCoordinator[TeamspeakData]):
    """Fetch data from a TeamSpeak 3 Server."""

    config_entry: TeamspeakConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: TeamspeakConfigEntry) -> None:
        """Initialize the coordinator."""
        self.api = TeamspeakApiClient(
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> TeamspeakData:
        """Fetch data from the TeamSpeak server in the executor."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except TeamspeakApiClientAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                "The TeamSpeak ServerQuery credentials are invalid"
            ) from err
        except TeamspeakApiClientError as err:
            raise UpdateFailed(str(err)) from err

    async def async_close(self) -> None:
        """Close the API client without blocking the event loop."""
        await self.hass.async_add_executor_job(self.api.close)


type TeamspeakConfigEntry = ConfigEntry[TeamspeakDataUpdateCoordinator]
