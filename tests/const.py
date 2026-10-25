"""Shared test data for the Teamspeak 3 Server integration."""

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.teamspeak.api import TeamspeakData

CONFIG_DATA = {
    CONF_HOST: "127.0.0.1",
    CONF_USERNAME: "serveradmin",
    CONF_PASSWORD: "secret",
}

SERVER_INFO_RAW = {
    "virtualserver_unique_identifier": "server-uuid",
    "virtualserver_status": "online",
    "virtualserver_name": "Test Server",
    "virtualserver_platform": "Linux",
    "virtualserver_port": "9987",
    "virtualserver_version": "3.13.7 Linux",
    "virtualserver_maxclients": "32",
    "virtualserver_reserved_slots": "0",
    "virtualserver_clientsonline": "3",
    "virtualserver_client_connections": "2",
    "virtualserver_channelsonline": "4",
    "virtualserver_created": "1700000000",
    "virtualserver_uptime": "3600",
}

SERVER_DATA: TeamspeakData = {
    "clients": [{"client_nickname": "Alice"}],
    "serverinfo": {
        "unique_identifier": "server-uuid",
        "status": "online",
        "name": "Test Server",
        "platform": "Linux",
        "port": 9987,
        "version": "3.13.7",
        "maxclients": 32,
        "reservedslots": 0,
        "clientsonline": 3,
        "clientconnections": 2,
        "channelsonline": 4,
        "created": 1700000000,
        "uptime": 3600,
    },
    "channels": [{"channel_name": "Lobby"}],
}
