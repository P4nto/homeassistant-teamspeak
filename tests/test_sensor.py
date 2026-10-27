"""Tests for the Teamspeak 3 Server sensor."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teamspeak.const import DOMAIN
from custom_components.teamspeak.sensor import TeamspeakSensor

from .const import CLIENTS_RAW, SERVER_DATA

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
        clients_state = hass.states.get("sensor.test_server_clients_online")
        uptime_state = hass.states.get("sensor.test_server_uptime")

    assert state is not None
    assert state.state == "online"
    assert state.attributes["serverinfo"]["unique_identifier"] == "server-uuid"
    assert state.attributes["clients"] == CLIENTS_RAW
    assert state.attributes["channels"] == [{"channel_name": "Lobby"}]
    assert state.attributes["attribution"]

    assert clients_state is not None
    assert clients_state.state == "2"
    assert uptime_state is not None
    assert uptime_state.state == "3600"
    assert uptime_state.attributes["unit_of_measurement"] == "s"
    assert uptime_state.attributes["device_class"] == "duration"


def test_client_and_channel_attributes_are_not_recorded():
    """Test that large client and channel lists stay out of history."""
    assert TeamspeakSensor._unrecorded_attributes == frozenset({"clients", "channels"})
