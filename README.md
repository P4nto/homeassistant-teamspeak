[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Component to integrate with a [Teamspeak 3 Server instance][teamspeak3_server]._

_DISCLAIMER: This project is a private open source project and doesn't have any connection with TeamSpeak Systems, Inc._

> This repository is a fork of [Larsiiii/homeassistant-teamspeak](https://github.com/Larsiiii/homeassistant-teamspeak),
> maintained at [gitlab.p4nto.de](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak).
> The original work is licensed under the MIT License.

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Shows info from the configured Teamspeak 3 Server.


The following information can be found under Attributes
### Serverinfo
Attribute | Description
-- | --
`unique_identifier` | Unique identifier of the configured Teamspeak Server
`status` | Online status
`name` | Servername
`platform` | Platform the server is hosted on (e.g Windows, Linux, Mac)
`port` | Port the server listens on
`version` | Currently installed Teamspeak verison
`maxclients` | Maximum simultaneous allowed client connections
`reservedslots` | Number of reserved slots
`clientsonline` | Number of connections (includes Server query users)
`clientconnections` | Number of connected clients
`channelsonline` | Number of available channels
`created` | Unix time stamp of server creation date
`uptime` | Seconds since server start

### Clients
### Channels

## Local development

The repository includes a Visual Studio Code devcontainer with Python 3.10,
Home Assistant 2022.6.7, the `ts3` dependency and the linting tools. See
[.devcontainer/README.md](.devcontainer/README.md) for details.

```bash
git clone https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak.git
cd homeassistant-teamspeak
code .
```

Reopen the folder in the container and run the
`Run Home Assistant on port 9123` task. Home Assistant is then available at
<http://localhost:9123>.

The pinned Home Assistant version is the baseline for the imported code. Moving
the integration to a current Home Assistant release is a separate follow-up
task.

## Installation
### Via HACS
HACS custom repositories expect a GitHub repository. Because this fork is hosted
on GitLab, install it manually as described below.
### Manual
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `teamspeak`.
4. Download _all_ the files from the `custom_components/teamspeak/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Teamspeak 3 Server"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/teamspeak/translations/en.json
custom_components/teamspeak/__init__.py
custom_components/teamspeak/api.py
custom_components/teamspeak/config_flow.py
custom_components/teamspeak/const.py
custom_components/teamspeak/entity.py
custom_components/teamspeak/manifest.json
custom_components/teamspeak/sensor.py
```

## Configuration is done in the UI

1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Teamspeak 3 Server"
2. Enter the IP address of your Teamspeak 3 Server
3. Enter username and password for a valid Server Query Account. The credentials for the Server Query Admin Account can be found in the Teamspeak server logs after the first start:
```
------------------------------------------------------------------
               Server Query Admin Account created
         loginname= "serveradmin", password= "ZS8PRONS"
         apikey= "BADUFzEGXK60NntGmTWYGkfH6nSrM9Dh_SThG7X"
------------------------------------------------------------------
```

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[teamspeak3_server]: https://www.teamspeak.com/en/
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge
