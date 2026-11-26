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
    _as_int,
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


class _BrokenErrorResponse:
    """A response whose error field fails while being parsed."""

    @property
    def error(self) -> dict[str, str]:
        raise ValueError("malformed error")


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


@pytest.mark.parametrize(
    "response", [SimpleNamespace(), _BrokenErrorResponse()], ids=["missing", "parser"]
)
def test_malformed_query_error_becomes_communication_error(response) -> None:
    """A malformed ServerQuery error must not escape from the error handler."""
    session = _session()
    session.login.side_effect = ts3.query.TS3QueryError(response)

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "wrong")
        with pytest.raises(
            TeamspeakApiClientCommunicationError, match="malformed ServerQuery error"
        ):
            client.get_data()

    session.close.assert_called_once()


def test_get_data_with_non_string_version() -> None:
    """A non-string version value must not break normalization."""
    session = _session()
    serverinfo = dict(SERVER_INFO_RAW)
    serverinfo["virtualserver_version"] = 3137
    session.serverinfo.return_value.parsed = [serverinfo]

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        data = client.get_data()

    assert data["serverinfo"]["version"] == "3137"


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


def test_as_int_handles_none_and_invalid_values() -> None:
    """Test that malformed ServerQuery numbers become None."""
    assert _as_int(None) is None
    assert _as_int("42") == 42
    assert _as_int("not-a-number") is None


def test_login_query_error_closes_session() -> None:
    """Test that a non-auth login error closes the new session."""
    session = _session()
    session.login.side_effect = _query_error("1793")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError):
            client.get_data()

    session.close.assert_called_once()


def test_use_auth_error_closes_session() -> None:
    """Test that an auth error after connecting drops the ServerQuery session."""
    session = _session()
    session.use.side_effect = _query_error("520")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientAuthenticationError):
            client.get_data()

    session.quit.assert_called_once()
    assert client._session is None


def test_close_swallows_quit_error() -> None:
    """Test that a failing quit does not break unload."""
    session = _session()
    session.quit.side_effect = RuntimeError("already gone")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        client.get_data()
        client.close()

    assert client._session is None


def test_login_error_survives_failing_session_close() -> None:
    """Test that a broken close does not mask the original login error."""
    session = _session()
    session.login.side_effect = _query_error("1793")
    session.close.side_effect = RuntimeError("already gone")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(TeamspeakApiClientCommunicationError, match="1793"):
            client.get_data()


def test_invalid_serverinfo_closes_session() -> None:
    """Test that malformed ServerQuery data closes the session."""
    session = _session()
    session.serverinfo.side_effect = ValueError("bad payload")

    with patch(TS3_CONNECTION, return_value=session):
        client = TeamspeakApiClient("127.0.0.1", "serveradmin", "secret")
        with pytest.raises(
            TeamspeakApiClientCommunicationError, match="Could not read data"
        ):
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
