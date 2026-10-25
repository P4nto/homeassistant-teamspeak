"""Tests for the Teamspeak 3 Server config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teamspeak.api import (
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientCommunicationError,
)
from custom_components.teamspeak.const import DOMAIN

from .const import CONFIG_DATA, SERVER_DATA

CONFIG_FLOW_CLIENT = "custom_components.teamspeak.config_flow.TeamspeakApiClient"
COORDINATOR_CLIENT = "custom_components.teamspeak.coordinator.TeamspeakApiClient"


async def test_user_flow(hass):
    """Test a successful user flow."""
    with (
        patch(CONFIG_FLOW_CLIENT) as client_class,
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
    ):
        client_class.return_value.get_data.return_value = SERVER_DATA
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Server"
    assert result["data"] == CONFIG_DATA
    assert result["result"].unique_id == "server-uuid"
    client_class.return_value.close.assert_called_once()


async def test_user_flow_authentication_error(hass):
    """Test invalid credentials."""
    with patch(CONFIG_FLOW_CLIENT) as client_class:
        client_class.return_value.get_data.side_effect = (
            TeamspeakApiClientAuthenticationError
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_connection_error(hass):
    """Test a connection error."""
    with patch(CONFIG_FLOW_CLIENT) as client_class:
        client_class.return_value.get_data.side_effect = (
            TeamspeakApiClientCommunicationError
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_already_configured(hass):
    """Test that a known server is rejected."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=CONFIG_DATA,
        unique_id="server-uuid",
    )
    entry.add_to_hass(hass)

    with patch(CONFIG_FLOW_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow(hass):
    """Test re-authentication and unique ID migration."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with (
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
        patch(CONFIG_FLOW_CLIENT) as flow_client_class,
    ):
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        flow_client_class.return_value.get_data.return_value = SERVER_DATA

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
        )
        assert result["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "new-user",
                CONF_PASSWORD: "new-password",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.unique_id == "server-uuid"
    assert entry.data[CONF_USERNAME] == "new-user"
    assert entry.data[CONF_PASSWORD] == "new-password"


async def test_reauth_flow_aborts_on_unique_id_collision(hass):
    """Test that reauth cannot steal another entry's unique ID."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=CONFIG_DATA,
        unique_id="server-uuid",
    )
    entry.add_to_hass(hass)
    reauth_entry = MockConfigEntry(
        domain=DOMAIN,
        data=CONFIG_DATA,
        unique_id="other-uuid",
    )
    reauth_entry.add_to_hass(hass)

    with patch(CONFIG_FLOW_CLIENT) as client_class:
        client_class.return_value.get_data.return_value = SERVER_DATA

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": reauth_entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "new-user",
                CONF_PASSWORD: "new-password",
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_flow_invalid_credentials(hass):
    """Test a failed re-authentication."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with (
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
        patch(CONFIG_FLOW_CLIENT) as flow_client_class,
    ):
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        flow_client_class.return_value.get_data.side_effect = (
            TeamspeakApiClientAuthenticationError
        )

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "wrong-user",
                CONF_PASSWORD: "wrong-password",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_reauth_flow_connection_error(hass):
    """Test a connection error during re-authentication."""
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG_DATA)
    entry.add_to_hass(hass)

    with (
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
        patch(CONFIG_FLOW_CLIENT) as flow_client_class,
    ):
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        flow_client_class.return_value.get_data.side_effect = (
            TeamspeakApiClientCommunicationError
        )

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_REAUTH,
                "entry_id": entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "new-user",
                CONF_PASSWORD: "new-password",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_host_and_password(hass):
    """Test that the form contains the expected fields."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    schema = result["data_schema"].schema
    assert CONF_HOST in schema
    assert CONF_USERNAME in schema
    assert CONF_PASSWORD in schema
