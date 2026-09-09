# Analysis Specification

## Document control

- Project:
- Specification version:
- Freeze date:
- Author/approver:
- Status: `DRAFT | FROZEN | AMENDED`
- Code repository and commit:
- Related manuscript/table:

## 1. Research question and estimand

- Research question:
- Theoretical construct(s):
- Target estimand:
- Associational or causal interpretation:
- Identification assumptions:
- Claims this design can support:
- Claims this design cannot support:

## 2. Unit, population, and sample

- Unit of analysis:
- Unique key:
- Population:
- Date range:
- Inclusion rules:
- Exclusion rules:
- Expected row count and tolerance:
- Expected entity count and tolerance:
- Panel balanced/unbalanced:

## 3. Data sources and lineage

| source_id | file/provider | immutable version/date | unit | key | expected rows | role | notes |
|---|---|---|---|---|---:|---|---|
| | | | | | | | |

## 4. Merge and crosswalk plan

| merge_id | master | using | key(s) | cardinality | temporal validity rule | unmatched policy | expected match rate |
|---|---|---|---|---|---|---|---:|
| | | | | | | | |

## 5. Variables

Attach `variable_dictionary.csv`.

- Outcome(s):
- Focal predictor(s):
- Moderator(s):
- Mediator(s):
- Control variables:
- Instrument(s):
- Fixed-effect identifiers:
- Cluster identifier(s):
- Weights/exposure/offset:
- AI/ML-generated variables:

## 6. Timing and information set

- Observation date convention:
- Outcome window:
- Predictor measurement window:
- Lag/lead rules:
- Event-date selection rule:
- Fiscal/calendar alignment:
- Future-information prohibition:
- Post-treatment-variable assessment:

## 7. Missing data and outliers

- Missingness definition, including extended Stata missing codes:
- Complete-case or imputation rule:
- Imputation model and validation, if any:
- Winsorization/trimming rule:
- Transformations and units:

## 8. Main estimator

- Model ID:
- Estimator/link:
- Equation:
- Estimation sample flag:
- Fixed effects:
- Clustering/variance estimator:
- Weights/exposure/offset:
- Software command and required package:
- Interpretation of focal coefficient:

## 9. Theory-driven robustness tests

| model_id | change from main model | substantive rationale | expected diagnostic value | decision rule |
|---|---|---|---|---|
| | | | | |

Do not list models solely because they might improve significance.

## 10. AI/ML measurement plan

For each generated variable:

- latent construct and proxy relationship:
- model/version/prompt:
- information available to model:
- gold-sample design:
- validation metrics:
- subgroup/time validation:
- threshold/aggregation rule:
- repeated-run/model sensitivity:
- downstream measurement-aware inference plan:

## 11. Expected sample flow

Attach `expected_sample_flow.csv`.

## 12. Required outputs

- final analytic file:
- data audit report:
- model registry:
- tables:
- figures:
- manuscript numbers to reconcile:

## 13. Blockers

| blocker_id | unresolved question | scientific consequence | owner | required decision |
|---|---|---|---|---|
| | | | | |

## 14. Approval

- Approved by:
- Approval date:
- Allowed implementation discretion:
- Prohibited implementation changes:
