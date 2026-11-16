"""Tests for the Teamspeak 3 Server config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant.common import MockConfigEntry

from custom_components.teamspeak.api import (
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientCommunicationError,
)
from custom_components.teamspeak.const import DOMAIN

from .const import (
    CONFIG_DATA,
    CONFIG_DATA_WITHOUT_PORT,
    SERVER_DATA,
    SERVER_DATA_WITHOUT_UNIQUE_ID,
)

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
    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10011
    )
    client_class.return_value.close.assert_called_once()


async def test_user_flow_custom_port(hass):
    """Test that a custom ServerQuery port is stored and used."""
    with (
        patch(CONFIG_FLOW_CLIENT) as client_class,
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
    ):
        client_class.return_value.get_data.return_value = SERVER_DATA
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {**CONFIG_DATA, CONF_PORT: "10012"}
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PORT] == 10012
    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10012
    )


async def test_user_flow_defaults_port(hass):
    """Test that entries without a port use the ServerQuery default."""
    with (
        patch(CONFIG_FLOW_CLIENT) as client_class,
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
    ):
        client_class.return_value.get_data.return_value = SERVER_DATA
        coordinator_client_class.return_value.get_data.return_value = SERVER_DATA
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA_WITHOUT_PORT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PORT] == 10011
    client_class.assert_called_once_with(
        "127.0.0.1", "serveradmin", "secret", port=10011
    )


async def test_user_flow_without_unique_identifier_uses_host(hass):
    """Test setup of a server that returns no unique identifier."""
    with (
        patch(CONFIG_FLOW_CLIENT) as client_class,
        patch(COORDINATOR_CLIENT) as coordinator_client_class,
    ):
        client_class.return_value.get_data.return_value = SERVER_DATA_WITHOUT_UNIQUE_ID
        coordinator_client_class.return_value.get_data.return_value = (
            SERVER_DATA_WITHOUT_UNIQUE_ID
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_DATA
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "127.0.0.1"


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
    flow_client_class.assert_called_once_with(
        "127.0.0.1", "new-user", "new-password", port=10011
    )


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
    assert CONF_PORT in schema
    assert CONF_USERNAME in schema
    assert CONF_PASSWORD in schema
