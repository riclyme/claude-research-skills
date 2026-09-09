---
name: stata-research-assurance
description: Build, audit, reproduce, and validate Stata 19 empirical-research pipelines. Use when the user asks to freeze an econometric design, generate modular do-files, inspect Stata code/logs/data, reconcile changing results, check merges, sample attrition, variable timing, fixed effects, clustering, lags, or validate AI/ML-generated covariates and matching labels. Do not use for a one-line Stata syntax question unless the user requests the full assurance workflow.
license: MIT
compatibility: Works with ChatGPT, Codex, Claude Code, and other Agent Skills-compatible clients. Stata 19 is expected for execution; Python 3.10+ is optional for the bundled helper scripts.
metadata:
  author: Yue Zhao
  maintainer: riclyme
  version: "0.1.0"
  status: pilot
---

# Stata Research Assurance

Use this skill to turn an empirical research design into an auditable Stata pipeline and to investigate whether reported results are correct, stable, and reproducible.

The skill governs the **process**. It does not decide the theory, estimand, identification strategy, fixed effects, controls, lag structure, or clustering level without project-specific justification.

## Core principle

Separate four questions that are often confused:

1. **Design validity** — Is the theoretical construct, estimand, sample, and identification strategy defensible?
2. **Measurement validity** — Are constructed, matched, text-derived, or AI-generated variables reliable proxies?
3. **Computational validity** — Does the code correctly transform the intended inputs into the intended analytic data and estimates?
4. **Inferential validity** — Do the estimator, uncertainty calculations, and conclusions account for the data-generating and measurement process?

A successful Stata run establishes none of these by itself.

## Modes

Select the narrowest mode that fulfills the request. State the selected mode at the start of the work product.

### `FREEZE`

Use before writing or materially revising code. Convert the research plan into a locked, reviewable specification.

### `BUILD`

Generate or revise a modular Stata 19 pipeline that implements a frozen specification and includes machine-checkable safeguards.

### `AUDIT`

Adversarially inspect an existing specification, data lineage, do-files, logs, analytic data, and reported results. Do not assume that code is correct because it ran.

### `REPRODUCE`

Rebuild results from the earliest available immutable inputs in a clean environment, then reconcile every difference from the reference results.

### `AI-MEASURE`

Validate variables or records produced by an LLM, classifier, embedding, topic model, entity matcher, algorithmic crosswalk, or other estimated upstream model. Run this mode in addition to `BUILD`, `AUDIT`, or `REPRODUCE` whenever an AI/ML-generated variable enters the analysis.

## Non-negotiable rules

1. Never choose, drop, lag, transform, winsorize, interact, or redefine a variable because doing so improves statistical significance.
2. Never alter the sample, fixed effects, clustering level, estimator, or control set without documenting the substantive reason and versioning the specification.
3. Treat raw data as read-only. Never overwrite, clean in place, or save derived variables into a raw file.
4. Preserve a traceable chain from raw input to intermediate data, final analytic data, model output, table, and manuscript claim.
5. Do not silently resolve a material ambiguity. Record it as a blocker or request a decision.
6. Do not use overall predictive accuracy as proof that an AI-generated covariate is safe for downstream inference.
7. Do not call a result reproduced when only the final analytic file was reused. Full reproduction starts from the earliest available immutable input.
8. Do not accept an AI narrative summary as evidence. Evidence consists of files, code, logs, counts, checksums, estimates, and explicit assumptions.
9. Keep builder and auditor roles separate. In `AUDIT`, challenge the implementation rather than defend prior choices.
10. Use the user's language for explanation. Keep code, file names, and machine-readable outputs in English unless requested otherwise.

## Mode selection

Apply these defaults:

- A request to “write the Stata code” starts with `FREEZE`, then proceeds to `BUILD` after unresolved blockers are cleared.
- A bundle containing do-files and logs starts in `AUDIT`.
- A claim that “the result changed,” “cannot be replicated,” or “flipped sign” starts in `REPRODUCE` plus `AUDIT`.
- A variable created by AI/ML, text analysis, algorithmic matching, or probabilistic classification automatically activates `AI-MEASURE`.
- A one-off syntax request remains a normal Stata answer unless the user explicitly asks for assurance, audit, or reproducibility.

---

# `FREEZE` mode

## Required inputs

Identify or request only genuinely unresolved items:

- research question and theoretical estimand;
- unit of analysis and unique key;
- population, sample period, and inclusion/exclusion rules;
- outcome, focal predictors, moderators/mediators, controls, instruments, and constructed variables;
- timing convention, event date, lag/lead rules, and allowable information set;
- estimator and link function;
- fixed effects and clustering level;
- main model and theory-driven robustness tests;
- missing-data policy, outlier policy, and transformations;
- expected input files, merge keys, cardinalities, and approximate row counts;
- manuscript claims or reference tables that the code must reproduce;
- all AI/ML-generated or algorithmically matched variables.

## Required outputs

Create:

1. `analysis_spec.md` using `assets/analysis-spec-template.md`.
2. `variable_dictionary.csv` with one row per analytic variable.
3. `expected_sample_flow.csv` with each intended filter and expected direction of row-count change.
4. `decision_log.md` for amendments after the freeze date.

Mark each specification item as `LOCKED`, `PROVISIONAL`, or `BLOCKED`.

## Freeze gate

Do not proceed to production code when any blocker could change the unit of analysis, sample, variable meaning, timing, estimator, fixed effects, or clustering level. Boilerplate and diagnostics may be drafted, but substantive model code must remain explicitly provisional.

After the specification is frozen, changes require a dated amendment in `decision_log.md` containing:

- previous rule;
- new rule;
- substantive reason;
- affected files/models;
- whether the change was made before or after viewing results.

---

# `BUILD` mode

Read `references/stata-code-standards.md` before producing code.

## Project structure

Generate or preserve this modular structure unless the project already has a documented equivalent:

```text
analysis_spec.md
variable_dictionary.csv
decision_log.md
code/
  00_master.do
  01_import_raw.do
  02_clean_merge.do
  03_construct_variables.do
  04_descriptives.do
  05_main_models.do
  06_robustness.do
  07_tables_figures.do
  90_data_audit.do
  91_results_audit.do
data/
  raw/                 # immutable
  intermediate/
  final/
logs/
output/
  tables/
  figures/
audit/
```

The helper `scripts/scaffold_stata_project.py` can create this skeleton.

## Build requirements

Every production pipeline must:

- run from a clean Stata 19 session through `00_master.do`;
- use relative paths or one explicitly defined project root;
- open text logs and close them deterministically;
- print the Stata version, run timestamp, working directory, and key package versions;
- set and report seeds for stochastic procedures;
- verify input existence before use;
- assert unique keys before merges, panel declarations, and reshapes;
- record row counts before and after every merge, append, reshape, collapse, filter, and deduplication;
- retain sample flags instead of prematurely dropping observations;
- verify ranges, coding direction, missingness, and invariants for key variables;
- verify time ordering before generating lags, leads, or event windows;
- report estimation N, number of clusters, fixed-effect dimensions, and omitted/singleton observations;
- save final analytic data separately from raw and intermediate data;
- produce a machine-readable result extract rather than relying on copied console output;
- end with a unique completion marker only after every required module succeeds.

## Prohibited patterns

Do not use these without a documented, reviewed exception:

- `merge ..., force`, `append ..., force`, `destring ..., force`;
- unexplained `capture` around data construction or estimation;
- `drop if`, `keep if`, or `duplicates drop` without before/after counts and a rule from the frozen specification;
- hard-coded coefficients, standard errors, p-values, N, or table cells;
- absolute user-specific paths inside shared production code;
- overwriting raw files;
- manually edited analytic data without a reproducible adjudication file;
- searching model variants until a desired sign or p-value appears.

## Build completion package

Return or save:

- all do-files;
- all logs;
- input and output manifests with SHA-256 hashes;
- analytic-data dictionary;
- actual sample attrition table;
- merge diagnostics;
- model registry;
- machine-readable estimates;
- unresolved warning register.

---

# `AUDIT` mode

Read `references/audit-rubric.md` before assigning severity.

## Minimum evidence bundle

Prefer:

- frozen specification and decision log;
- all do-files actually used;
- complete text logs from a clean run;
- raw/intermediate/final file manifests;
- final analytic data or sufficient extracts for independent checks;
- reference tables, manuscript results, and the code that produced them;
- AI measurement validation files when applicable.

If evidence is missing, continue with the available material but explicitly bound every conclusion. Never infer that an absent log, file, or check passed.

## Audit sequence

Audit in this order:

1. **Provenance and versioning** — identify the exact inputs, code commit, software version, package versions, seeds, and run date.
2. **Unit and keys** — verify the unit of analysis, unique keys, duplicate policy, panel structure, and entity identifiers.
3. **Data lineage** — trace every final variable to source fields and transformations.
4. **Merges and crosswalks** — verify cardinality, unmatched records, duplicate amplification, temporal validity, and adjudications.
5. **Sample construction** — reconstruct attrition and explain every model-to-model N change.
6. **Variable construction** — verify formulas, units, signs, scaling, winsorization, missing-value handling, and denominator definitions.
7. **Timing** — verify lags, leads, event windows, fiscal/calendar alignment, and absence of future or post-treatment information.
8. **Estimator** — verify model family, likelihood/estimand, weights, offsets/exposure, fixed effects, clustering, and finite-sample issues.
9. **Results pipeline** — verify that stored estimates, tables, figures, and manuscript numbers come from the audited run.
10. **Independent checks** — recompute high-value counts and at least one main result through an independent code path when feasible.
11. **Stability** — run only theory- or design-motivated perturbations; do not equate specification fishing with robustness.
12. **AI measurement** — apply `AI-MEASURE` when any upstream algorithm generated an analytic variable.

## Required audit outputs

Create:

- `AUDIT_REPORT.md` using `assets/audit-report-template.md`;
- `ISSUE_REGISTER.csv` using `assets/issue-register-template.csv`;
- `REQUIRED_RERUNS.do` containing only checks or reruns needed to resolve findings;
- `REPRODUCIBILITY_STATUS.md` with one of the statuses defined in `references/audit-rubric.md`.

For every finding, report:

- severity;
- affected claim/model/file;
- exact evidence;
- why it matters;
- deterministic test or rerun;
- acceptance criterion;
- current disposition.

Do not write “looks correct” without naming the evidence and scope of the check.

---

# `REPRODUCE` mode

## Reproduction protocol

1. Record the reference commit, Stata version, package versions, operating system, and expected outputs.
2. Create SHA-256 manifests with `scripts/build_manifest.py`.
3. Start a clean Stata session.
4. Clear or move prior derived outputs; never reuse stale intermediates unless testing an explicitly labeled checkpoint reproduction.
5. Run only `00_master.do`.
6. Scan logs with `scripts/check_stata_logs.py`.
7. Compare output files, row counts, model N, coefficients, standard errors, and table cells with the reference run.
8. Classify every difference as input drift, code drift, environment drift, stochastic variation, nondeterminism, or unexplained discrepancy.
9. Independently recompute the principal descriptive counts and at least one main coefficient when feasible.
10. Report exact equality, tolerance-based equality, or failure. State tolerances before comparing results.

A checkpoint-only rerun may establish **result replication from the checkpoint**, but not **full pipeline reproduction**.

---

# `AI-MEASURE` mode

Read `references/ai-generated-measures.md` before analysis.

## First classify the generated object

Label it as one or more of:

- binary label;
- multiclass label;
- continuous score or rating;
- entity match, crosswalk, or record linkage;
- topic share, embedding, similarity, or aggregated index;
- synthetic or imputed data;
- AI-generated code only.

AI-generated code alone primarily creates a computational-validity problem. AI-generated data or covariates additionally create measurement- and inference-validity problems.

## Required validation evidence

Request or construct, when applicable:

- frozen construct definition and coding rubric;
- model/provider/version, exact prompt, temperature/seed where available, date, and raw response;
- independent holdout or human-coded gold sample;
- coder identities or roles, agreement, and adjudication rule;
- confusion matrix, false-positive rate, false-negative rate, precision, recall, prevalence, and uncertainty;
- calibration and repeated-run stability for scores/probabilities;
- subgroup, time-period, language, industry, or source-specific error rates;
- threshold and alternate-model sensitivity;
- count of source units supporting each observation-level index;
- audit trail for ambiguous matches and manual corrections;
- naive and measurement-aware downstream estimates.

## Inference rule

Do not certify ordinary two-step regression merely because prediction accuracy, correlation, or out-of-sample RMSE is strong. Treat the generated variable as an estimated proxy and evaluate whether its measurement error is negligible relative to downstream sampling uncertainty.

For common label or index settings, report the diagnostics and consider bias-corrected or joint-model approaches described in `references/ai-generated-measures.md`. For an upstream model not covered by a validated correction, run transparent sensitivity bounds or a defensible measurement model rather than inventing a formula.

## Leakage rule

Flag as critical when the upstream model had access to:

- the downstream outcome;
- future information relative to the observation date;
- post-treatment variables;
- test-set labels during prompt/model/threshold tuning;
- manuscript conclusions or desired classifications that could influence labeling.

---

# Stop conditions

Stop the affected pipeline stage and report a blocker when any of the following occurs:

- an expected unique key is not unique;
- a merge cardinality differs from the specification;
- unmatched or multiplied records are unexplained;
- the unit of analysis changes silently;
- a lag or event date cannot be unambiguously aligned;
- a key variable is overwritten or changes coding direction;
- a sample rule cannot be traced to the frozen specification;
- estimation N changes without a reconciled reason;
- the requested fixed effect or cluster identifier is unavailable or invalid;
- Stata returns an error, fails to converge, or does not print the completion marker;
- a final table cannot be traced to stored estimates from the audited run;
- an AI-generated measure lacks enough validation to support the claimed use.

Continue unaffected diagnostic work where possible, but do not substitute an assumption for a required decision.

# Final response contract

Conclude each use with:

1. selected mode(s);
2. work completed;
3. evidence inspected or generated;
4. reproducibility status;
5. highest-severity unresolved issue;
6. exact next executable action.

Use concise prose for the summary and place detailed evidence in the required artifacts.

# Invocation examples

- `Use $stata-research-assurance in FREEZE mode for this panel-data project.`
- `Use $stata-research-assurance in BUILD mode. Generate Stata 19 do-files from analysis_spec.md without changing the design.`
- `Use $stata-research-assurance in AUDIT mode on these do-files, logs, data manifests, and manuscript tables.`
- `Use $stata-research-assurance in REPRODUCE mode. The old and new coefficients have opposite signs.`
- `Use $stata-research-assurance in AI-MEASURE mode for an LLM-coded binary variable and its downstream regressions.`

# Supporting files

- Stata implementation rules: `references/stata-code-standards.md`
- Audit severity and readiness rubric: `references/audit-rubric.md`
- AI/ML-generated-variable protocol: `references/ai-generated-measures.md`
- Methodological foundation: `references/methodological-foundation.md`
- Specification template: `assets/analysis-spec-template.md`
- Audit report template: `assets/audit-report-template.md`
