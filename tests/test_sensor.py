"""Tests for the Teamspeak 3 Server sensor."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teamspeak.const import DOMAIN
from custom_components.teamspeak.sensor import TeamspeakSensor, _format_uptime

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
    assert uptime_state.state == "1 hour"
    assert "unit_of_measurement" not in uptime_state.attributes
    assert "device_class" not in uptime_state.attributes


@pytest.mark.parametrize(
    ("seconds", "language", "expected"),
    [
        (0, "de", "0 Minuten"),
        (59, "de", "0 Minuten"),
        (60, "de", "1 Minute"),
        (3600, "en", "1 hour"),
        (3660, "en", "1 hour, 1 minute"),
        (90061, "de", "1 Tag, 1 Stunde, 1 Minute"),
        (172800, "de", "2 Tage"),
        (183240, "en", "2 days, 2 hours, 54 minutes"),
    ],
)
def test_format_uptime(seconds, language, expected):
    """Test formatting uptime in days, hours and minutes."""
    assert _format_uptime(seconds, language) == expected


def test_client_and_channel_attributes_are_not_recorded():
    """Test that large client and channel lists stay out of history."""
    assert TeamspeakSensor._unrecorded_attributes == frozenset({"clients", "channels"})
