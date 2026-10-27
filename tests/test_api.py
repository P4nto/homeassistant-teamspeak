"""Tests for the TeamSpeak API client."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import ts3

from custom_components.teamspeak.api import (
    TeamspeakApiClient,
    TeamspeakApiClientAuthenticationError,
    TeamspeakApiClientCommunicationError,
)

from .const import CLIENTS_RAW, SERVER_INFO_RAW

TS3_CONNECTION = "custom_components.teamspeak.api.ts3.query.TS3Connection"


def _session() -> MagicMock:
    session = MagicMock()
    session.serverinfo.return_value.parsed = [SERVER_INFO_RAW]
    session.clientlist.return_value.parsed = CLIENTS_RAW
    session.channellist.return_value.parsed = [{"channel_name": "Lobby"}]
    return session


def _query_error(error_id: str) -> ts3.query.TS3QueryError:
    response = SimpleNamespace(error={"id": error_id, "msg": "ServerQuery error"})
    return ts3.query.TS3QueryError(response)


def test_get_data() -> None:
    """Test fetching and normalizing server data."""
    session = _session()
    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        data = client.get_data()

    session.open.assert_called_once_with("127.0.0.1", 10011, timeout=10)
    session.login.assert_called_once_with(
        client_login_name="serveradmin",
        client_login_password="secret",
    )
    session.use.assert_called_once_with(sid=1)
    assert data["serverinfo"]["unique_identifier"] == "server-uuid"
    assert data["serverinfo"]["port"] == 9987
    assert data["serverinfo"]["version"] == "3.13.7"
    assert data["serverinfo"]["maxclients"] == 32
    assert data["serverinfo"]["clientsonline"] == 3
    assert data["serverinfo"]["active_clients"] == 2
    assert data["clients"] == CLIENTS_RAW
    assert data["channels"] == [{"channel_name": "Lobby"}]


def test_get_data_without_version() -> None:
    """Test that a missing version does not break normalization."""
    session = _session()
    serverinfo = dict(SERVER_INFO_RAW)
    serverinfo.pop("virtualserver_version")
    session.serverinfo.return_value.parsed = [serverinfo]

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        data = client.get_data()

    assert data["serverinfo"]["version"] is None


def test_active_clients_ignores_query_clients() -> None:
    """Test that query clients are not counted as active clients."""
    session = _session()
    session.clientlist.return_value.parsed = [
        {"client_nickname": "serveradmin", "client_type": "1"},
        {"client_nickname": "Alice"},
    ]

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        data = client.get_data()

    assert data["serverinfo"]["active_clients"] == 1


def test_authentication_error() -> None:
    """Test rejected credentials."""
    session = _session()
    session.login.side_effect = _query_error("520")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "wrong")
        with pytest.raises(TeamspeakApiClientAuthenticationError):
            client.get_data()

    session.close.assert_called_once()


def test_connection_error() -> None:
    """Test an unreachable server."""
    session = _session()
    session.open.side_effect = TimeoutError

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError):
            client.get_data()

    session.close.assert_called_once()


def test_query_error() -> None:
    """Test a non-authentication ServerQuery error."""
    session = _session()
    session.serverinfo.side_effect = _query_error("1793")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError):
            client.get_data()

    session.quit.assert_called_once()


def test_unexpected_login_error_closes_session() -> None:
    """Test that an unexpected login error closes the new session."""
    session = _session()
    session.login.side_effect = RuntimeError("unexpected")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError):
            client.get_data()

    session.close.assert_called_once()


def test_unexpected_data_error_closes_session() -> None:
    """Test that an unexpected query error closes the existing session."""
    session = _session()
    session.serverinfo.side_effect = RuntimeError("unexpected")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError):
            client.get_data()

    session.quit.assert_called_once()


def test_close() -> None:
    """Test closing the session."""
    session = _session()
    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        client.get_data()
        client.close()
        client.close()

    session.quit.assert_called_once()
