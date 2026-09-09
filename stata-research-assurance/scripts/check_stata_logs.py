#!/usr/bin/env python3
"""Scan Stata text logs for errors, high-risk warnings, and completion markers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ERROR_PATTERNS = {
    "stata_return_code": re.compile(r"\br\(\d+\);", re.IGNORECASE),
    "file_not_found": re.compile(r"\b(file|path).*(not found|does not exist)", re.IGNORECASE),
    "no_observations": re.compile(r"\bno observations\b", re.IGNORECASE),
    "convergence_failure": re.compile(
        r"(convergence not achieved|not concave|could not calculate numerical derivatives)",
        re.IGNORECASE,
    ),
    "syntax_problem": re.compile(
        r"(invalid syntax|unmatched quote|ambiguous abbreviation|too few variables specified)",
        re.IGNORECASE,
    ),
}

WARNING_PATTERNS = {
    "omitted_or_collinear": re.compile(r"\b(omitted|collinear)\b", re.IGNORECASE),
    "singleton": re.compile(r"\bsingleton", re.IGNORECASE),
    "perfect_prediction": re.compile(r"perfect prediction|complete separation", re.IGNORECASE),
    "few_clusters": re.compile(r"few clusters|small number of clusters", re.IGNORECASE),
    "missing_values_generated": re.compile(r"missing values generated", re.IGNORECASE),
}

COMPLETION_PATTERN = re.compile(r"ASSURANCE\|COMPLETE")


def scan(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    for number, line in enumerate(lines, start=1):
        for name, pattern in ERROR_PATTERNS.items():
            if pattern.search(line):
                errors.append({"type": name, "line": number, "text": line.strip()[:500]})
        for name, pattern in WARNING_PATTERNS.items():
            if pattern.search(line):
                warnings.append({"type": name, "line": number, "text": line.strip()[:500]})

    return {
        "file": str(path),
        "completion_marker": bool(COMPLETION_PATTERN.search(text)),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Log files or directories")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--allow-no-completion-marker",
        action="store_true",
        help="Do not fail when a scanned log lacks ASSURANCE|COMPLETE",
    )
    args = parser.parse_args()

    files: list[Path] = []
    for candidate in args.paths:
        candidate = candidate.expanduser()
        if candidate.is_dir():
            files.extend(sorted(candidate.rglob("*.log")))
        elif candidate.is_file():
            files.append(candidate)
        else:
            parser.error(f"Path does not exist: {candidate}")

    if not files:
        parser.error("No .log files found")

    results = [scan(path) for path in files]
    error_count = sum(len(item["errors"]) for item in results)  # type: ignore[arg-type]
    warning_count = sum(len(item["warnings"]) for item in results)  # type: ignore[arg-type]
    completed = any(bool(item["completion_marker"]) for item in results)

    report = {
        "files_scanned": len(results),
        "error_count": error_count,
        "warning_count": warning_count,
        "completion_marker_found": completed,
        "results": results,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"Scanned {len(results)} log(s): {error_count} error hit(s), "
            f"{warning_count} warning hit(s), completion={completed}"
        )
        for item in results:
            print(f"\n[{item['file']}] completion={item['completion_marker']}")
            for finding in item["errors"]:  # type: ignore[assignment]
                print(f"  ERROR L{finding['line']} {finding['type']}: {finding['text']}")
            for finding in item["warnings"]:  # type: ignore[assignment]
                print(f"  WARN  L{finding['line']} {finding['type']}: {finding['text']}")

    if error_count:
        return 2
    if not completed and not args.allow_no_completion_marker:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
