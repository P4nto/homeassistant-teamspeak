# Changelog

Notable changes are documented here in
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and match
`custom_components/teamspeak/manifest.json`.

These sections are the single source for the notes published on both GitLab and
GitHub. Earlier releases are listed on the
[GitLab releases page](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases)
and the
[GitHub releases page](https://github.com/P4nto/homeassistant-teamspeak/releases).

## [0.5.3] - 2026-11-26

### Changed

- Release pipelines fail before publishing when the preflight checks do not pass.
- GitHub mirroring no longer force-pushes and reads the release notes before
  pushing a tag.
- Documentation describes the removed `v0.5.2` tag correctly.

### Fixed

- Malformed ServerQuery error responses no longer surface as unexpected errors
  during setup, reauthentication or coordinator updates.
- Non-string `virtualserver_version` values are normalized without raising.
- A failed platform setup closes the ServerQuery session instead of leaving it
  open until Home Assistant restarts.

## [0.5.2] - 2026-11-26

### Added

- Configurable ServerQuery port during setup, defaulting to `10011` for entries
  created by earlier versions.

### Changed

- Require Home Assistant 2026.11 and Python 3.14.
- Point the setup flow, manifest and documentation at the GitHub repository used
  by the Marketplace; GitLab remains the development repository.
- Release tags use the plain `X.Y.Z` format and are checked before publishing.

### Fixed

- Releases carry notes generated from this changelog on both GitLab and GitHub.
- ServerQuery sessions are closed on login, query and unload errors.
- The status sensor now has an explicit name instead of inheriting only the
  device name.

## [0.5.1]

See the
[GitLab releases page](https://gitlab.p4nto.de/p4nto/homeassistant-teamspeak/-/releases)
for the notes of this and earlier releases.
