# Release- und Qualitäts-Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) oder superpowers:executing-plans, sobald der Agentenwechsel erfolgt ist.

**Goal:** Den Release-Prozess nach `0.5.2` stabilisieren, Doku/Links konsistent machen, den Status-Sensor korrekt benennen und die verbleibenden Fehlerpfade testen.

**Architecture:** GitLab bleibt Quelle, GitHub bleibt HACS-/Marketplace-Mirror. Die Manifest-Version ist die einzige Versionsquelle; Tags heißen künftig exakt `X.Y.Z`. Release Notes kommen aus einer `CHANGELOG.md` und werden für GitLab und GitHub aus derselben Datei erzeugt.

**Tech Stack:** Python 3.14, Home Assistant 2026.11, pytest/pytest-homeassistant, Ruff, GitLab CI (Alpine, jq/curl/git).

**Spec:** Gespräch vom 26.11.2026 plus Repo-Audit; keine separate Spec-Datei.

## Design-Entscheidung

Kanonisch wird `X.Y.Z` ohne `v`. Das funktionierende Release und der GitHub-Tag heißen bereits `0.5.2`, und das Manifest enthält ebenfalls `0.5.2`. Die `v`-Reihe ist historisch; `v0.5.2` zeigt auf den falschen Commit und hat kein Asset. Historische `v`-Tags bleiben unangetastet; der kaputte `v0.5.2` wird nach Freigabe bereinigt.

## Global Constraints

- Home Assistant `>= 2026.11.0`, Python `3.14`.
- GitLab ist Entwicklungs- und Release-Quelle; GitHub ist Mirror für Marketplace/HACS.
- `GITHUB_TOKEN` bleibt geschützte, maskierte CI-Variable und wird nie ins Repo oder Log geschrieben.
- Tag-Format: `^\d+\.\d+\.\d+$`, exakt gleich `manifest.json.version`.
- Release-Jobs bleiben `interruptible: false`; GitHub-Mirror bleibt über `resource_group: github-mirror` serialisiert.
- Änderungen laufen über Feature-Branch, Commit, Push und MR nach `master`, Assignee `p4nto`.
- Keine Produktiv-Deployments oder Runner-Änderungen aus diesem Plan.
- Entity-Unique-IDs bleiben stabil; der Status-Sensor erhält bewusst einen neuen Anzeigenamen (und damit für Neuanlagen eine neue Entity-ID; bestehende Registry-Einträge bleiben unverändert).

## Review Focus

| Risiko | Erwartetes Verhalten | Test |
|---|---|---|
| Falsches Tag-Präfix (`v0.5.3`) | Pipeline bricht vor dem Release ab | `tests/test_release_config.py` |
| Tag war bei Pipeline-Start nicht geschützt | Preflight bricht mit verständlicher Meldung ab | Task 1 `release-preflight` |
| Status-Sensor heißt nur wie das Gerät | Anzeigename ist „Test Server Status“, Unique-ID bleibt unverändert | `tests/test_sensor.py` |
| Auth-Fehler im Coordinator | `ConfigEntryAuthFailed`, nicht `UpdateFailed` | `tests/test_coordinator.py` |
| Release Notes leer/falsch | Notes aus `CHANGELOG.md` passen zur Manifest-Version | `tests/test_changelog.py` |

---

## Task 1: Tag-Konvention und Release-Preflight

**Files:**
- Modify: `.gitlab-ci.yml:82-98`, `:100-133`, `:135-199`
- Modify: `CONTRIBUTING.md:37-57`
- Create: `tests/test_release_config.py`

**Interfaces:**
- Consumes: `custom_components/teamspeak/manifest.json` → `.version`
- Produces: kanonischer Tag-Regex `^\d+\.\d+\.\d+$`, Job `release-preflight`, Doku der Protected-Tag-Reihenfolge

- [ ] **Step 1: Failing Test schreiben**

`tests/test_release_config.py` prüft: alle drei Release-Rules verwenden exakt `$CI_COMMIT_TAG =~ /^\d+\.\d+\.\d+$/`; `.gitlab-ci.yml` enthält weder `v?` noch `${CI_COMMIT_TAG#v}`.

- [ ] **Step 2: Test laufen lassen**

Run: `.venv/bin/pytest tests/test_release_config.py -v`. Expected: FAIL.

- [ ] **Step 3: CI-Regeln umstellen**

Alle drei `v?\d+\.\d+\.\d+`-Rules auf `^\d+\.\d+\.\d+$` setzen; `VERSION="${CI_COMMIT_TAG#v}"` durch `VERSION="${CI_COMMIT_TAG}"` ersetzen.

- [ ] **Step 4: `release-preflight` ergänzen**

Neuer Job in `validate` mit Rules für `^\d+\.\d+\.\d+$`, `jq`, Prüfung `CI_COMMIT_TAG == manifest.version`, `GITHUB_REPOSITORY` und `GITHUB_TOKEN` mit klarer Fehlermeldung zum Protected Tag. `mirror-github.needs` um `job: release-preflight, optional: true` ergänzen.

- [ ] **Step 5: CONTRIBUTING aktualisieren**

Release-Beispiel auf `git tag -a 0.5.3` umstellen. Ergänzen: Tag erst nach Version-Bump, Tag vor Pipeline-Start schützen, bei bereits gestarteter Pipeline neue Pipeline starten. Hinweis: `v0.5.2` ist veraltet.

- [ ] **Step 6: Test und Lint laufen lassen**

Run: `.venv/bin/pytest tests/test_release_config.py -v && .venv/bin/ruff check . && .venv/bin/ruff format --check .`. Expected: PASS.

- [ ] **Step 7: Commit**

`git add .gitlab-ci.yml CONTRIBUTING.md tests/test_release_config.py && git commit -m "ci: enforce plain version tags and add release preflight"`

- [ ] **Step 8: Manuelle Nachbereitung nach dem MR**

Mit Maintainer-Rechten kaputten `v0.5.2`-Tag/Release in GitLab und GitHub bereinigen; `0.5.2` bleibt unangetastet.

---

## Task 2: Doku- und Tracker-Links konsistent

**Files:**
- Modify: `custom_components/teamspeak/manifest.json:11,14`
- Modify: `custom_components/teamspeak/config_flow.py:27`
- Modify: `CONTRIBUTING.md:10-15`, `:63-66`
- Modify: `README.md:40`, `:86`, `:135`
- Create: `tests/test_metadata.py`

**Interfaces:**
- Consumes: GitHub-Repo-URL `https://github.com/P4nto/homeassistant-teamspeak`
- Produces: einheitliche Nutzer-Links; klare Trennung „GitHub = Nutzer/Bugs“, „GitLab = Entwicklung“

- [ ] **Step 1: Failing Tests schreiben**

`tests/test_metadata.py`: Manifest-URLs zeigen auf GitHub; CONTRIBUTING beschreibt GitLab nicht als Issue-Tracker; README dokumentiert den ServerQuery-Port und behauptet keine vollständige HA-Sprachlokalisierung.

- [ ] **Step 2: Tests laufen lassen**

Run: `.venv/bin/pytest tests/test_metadata.py -v`. Expected: FAIL.

- [ ] **Step 3: Dateien anpassen**

`manifest.json`: `documentation` = `https://github.com/P4nto/homeassistant-teamspeak#readme`, `issue_tracker` = `https://github.com/P4nto/homeassistant-teamspeak/issues`. `config_flow.py`: `DESCRIPTION_URL` auf dieselbe README-URL. `CONTRIBUTING.md`: GitLab nur Code/MR, öffentliche Bugs GitHub. `README.md`: Port im Konfigurationsschritt, Uptime-Text auf „German and English labels are built in“, Marketplace-Restart-Hinweis präzisieren.

- [ ] **Step 4: Tests und Lint laufen lassen**

Run: `.venv/bin/pytest tests/test_metadata.py -v && .venv/bin/ruff check . && .venv/bin/ruff format --check .`. Expected: PASS.

- [ ] **Step 5: Commit**

`git add custom_components/teamspeak/manifest.json custom_components/teamspeak/config_flow.py CONTRIBUTING.md README.md tests/test_metadata.py && git commit -m "docs: align GitHub links and clarify setup docs"`

---

## Task 3: Status-Sensor korrekt benennen

**Files:**
- Modify: `custom_components/teamspeak/sensor.py:66-71`
- Modify: `custom_components/teamspeak/strings.json:32-41`
- Modify: `custom_components/teamspeak/translations/de.json:32-41`
- Modify: `custom_components/teamspeak/translations/en.json:32-41`
- Modify: `tests/test_sensor.py:37-53`

**Interfaces:**
- Consumes: bestehender Unique-ID ohne Suffix
- Produces: `entity.sensor.status.name`; Anzeigename „Test Server Status“, Unique-ID unverändert

**Korrektur während der Umsetzung:** Die ursprüngliche Annahme „Anzeigename `Status`, Entity-ID `sensor.test_server`" war falsch. Home Assistant kombiniert bei `_attr_has_entity_name = True` den Gerätenamen mit dem übersetzten Entity-Namen und leitet daraus die Entity-ID ab. Bestehende Registry-Einträge behalten ihre Entity-ID; neue Installationen erhalten `sensor.test_server_status`.

- [ ] **Step 1: Failing Test schreiben**

Im bestehenden Setup-Test: `assert state.entity_id == "sensor.test_server_status"`, `assert state.attributes["friendly_name"] == "Test Server Status"` und `assert er.async_get(hass).async_get(state.entity_id).unique_id == entry.entry_id`.

- [ ] **Step 2: Test laufen lassen**

Run: `.venv/bin/pytest tests/test_sensor.py::test_sensor_state_and_attributes -v`. Expected: FAIL.

- [ ] **Step 3: Implementierung**

`TeamspeakSensor` bekommt `_attr_translation_key = "status"`. `__init__` bleibt unverändert. In allen drei JSON-Dateien `entity.sensor.status.name` mit Wert `"Status"` ergänzen.

- [ ] **Step 4: Test laufen lassen**

Run: `.venv/bin/pytest tests/test_sensor.py -v`. Expected: PASS.

- [ ] **Step 5: Commit**

`git add custom_components/teamspeak/sensor.py custom_components/teamspeak/strings.json custom_components/teamspeak/translations/de.json custom_components/teamspeak/translations/en.json tests/test_sensor.py && git commit -m "fix: name the server status sensor"`

---

## Task 4: Fehlerpfade testen

**Files:**
- Create: `tests/test_coordinator.py`
- Modify: `tests/test_api.py`
- Modify: `tests/test_sensor.py`

**Interfaces:**
- Consumes: `TeamspeakApiClient.get_data`, `TeamspeakDataUpdateCoordinator._async_update_data`, `_as_int`, `TeamspeakUptimeSensor`
- Produces: abgedeckte Auth-/Kommunikationsfehler, Close-Fehler und fehlende Uptime

- [ ] **Step 1: Failing Tests schreiben**

Tests: `test_coordinator_auth_error_raises_config_entry_auth_failed`, `test_coordinator_communication_error_raises_update_failed`, `test_as_int_handles_none_and_invalid_values`, `test_login_query_error_closes_session`, `test_use_auth_error_closes_session`, `test_close_swallows_quit_error`, `test_uptime_missing_returns_none`.

- [ ] **Step 2: Tests laufen lassen**

Run: `.venv/bin/pytest tests/test_coordinator.py tests/test_api.py tests/test_sensor.py -v`. Expected: neue Tests laufen; echte Fehler werden sichtbar.

- [ ] **Step 3: Nur bei echtem Befund produzierenden Code ändern**

Erwartung: keine Produktionsänderung nötig.

- [ ] **Step 4: Volle Suite mit Coverage laufen lassen**

Run: `.venv/bin/pytest --cov=custom_components.teamspeak --cov-report=term-missing`. Expected: alle Tests grün; `coordinator.py:53-58` und `sensor.py:110-116` nicht mehr unabgedeckt.

- [ ] **Step 5: Commit**

`git add tests/test_coordinator.py tests/test_api.py tests/test_sensor.py && git commit -m "test: cover auth, close and missing-data paths"`

---

## Task 5: CHANGELOG und geteilte Release Notes

**Files:**
- Create: `CHANGELOG.md`
- Create: `scripts/release_notes.py`
- Create: `tests/test_changelog.py`
- Modify: `.gitlab-ci.yml:100-133`, `:135-199`
- Modify: `README.md`

**Interfaces:**
- Consumes: `CHANGELOG.md`, `manifest.json.version`
- Produces: `release_notes.txt` als Artefakt; identischer Body für GitLab- und GitHub-Release

- [ ] **Step 1: Failing Tests schreiben**

`tests/test_changelog.py`: `test_changelog_contains_current_manifest_version`, `test_extract_release_notes_stops_at_next_section`, `test_extract_release_notes_raises_for_missing_version`.

- [ ] **Step 2: Tests laufen lassen**

Run: `.venv/bin/pytest tests/test_changelog.py -v`. Expected: FAIL.

- [ ] **Step 3: `scripts/release_notes.py` anlegen**

Signatur `extract_release_notes(content: str, version: str) -> str`. Verhalten: Abschnitt `## [version]` bis nächsten `## [` zurückgeben, `strip()`, bei fehlendem Abschnitt `ValueError("No changelog section for ...")`. CLI: `python3 scripts/release_notes.py CHANGELOG.md VERSION`.

- [ ] **Step 4: `CHANGELOG.md` anlegen**

Keep-a-Changelog-Format. Eintrag `## [0.5.2]` mit realen Punkten: HA 2026.11, konfigurierbarer ServerQuery-Port, gehärtete Release-Pipeline. Ältere Versionen kurz verlinkt; README verlinkt die Datei.

- [ ] **Step 5: CI umstellen**

`create-release`: `python3`, Notestexte nach `release_notes.txt`, `jq --rawfile body`, Artefakte `release_notes.txt` und Zip. `mirror-github`: `needs` um `job: create-release, artifacts: true, optional: true`, `python3`, `BODY="$(cat release_notes.txt)"`, `--arg body "$BODY"`.

- [ ] **Step 6: Tests, Lint und YAML-Check laufen lassen**

Run: `.venv/bin/pytest tests/test_changelog.py -v && .venv/bin/ruff check . && .venv/bin/ruff format --check . && python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"`. Expected: PASS.

- [ ] **Step 7: Commit**

`git add CHANGELOG.md scripts/release_notes.py tests/test_changelog.py .gitlab-ci.yml README.md && git commit -m "ci: generate release notes from changelog"`

---

## Abschlussprüfung

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest --cov=custom_components.teamspeak --cov-report=term-missing
python3 -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"
git diff --check
```
