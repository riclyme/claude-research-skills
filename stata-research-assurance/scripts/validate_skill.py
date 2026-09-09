#!/usr/bin/env python3
"""Validate the minimum Agent Skills structure using only the Python standard library."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")

    result: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        if not raw_line or raw_line.startswith(" ") or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.skill_dir.expanduser().resolve()
    skill_file = root / "SKILL.md"
    errors: list[str] = []

    if not skill_file.is_file():
        errors.append("Missing SKILL.md")
    else:
        try:
            metadata = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
            name = metadata.get("name", "")
            description = metadata.get("description", "")
            if not name:
                errors.append("Missing required frontmatter field: name")
            elif not NAME_PATTERN.fullmatch(name):
                errors.append("name must contain lowercase letters, numbers, and single hyphens only")
            elif len(name) > 64:
                errors.append("name exceeds 64 characters")
            if name and name != root.name:
                errors.append(f"name '{name}' does not match directory '{root.name}'")
            if not description:
                errors.append("Missing required frontmatter field: description")
            elif len(description) > 1024:
                errors.append("description exceeds 1024 characters")
            if skill_file.read_text(encoding="utf-8").count("\n") > 500:
                errors.append("SKILL.md exceeds the recommended 500 lines")
        except ValueError as exc:
            errors.append(str(exc))

    for optional in ["scripts", "references", "assets"]:
        path = root / optional
        if path.exists() and not path.is_dir():
            errors.append(f"{optional} exists but is not a directory")

    if errors:
        print("Skill validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 2

    print(f"Skill validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
