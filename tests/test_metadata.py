"""Tests for user-facing metadata and documentation links."""

from __future__ import annotations

import json
from pathlib import Path

GITHUB_REPO = "https://github.com/P4nto/homeassistant-teamspeak"
README_URL = f"{GITHUB_REPO}#readme"
ISSUES_URL = f"{GITHUB_REPO}/issues"


def test_manifest_points_users_to_github() -> None:
    """Manifest links must match the GitHub-based installation docs."""
    manifest = json.loads(Path("custom_components/teamspeak/manifest.json").read_text())
    assert manifest["documentation"] == README_URL
    assert manifest["issue_tracker"] == ISSUES_URL


def test_config_flow_uses_the_same_documentation_url() -> None:
    """The setup flow must not send users to a different tracker."""
    source = Path("custom_components/teamspeak/config_flow.py").read_text()
    assert f'DESCRIPTION_URL = "{README_URL}"' in source


def test_contributing_separates_github_and_gitlab() -> None:
    """GitLab hosts development; public bug reports belong on GitHub."""
    text = Path("CONTRIBUTING.md").read_text()
    assert "GitHub issues" in text
    assert "GitLab is used to host code and to track issues" not in text


def test_contributing_marks_v052_as_removed() -> None:
    """The deleted v0.5.2 tag must not be described as still present."""
    text = Path("CONTRIBUTING.md").read_text()
    assert "points at the wrong commit" not in text
    assert "`v0.5.2` tag was removed" in text


def test_readme_documents_query_port() -> None:
    """The configurable ServerQuery port must appear in setup instructions."""
    text = Path("README.md").read_text()
    assert "ServerQuery port" in text


def test_readme_does_not_overstate_uptime_localization() -> None:
    """Uptime labels are built in for German and English only."""
    text = Path("README.md").read_text()
    assert "localized to the Home Assistant language" not in text
    assert "German and English labels are built in" in text
