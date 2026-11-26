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


def test_preflight_blocks_release_creation() -> None:
    """A failed preflight must prevent the GitLab release."""
    needs = yaml.safe_load(CI_FILE.read_text())["create-release"]["needs"]
    assert "release-preflight" in needs


def test_mirror_reads_notes_before_tag_push() -> None:
    """The tag must never be pushed before the notes artifact was read."""
    script = yaml.safe_load(CI_FILE.read_text())["mirror-github"]["script"]
    text = "\n".join(script)
    tag_push = "refs/tags/${CI_COMMIT_TAG}:refs/tags/"
    assert text.index("cat release_notes.txt") < text.index(tag_push)


def test_mirror_does_not_force_push() -> None:
    """Divergence must fail instead of overwriting GitHub history."""
    assert "git push --force" not in CI_FILE.read_text()


def test_default_branch_mirror_keeps_release_job_optional() -> None:
    """A default-branch pipeline has no release job and must still mirror."""
    needs = yaml.safe_load(CI_FILE.read_text())["mirror-github"]["needs"]
    entry = next(item for item in needs if item["job"] == "create-release")
    assert entry["optional"] is True


def test_ci_has_no_legacy_tag_stripping() -> None:
    """The legacy v-prefix and tag stripping must be gone."""
    text = CI_FILE.read_text()
    assert "v?" not in text
    assert "${CI_COMMIT_TAG#v}" not in text
