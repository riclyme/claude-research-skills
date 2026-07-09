---
name: stata-iv-robustness
description: Runs the complete IV endogeneity robustness suite for a binary or count outcome paper — first-stage OLS, Wu-Hausman endogeneity test (ivregress 2sls + estat endogenous), and IV-probit (twostep). Extracts all coefficients from every step using the printcoef pattern and produces formatted output ready for Word table building. Use when you say "run IV robustness", "endogeneity test", "first-stage IV", or "instrument validity check".
author: Yue Zhao (BG Divestment Project, Jul 2026)
version: 1.0.0
argument-hint: "[endog_var] [instruments] [controls] [depvar] [checkpoint_path]"
allowed-tools: ["Read", "Write", "Bash"]
---

# `/stata-iv-robustness` — Full IV Endogeneity Robustness Suite

Runs three steps in sequence and extracts all coefficients for table building:
1. **First-stage OLS**: endogenous variable ~ instruments + controls; reports joint F-test
2. **2SLS + Wu-Hausman**: `ivregress 2sls` + `estat endogenous` for exogeneity test
3. **IV-Probit (twostep)**: `ivprobit` for binary DV; `estat endogenous` for Wald test

## When to use
- Reviewer asks "is your main IV endogenous?"
- You want to add an IV section to the appendix
- DV is binary (logit/probit context)

## Critical pitfalls (learned from BG Divestment project)

| Pitfall | Wrong | Right |
|---------|-------|-------|
| `vce` for ivprobit twostep | `ivprobit ..., twostep vce(robust)` → **r(198) error** | `ivprobit ..., twostep` (no vce option) |
| Nested braces in Stata | `foreach m { if { foreach { } } }` → **r(198) brace error** | Use `program printcoef ... end` pattern instead |
| Cluster variable | `vce(cluster firm_id)` when var is `co_code` | Always check variable names with `ds` first |
| Reporting first-stage | Hardcoding numbers from memory | Always run actual regression and parse log |

## Stata template

```stata
* iv_suite.do
log using "PATH/iv_suite.log", replace text
use "PATH/CHECKPOINT.dta", clear

* ── Coefficient extraction program ────────────────────────────────────────────
capture program drop printcoef
program printcoef
    args vname label
    capture local b = _b[`vname']
    if _rc != 0 {
        di "MISSING|`label'|.|.|."
        exit
    }
    local se = _se[`vname']
    local z  = `b' / `se'
    local p  = 2 * (1 - normal(abs(`z')))
    di "COEF|`label'|`b'|`se'|`p'"
end

* ── Step 1: First-stage OLS ────────────────────────────────────────────────────
di "===FIRSTSTAGE==="
reg ENDOG_VAR INSTRUMENT1 INSTRUMENT2 CONTROLS i.year i.industry_fe, vce(robust)
di "N=" e(N) " R2=" e(r2)
test INSTRUMENT1 INSTRUMENT2        // joint F on excluded instruments
di "F_instruments=" r(F) " p=" r(p)
printcoef INSTRUMENT1 "Instrument 1 label"
printcoef INSTRUMENT2 "Instrument 2 label"
printcoef CONTROL1    "Control 1 label"
* [repeat for all controls]

* ── Step 2: 2SLS + Wu-Hausman ───────────────────────────────────────────────────
di "===2SLS==="
ivregress 2sls DEPVAR (ENDOG_VAR = INSTRUMENT1 INSTRUMENT2) ///
    CONTROLS i.year i.industry_fe, vce(robust)
di "N=" e(N)
estat endogenous
di "WuHausman above"

* ── Step 3: IV-Probit (twostep) — no vce(robust) allowed ────────────────────────
di "===IVPROBIT==="
ivprobit DEPVAR (ENDOG_VAR = INSTRUMENT1 INSTRUMENT2) ///
    CONTROLS i.year i.industry_fe, twostep
di "N=" e(N)
printcoef ENDOG_VAR "Main IV (instrumented)"
* [repeat for all controls]
estat endogenous
di "Wald exogeneity above"

di "===DONE==="
log close
```

## Parsing the log for coefficients
After running, extract COEF lines:
```bash
grep "COEF\|===\|N=\|F_\|WuHausman\|Wald\|endogenous" iv_suite.log
```

Output format: `COEF|label|b|se|p`

Use these values to populate the `FS_ROWS` and `IVP_ROWS` dicts in your Word table python script.

## Instrument validity checklist
- [ ] First-stage F > 10 (ideally > 100) → instrument relevance
- [ ] Wu-Hausman p > 0.05 → consistent with exogeneity
- [ ] IV-probit Wald test p > 0.05 → consistent with exogeneity  
- [ ] N drop between main model and IV model → check if due to missing instrument lags
- [ ] Instruments are lagged (t-2, t-3) → temporal separation from DV

## Stata executable
`/Applications/StataNow/StataMP.app/Contents/MacOS/stata-mp`
