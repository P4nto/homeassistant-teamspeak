#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m venv .venv
.venv/bin/python -m pip install --upgrade "pip>=21.0,<22.2" wheel
.venv/bin/pip install --requirement requirements-dev.txt

ln -sfn ../custom_components .devcontainer/custom_components

echo "Development environment ready."
echo "Start Home Assistant with: .venv/bin/hass -c .devcontainer"
