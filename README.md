[![Pipeline](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/badges/master/pipeline.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/pipelines)
[![Latest release](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/badges/release.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

_Component to integrate a [TeamSpeak 3 Server](https://www.teamspeak.com/en/) with Home Assistant._

_DISCLAIMER: This project is a private open source project and is not affiliated with TeamSpeak Systems, Inc._

> This repository is a fork of [Larsiiii/homeassistant-teamspeak](https://github.com/Larsiiii/homeassistant-teamspeak),
> maintained at [gitlab.p4nto.de](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak)
> and mirrored to [GitHub](https://github.com/P4nto/homeassistant-teamspeak) for HACS.
> The original work is licensed under the MIT License.

## Requirements

- Home Assistant **2026.10** or newer
- Python **3.14** (provided by Home Assistant)
- A reachable TeamSpeak 3 Server with the ServerQuery interface on port **10011**
- A ServerQuery account with permission to query the virtual server

## Security

TeamSpeak's ServerQuery protocol uses an **unencrypted Telnet connection** on
port `10011`. Do not expose this port to the internet. Restrict it to Home
Assistant, your local network or a VPN, and use a dedicated ServerQuery account
with only the permissions required to query the virtual server. The integration
cannot encrypt this connection.

## Platforms

Platform | Description
-- | --
`sensor` | Shows the status, client count and uptime of the configured TeamSpeak 3 Server.

The integration creates the following sensors:

Sensor | Description
-- | --
Server status | Virtual server status (for example `online`)
Clients online | Number of active voice clients. ServerQuery connections such as `serveradmin` are not counted.
Uptime | Uptime in days, hours and minutes, localized to the Home Assistant language

The server status sensor exposes the following information as attributes.

### Serverinfo

Attribute | Description
-- | --
`unique_identifier` | Unique identifier of the TeamSpeak server
`status` | Online status
`name` | Server name
`platform` | Platform the server is hosted on (for example Linux)
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

### Clients and channels

The complete `clientlist` and `channellist` responses are exposed as the
`clients` and `channels` attributes. These attributes are excluded from the
Home Assistant recorder history because they can contain client names and large
lists; they remain available in the current entity state.

## Installation

The GitLab repository is mirrored to GitHub for HACS. Use the GitHub repository
URL as a custom integration repository. Manual installation from GitLab is also
supported.

### HACS

1. Open **HACS -> Integrations**.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/P4nto/homeassistant-teamspeak` with category
   **Integration**.
4. Search for **Teamspeak 3 Server**, install it and restart Home Assistant.

### Manual

1. Download the latest `teamspeak-*.zip` from the
   [GitLab releases page](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases),
   or copy the files from `custom_components/teamspeak/` in this repository.
2. Place the `teamspeak` directory in your Home Assistant
   `custom_components` directory.
3. Restart Home Assistant.
4. In the Home Assistant UI go to **Settings -> Devices & services -> Add
   integration** and search for **Teamspeak 3 Server**.

The result should look like this:

```text
custom_components/teamspeak/
├── __init__.py
├── api.py
├── brand/
│   ├── icon.png
│   ├── icon@2x.png
│   ├── logo.png
│   └── logo@2x.png
├── config_flow.py
├── const.py
├── coordinator.py
├── entity.py
├── manifest.json
├── sensor.py
├── strings.json
└── translations/
    ├── de.json
    └── en.json
```

Home Assistant installs the Python dependency (`ts3`) from `manifest.json`
automatically. The `telnetlib` compatibility package required by `ts3` on
Python 3.13+ is already shipped by Home Assistant.

## Configuration

Configuration is done in the UI:

1. Go to **Settings -> Devices & services -> Add integration** and search for
   **Teamspeak 3 Server**.
2. Enter the host and the ServerQuery credentials.
3. The generated credentials for the ServerQuery admin account are shown in the
   TeamSpeak server log after the first start. The values below are
   placeholders; use the values from your own server log:

```text
------------------------------------------------------------------
               Server Query Admin Account created
         loginname= "serveradmin", password= "<generated-password>"
------------------------------------------------------------------
```

The `apikey` printed by TeamSpeak is not used by this integration.

If the credentials stop working, Home Assistant starts a re-authentication
flow. The sensor becomes unavailable while the server cannot be queried.

## Local development

The repository includes a Visual Studio Code devcontainer with Python 3.14,
Home Assistant 2026.10.3, the integration dependencies, Ruff and the test
dependencies. See [.devcontainer/README.md](.devcontainer/README.md) for
details.

```bash
git clone https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak.git
cd homeassistant-teamspeak
code .
```

Reopen the folder in the container and run the
`Run Home Assistant on port 9123` task. Home Assistant is then available at
<http://localhost:9123>.

Useful commands:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
.venv/bin/hass -c .devcontainer --script check_config
```

The GitLab pipeline runs Ruff, the PHCC test suite, Hassfest and a release job
on version tags.

## Contributions

If you want to contribute, please read the
[contribution guidelines](CONTRIBUTING.md).

## Credits

- Original integration by [Larsiiii](https://github.com/Larsiiii).
- The generic headset brand icon and logo are based on
  [Material Design Icons](https://pictogrammers.com/library/mdi/) (`mdi-headset`),
  licensed under Apache-2.0. They are not the TeamSpeak logo.
