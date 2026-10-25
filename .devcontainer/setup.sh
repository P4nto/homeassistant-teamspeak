#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m venv .venv
.venv/bin/python -m pip install --upgrade pip wheel
.venv/bin/pip install --requirement requirements-dev.txt
.venv/bin/pip check

ln -sfn ../custom_components .devcontainer/custom_components

echo "Development environment ready."
echo "Start Home Assistant with: .venv/bin/hass -c .devcontainer"
echo "Run the tests with: .venv/bin/pytest"
echo "Run the linter with: .venv/bin/ruff check . && .venv/bin/ruff format --check ."
