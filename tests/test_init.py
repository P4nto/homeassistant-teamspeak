"""Tests for setting up and unloading the integration."""

from __future__ import annotations

from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teamspeak.api import TeamspeakApiClientCommunicationError
from custom_components.teamspeak.const import DOMAIN

from .const import CONFIG_DATA, SERVER_DATA

COORDINATOR_CLIENT = "custom_components.teamspeak.coordinator.TeamspeakApiClient"


async def test_setup_and_unload(hass):
    """Test setting up and unloading an entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with patch(COORDINATOR_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.runtime_data is not None
        states = hass.states.async_all("sensor")
        assert len(states) == 3
        status = hass.states.get("sensor.test_server")
        assert status is not None
        assert status.state == "online"
        assert status.attributes["serverinfo"]["name"] == "Test Server"

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    client_class.return_value.close.assert_called_once()


async def test_setup_connection_error(hass):
    """Test setup when the server cannot be reached."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with patch(COORDINATOR_CLIENT) as client_class:
        client_class.return_value.get_data.side_effect = (
            TeamspeakApiClientCommunicationError
        )

        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert not hass.states.async_all("sensor")
