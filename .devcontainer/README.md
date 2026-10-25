# Developing with Visual Studio Code and devcontainers

The devcontainer provides a Python 3.14 environment with Home Assistant
2026.10.3, the integration dependencies, Ruff and the test dependencies.

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
`requirements-dev.txt`, verifies the dependencies and links `custom_components`
into the development configuration. The Home Assistant configuration lives in
`.devcontainer/configuration.yaml`.

## Tasks

Run **Tasks: Run Task** from the command palette. The available tasks are:

Task | Description
-- | --
Run Home Assistant on port 9123 | Start Home Assistant with the integration and the configuration in `.devcontainer/configuration.yaml`.
Check Home Assistant configuration | Validate the Home Assistant configuration.
Lint integration | Run Ruff against the repository.
Run tests | Run the PHCC test suite.

Home Assistant is available at <http://localhost:9123>.

## Manual commands

```bash
.venv/bin/hass -c .devcontainer
.venv/bin/hass -c .devcontainer --script check_config
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest
```
