# Design: Release-CI-Haertung und Doku-Korrektur (2026-11-26)

## Ziel

Die Release-Pipeline darf kein GitLab-Release erzeugen, wenn die
Vorpruefung fehlgeschlagen ist, und darf ein GitHub-Tag nicht veröffentlichen,
bevor die Release Notes fertig sind. Ausserdem soll die Doku den gelöschten
Tag `v0.5.2` nicht mehr als vorhanden beschreiben.

## Nicht-Ziele

- Kein neues Release, kein neuer Tag, kein Pipeline-Retry.
- Keine Änderung an Integrationslogik, Manifest-Version oder bestehenden
  historischen `v`-Tags.
- Kein Deployment und kein Zugriff auf Produktivsysteme.

## Aenderungen

### 1. `release-preflight` wird harte Abhaengigkeit

`.gitlab-ci.yml`: `create-release.needs` ergaenzt `release-preflight` (ohne
`optional`). Damit blockt ein fehlendes `GITHUB_TOKEN` oder ein
Manifest-Mismatch auch das GitLab-Release.

`check-version` bleibt zusaetzlich erhalten; die doppelte Manifest-Pruefung
ist harmlos und wird nicht angetastet.

### 2. GitHub-Mirror liest die Release Notes vor dem Push

`create-release` muss in `mirror-github.needs` `optional: true` bleiben, sonst
wird der Mirror auf dem Default-Branch geskippt (dort gibt es keinen
Release-Job). Stattdessen liest der Tag-Zweig von `mirror-github` die Datei
`release_notes.txt` **vor** dem `git push` und bricht bei fehlendem Artefakt ab.
Damit wird kein Tag nach GitHub veröffentlicht, wenn die Notes fehlen.

### 3. Keine Force-Pushes mehr

Die beiden `git push --force`-Aufrufe in `mirror-github` werden auf normale
Pushes umgestellt. Bei einer Divergenz zwischen GitLab und GitHub bricht der
Job ab, statt fremde Aenderungen zu ueberschreiben. Das ist bei einem Mirror
die sicherere Default-Reaktion; eine bewusste Wiederherstellung kann weiterhin
manuell mit `--force` erfolgen.

### 4. Doku korrigieren

`CONTRIBUTING.md` ersetzt den Satz „`v0.5.2` is obsolete and points at the
wrong commit“ durch eine Aussage, dass der Tag entfernt wurde und historische
`v`-Tags unveraendert bleiben.

### 5. Tests

- `tests/test_release_config.py`: `release-preflight` in `create-release.needs`
  und `create-release` als Pflicht-Need in `mirror-github` pinpen; ausserdem
  pruefen, dass keine `git push --force`-Zeile mehr vorkommt.
- `tests/test_metadata.py` oder `tests/test_changelog.py`: pruefen, dass die
  Doku nicht mehr behauptet, `v0.5.2` zeige auf den falschen Commit.

## Verifikation

- `ruff check .`, `ruff format --check .`
- `pytest --cov=custom_components.teamspeak --cov-report=term-missing`
- YAML-Parse von `.gitlab-ci.yml`, `git diff --check`
- Kein Release-Tag, kein Pipeline-Retry, kein Deploy
