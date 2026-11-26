# Release-CI-Härtung und Doku-Korrektur Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die Release-Pipeline blockt fehlgeschlagene Vorprüfungen und veröffentlicht kein GitHub-Tag ohne Release Notes; die Doku beschreibt den gelöschten Tag korrekt.

**Architecture:** Reine CI-/Test-/Doku-Änderung. `.gitlab-ci.yml` bekommt eine harte `release-preflight`-Abhängigkeit für `create-release`; `mirror-github` liest die Notes vor dem Push und pusht ohne `--force`. Tests pinnen die YAML-Struktur, damit die Abhängigkeiten nicht wieder gelockert werden.

**Tech Stack:** GitLab CI YAML, pytest, PyYAML, Python 3.14, Markdown-Doku.

**Spec:** `docs/superpowers/designs/2026-11-26-ci-hardening.md`

## Global Constraints

- Kein Release-Tag, kein Pipeline-Retry, kein Deployment.
- Keine Tokens, Passwörter oder Secrets in Dateien, Logs oder Commits.
- `GITHUB_REPOSITORY` bleibt `"P4nto/homeassistant-teamspeak"` in `.gitlab-ci.yml`; `GITHUB_TOKEN` bleibt geschützte CI-Variable.
- Release-Tags bleiben `X.Y.Z` ohne `v`-Präfix.
- Historische `v`-Tags bleiben unangetastet; `v0.5.2` ist gelöscht.
- Manifest-Version bleibt `0.5.2`; es wird keine Version bumped.

## Review Focus

- Fehlendes `GITHUB_TOKEN` auf einem Tag: Preflight muss `create-release` blockieren → `test_preflight_blocks_release_creation` (Task 1).
- Fehlender Changelog-Abschnitt: `create-release` scheitert, ohne dass `mirror-github` einen Tag pusht → `test_mirror_reads_notes_before_tag_push` (Task 2).
- Divergenz GitLab/GitHub: Push muss abbrechen statt fremde History zu überschreiben → `test_mirror_does_not_force_push` (Task 2).
- Default-Branch-Pipeline ohne Release-Job: Mirror muss weiterhin laufen → `test_default_branch_mirror_keeps_release_job_optional` (Task 2).
- Gelöschter Tag in der Doku: darf nicht als vorhanden beschrieben werden → `test_contributing_marks_v052_as_removed` (Task 3).

---

### Task 1: Preflight blockt das GitLab-Release

**Files:**
- Modify: `.gitlab-ci.yml:116-121`
- Test: `tests/test_release_config.py`

**Interfaces:**
- Consumes: `CI_FILE` und `_rule_conditions` aus `tests/test_release_config.py`.
- Produces: `create-release.needs` enthält `release-preflight` als Pflicht-Need.

- [ ] **Step 1: Failing Test schreiben**

```python
def test_preflight_blocks_release_creation() -> None:
    """A failed preflight must prevent the GitLab release."""
    needs = yaml.safe_load(CI_FILE.read_text())["create-release"]["needs"]
    assert "release-preflight" in needs
```

- [ ] **Step 2: Test ausführen und Failure prüfen**

Run: `/home/pollux/homeassistant-teamspeak/.venv/bin/pytest tests/test_release_config.py::test_preflight_blocks_release_creation -q`
Expected: FAIL — `release-preflight` fehlt in `needs`.

- [ ] **Step 3: Minimal implementieren**

In `.gitlab-ci.yml` im Job `create-release` die Liste `needs` um `- release-preflight` ergänzen. Kein `optional`, keine neuen Jobs.

- [ ] **Step 4: Test ausführen**

Run: `/home/pollux/homeassistant-teamspeak/.venv/bin/pytest tests/test_release_config.py -q`
Expected: PASS — alle Tests in der Datei grün.

- [ ] **Step 5: Commit**

```bash
git add .gitlab-ci.yml tests/test_release_config.py
git commit -m "ci: make release preflight a hard dependency"
```

### Task 2: GitHub-Mirror ohne Force-Push und mit Notes-Guard

**Files:**
- Modify: `.gitlab-ci.yml:195-229`
- Test: `tests/test_release_config.py`

**Interfaces:**
- Consumes: `CI_FILE` aus `tests/test_release_config.py`.
- Produces: `mirror-github` liest `release_notes.txt` vor dem Tag-Push und verwendet `git push` ohne `--force`.

- [ ] **Step 1: Failing Tests schreiben**

```python
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
```

- [ ] **Step 2: Tests ausführen und Failures prüfen**

Run: `/home/pollux/homeassistant-teamspeak/.venv/bin/pytest tests/test_release_config.py -q`
Expected: 2 FAILs (Notes nach dem Push, `--force` vorhanden); der dritte Test pinnt bereits grünes Verhalten.

- [ ] **Step 3: Minimal implementieren**

In `.gitlab-ci.yml` im Job `mirror-github`:

1. Im Tag-Zweig `BODY="$(cat release_notes.txt)"` direkt vor den `git push`-Aufruf setzen und die alte Zeile nach dem Push entfernen.
2. `git push --force github "HEAD:refs/heads/${CI_DEFAULT_BRANCH}"` → `git push github "HEAD:refs/heads/${CI_DEFAULT_BRANCH}"`.
3. `git push --force github "refs/tags/${CI_COMMIT_TAG}:refs/tags/${CI_COMMIT_TAG}"` → `git push github "refs/tags/${CI_COMMIT_TAG}:refs/tags/${CI_COMMIT_TAG}"`.
4. `create-release` in `needs` bewusst `optional: true` lassen.

- [ ] **Step 4: Tests ausführen**

Run: `/home/pollux/homeassistant-teamspeak/.venv/bin/pytest tests/test_release_config.py -q`
Expected: PASS — alle Tests in der Datei grün.

- [ ] **Step 5: Commit**

```bash
git add .gitlab-ci.yml tests/test_release_config.py
git commit -m "ci: guard GitHub mirror before pushing tags"
```

### Task 3: Doku korrigieren und Gesamtprüfung

**Files:**
- Modify: `CONTRIBUTING.md:40-42`
- Test: `tests/test_metadata.py`

**Interfaces:**
- Consumes: bestehende `test_metadata.py`-Konvention (`Path("CONTRIBUTING.md").read_text()`).
- Produces: Doku behauptet nicht mehr, `v0.5.2` zeige auf den falschen Commit.

- [ ] **Step 1: Failing Test schreiben**

```python
def test_contributing_marks_v052_as_removed() -> None:
    """The deleted v0.5.2 tag must not be described as still present."""
    text = Path("CONTRIBUTING.md").read_text()
    assert "points at the wrong commit" not in text
    assert "`v0.5.2` tag was removed" in text
```

- [ ] **Step 2: Test ausführen und Failure prüfen**

Run: `/home/pollux/homeassistant-teamspeak/.venv/bin/pytest tests/test_metadata.py::test_contributing_marks_v052_as_removed -q`
Expected: FAIL — alter Satz steht noch in der Datei.

- [ ] **Step 3: Minimal implementieren**

In `CONTRIBUTING.md` den Satz

`The old \`v\`-prefixed tags are historical; \`v0.5.2\` is obsolete and points at the wrong commit.`

ersetzen durch:

`The old \`v\`-prefixed tags are historical; the obsolete \`v0.5.2\` tag was removed.`

- [ ] **Step 4: Gesamtprüfung ausführen**

Run:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest --cov=custom_components.teamspeak --cov-report=term-missing
python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.gitlab-ci.yml').read_text())"
git diff --check
```

Expected: Ruff grün, pytest grün mit 100 % Coverage, YAML-Parse grün, `git diff --check` leer.

- [ ] **Step 5: Commit**

```bash
git add CONTRIBUTING.md tests/test_metadata.py
git commit -m "docs: mark removed v0.5.2 tag as removed"
```
