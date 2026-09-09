#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest for a research directory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path, output: Path, excludes: set[str]) -> Iterable[Path]:
    output_resolved = output.resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.resolve() == output_resolved:
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel == item or rel.startswith(f"{item.rstrip('/')}/") for item in excludes):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory to hash recursively")
    parser.add_argument("--output", type=Path, default=Path("manifest.csv"))
    parser.add_argument(
        "--exclude",
        action="append",
        default=[".git", ".DS_Store"],
        help="Relative path or directory prefix to exclude; may be repeated",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Root directory does not exist: {root}")

    output = args.output.expanduser()
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | int]] = []
    for path in iter_files(root, output, set(args.exclude)):
        stat = path.stat()
        rows.append(
            {
                "relative_path": path.relative_to(root).as_posix(),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
                "sha256": sha256_file(path),
            }
        )

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "size_bytes", "modified_utc", "sha256"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} manifest rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
