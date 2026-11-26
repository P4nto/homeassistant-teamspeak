"""Tests for the Teamspeak data update coordinator."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant.common import MockConfigEntry

from custom_components.teamspeak.api import (
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientCommunicationError,
)
from custom_components.teamspeak.const import DOMAIN
from custom_components.teamspeak.coordinator import TeamspeakDataUpdateCoordinator

from .const import CONFIG_DATA, SERVER_DATA


async def test_coordinator_auth_error_raises_config_entry_auth_failed(hass) -> None:
    """Invalid credentials must trigger reauthentication, not a plain update failure."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    coordinator = TeamspeakDataUpdateCoordinator(hass, entry)

    with (
        patch.object(
            coordinator.api,
            "get_data",
            side_effect=TeamspeakApiClientAuthenticationError("rejected"),
        ),
        pytest.raises(ConfigEntryAuthFailed),
    ):
        await coordinator._async_update_data()


async def test_coordinator_communication_error_raises_update_failed(hass) -> None:
    """ServerQuery failures must surface as UpdateFailed with the original message."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    coordinator = TeamspeakDataUpdateCoordinator(hass, entry)

    with (
        patch.object(
            coordinator.api,
            "get_data",
            side_effect=TeamspeakApiClientCommunicationError("server unreachable"),
        ),
        pytest.raises(UpdateFailed, match="server unreachable"),
    ):
        await coordinator._async_update_data()


async def test_coordinator_returns_data(hass) -> None:
    """The coordinator passes the normalized API data through unchanged."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)
    coordinator = TeamspeakDataUpdateCoordinator(hass, entry)

    with patch.object(coordinator.api, "get_data", return_value=SERVER_DATA):
        assert await coordinator._async_update_data() == SERVER_DATA
