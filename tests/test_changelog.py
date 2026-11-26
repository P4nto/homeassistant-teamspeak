"""Tests for changelog-backed release notes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.release_notes import extract_release_notes


def test_changelog_contains_current_manifest_version() -> None:
    """The manifest version must always have a changelog section."""
    manifest = json.loads(Path("custom_components/teamspeak/manifest.json").read_text())
    changelog = Path("CHANGELOG.md").read_text()

    assert f"## [{manifest['version']}]" in changelog


def test_extract_release_notes_stops_at_next_section() -> None:
    """Only the requested version section becomes release notes."""
    content = "## [1.0.0]\n\nFirst release.\n\n## [0.9.0]\n\nOlder release.\n"

    assert extract_release_notes(content, "1.0.0") == "First release."
    assert extract_release_notes(content, "0.9.0") == "Older release."


def test_ci_publishes_the_same_notes_to_both_releases() -> None:
    """GitLab and GitHub must consume the generated notes artifact."""
    ci = Path(".gitlab-ci.yml").read_text()

    assert "--rawfile body release_notes.txt" in ci
    assert "job: create-release" in ci
    assert "artifacts: true" in ci
    assert 'BODY="$(cat release_notes.txt)"' in ci


def test_extract_release_notes_accepts_dated_heading() -> None:
    """Keep-a-Changelog headings may carry a release date."""
    content = "## [0.5.2] - 2026-11-26\n\nNotes.\n\n## [0.5.1]\n\nOlder.\n"

    assert extract_release_notes(content, "0.5.2") == "Notes."


def test_extract_release_notes_raises_for_missing_version() -> None:
    """A missing section must fail the release instead of publishing empty notes."""
    with pytest.raises(ValueError, match=r"No changelog section for 9\.9\.9"):
        extract_release_notes("## [0.5.2]\n\nNotes.\n", "9.9.9")
