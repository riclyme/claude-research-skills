---
name: stata-coef-to-docx
description: End-to-end pipeline — runs Stata models using the printcoef pattern, parses the log to extract all coefficients (b, se, p), and generates a compact publication-quality Word (.docx) regression table in JMS/AMJ style without any manual copy-paste. Eliminates the risk of hardcoded wrong numbers. Use when you say "run models and make the table", "update the regression table with new results", or "build Table 2 from Stata output".
author: Yue Zhao (BG Divestment Project, Jul 2026)
version: 1.0.0
argument-hint: "[checkpoint.dta] [models_spec] [outfile.docx]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# `/stata-coef-to-docx` — Stata → Coefficients → Word Table (no manual copy-paste)

Runs Stata models, extracts every coefficient automatically from the log, and generates a compact Word regression table. **The key insight**: manually copying numbers from Stata log → python dict is the #1 source of errors (wrong values, stale numbers). This skill automates the full chain.

## Why this exists
In the BG Divestment project, TABLE A3 (first-stage IV) was submitted with HARDCODED WRONG VALUES (β=0.164 when actual was β=0.076) because the numbers were typed by hand from a different version. This skill prevents that by never having humans in the copy-paste loop.

## When to use
- Building or updating any regression table (main results, robustness, IV)
- After running new Stata models and needing the Word table updated
- When you change model specification and need to regenerate the table

## Workflow (4 steps, fully automated)

### Step 1: Write the Stata do-file with printcoef extraction

```stata
* models_extract.do
log using "LOGPATH.log", replace text
use "CHECKPOINT.dta", clear

capture program drop printcoef
program printcoef
    args vname label
    capture local b = _b[`vname']
    if _rc != 0 { di "COEF|`label'|.|.|."; exit }
    local se = _se[`vname']
    local z  = `b' / `se'
    local p  = 2 * (1 - normal(abs(`z')))
    di "COEF|`label'|`b'|`se'|`p'"
end

* Run each model, print header, extract all coefficients
di "===MODEL1==="
YOUR_REGRESSION_COMMAND, vce(robust)
di "N=" e(N) " LL=" e(ll)
printcoef VAR1 "Variable 1 label"
printcoef VAR2 "Variable 2 label"
* [etc]

di "===DONE==="
log close
```

### Step 2: Run Stata and parse the log

```bash
/Applications/StataNow/StataMP.app/Contents/MacOS/stata-mp -b do models_extract.do
grep "COEF\|===\|N=" LOGPATH.log
```

### Step 3: Auto-generate the DATA dict (Python)

Parse log lines of the form `COEF|label|b|se|p` into a python dict:

```python
import re, subprocess

def parse_coef_log(logfile):
    """Parse printcoef output → {label: (b, se, p)} per model"""
    models = {}
    current = None
    with open(logfile) as f:
        for line in f:
            m = re.match(r'===(\w+)===', line)
            if m:
                current = m.group(1)
                models[current] = {}
            c = re.match(r'COEF\|(.+?)\|([.\d-]+)\|([.\d-]+)\|([.\de-]+)', line)
            if c and current:
                label, b, se, p = c.groups()
                try:
                    models[current][label] = (float(b), float(se), float(p))
                except ValueError:
                    models[current][label] = None
    return models
```

### Step 4: Build Word table with python-docx

Use the `academic-table-formatter` agent with the extracted data dict. The table style rules:
- 1 row per variable, 3 paragraphs per cell: `β***`, `[p]` (italic, size 8), `(SE)` (size 8)
- Line spacing 10pt, space_after 0pt within each cell
- Borders: thick top + thin under header + thick bottom only (no internal lines)
- Left-aligned table + left-aligned titles (for appendix)
- Merged rows for moderator variables: in the model that tests Hk, show the moderator coefficient; in other models, show the corresponding control variable coefficient in the same row

## Important: Merged moderator rows

When BG size is both a moderator (Model 2) and a control (Models 1,3,4), use a SINGLE row:
```python
# List-type key = merged row: entry[j] is the DATA key for column j
ROWS = [
    ("BG size", ['log_bg_aff', 'c_size', 'log_bg_aff', 'log_bg_aff'], False),
    # M1 shows log_bg_aff, M2 shows c_size, M3 shows log_bg_aff, M4 shows log_bg_aff
]
```

Never show the same construct twice (once as moderator, once as control) — it confuses reviewers.

## Stata executable
`/Applications/StataNow/StataMP.app/Contents/MacOS/stata-mp`

## Checkpoint rule
Before running: check if `analysis_manuscript_models.dta` checkpoint exists.
If it does, `use checkpoint, clear` and skip data construction (saves 30-60 min).
Only rebuild from scratch if variable definitions changed or new data was merged.
