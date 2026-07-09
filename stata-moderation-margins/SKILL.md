---
name: stata-moderation-margins
description: Generates Zelner-style continuous marginal effect plots for moderation hypotheses tested with logit/probit. Produces a multi-panel PNG showing dy/dx of the focal variable evaluated across the full empirical range of each moderator, with rspike 95% CI bars. Use when you say "generate moderation plots", "Zelner plot for H2-H4", or "marginal effects across moderator range". NOT for count models (NBreg) — use coefficient plots instead.
author: Yue Zhao (BG Divestment Project, Jul 2026)
version: 1.0.0
argument-hint: "[focal_var] [moderator1:range1] [moderator2:range2] ... [model_controls] [outfile.png]"
allowed-tools: ["Read", "Write", "Bash"]
---

# `/stata-moderation-margins` — Zelner Moderation Marginal Effect Plots

Produces publication-quality marginal effect plots for **binary logit/probit moderation** hypotheses (the Zelner 2010 approach). Each panel shows how the marginal effect of the focal variable on Pr(y=1) changes continuously across a moderator's empirical range. Vertical bars = 95% CI (rspike style). Panels combined into one PNG.

## When to use
- You have moderation hypotheses (H2, H3, H4…) tested with xtlogit / logit / probit
- You need a figure for the main text or appendix showing the moderation graphically
- The DV is **binary** (dummy). For count DVs, just show IRR coefficients — Zelner is not appropriate.

## When NOT to use
- NBreg / Poisson / count outcomes → use IRR bar plots instead
- Simple linear moderation → OLS interaction plot is sufficient
- You only want one moderator → still works, just produces 1 panel

## Inputs you must provide
1. **Checkpoint path**: path to the analysis `.dta` file (post data-construction)
2. **Model spec per panel**: each moderation hypothesis needs its own model. Provide:
   - Focal variable name (e.g. `c_norm_eigen`)
   - Moderator variable name (e.g. `c_size`)
   - Interaction term notation (e.g. `c.c_norm_eigen##c.c_size`)
   - Controls list
   - Moderator empirical range (from `summarize`: min, max, step size for ~60 points)
3. **Output path**: full path for the PNG

## Stata template (adapt per project)

```stata
* zelner_moderation.do
use "PATH/TO/CHECKPOINT.dta", clear
set scheme s1mono

* ── Panel A: [Moderator 1 label] ─────────────────────────────────────────────
quietly xtlogit DEPVAR c.FOCAL##c.MODERATOR1 ///
    CONTROLS ///
    i.year i.industry_fe, re vce(robust)

* ~60 evenly-spaced values across [min, max] of moderator
margins, dydx(FOCAL) at(MODERATOR1 = (MIN(STEP)MAX)) predict(pu0)

marginsplot, ///
    title("(A) [Panel Title]", size(medsmall) margin(b=1)) ///
    xtitle("[Moderator label] (mean-centered)", size(small)) ///
    ytitle("Change in Pr(Divestiture)", size(small)) ///
    recastci(rspike) ///
    plot1opts(lcolor(black) lwidth(thin) msymbol(none)) ///
    ci1opts(lcolor(black) lwidth(vthin)) ///
    yline(0, lpattern(dash) lcolor(gs10)) ///
    graphregion(color(white)) plotregion(margin(sides)) ///
    legend(off) ///
    name(pA, replace)

* [Repeat for pB, pC, etc.]

* ── Combine panels ────────────────────────────────────────────────────────────
graph combine pA pB pC, ///
    cols(3) rows(1) ycommon ///
    graphregion(color(white)) ///
    xsize(10) ysize(3.5)

graph export "OUTPUT_PATH.png", replace width(2400) height(840)
di "Saved: OUTPUT_PATH.png"
```

## Key details that always trip you up
- Use `predict(pu0)` not `predict(pr)` for xtlogit RE — this gives population-averaged Pr at u_i=0
- Use `c.VAR##c.VAR` notation (not `i.`) for continuous-by-continuous interactions
- `ycommon` is essential for comparing magnitudes across panels
- Step size = (max - min) / 60 → round to 3 significant figures
- Always mean-center moderators BEFORE computing the range — center is at 0

## Output note
The figure caption should say: "Each panel plots the marginal effect of [focal] on Pr([DV]) evaluated at approximately 60 evenly spaced values of the moderator across its empirical range. Vertical bars = 95% confidence intervals."

## Stata executable (Mac)
Always use: `/Applications/StataNow/StataMP.app/Contents/MacOS/stata-mp`
Never use Stata 17 (license expired).
