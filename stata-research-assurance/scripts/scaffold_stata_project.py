#!/usr/bin/env python3
"""Create an auditable Stata 19 project skeleton without overwriting existing work."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MODULES = [
    "00_master.do",
    "01_import_raw.do",
    "02_clean_merge.do",
    "03_construct_variables.do",
    "04_descriptives.do",
    "05_main_models.do",
    "06_robustness.do",
    "07_tables_figures.do",
    "90_data_audit.do",
    "91_results_audit.do",
]

MASTER = r'''version {stata_version}
clear all
set more off
set varabbrev off
set seed 20260909

capture log close _all
local runstamp = subinstr("`c(current_date)'_`c(current_time)'", ":", "-", .)
local runstamp = subinstr("`runstamp'", " ", "_", .)
log using "logs/master_`runstamp'.log", replace text name(master)

di as text "ASSURANCE|START"
di as text "ASSURANCE|STATA_VERSION|`c(stata_version)'"
di as text "ASSURANCE|DATE|`c(current_date)'"
di as text "ASSURANCE|TIME|`c(current_time)'"
di as text "ASSURANCE|PWD|`c(pwd)'"

foreach module in 01_import_raw 02_clean_merge 03_construct_variables ///
    04_descriptives 05_main_models 06_robustness 07_tables_figures ///
    90_data_audit 91_results_audit {{
    di as text "ASSURANCE|MODULE_START|`module'"
    do "code/`module'.do"
    if _rc {{
        di as error "ASSURANCE|MODULE_FAIL|`module'|RC=" _rc
        log close master
        exit _rc
    }}
    di as result "ASSURANCE|MODULE_PASS|`module'"
}}

di as result "ASSURANCE|COMPLETE"
log close master
'''

MODULE_TEMPLATE = r'''version {stata_version}

* Module: {module}
* Implement only rules documented in analysis_spec.md.
* Do not overwrite raw data or silently suppress errors.

di as text "ASSURANCE|PLACEHOLDER|{module}"
'''


def copy_template(skill_root: Path, asset_name: str, destination: Path) -> None:
    source = skill_root / "assets" / asset_name
    if not source.is_file():
        raise FileNotFoundError(f"Bundled template missing: {source}")
    shutil.copyfile(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--stata-version", default="19.0")
    parser.add_argument(
        "--force-empty",
        action="store_true",
        help="Allow creation in an existing but empty directory; never overwrites files",
    )
    args = parser.parse_args()

    root = args.output_dir.expanduser().resolve()
    if root.exists():
        if not root.is_dir():
            parser.error(f"Output exists and is not a directory: {root}")
        if any(root.iterdir()) or not args.force_empty:
            parser.error(
                "Output directory already exists. Use a new path; --force-empty only permits an empty directory."
            )
    else:
        root.mkdir(parents=True)

    for relative in [
        "code",
        "data/raw",
        "data/intermediate",
        "data/final",
        "logs",
        "output/tables",
        "output/figures",
        "audit",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parents[1]
    copy_template(skill_root, "analysis-spec-template.md", root / "analysis_spec.md")
    copy_template(skill_root, "variable-dictionary-template.csv", root / "variable_dictionary.csv")
    copy_template(skill_root, "expected-sample-flow-template.csv", root / "expected_sample_flow.csv")
    copy_template(skill_root, "issue-register-template.csv", root / "audit" / "ISSUE_REGISTER.csv")
    copy_template(skill_root, "audit-report-template.md", root / "audit" / "AUDIT_REPORT.md")

    (root / "decision_log.md").write_text(
        "# Decision Log\n\nRecord all post-freeze changes, reasons, affected files, and whether results had been viewed.\n",
        encoding="utf-8",
    )

    for module in MODULES:
        path = root / "code" / module
        if module == "00_master.do":
            content = MASTER.format(stata_version=args.stata_version)
        else:
            content = MODULE_TEMPLATE.format(
                stata_version=args.stata_version, module=module.removesuffix(".do")
            )
        path.write_text(content, encoding="utf-8")

    for keep in [
        "data/raw/.gitkeep",
        "data/intermediate/.gitkeep",
        "data/final/.gitkeep",
        "logs/.gitkeep",
        "output/tables/.gitkeep",
        "output/figures/.gitkeep",
    ]:
        (root / keep).touch()

    print(f"Created Stata research-assurance skeleton at {root}")
    print("Next: complete and freeze analysis_spec.md before implementing substantive code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
