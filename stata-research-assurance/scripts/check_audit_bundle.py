#!/usr/bin/env python3
"""Check whether a directory contains the minimum evidence for a Stata audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_SINGLE = ["analysis_spec.md", "variable_dictionary.csv"]
REQUIRED_GLOBS = {
    "stata_do_files": "**/*.do",
    "stata_logs": "**/*.log",
}
RECOMMENDED_GLOBS = {
    "decision_log": "**/decision_log.md",
    "manifest": "**/*manifest*.csv",
    "analytic_data": "**/*.dta",
    "reference_results": "**/*.{csv,xlsx,docx,tex,html}",
    "ai_validation": "**/*validation*.csv",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.bundle.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Bundle directory does not exist: {root}")

    required_missing: list[str] = []
    required_found: dict[str, list[str]] = {}
    recommended_found: dict[str, list[str]] = {}

    for name in REQUIRED_SINGLE:
        path = root / name
        if path.is_file():
            required_found[name] = [path.relative_to(root).as_posix()]
        else:
            required_missing.append(name)

    for label, pattern in REQUIRED_GLOBS.items():
        matches = sorted(p.relative_to(root).as_posix() for p in root.glob(pattern) if p.is_file())
        required_found[label] = matches
        if not matches:
            required_missing.append(label)

    for label, pattern in RECOMMENDED_GLOBS.items():
        # pathlib does not support brace expansion; handle the reference-results case explicitly.
        if "{" in pattern:
            matches: list[str] = []
            for suffix in ["*.csv", "*.xlsx", "*.docx", "*.tex", "*.html"]:
                matches.extend(
                    p.relative_to(root).as_posix()
                    for p in root.glob(f"**/{suffix}")
                    if p.is_file()
                )
            matches = sorted(set(matches))
        else:
            matches = sorted(p.relative_to(root).as_posix() for p in root.glob(pattern) if p.is_file())
        recommended_found[label] = matches

    report = {
        "bundle": str(root),
        "audit_ready": not required_missing,
        "required_missing": required_missing,
        "required_found": required_found,
        "recommended_found": recommended_found,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Audit ready: {report['audit_ready']}")
        if required_missing:
            print("Missing required evidence:")
            for item in required_missing:
                print(f"  - {item}")
        print("Recommended evidence present:")
        for label, matches in recommended_found.items():
            print(f"  - {label}: {len(matches)} file(s)")

    return 0 if not required_missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
