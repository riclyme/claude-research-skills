---
name: academic-docx-table
description: Builds publication-quality Word (.docx) regression tables for strategy/management journals (SMJ, JMS, AMJ, ASQ style) using python-docx. Covers SMJ manuscript conventions (double-space body, APA headings, tables at end), standard model progression (M1=controls, M2=IV+controls, M3+=moderator+IV+interaction+controls), compact β/[p]/(SE) cell format, academic top-bottom borders, landscape section breaks for wide tables, merged moderator rows, FE as "Yes", VIF reporting, and correlation+descriptive statistics tables (numbered lower-triangle with Mean/SD rows). Use when building or reformatting any regression, correlation, or descriptive statistics table in Word.
author: Yue Zhao (BG Divestment Project, Jul 2026)
version: 3.0.0
argument-hint: "[table_type: main|appendix|iv|corr|desc] [journal: SMJ|JMS|AMJ] [outfile.docx]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# `/academic-docx-table` — Publication-Quality Word Regression Tables (SMJ/JMS/AMJ)

Encodes the full Word table formatting convention refined over many iterations for the BG Divestment project. Applies to Table 2 (main), TABLE A1–A4 (appendix), and any future regression output tables.

---

## PART 1 — SMJ Manuscript Formatting Conventions

### Document-level: double-space body text, Times New Roman 12pt

```python
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
style.paragraph_format.space_after = Pt(0)
```

Section headings follow APA level hierarchy:
- **Level 1** (Method, Results, Discussion): centered, bold, Title Case
- **Level 2** (Sample, Measures, etc.): left-aligned, bold, Title Case
- **Level 3** (sub-sections): left-aligned, bold italic, Title Case, period, run-in text

```python
def heading1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(12)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

def heading2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(12)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

def heading3(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text + ".")
    r.bold = True
    r.italic = True
    r.font.size = Pt(12)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
```

### Tables go at the END of the manuscript (after references)

SMJ and most top management journals require all tables and figures at the end, each on its own page, after the reference list. Order: References → Tables (in order) → Figures (in order).

Structure of each table page:
1. Page break
2. Table title — immediately above the table, NO blank line between title and table
3. The table itself
4. Table notes below the table

```python
# Each table starts on a new page
doc.add_page_break()

# Title flush to table — no blank paragraph between them
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = p.add_run("Table 2. ")
r.bold = True
r.font.size = Pt(12)
r2 = p.add_run("Logistic Regression Results Predicting Divestiture")
r2.bold = False
r2.font.size = Pt(12)
p.paragraph_format.space_after = Pt(0)   # NO gap before table
p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

# Table immediately follows — no vsp(), no add_paragraph()
tbl = doc.add_table(...)
```

Title format: **"Table N."** (bold) + title text (not bold), on one line. No period after the title. Sentence case for the title text.

---

## PART 2 — Standard Model Progression

Every regression table follows this fixed column structure:

| Column | Label | Contents |
|--------|-------|----------|
| M1 | Model 1 | **Controls only** — no focal IV, no moderators, no interactions |
| M2 | Model 2 | **Focal IV + all controls** — tests H1 (main effect) |
| M3 | Model 3 | **Moderator 1 + IV + Interaction 1 + all controls** — tests H2 |
| M4 | Model 4 | **Moderator 2 + IV + Interaction 2 + all controls** — tests H3 |
| M5 | Model 5 | **Moderator 3 + IV + Interaction 3 + all controls** — tests H4 |

Rules:
- Each model adds ONE new moderator + its interaction. Do NOT include previous moderators (to avoid collinearity confounds in reporting).
- Variables that are moderators in one model appear as controls (using their control-variable Stata name) in other models — use the **merged row** pattern (Part 3 below) to show them only once per row.
- M1 is always the baseline. Report it even if nothing is significant.

### Fixed effects: report as "Yes" / "—"

Never report year FE or industry FE coefficients. Instead, add footer rows:

```python
FOOTER = [
    ("Observations",        ["11,322", "11,322", "11,322", "11,322", "11,322"]),
    ("Year fixed effects",  ["Yes",    "Yes",    "Yes",    "Yes",    "Yes"   ]),
    ("Industry fixed effects",["Yes",  "Yes",    "Yes",    "Yes",    "Yes"   ]),
    ("Log-likelihood",      ["-2341",  "-2298",  "-2287",  "-2301",  "-2284" ]),
]
# M1 has no IV, so Pseudo R² or LL should increase monotonically through M2–M5
```

### VIF reporting

Report VIF for ONE model only — the most complete model (e.g., M5), **without** year FE and industry FE (adding FE inflates VIF artificially).

```stata
* In Stata — run the full model without FEs, then vif
reg depvar iv moderator interaction controls   // no i.year i.nic_two
estat vif
* Report: mean VIF < 10 (ideally < 5). If any single VIF > 10, flag it.
```

In the paper text (not a table): "Mean VIF = X.XX (max = X.XX), well below the threshold of 10, indicating no multicollinearity concern."

No separate VIF table needed unless a reviewer explicitly requests one.

---

## Cell format: compact 3-paragraph style

Each coefficient cell contains exactly 3 paragraphs — no more, no less:

```python
def ct(cell, b, se, p, bold=False):
    """Write β***/[p]/(SE) into a table cell."""
    cell.text = ""
    stars = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

    # Line 1: coefficient + stars
    p1 = cell.add_paragraph()
    r1 = p1.add_run(f"{b:.3f}{stars}")
    r1.bold = bold
    r1.font.size = Pt(10)

    # Line 2: p-value in brackets, italic, small
    p2 = cell.add_paragraph()
    r2 = p2.add_run(f"[{p:.3f}]")
    r2.italic = True
    r2.font.size = Pt(8)

    # Line 3: SE in parentheses, small
    p3 = cell.add_paragraph()
    r3 = p3.add_run(f"({se:.3f})")
    r3.font.size = Pt(8)

    for para in cell.paragraphs:
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.space_after  = Pt(0)
        para.paragraph_format.line_spacing = Pt(10)
```

Label cells (left column):
```python
def ct_label(cell, text, bold=False, indent=False):
    cell.text = ""
    p = cell.add_paragraph()
    r = p.add_run(("  " if indent else "") + text)
    r.bold = bold
    r.font.size = Pt(10)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    p.paragraph_format.line_spacing = Pt(10)
```

## Border style (academic top-bottom only)

No internal lines. Thick top + thin under header + thick bottom:

```python
from docx.oxml.ns import qn
from docx.oxml   import OxmlElement

def clear_table_borders(tbl):
    """Remove all default table borders."""
    tblPr = tbl._tbl.tblPr
    for tag in ['tblBorders']:
        el = tblPr.find(qn(f'w:{tag}'))
        if el is not None:
            tblPr.remove(el)

def set_cell_border(cell, **kwargs):
    """Set individual cell borders. kwargs: top=, bottom=, left=, right= each = {'sz': N, 'val': 'single'}"""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge, spec in kwargs.items():
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'),   spec.get('val',   'single'))
        el.set(qn('w:sz'),    str(spec.get('sz', 4)))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), '000000')
        tcBorders.append(el)
    tcPr.append(tcBorders)

# Usage — apply after clear_table_borders():
# Top row (thick top + thin bottom):
for cell in tbl.rows[0].cells:
    set_cell_border(cell,
        top=    {'sz': 12, 'val': 'single'},
        bottom= {'sz': 4,  'val': 'single'})

# Last row (thick bottom only):
for cell in tbl.rows[-1].cells:
    set_cell_border(cell,
        bottom= {'sz': 12, 'val': 'single'})
```

## Landscape section (for wide tables)

Wide tables (5+ model columns) need landscape orientation. Apply via XML, not through the Word UI:

```python
from docx.oxml.ns import qn
from docx.oxml   import OxmlElement
from docx         import Document
from docx.shared  import Inches, Pt

def add_landscape_section(doc):
    """Add a landscape section break for the next content."""
    sectPr = OxmlElement('w:sectPr')
    pgSz   = OxmlElement('w:pgSz')
    pgSz.set(qn('w:w'),      '15840')   # 11 inches in twips
    pgSz.set(qn('w:h'),      '12240')   # 8.5 inches in twips
    pgSz.set(qn('w:orient'), 'landscape')
    pgMar  = OxmlElement('w:pgMar')
    pgMar.set(qn('w:top'),    '720')
    pgMar.set(qn('w:right'),  '720')
    pgMar.set(qn('w:bottom'), '720')
    pgMar.set(qn('w:left'),   '720')
    sectPr.append(pgSz)
    sectPr.append(pgMar)
    # Attach to last paragraph before the table
    last_para = doc.paragraphs[-1]
    last_para._p.get_or_add_pPr().append(sectPr)
```

## Merged moderator rows (eliminates duplicate variable display)

When BG size is BOTH a moderator (in model M3) and a control (in M1, M2, M4, M5), use ONE row with a list-type key. Each entry in the list gives the DATA key for that column:

```python
ROWS = [
    # (label, key, is_bold_hint)
    ("Board centrality (H1)",          'c_norm_eigen',                                               True),
    # BG size: M1=control log_bg_aff, M2=control, M3=moderator c_size, M4=control, M5=control
    ("BG size",                        ['log_bg_aff','log_bg_aff','c_size','log_bg_aff','log_bg_aff'], False),
    ("Board centrality × BG size (H2)",'c_size_int',                                                 True),
    # BG div: M1-M2=control, M3=control, M4=moderator c_div, M5=control
    ("BG diversification",             ['bg_div_unrelated','bg_div_unrelated','bg_div_unrelated','c_div','bg_div_unrelated'], False),
    ...
]

# Rendering loop — use isinstance to guard separator and bold logic:
CTRL_KEYS = {'log_firm_sales', 'roa', 'leverage', ...}
BOLD_KEYS  = {'c_norm_eigen', 'c_size_int', 'c_div_int', 'c_age_int'}

sep_done = False
for label_text, key, _ in ROWS:
    # Control variable separator — fires only on first string key in CTRL_KEYS
    if isinstance(key, str) and key in CTRL_KEYS and not sep_done:
        sep_row = tbl.add_row()
        sep_row.cells[0].text = "Control variables"
        sep_done = True

    is_bold = isinstance(key, str) and key in BOLD_KEYS

    if isinstance(key, list):
        vals = [DATA[key[j]][j] for j in range(len(key))]
    else:
        vals = DATA[key]   # list of (b, se, p) per column
```

**Rule**: Never list the same construct twice (once as moderator, once as control). Reviewers will flag it as an error.

## Single-spaced appendix helpers

```python
from docx.enum.text import WD_LINE_SPACING

def set_single_spacing(style):
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

def vsp(doc):
    """Thin 3pt vertical spacer — replaces blank doc.add_paragraph()."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.line_spacing = Pt(3)

# In appendix: replace ALL standalone doc.add_paragraph() calls with vsp(doc)
# Use WD_LINE_SPACING.SINGLE everywhere (not DOUBLE) for body, headings, titles
```

## Left-aligned table and title (appendix convention)

```python
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text  import WD_ALIGN_PARAGRAPH

tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

def left_title(doc, text, bold=False, size=12):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(2)
```

## Star notation convention

| Symbol | Threshold |
|--------|-----------|
| ***    | p < 0.01  |
| **     | p < 0.05  |
| *      | p < 0.10  |

Always add footnote: `* p < 0.10, ** p < 0.05, *** p < 0.01. Standard errors in parentheses.`

## Full script skeleton

```python
from docx               import Document
from docx.shared        import Inches, Pt, RGBColor
from docx.enum.text     import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table    import WD_TABLE_ALIGNMENT
from docx.oxml.ns       import qn
from docx.oxml          import OxmlElement

doc = Document()

# Set default style to single-spaced 11pt
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(11)
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

# Add landscape section if needed
add_landscape_section(doc)

# Add table title (left-aligned)
left_title(doc, "Table X. [Table Title]", bold=True, size=12)
left_title(doc, "[subtitle or note]", bold=False, size=10)
vsp(doc)

# Build table
n_cols = 1 + N_MODELS   # label col + model cols
tbl = doc.add_table(rows=1 + len(ROWS) + len(FOOTER), cols=n_cols)
tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
clear_table_borders(tbl)

# Header row
hdr = tbl.rows[0]
hdr.cells[0].text = ""
for j, label in enumerate(MODEL_LABELS):
    hdr.cells[j+1].text = label

# Data rows
for i, (label_text, key, _) in enumerate(ROWS):
    row = tbl.rows[i + 1]
    ct_label(row.cells[0], label_text, bold=(isinstance(key,str) and key in BOLD_KEYS))
    if isinstance(key, list):
        vals = [DATA[key[j]][j] for j in range(N_MODELS)]
    else:
        vals = DATA[key]
    for j, (b, se, p) in enumerate(vals):
        ct(row.cells[j+1], b, se, p)

# Apply borders
for cell in tbl.rows[0].cells:
    set_cell_border(cell, top={'sz':12,'val':'single'}, bottom={'sz':4,'val':'single'})
for cell in tbl.rows[-1].cells:
    set_cell_border(cell, bottom={'sz':12,'val':'single'})

doc.save("OUTPUT.docx")
```

---

## PART 3 — Wide Tables: Landscape Section Break + Correlation / Descriptive Statistics

### When to use landscape

Any table with more than ~6 columns (correlation matrices, descriptive stats with many variables) must use landscape orientation with a **section break** that fully isolates it from the portrait main text.

```python
def insert_landscape_section(doc):
    """
    Insert a continuous section break BEFORE the current content, switching to landscape.
    Call this before adding the table title. Then call insert_portrait_section() after
    the table to return to portrait.
    """
    # Add a paragraph to host the section break
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    pgSz = OxmlElement('w:pgSz')
    pgSz.set(qn('w:w'),      '15840')  # 11 inches
    pgSz.set(qn('w:h'),      '12240')  # 8.5 inches
    pgSz.set(qn('w:orient'), 'landscape')
    pgMar = OxmlElement('w:pgMar')
    pgMar.set(qn('w:top'),    '720')   # 0.5 inch margins — maximize table width
    pgMar.set(qn('w:right'),  '720')
    pgMar.set(qn('w:bottom'), '720')
    pgMar.set(qn('w:left'),   '720')
    sectPr.append(pgSz)
    sectPr.append(pgMar)
    pPr.append(sectPr)

def insert_portrait_section(doc):
    """Return to portrait after the landscape table."""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    pgSz = OxmlElement('w:pgSz')
    pgSz.set(qn('w:w'), '12240')   # 8.5 inches
    pgSz.set(qn('w:h'), '15840')   # 11 inches
    pgMar = OxmlElement('w:pgMar')
    pgMar.set(qn('w:top'),    '1440')  # standard 1-inch margins
    pgMar.set(qn('w:right'),  '1440')
    pgMar.set(qn('w:bottom'), '1440')
    pgMar.set(qn('w:left'),   '1440')
    sectPr.append(pgSz)
    sectPr.append(pgMar)
    pPr.append(sectPr)

# Usage:
insert_landscape_section(doc)  # switch to landscape
# ... add table title and table ...
insert_portrait_section(doc)   # return to portrait
```

### Correlation + Descriptive Statistics table format

**Exact format from the screenshot:**

- Title: **"Table 2a."** (bold) + rest of title (normal) — all one paragraph, space_after=0
- Column headers: "Variables" | (1) | (2) | (3) | ... | (N) — centered, 8pt
- Variable rows: "(1) Divestiture dummy" | 1.00 | [correlations] — lower triangle only, upper blank
- Stars: * only (p<0.10 threshold — correlations use this threshold)
- Bottom rows: "Mean" and "SD" — same table, no separator
- Note: italic, 8pt, below table: "Note: Obs. = N,NNN. *** p<0.01, ** p<0.05, * p<0.1."
- Font: 8pt throughout (to fit 16 columns on landscape page)
- Table width: AUTO-fit to page (use `tbl.style = 'Table Grid'` then clear borders)

```python
import numpy as np
from scipy import stats

def make_corr_desc_table(doc, df, var_names, var_labels, title, note_obs):
    """
    Build a correlation + descriptive statistics table.
    
    Args:
        df:          pandas DataFrame with data
        var_names:   list of column names in df (in order)
        var_labels:  list of display labels (same order)
        title:       e.g. "Table 2a. Descriptive statistics and correlation table (DV: divestiture dummy)"
        note_obs:    e.g. "11,368"
    """
    n_vars = len(var_names)

    # --- Compute correlations and p-values ---
    corr_matrix = np.zeros((n_vars, n_vars))
    pval_matrix = np.ones((n_vars, n_vars))
    for i in range(n_vars):
        for j in range(n_vars):
            if i == j:
                corr_matrix[i, j] = 1.0
                pval_matrix[i, j] = 0.0
            elif i > j:
                r, p = stats.pearsonr(df[var_names[i]].dropna(), df[var_names[j]].dropna())
                corr_matrix[i, j] = r
                pval_matrix[i, j] = p

    means = [df[v].mean() for v in var_names]
    sds   = [df[v].std()  for v in var_names]

    # --- Table title (bold number + normal text, no gap before table) ---
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Split "Table 2a." from the rest
    bold_part, rest = title.split('. ', 1) if '. ' in title else (title, '')
    r1 = p_title.add_run(bold_part + '. ')
    r1.bold = True
    r1.font.size = Pt(10)
    if rest:
        r2 = p_title.add_run(rest)
        r2.bold = False
        r2.font.size = Pt(10)
    p_title.paragraph_format.space_after  = Pt(0)   # title glues to table
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # --- Table: n_vars rows + Mean + SD, cols = label + n_vars numbers ---
    n_rows = n_vars + 2   # +2 for Mean, SD
    n_cols = 1 + n_vars
    tbl = doc.add_table(rows=n_rows + 1, cols=n_cols)  # +1 for header
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    clear_table_borders(tbl)

    FONT_SIZE = Pt(8)

    def cell_text(cell, text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER):
        cell.text = ''
        p = cell.add_paragraph()
        p.alignment = align
        r = p.add_run(text)
        r.font.size = FONT_SIZE
        r.bold   = bold
        r.italic = italic
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(0)
        p.paragraph_format.line_spacing = Pt(9)

    # Header row
    hdr = tbl.rows[0]
    cell_text(hdr.cells[0], 'Variables', bold=False, align=WD_ALIGN_PARAGRAPH.LEFT)
    for j in range(n_vars):
        cell_text(hdr.cells[j + 1], f'({j+1})')

    # Variable rows — lower triangle only
    def fmt_corr(r, p):
        stars = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else ''
        return f'{r:.2f}{stars}'

    for i in range(n_vars):
        row = tbl.rows[i + 1]
        cell_text(row.cells[0], f'({i+1}) {var_labels[i]}', align=WD_ALIGN_PARAGRAPH.LEFT)
        for j in range(n_vars):
            if j > i:
                cell_text(row.cells[j + 1], '')          # upper triangle blank
            elif j == i:
                cell_text(row.cells[j + 1], '1.00')      # diagonal
            else:
                val = fmt_corr(corr_matrix[i, j], pval_matrix[i, j])
                cell_text(row.cells[j + 1], val)

    # Mean row
    mean_row = tbl.rows[n_vars + 1]
    cell_text(mean_row.cells[0], 'Mean', align=WD_ALIGN_PARAGRAPH.LEFT)
    for j in range(n_vars):
        cell_text(mean_row.cells[j + 1], f'{means[j]:.2f}')

    # SD row
    sd_row = tbl.rows[n_vars + 2]
    cell_text(sd_row.cells[0], 'SD', align=WD_ALIGN_PARAGRAPH.LEFT)
    for j in range(n_vars):
        cell_text(sd_row.cells[j + 1], f'{sds[j]:.2f}')

    # Borders
    for cell in tbl.rows[0].cells:
        set_cell_border(cell, top={'sz':12,'val':'single'}, bottom={'sz':4,'val':'single'})
    for cell in tbl.rows[-1].cells:
        set_cell_border(cell, bottom={'sz':12,'val':'single'})

    # Note below table
    p_note = doc.add_paragraph()
    r_note = p_note.add_run(f'Note: Obs. = {note_obs}. *** p<0.01, ** p<0.05, * p<0.1.')
    r_note.italic = True
    r_note.font.size = Pt(8)
    p_note.paragraph_format.space_before = Pt(2)
    p_note.paragraph_format.space_after  = Pt(0)
    p_note.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
```

### Full workflow for a wide correlation table

```python
# In your make_tables.py script:

# 1. Switch to landscape (isolates from portrait body)
insert_landscape_section(doc)

# 2. Build Table 2a (binary DV sample)
make_corr_desc_table(
    doc, df_binary, var_names, var_labels,
    title="Table 2a. Descriptive statistics and correlation table (DV: divestiture dummy)",
    note_obs="11,368"
)

doc.add_page_break()

# 3. Build Table 2b (count DV sample) — same landscape section
make_corr_desc_table(
    doc, df_count, var_names_count, var_labels_count,
    title="Table 2b. Descriptive statistics and correlation table (DV: count of divestitures)",
    note_obs="12,085"
)

# 4. Return to portrait for the next section
insert_portrait_section(doc)
```

### Key sizing rules to fit 16 columns on one page

- Font: **8pt** throughout (header + data + Mean/SD)
- Line spacing: **9pt** (tighter than standard)
- Margins: **0.5 inch** on all sides in landscape (set in `insert_landscape_section`)
- Column width: let Word auto-fit — do NOT set manual column widths for correlation tables
- If still overflowing: reduce font to 7.5pt and line spacing to 8pt

---

## PART 4 — Inline Statistical Reporting: Italic Notation + Subscripts

### The format (from screenshot)

```
(β = 0.04; RSE = 0.02; p = 0.01).
```

Rules (APA 7th edition, SMJ convention):
- **Italic**: Greek letters (β, α, γ), and single-letter roman statistics (p, t, F, r, z, N when = sample size used as a variable)
- **Roman (not italic)**: multi-letter abbreviations (RSE, SE, SD, VIF, IRR), numbers, equals signs, semicolons, parentheses
- **Subscripts**: automatic small sizing via `font.subscript = True` — e.g., β₁, χ²(df)
- Separator: semicolons (`;`), not commas
- Whole expression in parentheses; period goes AFTER the closing parenthesis (outside)

### Unicode Greek letters (copy-paste ready)

| Symbol | Unicode | Usage |
|--------|---------|-------|
| β | `β` | regression coefficient |
| α | `α` | significance level / Cronbach's alpha |
| γ | `γ` | coefficient in structural models |
| χ | `χ` | chi-square (write χ²) |
| σ | `σ` | standard deviation (in formulas) |
| μ | `μ` | population mean (in formulas) |
| Δ | `Δ` | delta / change |

### python-docx helper: `inline_stat()`

Appends a formatted inline stat report to an existing paragraph.

```python
def inline_stat(para, stats_list, terminal_period=True):
    """
    Append a formatted inline stat report to `para`.

    Args:
        para:        a docx Paragraph object (already has preceding text)
        stats_list:  list of (symbol, value, italic_symbol) tuples, e.g.:
                     [('β', '0.04', True),   # β = 0.04
                      ('RSE',    '0.02', False),   # RSE = 0.02
                      ('p',      '0.01', True)]    # p = 0.01
        terminal_period: add period after closing parenthesis (default True)

    Example output appended to para:  (β = 0.04; RSE = 0.02; p = 0.01).
    """
    STAT_SIZE = Pt(11)   # match surrounding body text size

    def run(text, italic=False, subscript=False, superscript=False):
        r = para.add_run(text)
        r.italic      = italic
        r.font.size   = STAT_SIZE
        if subscript:
            r.font.subscript   = True
        if superscript:
            r.font.superscript = True
        return r

    run(' (')
    for i, (symbol, value, is_italic) in enumerate(stats_list):
        if i > 0:
            run('; ')
        run(symbol, italic=is_italic)
        run(' = ')
        run(value, italic=False)
    run(')')
    if terminal_period:
        run('.')


# ── Usage examples ──────────────────────────────────────────────────────────────

# Basic: (β = 0.04; RSE = 0.02; p = 0.01).
p = doc.add_paragraph('Board centrality is positively related to divestiture')
inline_stat(p, [
    ('β', '0.04', True),
    ('RSE',    '0.02', False),
    ('p',      '0.01', True),
])

# With chi-square and df subscript:
# χ²(1) = 0.023, p = 0.879
p2 = doc.add_paragraph('Wu-Hausman endogeneity test: ')
run_chi = p2.add_run('χ')
run_chi.italic = True
run_chi.font.size = Pt(11)
run_sup = p2.add_run('2')
run_sup.font.superscript = True
run_sup.font.size = Pt(9)
run_df = p2.add_run('(1)')
run_df.font.size = Pt(11)
inline_stat(p2, [
    ('',  '0.023', False),   # value only after the χ²(1)
    ('p', '0.879', True),
], terminal_period=False)
```

### Subscript and superscript rules

```python
# Subscript: β₁  →  β + subscript "1"
r_beta = para.add_run('β')
r_beta.italic = True
r_sub = para.add_run('1')
r_sub.font.subscript = True
r_sub.font.size = Pt(8)   # slightly smaller than body

# Superscript: χ²  →  χ + superscript "2"
r_chi = para.add_run('χ')
r_chi.italic = True
r_sup = para.add_run('2')
r_sup.font.superscript = True
r_sup.font.size = Pt(8)

# Degrees of freedom in parentheses after superscript: F(2, 11989)
# Write as plain text — no sub/superscript needed
para.add_run('F(2, 11989) = 111.96')
# Then italicize the F only:
r_F = para.add_run('F')
r_F.italic = True
para.add_run('(2, 11989) = 111.96')
```

### Standard inline reporting phrases (copy templates)

```python
# Logit coefficient in body text
"Board centrality significantly increases divestiture likelihood"
inline_stat(p, [('β','0.043',True), ('SE','0.018',False), ('p','0.017',True)])

# NBreg IRR in body text  
"The incidence rate ratio is 1.08"
inline_stat(p, [('IRR','1.08',False), ('p','0.003',True)])

# IV first-stage F-stat
"The instruments are jointly significant"
inline_stat(p, [('F','111.96',True), ('p','<0.001',True)])

# Endogeneity test
"The Wu-Hausman test is consistent with exogeneity"
# write χ²(1) manually (see above), then:
inline_stat(p, [('p','0.879',True)], terminal_period=True)
```

### What NOT to italicize (common mistakes)

| Wrong | Right | Reason |
|-------|-------|--------|
| *SE* | SE | Multi-letter abbreviation → roman |
| *RSE* | RSE | Multi-letter abbreviation → roman |
| *VIF* | VIF | Abbreviation → roman |
| *IRR* | IRR | Abbreviation → roman |
| *SD* | SD | Abbreviation → roman |
| *df* | *df* | Exception: df IS italic in APA 7 |
| β (roman) | *β* | Greek letters always italic |
| p (roman) | *p* | Single roman letter → italic |

---

## PART 5 — Appendix Reporting Rule: Always Full Model, Never Summarized

**Rule**: Every robustness check table in the appendix must report the **complete model** — every variable, every coefficient, SE, and p-value. Never abbreviate with notes like "controls included" or show only the focal variable row.

This matches the same compact β/[p]/(SE) format used in the main text Table 2.

### What full model means

Every appendix table must include ALL of:
- Focal IV (e.g., board centrality)
- Moderators + interaction terms (where applicable)
- All control variables (firm-level, BG-level, industry-level)
- Fixed effects footer rows ("Year fixed effects: Yes", "Industry fixed effects: Yes")
- N, log-likelihood or pseudo-R², and any model-specific fit stats

### What is NOT allowed

```
# WRONG — never do this in appendix tables:
"Board centrality   0.043***"
"Controls           Included"   ← not acceptable
"Fixed effects      Yes"
```

```
# WRONG — never summarize:
"Results are consistent with Table 2. Full results available upon request."
```

### Why

Reviewers at SMJ/JMS/AMJ routinely check appendix robustness tables in detail. A summarized appendix signals that the author is hiding something or didn't actually run the full model. Full reporting also allows readers to check multicollinearity, sign reversals in controls, and sample size differences across specifications.

### Applies to all appendix table types

- NBreg / Poisson count model robustness (TABLE A1)
- Alternative IV specifications (TABLE A3 first-stage, TABLE A4 IV-probit)
- Alternative DV definitions
- Subsample splits
- Any other robustness check

### Code reminder

Use the same `ROWS` list structure as the main table — including all control variables — and the same `ct()` / `ct_label()` cell functions. Do not create a shorter ROWS list for appendix tables.

---

## PART 6 — Manuscript Structure & Section-by-Section Writing Conventions

The full-manuscript skeleton for SMJ/JMS/AMJ empirical papers. Section order, required elements per section, and phrasing templates. Use this whenever drafting or restructuring a manuscript in Word.

### Page 1: Title Page

Title, Abstract, and Keywords all fit on **one page**. Page break immediately after Keywords.

- Paper title: **centered, ALL CAPS, bold**
- "**ABSTRACT**" heading: centered, bold
- Abstract body: double-spaced, no first-line indent, **150 words max** (aim for 130–150)
- "**Keywords:**" (bold) followed by **≤ 6 terms**, lowercase, comma-separated
- Page break before Introduction

#### Abstract content rules (strict)

The abstract has exactly four jobs — in this order:

| # | Job | What to write |
|---|-----|---------------|
| 1 | **What we study** | Topic, setting, phenomenon (1–2 sentences) |
| 2 | **Theory** | The overarching theoretical lens and the core argument (1–2 sentences) |
| 3 | **Most important finding** | The single most striking empirical result — in plain language, no coefficients (1 sentence) |
| 4 | **Contribution** | Theory contribution first; briefly note empirical contribution if space allows (1–2 sentences) |

#### What the abstract must NOT contain

- **No citations** — not even one (e.g., "Drawing on Hambrick & Mason, 1984" → forbidden)
- **No hypothesis labels** — never write "H1", "Hypothesis 2", "consistent with H3" etc.
- **No specific coefficients or p-values** — say "positively associated", not "β = 0.04, p < 0.01"
- **No discussion of robustness checks or methodology details** — save for Methods
- **No sub-clause listing of moderators** — pick the most theoretically interesting finding; do not enumerate all hypotheses

#### What to emphasize

- The **theory contribution** is always the headline — what conceptual advance does this paper make?
- The **overarching theory** (e.g., "attention-based view", "network embeddedness") should be named explicitly
- One crisp finding that a reader will remember — the "punchline"

```python
# Title page — all three elements on one page, then page break
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_title.add_run("WHEN DO BUSINESS GROUP AFFILIATES DIVEST?")
r.bold = True
r.font.size = Pt(12)
p_title.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

heading1(doc, "ABSTRACT")

# Abstract body — 130-150 words, no citations, no H1/H2 labels
p_abs = doc.add_paragraph(
    "We examine when business group affiliates engage in divestitures — "
    "a strategic renewal option that group-specific exit barriers typically suppress. "
    "Drawing on the attention-based view, we argue that an affiliate's position in the "
    "group's board interlock network shapes how much attention ultimate owners direct "
    "toward it, which in turn determines the affiliate's access to internal capital "
    "and its inertial commitment to the group. More central affiliates face higher "
    "exit barriers and are therefore less likely to divest. Analyzing a panel of "
    "1,964 affiliated firms across 456 business groups in India (2003–2021), "
    "we find strong support for this argument. The moderating role of group size "
    "and diversification further clarifies when network position matters most. "
    "Our findings extend the attention-based view to intra-group network dynamics "
    "and contribute to the divestiture literature by identifying network-level "
    "antecedents of exit barrier variation."
)
p_abs.paragraph_format.first_line_indent = None
p_abs.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE

p_kw = doc.add_paragraph()
r_kw = p_kw.add_run("Keywords:  ")
r_kw.bold = True
p_kw.add_run("divestiture, business group, board interlock, attention-based view, network position, emerging markets")
# Max 6 terms — if you have more, cut the least distinctive one

doc.add_page_break()
```

### Introduction (2–3 pages)

Must contain these elements **in order**:

| # | Element | What it does |
|---|---------|--------------|
| 1 | Phenomenon / motivation | Open with an empirical fact or real-world observation that establishes why the topic matters (1–2 paragraphs) |
| 2 | Gap statement | What the existing literature has and has not explained |
| 3 | Research question | One explicit, clearly stated question |
| 4 | Theoretical framework preview | Name the theoretical lens(es) used and how they are combined/extended |
| 5 | Conceptual framework figure | Reference "Figure 1" (the conceptual model) here |
| 6 | Three contributions | Structured list, theoretical contribution first |

Details:

1. **Phenomenon/motivation** — Open with an empirical fact or real-world observation, not with theory. Establish why the topic matters before citing anyone.
2. **Gap statement** — Use language like "However, little is known about..." or "Prior work has focused on X, yet Y remains unexplored."
3. **Research question** — One explicit sentence, e.g., "We ask: when do business group affiliates divest?" Do not bury it or leave it implicit.
4. **Theoretical framework preview** — Name the lens(es) (e.g., resource dependence + internal capital markets) and state how they are combined or extended.
5. **Conceptual framework figure** — "Figure 1" is *always* the conceptual model: focal IV → DV, with moderating arrows for each hypothesis. It is referenced in the Introduction but physically placed at the end of the manuscript (see end-of-manuscript order below).
6. **Three contributions** — a structured list, each 2–4 sentences:
   1. **Theoretical contribution** — always first and most important
   2. **Empirical/methodological contribution**
   3. **Managerial or contextual contribution**

### Theoretical Background & Hypotheses Development

- **Background section first**: elaborate the theoretical building blocks before presenting any hypothesis. Do NOT state hypotheses inside the background section — build the logic first, then predict.
- **Each hypothesis gets its own subsection** (Level 2 or 3 heading), with the argumentation leading into the formal statement.

Hypothesis statement format:

```
Hypothesis 1 (H1): [Full statement of prediction, direction, and mechanism].
```

Rules:
- One sentence, complete, **directional** (positive/negative/stronger/weaker)
- Bold the "**Hypothesis 1 (H1):**" label; the statement itself is typically italic
- State the **mechanism**, not just the correlation ("X increases Y *because* Z")
- Moderation hypotheses use the standard template: "The positive relationship between X and Y is stronger (weaker) when Z is higher (lower)"

```python
def hypothesis(doc, label, statement):
    """e.g., hypothesis(doc, 'Hypothesis 1 (H1):', 'Board centrality increases ...')"""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    r1 = p.add_run(label + " ")
    r1.bold = True
    r2 = p.add_run(statement)
    r2.italic = True
```

### Method

Four subsections, in this order:

1. **Sample and Data** — describe the population, years covered, country/context, data sources, selection criteria, and final N.
2. **Variables** — strict ordering: DV first, then focal IV, then moderators, then controls. For **every** control variable, state (a) what it measures and (b) **why** it is included — what confound it addresses. Never list controls without justification.
3. **Econometric Modeling** — justify the estimator choice (why logit/probit/NBreg/RE, not just "we use logit"). Discuss panel structure, clustering of standard errors, and the fixed-effects strategy.
4. **Endogeneity** — briefly flag the endogeneity concern and point to the Appendix for IV robustness results.

### Results

- Report models **in sequence** (M1 → M2 → M3 …), narrating what each addition does ("Model 2 adds the focal IV to the baseline controls...").
- For **every** significant result, state direction + rough magnitude. Never write just "significant."
- Explain significant **controls** too — if firm size is significant, note what that implies.
- For moderation hypotheses, always supplement the coefficient with either:
  - (a) marginal effects across the full moderator range (Zelner-plot style), or
  - (b) predicted probabilities at ±1 SD of the moderator.

  State which you used and why.
- Reference the figure for moderation: "As shown in Figure 2, the marginal effect of X on Pr(Y) is positive and increases with Z."

### Robustness Checks & Endogeneity (in Results section; tables in Appendix)

- Main text carries only a brief paragraph: "We conducted several robustness checks. Results are reported in the Online Appendix."
- **Name each check** in that paragraph: alternative DV, alternative estimator (e.g., NBreg), alternative sample, lagged IV, IV/2SLS.
- Each robustness table goes in the Online Appendix as a **separate file** — never truncated, always the full model (see Part 5).
- Endogeneity: Wu-Hausman test + IV-probit. Report in text as:

  > "The Wu-Hausman test is consistent with exogeneity (χ²(1) = X.XX, *p* = X.XX). IV-probit results (TABLE A4) are directionally consistent with our main findings."

  (Format the χ² and *p* per Part 4 inline-stat conventions.)

### Discussion

Two subsections:

**First subsection — Interpretation of Results** (this is most of the Discussion):
- Interpret each hypothesis result in plain language — **no coefficients, no p-values**
- Use language like "Consistent with H1, we find that..." or "Contrary to H2, the data suggest..."
- Elaborate on **why** the pattern makes sense given the theory — add nuance beyond what the Introduction already said
- Address any surprising null or unexpected results head-on; do not skip them

**Second subsection — Managerial Implications**:
- Answer: how can a practicing manager use this paper's insights?
- Be concrete: "Our findings suggest that group headquarters should prioritize..."
- Avoid generic statements like "managers should pay attention to X"

### Conclusion

- Short — 1 page maximum
- Restate the research question and give a one-sentence answer
- Brief reminder of the main finding — **no new content**
- Do NOT introduce new theory or claims here

### Future Research (within or after the Conclusion)

Frame limitations as future research opportunities. The pattern:

> "Due to [data/context/scope limitation], we cannot speak to [X]. Future research could..."

Rules:
- Emphasize that limitations are acceptable **within this setting** — don't oversell the limitation
- 3–5 forward-looking suggestions

### References

- **APA 7th edition** format
- Alphabetical by first author's last name
- All in-text citations: (Author, Year) or Author (Year) — **no footnotes for citations**
- Journal names spelled out in full (never abbreviated: "Strategic Management Journal", not "SMJ" or "Strateg. Manag. J.")

### End-of-manuscript order (strict)

```
References
[page break]
Table 1. [first table]
[page break]
Table 2. [second table]
...
[page break]
Figure 1. Conceptual Framework
[page break]
Figure 2. [next figure]
...
```

Every table and figure on its own page (page break between each — see Part 1). All tables come before all figures. Figure 1 is always the conceptual framework referenced in the Introduction.

### Quick-reference: full section skeleton

| Order | Section | Key rule |
|-------|---------|----------|
| 1 | Title page (title + abstract + keywords) | ALL-CAPS bold title; 150–250-word abstract; page break after |
| 2 | Introduction | 6 elements in order; ends with three contributions |
| 3 | Theoretical Background | Building blocks only — no hypotheses here |
| 4 | Hypotheses Development | One subsection per hypothesis; bold label, directional statement, mechanism |
| 5 | Method | Sample and Data → Variables → Econometric Modeling → Endogeneity |
| 6 | Results | M1→M5 narration; direction + magnitude; moderation figures |
| 7 | Robustness (in Results) | Brief paragraph in text; full tables in Online Appendix |
| 8 | Discussion | Interpretation (no stats) → Managerial Implications |
| 9 | Conclusion | ≤1 page; restate RQ + answer; nothing new |
| 10 | Future Research | Limitations reframed as opportunities; 3–5 suggestions |
| 11 | References | APA 7; alphabetical; full journal names |
| 12 | Tables, then Figures | One per page; Figure 1 = conceptual framework |

---

## PART 7 — In-Text Citations, References, and Post-Writing Citation Audit

### In-text citation rules

**Target**: at least one citation per argumentative sentence. Every factual claim, theoretical proposition, or empirical assertion needs a source. If you genuinely cannot find a citation for a claim, you may leave it uncited — but this should be rare, not the default.

#### Citation priority order (apply in sequence)

1. **Target journal's own papers** — if submitting to SMJ, prefer SMJ citations; if AMJ, prefer AMJ. Editors notice when their journal is absent from the reference list.
2. **Classic / foundational theory papers** — the original source for any theoretical lens you invoke (e.g., Hambrick & Mason 1984 for upper echelons; Ocasio 1997 for attention-based view; Kogut & Zander 1992 for knowledge-based view). Always cite the original, not a summary.
3. **Most recent publications** — for empirical claims, prefer the last 3–5 years. Shows you know the current frontier.
4. **High-impact outlets** — AMJ, ASQ, SMJ, Org Science, Strat Mgmt J, JMS, JIBS, Management Science, Academy of Management Review.

#### Citation format (APA 7, in-text)

```
One author:       (Ocasio, 1997)
Two authors:      (Khanna & Palepu, 2000)
Three or more:    (Carney et al., 2011)
Author as subject: Ocasio (1997) argues that...
Multiple sources:  (Hoskisson et al., 2005; Leff, 1978; Morck et al., 2005)
                   — alphabetical by first author inside the parenthesis
```

#### What must be cited

| Must cite | Example claim |
|-----------|---------------|
| Theoretical propositions | "Attention is a scarce resource" |
| Empirical regularities | "Business groups are prevalent in emerging economies" |
| Variable operationalizations | "We measure board centrality using eigenvector centrality, following X" |
| Methodological choices | "We use random-effects logit, consistent with Y" |
| Any named effect or construct | "The internal capital market effect (Z)" |

#### What does NOT need a citation

- Mathematical definitions
- Descriptions of your own data or sample
- Results you are reporting from your own analysis
- Common knowledge in the field (e.g., "India is an emerging economy")

---

### Reference list rules (APA 7)

- Alphabetical by first author's last name
- All authors listed (no "et al." in the reference entry — only in text)
- Journal names spelled out in full (no abbreviations)
- Include DOI where available
- Every in-text citation must have exactly one matching reference entry
- Every reference entry must be cited at least once in the text

**Format examples:**

```
Journal article:
Khanna, T., & Palepu, K. (2000). Is group affiliation profitable in emerging markets?
    An analysis of diversified Indian business groups. Journal of Finance, 55(2), 867–891.
    https://doi.org/10.1111/0022-1082.00229

Book:
Williamson, O. E. (1985). The economic institutions of capitalism. Free Press.

Book chapter:
Granovetter, M. (1995). Coase revisited: Business groups in the modern economy.
    In S. Ghoshal & D. E. Westney (Eds.), Organization theory and the multinational
    corporation (pp. 93–129). Macmillan.
```

---

### Post-writing citation audit (MANDATORY before submission)

After the full manuscript is drafted, run a systematic audit. This is the most important step — hallucinated or misattributed citations are a serious academic integrity issue and a common AI failure mode.

#### Audit checklist

**Step 1 — Cross-reference check (structural)**
- Extract every `(Author, Year)` from the text → list A
- Extract every entry from the Reference list → list B
- Confirm: every item in A appears in B; every item in B appears in A
- Flag any orphan citations (in text but not in references) or orphan references (in list but not cited)

**Step 2 — Existence verification (factual)**
For every citation, verify the paper actually exists:
- Search Google Scholar or Semantic Scholar for exact title + author + year
- Verify: journal name, volume, page numbers, DOI all match
- If a paper cannot be found: REMOVE IT. Do not guess or reconstruct.

**Step 3 — Content accuracy check (semantic)**
For the 10–15 most load-bearing citations (foundational theory, key empirical claims):
- Read the actual abstract or paper
- Confirm the citation supports the specific claim you made
- Flag cases where your text misrepresents the cited paper's argument

**Step 4 — Journal fit check**
- Count citations by journal. Is your target journal represented?
- Are your classic theory sources (the ones any reviewer would expect) all present?
- Is there a suspiciously recent paper missing that a reviewer will notice?

#### Python audit helper (structural check only)

```python
import re

def audit_citations(text, references):
    """
    Structural audit: find orphan citations and orphan references.
    
    Args:
        text:       full manuscript text as a string
        references: list of strings like "Khanna & Palepu, 2000" (Author(s), Year)
    """
    # Extract all (Author..., Year) patterns from text
    pattern = r'\(([A-Z][^)]+?,\s*\d{4}[^)]*)\)'
    in_text = set()
    for match in re.findall(pattern, text):
        # Handle "et al." and multiple citations separated by ;
        for cite in match.split(';'):
            cite = cite.strip()
            in_text.add(cite)

    ref_set = set(r.strip() for r in references)

    orphan_citations   = in_text - ref_set    # cited but no reference entry
    orphan_references  = ref_set  - in_text   # reference entry but never cited

    if orphan_citations:
        print("CITATIONS WITH NO REFERENCE ENTRY:")
        for c in sorted(orphan_citations):
            print(f"  ⚠ {c}")
    if orphan_references:
        print("REFERENCE ENTRIES NEVER CITED IN TEXT:")
        for r in sorted(orphan_references):
            print(f"  ⚠ {r}")
    if not orphan_citations and not orphan_references:
        print("✓ All citations have matching references and vice versa.")
```

#### ⚠ AI-specific warning

Language models (including Claude) can confabulate plausible-sounding citations — correct author name, plausible year, real journal, but the paper does not exist. **Never trust a citation I generate without independently verifying it in Google Scholar.** This applies especially to:
- Papers with 3+ authors (easy to mix up)
- Papers before 1990 (harder to find digitally)
- Working papers or conference proceedings
- Any citation where I provide a DOI — DOIs can be fabricated too

When in doubt: remove the citation rather than risk a fabricated reference.

---

## PART 8 — Prose Style Rules & In-Text Table/Figure Placeholders

### Writing style rules (anti-AI-voice)

These patterns are characteristic of AI-generated academic text. Avoid all of them.

#### Banned punctuation: the em-dash as a comma substitute

Never use an em-dash (—) to replace a comma, colon, or parenthetical. It reads as AI-generated and is stylistically wrong in academic prose.

```
WRONG:  "Business groups—complex organizational structures—present unique challenges."
RIGHT:  "Business groups, which are complex organizational structures, present unique challenges."

WRONG:  "The result holds—suggesting that network position matters."
RIGHT:  "The result holds, suggesting that network position matters."
```

Em-dashes are acceptable only for a true interruption or abrupt break, which almost never occurs in academic writing.

#### Banned words and phrases (AI clichés)

| Banned | Why | Replace with |
|--------|-----|--------------|
| pivot | Overused AI word | shift, turn, redirect, move |
| delve | AI hallmark | examine, investigate, explore |
| nuanced | Often empty | be specific about what varies and how |
| multifaceted | Empty intensifier | describe the actual dimensions |
| it is worth noting that | Filler | just say the thing |
| importantly | Overused hedge | delete or restructure sentence |
| robust (outside statistics) | Vague | specify what held up and under what conditions |
| leverage (as verb) | Jargon creep | use, draw on, apply |

#### Substance over length

Every sentence must carry information. If removing a sentence loses no meaning, remove it.

```
WRONG (verbose, empty):
"This finding is particularly significant in that it highlights the important role
that network position plays in shaping the divestiture decisions of affiliated firms
within the broader context of business group governance structures."

RIGHT (same content, 1/3 the words):
"Network position shapes affiliate divestiture decisions within business groups."
```

Test: after writing a paragraph, ask "what is the one thing this paragraph says?" 
If you cannot answer in one sentence, the paragraph needs cutting.

#### Pronoun: always "we", never "I"

Even single-authored papers use "we" in management journals. "I" is not used.

```
WRONG:  "I argue that..."  /  "In this paper, I examine..."
RIGHT:  "We argue that..."  /  "In this paper, we examine..."
```

---

### In-text table and figure placeholders

Tables and figures are placed at the end of the manuscript (Part 1), but you must insert a centered placeholder in the body text at the point where the table/figure should appear when typeset.

**Format**: centered, bracketed, ALL CAPS, double-spaced (matching surrounding text).

```
[INSERT TABLE 2 HERE]

[INSERT FIGURE 1 HERE]
```

```python
def insert_placeholder(doc, label):
    """
    Insert a centered [INSERT TABLE N HERE] or [INSERT FIGURE N HERE] placeholder.
    Matches the double-spacing of surrounding body text.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"[INSERT {label.upper()} HERE]")
    r.font.size = Pt(12)
    # Keep double spacing — matches surrounding body text
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)

# Usage — place immediately after the sentence that introduces the table/figure:
# "Table 2 reports the results of our main analysis."
insert_placeholder(doc, "Table 2")
# Then continue body text normally.
```

**Placement rule**: the placeholder goes on its own line, immediately after the sentence introducing the table/figure — not at the start of a section, not floating in the middle of a paragraph.

```
WRONG: placeholder at top of Results section before any text
RIGHT: "...as shown in Table 2."  [INSERT TABLE 2 HERE]  "Model 1 is the baseline..."
```

---

## PART 9 — Body Text Alignment and Paragraph Indentation

### Justification: full (双向对齐)

All body text must be fully justified (left and right edges both aligned). This is the standard for SMJ/JMS/AMJ.

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Set on the Normal style so all body paragraphs inherit it
style = doc.styles['Normal']
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
```

### Paragraph indentation: section-first rule

| Paragraph position | First-line indent |
|--------------------|-------------------|
| First paragraph after a section/subsection heading | **No indent** |
| All subsequent paragraphs within the same section | **0.5 inch indent** |

This follows the standard print convention: indent signals "new paragraph within the same thought thread"; no indent signals "fresh start after a heading."

```python
INDENT = Inches(0.5)

def body_first(doc, text):
    """First paragraph of a section — justified, no indent."""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = None   # no indent
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    return p

def body(doc, text):
    """Subsequent paragraphs — justified, 0.5-inch first-line indent."""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = INDENT
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    return p

# Usage:
heading2(doc, "Sample and Data")
body_first(doc, "Our sample comprises 1,964 affiliated firms...")   # no indent
body(doc, "We obtain financial data from CMIE Prowess IQ...")       # 0.5-inch indent
body(doc, "The final sample spans 2003 to 2021...")                 # 0.5-inch indent
```

### Do NOT add blank lines between paragraphs

In a double-spaced manuscript, blank lines between paragraphs look like section breaks. Use indentation (above) to signal paragraph boundaries — never `doc.add_paragraph()` between body paragraphs.

```python
# WRONG — adds visual gap that looks like a section break
body(doc, "First paragraph.")
doc.add_paragraph()          # ← never do this between body paragraphs
body(doc, "Second paragraph.")

# RIGHT — indentation alone marks the new paragraph
body(doc, "First paragraph.")
body(doc, "Second paragraph.")   # indent signals the break
```
