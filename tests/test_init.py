"""Tests for setting up and unloading the integration."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.const import CONF_PORT
from pytest_homeassistant.common import MockConfigEntry

from custom_components.teamspeak.api import TeamspeakApiClientCommunicationError
from custom_components.teamspeak.const import DOMAIN

from .const import CONFIG_DATA, CONFIG_DATA_WITHOUT_PORT, SERVER_DATA

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
        status = hass.states.get("sensor.test_server_status")
        assert status is not None
        assert status.state == "online"
        assert status.attributes["serverinfo"]["name"] == "Test Server"

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10011
    )
    client_class.return_value.close.assert_called_once()


async def test_setup_uses_configured_port(hass):
    """Test that the configured ServerQuery port is used."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**CONFIG_DATA, CONF_PORT: 10012},
    )
    entry.add_to_hass(hass)

    with patch(COORDINATOR_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10012
    )


async def test_setup_defaults_port_for_existing_entries(hass):
    """Test that entries without a stored port use the default port."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA_WITHOUT_PORT)
    entry.add_to_hass(hass)

    with patch(COORDINATOR_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10011
    )


async def test_setup_closes_session_when_platform_setup_fails(hass):
    """A failed platform setup must not leak the ServerQuery session."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with (
        patch(COORDINATOR_CLIENT) as client_class,
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            side_effect=RuntimeError("platform failed"),
        ),
    ):
        client_class.return_value.get_data.return_value = SERVER_DATA
        assert not await hass.config_entries.async_setup(entry.entry_id)
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
