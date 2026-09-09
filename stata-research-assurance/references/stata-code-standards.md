# Stata 19 Code Standards

Use these standards for production empirical research code. Adapt commands to the project, but preserve the controls they implement.

## 1. Deterministic master entry point

`code/00_master.do` is the only production entry point.

```stata
version 19.0
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

* Define one project root if relative execution cannot be guaranteed.
* global PROJECT_ROOT "/path/to/project"

foreach module in ///
    01_import_raw ///
    02_clean_merge ///
    03_construct_variables ///
    04_descriptives ///
    05_main_models ///
    06_robustness ///
    07_tables_figures ///
    90_data_audit ///
    91_results_audit {

    di as text "ASSURANCE|MODULE_START|`module'"
    do "code/`module'.do"
    if _rc {
        di as error "ASSURANCE|MODULE_FAIL|`module'|RC=" _rc
        log close master
        exit _rc
    }
    di as result "ASSURANCE|MODULE_PASS|`module'"
}

di as result "ASSURANCE|COMPLETE"
log close master
```

Do not put `capture` around the module execution. A failed module must stop the run.

## 2. Input verification

Before using a file:

```stata
capture confirm file "data/raw/source.dta"
if _rc {
    di as error "ASSURANCE|MISSING_INPUT|data/raw/source.dta"
    exit 601
}
```

Before using a variable:

```stata
foreach v in firm_id year outcome focal_x cluster_id {
    capture confirm variable `v'
    if _rc {
        di as error "ASSURANCE|MISSING_VARIABLE|`v'"
        exit 111
    }
}
```

## 3. Immutable raw data

- Read from `data/raw/`.
- Save only to `data/intermediate/` or `data/final/`.
- Never `save ..., replace` into `data/raw/`.
- Preserve source variable names or create an explicit source-to-analysis crosswalk.
- Record source file checksums outside Stata with `scripts/build_manifest.py`.

## 4. Units and unique keys

Assert the intended key immediately after import and before every merge, reshape, collapse, panel declaration, or event construction.

```stata
isid firm_id year
```

When uniqueness is not expected, verify the intended cardinality explicitly:

```stata
bysort deal_id participant_id: assert _N == 1
bysort firm_id year: gen long n_rows_fy = _N
summarize n_rows_fy, detail
```

Never use `duplicates drop` as a substitute for identifying why duplicates exist.

## 5. Row-count reconciliation

Print standardized counts before and after every structural transformation.

```stata
count
local n_before = r(N)
di as text "ASSURANCE|ROWS_BEFORE|02_clean_merge|`n_before'"

* transformation here

count
local n_after = r(N)
di as text "ASSURANCE|ROWS_AFTER|02_clean_merge|`n_after'"
di as text "ASSURANCE|ROWS_DELTA|02_clean_merge|" (`n_after' - `n_before')
```

For filters, create flags first:

```stata
gen byte eligible_main = inrange(year, 2002, 2021) & !missing(outcome, focal_x)
tab eligible_main, missing
count if !eligible_main
* Keep the flag in the analytic data. Apply `if eligible_main` in estimation.
```

## 6. Merge controls

Verify both sides before merging. Use the cardinality implied by the specification.

```stata
use "data/intermediate/master.dta", clear
isid firm_id year
count
local n_master = r(N)

merge 1:1 firm_id year using "data/intermediate/covariates.dta", gen(_merge_cov)

tab _merge_cov, missing
count if _merge_cov == 1
local master_only = r(N)
count if _merge_cov == 2
local using_only = r(N)
count if _merge_cov == 3
local matched = r(N)

di as text "ASSURANCE|MERGE|covariates|MASTER_ONLY|`master_only'"
di as text "ASSURANCE|MERGE|covariates|USING_ONLY|`using_only'"
di as text "ASSURANCE|MERGE|covariates|MATCHED|`matched'"

* If the frozen specification requires zero using-only records:
* assert _merge_cov != 2
```

Do not drop `_merge*` variables until diagnostics have been saved. For time-varying crosswalks, test date validity rather than merging only on entity ID.

## 7. Missing values and extended missing codes

Stata's numeric missing values sort above all nonmissing numbers. Guard comparisons explicitly.

Wrong:

```stata
gen high_x = x > 10
```

Right:

```stata
gen byte high_x = x > 10 if !missing(x)
```

Report missingness before and after construction:

```stata
misstable summarize outcome focal_x controls
foreach v of varlist outcome focal_x controls {
    count if missing(`v')
    di as text "ASSURANCE|MISSING|`v'|" r(N)
}
```

## 8. Variable construction

For each key variable:

- preserve source fields;
- write one transparent formula;
- label units and direction;
- assert valid ranges;
- compare against hand-checkable examples;
- report summary statistics before and after transformation.

```stata
gen double roa = operating_income / total_assets if total_assets > 0 & !missing(operating_income, total_assets)
assert roa < .
summarize operating_income total_assets roa, detail
```

For binary variables:

```stata
assert inlist(divested, 0, 1) if !missing(divested)
tab divested, missing
```

For winsorization or trimming, preserve the original variable and log the number changed.

## 9. Time, panels, lags, and event windows

Verify uniqueness before `xtset` or `tsset`.

```stata
isid firm_id year
xtset firm_id year
xtdescribe
```

Generate lags only after panel declaration and inspect gaps:

```stata
gen double L1_focal_x = L.focal_x
count if !missing(focal_x) & missing(L1_focal_x)
di as text "ASSURANCE|LAG_MISSING|L1_focal_x|" r(N)
```

Do not replace a true panel lag with `_n-1` unless the specification explicitly defines row-order lagging and gaps are impossible.

For events, save the exact event date and the rule used to select among multiple dates. Assert that pre-treatment variables are measured before treatment.

## 10. Estimation sample reconciliation

Create a model registry with an explicit sample flag for every main model.

```stata
gen byte sample_m1 = eligible_main & !missing(outcome, focal_x, control1, cluster_id)
count if sample_m1
local expected_m1 = r(N)

reghdfe outcome focal_x control1 if sample_m1, absorb(firm_id year) vce(cluster cluster_id)
assert e(N) <= `expected_m1'

di as text "ASSURANCE|MODEL|M1|N|" e(N)
di as text "ASSURANCE|MODEL|M1|CLUSTERS|" e(N_clust)
```

When commands drop singleton observations or collinear variables, report the count and determine whether it affects comparability across models.

## 11. Fixed effects and clustering

- Match fixed effects to the estimand and data structure; do not add them mechanically.
- Verify that focal variables vary within the absorbed dimensions.
- Report the number of clusters and flag few-cluster settings.
- Cluster at the level justified by the dependence structure, not the level yielding preferred p-values.
- For multiway clustering, document each dimension and check software support.
- Do not interpret omitted variables as estimated zeros.

## 12. Weights, exposure, offsets, and nonlinear models

Document what each weight means. Frequency, analytic, probability, and importance weights are not interchangeable.

For count models, distinguish exposure from a control variable. For rare-event or separated binary outcomes, record convergence and separation diagnostics.

## 13. Error handling

Use `capture` only when a failure is expected and immediately inspect `_rc`.

```stata
capture confirm variable optional_var
if _rc == 0 {
    summarize optional_var
}
else {
    di as text "ASSURANCE|OPTIONAL_VARIABLE_ABSENT|optional_var"
}
```

Never use broad `capture` to hide failed merges, failed estimations, missing files, or invalid syntax.

## 14. Results and tables

Store estimates programmatically:

```stata
estimates store M1
matrix b_M1 = e(b)
matrix V_M1 = e(V)
```

Export from stored estimation results. Never retype coefficients or p-values. Save a machine-readable registry containing at least model ID, dependent variable, focal variable, coefficient, standard error, p-value or confidence interval, N, clusters, fixed effects, and code source.

## 15. Independent checks

At minimum:

- recalculate principal counts in `90_data_audit.do` without reading table outputs;
- recompute a principal model through a justified alternative implementation in `91_results_audit.do`;
- compare coefficient, standard error, N, and cluster count under a predeclared tolerance;
- fail the audit module when tolerance is exceeded without explanation.

## 16. Completion marker

Only `00_master.do` prints:

```text
ASSURANCE|COMPLETE
```

The marker must appear after all data, analysis, and audit modules finish successfully. Its absence means the production run is incomplete.
