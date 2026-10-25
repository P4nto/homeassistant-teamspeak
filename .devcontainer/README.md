# Developing with Visual Studio Code and devcontainers

The devcontainer provides a Python 3.10 environment with Home Assistant 2022.6.7, the
`ts3` dependency and the linting tools used by this repository.

## Prerequisites

- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/get-docker/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Getting started

1. Clone the repository.
2. Open the repository in Visual Studio Code.
3. Select **Reopen in Container** when prompted, or run
   **Dev Containers: Reopen in Container** from the command palette.

On the first start, `.devcontainer/setup.sh` creates `.venv`, installs
`requirements-dev.txt` and links `custom_components` into the development
configuration. The Home Assistant configuration lives in
`.devcontainer/configuration.yaml`.

## Tasks

Run **Tasks: Run Task** from the command palette. The available tasks are:

Task | Description
-- | --
Run Home Assistant on port 9123 | Start Home Assistant with the integration and the configuration in `.devcontainer/configuration.yaml`.
Check Home Assistant configuration | Validate the Home Assistant configuration.
Lint integration | Run flake8, isort and black against `custom_components/teamspeak`.

Home Assistant is available at <http://localhost:9123>.

## Manual commands

```bash
.venv/bin/hass -c .devcontainer
.venv/bin/hass -c .devcontainer --script check_config
.venv/bin/flake8 custom_components/teamspeak
.venv/bin/isort --check-only custom_components/teamspeak
.venv/bin/black --check custom_components/teamspeak
```

The pinned Home Assistant version is intentionally kept at 2022.6.7 for the
initial baseline. Modernizing the integration for a current Home Assistant
release is tracked as a separate task.
