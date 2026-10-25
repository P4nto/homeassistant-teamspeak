"""Tests for the Teamspeak 3 Server sensor."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teamspeak.const import DOMAIN

from .const import SERVER_DATA

COORDINATOR_CLIENT = "custom_components.teamspeak.coordinator.TeamspeakApiClient"


async def test_sensor_state_and_attributes(hass):
    """Test the sensor state and attributes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "127.0.0.1",
            CONF_USERNAME: "serveradmin",
            CONF_PASSWORD: "secret",
        },
    )
    entry.add_to_hass(hass)

    with patch(COORDINATOR_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.test_server")

    assert state is not None
    assert state.state == "online"
    assert state.attributes["serverinfo"]["unique_identifier"] == "server-uuid"
    assert state.attributes["clients"] == [{"client_nickname": "Alice"}]
    assert state.attributes["channels"] == [{"channel_name": "Lobby"}]
    assert state.attributes["attribution"]
