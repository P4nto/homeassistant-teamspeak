#!/usr/bin/env python3
"""Extract the release notes for one version from CHANGELOG.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def extract_release_notes(content: str, version: str) -> str:
    """Return the changelog section for version, without its heading."""
    heading = f"## [{version}]"
    lines = content.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.strip().startswith(heading)),
        None,
    )
    if start is None:
        raise ValueError(f"No changelog section for {version}")

    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("## [")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end]).strip()


def main() -> None:
    """Write the notes for the requested version to stdout."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("changelog", type=Path, help="Path to CHANGELOG.md")
    parser.add_argument("version", help="Version without a v prefix")
    args = parser.parse_args()

    print(extract_release_notes(args.changelog.read_text(), args.version))


if __name__ == "__main__":
    main()
