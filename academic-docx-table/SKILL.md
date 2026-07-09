---
name: academic-docx-table
description: Builds publication-quality Word (.docx) regression tables for strategy/management journals (SMJ, JMS, AMJ, ASQ style) using python-docx. Covers SMJ manuscript conventions (double-space body, APA headings, tables at end), standard model progression (M1=controls, M2=IV+controls, M3+=moderator+IV+interaction+controls), compact β/[p]/(SE) cell format, academic top-bottom borders, landscape sections, merged moderator rows, FE as "Yes", and VIF reporting. Use when building or reformatting any regression table or manuscript section in Word.
author: Yue Zhao (BG Divestment Project, Jul 2026)
version: 2.0.0
argument-hint: "[table_type: main|appendix|iv] [journal: SMJ|JMS|AMJ] [outfile.docx]"
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
