[![Pipeline](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/badges/master/pipeline.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/pipelines)
[![Latest release](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/badges/release.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

_Component to integrate a [TeamSpeak 3 Server](https://www.teamspeak.com/en/) with Home Assistant._

_DISCLAIMER: This project is a private open source project and is not affiliated with TeamSpeak Systems, Inc._

**This component sets up the following platform.**

Platform | Description
-- | --
`sensor` | Shows the status, client count and uptime of the configured TeamSpeak 3 Server.

The integration creates a status sensor, a clients online sensor and an uptime
sensor. The clients online sensor counts only active voice clients, so
ServerQuery connections such as `serveradmin` are not included.

The status sensor exposes the following information as attributes.

### Serverinfo

Attribute | Description
-- | --
`unique_identifier` | Unique identifier of the TeamSpeak server
`status` | Online status
`name` | Server name
`platform` | Platform the server is hosted on
`port` | Voice port the server listens on
`version` | Installed TeamSpeak version
`maxclients` | Maximum number of simultaneous client connections
`reservedslots` | Number of reserved slots
`clientsonline` | Number of connections (including ServerQuery clients)
`active_clients` | Number of active voice clients (excluding ServerQuery clients)
`clientconnections` | Number of connected clients
`channelsonline` | Number of available channels
`created` | Unix timestamp of the server creation date
`uptime` | Seconds since the server started

The complete `clientlist` and `channellist` responses are available as the
`clients` and `channels` attributes. They are excluded from recorder history to
avoid storing client names and large lists.

## Installation

The GitLab repository is mirrored to GitHub for HACS. Add
`https://github.com/P4nto/homeassistant-teamspeak` as a custom integration
repository in **HACS -> Integrations -> three-dot menu -> Custom repositories**,
install it and restart Home Assistant. See the README for manual installation.

## Security

TeamSpeak's ServerQuery protocol uses an unencrypted Telnet connection on port
`10011`. Do not expose this port to the internet. Restrict it to Home Assistant,
your local network or a VPN, and use a dedicated ServerQuery account with only
the required permissions.

## Configuration is done in the UI

1. Go to **Settings -> Devices & services -> Add integration**.
2. Search for **Teamspeak 3 Server**.
3. Enter the host and a valid ServerQuery account.
4. The ServerQuery admin credentials are shown in the TeamSpeak server log after
   the first start.
