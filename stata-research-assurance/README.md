# Stata Research Assurance Skill

A portable Agent Skill for building, auditing, reproducing, and validating Stata 19 empirical-research pipelines.

## What it does

The skill provides five coordinated modes:

- `FREEZE` — lock the estimand, sample, variables, timing, estimator, fixed effects, and clustering before production coding;
- `BUILD` — generate modular Stata code with assertions, logs, row-count reconciliation, merge diagnostics, and machine-readable outputs;
- `AUDIT` — adversarially inspect data lineage, code, logs, analytic data, tables, and manuscript claims;
- `REPRODUCE` — rerun from the earliest immutable inputs and explain any discrepancy;
- `AI-MEASURE` — validate LLM/classifier/topic/matching outputs and assess their downstream measurement-error implications.

## Install

### Codex CLI or IDE

Copy or symlink this directory into a Codex skill location, for example:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "/absolute/path/to/stata-research-assurance" \
  "$HOME/.agents/skills/stata-research-assurance"
```

Codex also scans a repository's `.agents/skills/` directory. Restart Codex if the skill does not appear.

### ChatGPT desktop

Open **Skills** in the sidebar and add the `stata-research-assurance` directory. The required entry point is `SKILL.md`.

### Other Agent Skills-compatible clients

Install the directory through the client's skill installer or place it in the client's supported skill folder. The skill follows the open Agent Skills directory format.

## Invoke

```text
Use $stata-research-assurance in FREEZE mode for this panel project.
```

```text
Use $stata-research-assurance in BUILD mode. Generate Stata 19 code from analysis_spec.md without changing the design.
```

```text
Use $stata-research-assurance in AUDIT and REPRODUCE modes on this do/log/data bundle.
```

```text
Use $stata-research-assurance in AI-MEASURE mode for this LLM-coded variable.
```

In ChatGPT, select the skill with `@` when available. In Codex, mention it with `$stata-research-assurance`.

## Helper scripts

All scripts use the Python standard library.

```bash
python scripts/validate_skill.py
python scripts/scaffold_stata_project.py /path/to/new-project
python scripts/build_manifest.py /path/to/project --output audit/input_manifest.csv
python scripts/check_audit_bundle.py /path/to/audit-bundle
python scripts/check_stata_logs.py /path/to/project/logs
```

## Pilot status

Version `0.1.0` is intentionally labeled a pilot. Test it on a complete project, record false alarms and missed checks, then revise the workflow before treating it as a stable lab standard.

## Methodological basis

See `references/methodological-foundation.md`. The skill distinguishes transparent measurement construction, downstream inference with generated covariates, and reproducible data/code engineering.
