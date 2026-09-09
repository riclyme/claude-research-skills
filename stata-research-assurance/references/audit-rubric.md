# Audit Severity and Reproducibility Rubric

Assign severity by the likely effect on the scientific claim, not by how easy the code is to fix.

## Severity levels

### `FATAL`

The current principal result cannot be interpreted as evidence for the stated claim.

Examples:

- wrong unit of analysis or uncontrolled duplicate amplification;
- outcome, future, or post-treatment information leaks into a predictor;
- incorrect dependent variable or reversed focal-variable coding;
- merge or sample construction creates a materially different population than specified;
- key result comes from stale or manually edited data that cannot be reconstructed;
- reported table does not originate from the claimed model or audited run;
- model cannot be reproduced and the discrepancy changes the substantive conclusion;
- fabricated, hard-coded, or copied result values;
- identification assumption is contradicted by the implementation.

Required disposition: withdraw or suspend the affected claim until corrected and rerun from an earlier trusted point.

### `MAJOR`

The result may remain usable, but magnitude, uncertainty, significance, or generalizability could materially change.

Examples:

- unexplained sample attrition or model-to-model N change;
- incorrect or unjustified fixed effects, clustering level, weights, lag, or event window;
- substantial unmatched records or time-invalid crosswalks;
- inconsistent missing-data or outlier treatment;
- AI-generated covariate lacks representative validation or measurement-error analysis;
- estimator convergence, separation, weak-cluster, or collinearity issue not addressed;
- data/code version mismatch that can be repaired but has not been reconciled;
- robustness claims based on significance-driven specification search.

Required disposition: rerun and reassess the affected claim before publication or submission.

### `MODERATE`

The issue limits confidence or interpretation but is unlikely to reverse the principal conclusion by itself.

Examples:

- incomplete provenance or package-version reporting;
- weak documentation of a defensible transformation;
- missing subgroup diagnostics for an otherwise validated classifier;
- insufficient independent checks;
- table notes omit important sample or estimator details;
- numerical differences within a plausible tolerance but not explained.

Required disposition: document, test, and resolve where feasible.

### `MINOR`

The issue affects maintainability or presentation rather than the current numerical conclusion.

Examples:

- inconsistent labels or file naming;
- redundant code;
- non-portable but correct path handling;
- missing comments for a transparent step;
- output formatting defects.

Required disposition: repair in normal code maintenance.

### `INFORMATIONAL`

A verified observation, best-practice suggestion, or limitation without a detected implementation error.

## Reproducibility statuses

Use exactly one primary status.

### `NOT ASSESSABLE`

The available evidence is insufficient to attempt reproduction or audit. State what is missing.

### `NOT REPRODUCIBLE`

The specified run cannot be completed or does not regenerate the reference result, and the discrepancy remains unresolved.

### `CHECKPOINT REPLICATED ONLY`

The result can be regenerated from a supplied final/intermediate analytic file, but the upstream raw-to-checkpoint pipeline was not reproduced.

### `REPRODUCIBLE WITH DISCREPANCIES`

The pipeline runs from the stated starting point, but one or more reference outputs differ beyond the predeclared tolerance.

### `REPRODUCIBLE BUT NOT VERIFIED`

The reference outputs are regenerated, but the design, measurement, or implementation has not received sufficient independent validation.

### `VERIFIED WITH QUALIFICATIONS`

The pipeline reproduces and the high-value design, data, code, and inference checks pass, with disclosed moderate/minor limitations.

### `READY FOR CLAIM-SPECIFIC USE`

The exact claim is supported by a reproduced pipeline, verified implementation, adequate measurement validation, and appropriate inference under the stated assumptions. This status applies to named claims, not to an entire project without qualification.

## Finding format

Every issue row must include:

- `issue_id`;
- `severity`;
- `domain`;
- `affected_claim_or_model`;
- `file_and_location`;
- `evidence`;
- `scientific_risk`;
- `required_test_or_fix`;
- `acceptance_criterion`;
- `status`;
- `owner`;
- `date_opened`;
- `date_closed`.

## Acceptance criteria

Write acceptance criteria before the rerun. Examples:

- “A `1:1 firm_id year` merge produces no duplicated master keys and fewer than 0.5% unresolved master-only records, all listed in adjudication.csv.”
- “The independently implemented main coefficient agrees within `1e-8` and the clustered standard error within `1e-6`.”
- “Every table coefficient matches the machine-readable model registry to the displayed rounding precision.”
- “The AI-label FPR confidence interval and downstream sensitivity analysis do not cross the predeclared substantive-decision boundary.”

Do not define success as “the coefficient remains significant.”
