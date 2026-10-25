"""API client for a TeamSpeak 3 Server."""

from __future__ import annotations

import logging
from typing import Any, TypedDict

import ts3

_LOGGER = logging.getLogger(__package__)

PORT = 10011
TIMEOUT = 10
VIRTUAL_SERVER_ID = 1

_AUTH_ERROR_IDS = {"520", "527"}


class TeamspeakApiClientError(Exception):
    """Base exception for the TeamSpeak API client."""


class TeamspeakApiClientAuthenticationError(TeamspeakApiClientError):
    """Raised when the ServerQuery credentials are rejected."""


class TeamspeakApiClientCommunicationError(TeamspeakApiClientError):
    """Raised when the TeamSpeak server cannot be reached or queried."""


class TeamspeakServerInfo(TypedDict):
    """Normalized server information."""

    unique_identifier: str | None
    status: str | None
    name: str | None
    platform: str | None
    port: int | None
    version: str | None
    maxclients: int | None
    reservedslots: int | None
    clientsonline: int | None
    clientconnections: int | None
    channelsonline: int | None
    created: int | None
    uptime: int | None


class TeamspeakData(TypedDict):
    """Data returned by the TeamSpeak API client."""

    clients: list[dict[str, str]]
    serverinfo: TeamspeakServerInfo
    channels: list[dict[str, str]]


def _as_int(value: str | None) -> int | None:
    """Convert a ServerQuery value to an integer."""
    if value is None:
        return None
    try:
        return int(value)
    except TypeError, ValueError:
        return None


def _is_auth_error(error: ts3.query.TS3QueryError) -> bool:
    """Return whether a ServerQuery error is an authentication error."""
    return str(error.resp.error.get("id")) in _AUTH_ERROR_IDS


class TeamspeakApiClient:
    """Client for the TeamSpeak 3 ServerQuery interface."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = PORT,
    ) -> None:
        """Initialize the API client."""
        self._host = host.strip()
        self._username = username
        self._password = password
        self._port = port
        self._session: ts3.query.TS3Connection | None = None

    def _open_session(self) -> ts3.query.TS3Connection:
        """Open and authenticate a ServerQuery session."""
        session = ts3.query.TS3Connection()
        try:
            session.open(self._host, self._port, timeout=TIMEOUT)
            session.login(
                client_login_name=self._username,
                client_login_password=self._password,
            )
        except ts3.query.TS3QueryError as err:
            session.close()
            if _is_auth_error(err):
                raise TeamspeakApiClientAuthenticationError(
                    "The TeamSpeak ServerQuery credentials were rejected"
                ) from err
            raise TeamspeakApiClientCommunicationError(
                f"TeamSpeak ServerQuery error: {err}"
            ) from err
        except (OSError, TimeoutError, ts3.query.TS3RecvError) as err:
            session.close()
            raise TeamspeakApiClientCommunicationError(
                f"Could not connect to the TeamSpeak server: {err}"
            ) from err

        self._session = session
        return session

    def get_data(self) -> TeamspeakData:
        """Fetch the current server state.

        This method performs blocking network I/O and must be called in an
        executor thread.
        """
        session = self._session or self._open_session()

        try:
            session.use(sid=VIRTUAL_SERVER_ID)
            serverinfo: dict[str, Any] = session.serverinfo().parsed[0]
            clients = session.clientlist().parsed or []
            channels = session.channellist().parsed or []
        except ts3.query.TS3QueryError as err:
            self.close()
            if _is_auth_error(err):
                raise TeamspeakApiClientAuthenticationError(
                    "The TeamSpeak ServerQuery credentials were rejected"
                ) from err
            raise TeamspeakApiClientCommunicationError(
                f"TeamSpeak ServerQuery error: {err}"
            ) from err
        except (
            IndexError,
            KeyError,
            OSError,
            TimeoutError,
            TypeError,
            ValueError,
            ts3.query.TS3RecvError,
        ) as err:
            self.close()
            raise TeamspeakApiClientCommunicationError(
                f"Could not read data from the TeamSpeak server: {err}"
            ) from err

        version = (serverinfo.get("virtualserver_version") or "").split(maxsplit=1)

        return {
            "clients": list(clients),
            "serverinfo": {
                "unique_identifier": serverinfo.get("virtualserver_unique_identifier"),
                "status": serverinfo.get("virtualserver_status"),
                "name": serverinfo.get("virtualserver_name"),
                "platform": serverinfo.get("virtualserver_platform"),
                "port": _as_int(serverinfo.get("virtualserver_port")),
                "version": version[0] if version else None,
                "maxclients": _as_int(serverinfo.get("virtualserver_maxclients")),
                "reservedslots": _as_int(
                    serverinfo.get("virtualserver_reserved_slots")
                ),
                "clientsonline": _as_int(serverinfo.get("virtualserver_clientsonline")),
                "clientconnections": _as_int(
                    serverinfo.get("virtualserver_client_connections")
                ),
                "channelsonline": _as_int(
                    serverinfo.get("virtualserver_channelsonline")
                ),
                "created": _as_int(serverinfo.get("virtualserver_created")),
                "uptime": _as_int(serverinfo.get("virtualserver_uptime")),
            },
            "channels": list(channels),
        }

    def close(self) -> None:
        """Close the ServerQuery session."""
        if self._session is None:
            return

        session = self._session
        self._session = None
        try:
            session.quit()
        except Exception:
            _LOGGER.debug("Error while closing the TeamSpeak session", exc_info=True)
