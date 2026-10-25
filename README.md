[![Pipeline](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/badges/master/pipeline.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/pipelines)
[![Latest release](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/badges/release.svg)](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

_Component to integrate a [TeamSpeak 3 Server](https://www.teamspeak.com/en/) with Home Assistant._

_DISCLAIMER: This project is a private open source project and is not affiliated with TeamSpeak Systems, Inc._

> This repository is a fork of [Larsiiii/homeassistant-teamspeak](https://github.com/Larsiiii/homeassistant-teamspeak),
> maintained at [gitlab.p4nto.de](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak).
> The original work is licensed under the MIT License.

## Requirements

- Home Assistant **2026.10** or newer
- Python **3.14** (provided by Home Assistant)
- A reachable TeamSpeak 3 Server with the ServerQuery interface on port **10011**
- A ServerQuery account with permission to query the virtual server

## Platforms

Platform | Description
-- | --
`sensor` | Shows the status and details of the configured TeamSpeak 3 Server.

The sensor state is the virtual server status (for example `online`). The
following information is available as attributes.

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
`clientconnections` | Number of connected clients
`channelsonline` | Number of available channels
`created` | Unix timestamp of the server creation date
`uptime` | Seconds since the server started

### Clients and channels

The complete `clientlist` and `channellist` responses are exposed as the
`clients` and `channels` attributes.

## Installation

HACS and the Home Assistant Marketplace only support repositories hosted on
GitHub. This fork is hosted on GitLab, so install it manually or use a release
archive.

### Manual

1. Download the latest `teamspeak-*.zip` from the
   [releases page](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases),
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
3. The credentials for the ServerQuery admin account are shown in the TeamSpeak
   server log after the first start:

```text
------------------------------------------------------------------
               Server Query Admin Account created
         loginname= "serveradmin", password= "ZS8PRONS"
         apikey= "BADUFzEGXK60NntGmTWYGkfH6nSrM9Dh_SThG7X"
------------------------------------------------------------------
```

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
