"""Tests for the release configuration."""

from __future__ import annotations

from pathlib import Path

import yaml

CI_FILE = Path(".gitlab-ci.yml")
PLAIN_TAG_RULE = r"$CI_COMMIT_TAG =~ /^\d+\.\d+\.\d+$/"


def _rule_conditions(job_name: str) -> list[str]:
    config = yaml.safe_load(CI_FILE.read_text())
    return [rule.get("if") for rule in config[job_name]["rules"]]


def test_release_rules_accept_only_plain_semver() -> None:
    """Tag pipelines must use plain X.Y.Z tags for every release job."""
    for job_name in ("check-version", "create-release", "mirror-github"):
        assert PLAIN_TAG_RULE in _rule_conditions(job_name), job_name


def test_ci_has_no_legacy_tag_stripping() -> None:
    """The legacy v-prefix and tag stripping must be gone."""
    text = CI_FILE.read_text()
    assert "v?" not in text
    assert "${CI_COMMIT_TAG#v}" not in text
