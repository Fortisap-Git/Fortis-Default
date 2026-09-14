# The fill spec — the only thing you write in Phase B

`scripts/build_workpaper.py spec.json` turns a JSON spec into the finished `.xlsm` in about two
seconds. You never write a per-client Python script. You write **data**: which cell gets which
value, formula or link, with which source. Rebuilding after a review fix is the same command.

Keep the spec at `work/<client>/spec.json`. It is the audit trail of the build.

## Top level

| Key | Meaning |
|---|---|
| `client` | `{"name", "entity_id", "year"}` — name goes into the two sheet names and C3; year sets C4 |
| `client2` | optional second taxpayer `{"name"}` for the `- 2` tabs (joint files) |
| `template` | path to the client's rolled-forward template from FYI, or `null` for the bundled master |
| `prior_workpaper` | prior-year `.xlsm` path (needed for `prior_sheet` clones), or `null` |
| `output` | where to save — `work/<client>/{Y} ITR Workpaper - First Last.xlsm` |
| `unhide` | hidden master tabs the return actually uses, e.g. `["Share Register", "Foreign Income"]` |
| `clones` | new working tabs (see below) |
| `sources` | the FYI documents you cite: `[{"id", "doc", "label"}]` — `doc` is the FYI document uuid from `fyi_find_documents`; `label` is the FYI document name. Declaring a source does **not** link it anywhere on its own: a document is linked only where a cell cites it, in that tab's Hyperlink column |
| `cells` | the figures (see below) |
| `controls` | cells that must evaluate to a value: `[{"sheet", "cell", "expect": 0}]` — checked by `verify_workpaper.py` |
| `queries` | Queries tab rows (see below) |
| `review_notes` | plain judgment rows for the Review Notes tab (Phase B) |
| `rev` | Phase E overrides — same shape as `cells`, applied after them |
| `review` | Phase E register `{"summary", "sections"}` — replaces `review_notes` (fold them in) |

Sheet names: use the alias `Summary` / `Deductions` for the client-1 tabs (the engine resolves the
rename), `Summary2` / `Deductions2` for client 2, otherwise the exact sheet name including the
master's trailing spaces (`Motor Vehicle `).

## Cells

One entry per populated cell. Exactly one of `value`, `formula`, `link`, `fyi`, `clear`.

```json
{"sheet": "Summary", "cell": "H16", "value": 412.00,
 "source": "prefill", "remark": "Per pre-fill; re-run before lodgement"}

{"sheet": "Rental Property - 12 Smith St", "cell": "F7",
 "formula": "=3900+2600+2600+2600+2600+2600+2600+2600+2600+2600+2600+2600",
 "source": "agent", "remark": "12 monthly statements; rent $2,600 from Aug"}

{"sheet": "Summary", "cell": "H36", "formula": "='Rental Property - 12 Smith St'!E52",
 "source": {"sheet": "Rental Property - 12 Smith St", "cell": "E52"}}

{"sheet": "Share Register", "cell": "A9", "value": "CSL Ltd"}
{"sheet": "Summary", "cell": "I19", "fyi": "ess"}                       # a bare FYI link
{"sheet": "Summary", "cell": "I30", "link": {"sheet": "CGT Summary", "cell": "D14"}}
{"sheet": "Rental Property - 12 Smith St", "cell": "G17", "clear": true}   # awaiting client
```

- `source` is either a source id (→ `=HYPERLINK()` to FYI), `{"sheet","cell"}` (→ internal link),
  or `{"text": "..."}`. It lands in the tab's **Hyperlink** column automatically: Summary **I**,
  Rental Property **H**. Other tabs have no Hyperlink column — give `source_cell` explicitly.
- **The Hyperlink column is the only place a document link goes.** One link per figure, against the
  figure it supports. The Summary tab's `Source Documents` block (heading at J1, the cells beneath
  and beside it) is left empty — we do not list every document on the file there, and nothing else
  links the sources in bulk.
- `remark` lands in the remark column: Summary **J**, Rental Property **I**; else give `remark_cell`.
- Writing a constant over a template formula is warned about. If intended (e.g. a Tax Credits cell),
  add `"overwrite_formula": true`.
- **Totals are never constants.** Where a figure aggregates statements, write the in-cell sum as a
  `formula`. Where it derives from another tab, write the cross-sheet formula. The `constants` check
  in `verify_workpaper.py` fails the build if a total row holds a number.
- Cells awaiting client data are `clear` (or simply absent) — never 0, never an estimate.

## Where things live (from `assets/template_meta.json`)

**Summary tab** — column H `$`, G `Tax Credits`, I `Hyperlink` (source link), J remarks, K reviewer sign-off.

| Row | Label | Row | Label | Row | Label |
|---|---|---|---|---|---|
| 12-13 | 1 Salary | 29 | 18 CGT – trust | 44-58 | D1–D15 (one row each, in order) |
| 14 | 2 Allowance | 30 | 18 CGT – shares | 60 | TOTAL DEDUCTIONS |
| 16 | 10 Interest | 31 | 18 CGT – property | 62 | TAXABLE INCOME |
| 17-18 | 11 Dividends | 33 | 20 Foreign – trust | 65-68 | Tax, Medicare, MLS, excess PHI |
| 19 | 12 ESS | 34 | 20 Foreign – other | 72-79 | PAYGW, WHT, instalments, franking, FITO, LITO, PHI rebate |
| 21, 23 | 13 Distributions | 36-37 | 21 Rental | 82-84 | Payable / per ITR / Variance |
| 26 | 15 Business | 39 | 24 Other income | 87-88 | RESC, RFB |
| 27 | 16 Non-commercial losses | 41 | TOTAL INCOME | 90-97 | PHI, M1, IT8, M2 days |

Summary row 84 `Variance` (`=H82-H83`) is the natural control once `per ITR` is keyed.

**Deductions tab** — B description, C items, D total. Blocks: D1 rows 11-21 (car), D2 23-28,
D3 30-33, D4 35-38, D5 40-49, D6 51-54, D7 56-59, D8 61-64, D9 66-69, D10 71-74 (row 71 is the
non-deductible GIC line — known master defect, its total sums it), D11 76-78, D12 80-81, D13 83-84,
D14 86-87, D15 89-95. Each block's last row is its total (formula). Use the blank lines inside a
block; if a block is short, raise it as a template issue rather than inserting rows.

**Rental Property tab** (and clones) — B:D prior year (Total / Agency / Owner), E:G current, H
source, I remark. Rows 7-8 income, 10 total income, 13-49 expenses in the master's order (18-19
Div 40, 22-23 loan interest, 27 agent commission, 34-35 Div 43, 40-49 sundries), 50 total
expenses, 52 net rent, 53 low-value pool (→ D6), 54 net after LVP, 55-56 owner split. Column F
(agency) figures are in-cell sums of the monthly statements; column G (owner) everything else.

**Queries tab** — numbered rows from 8 (row 9 is blank in the master; the engine uses the
master's own numbered rows and extends them). **Review Notes** — numbered rows from 8.

## Clones

```json
{"prior_sheet": "Rental Property - 12 Smith St", "as": "Rental Property - 12 Smith St",
 "after": "Rental Property", "roll": {"first_row": 7, "last_row": 56}}
```
Clones the prior-year tab (values, formulas, styles) and rolls E:G → B:D, then **clears every
constant in E:G down to row 56** so no prior-year figure survives in a current-year column.
Hyperlinks do not survive a clone — cite sources again through `cells`, in the Hyperlink column.

```json
{"template_sheet": "Rental Property", "as": "Rental Property - 12 Smith St"}
```
First year on file: a fresh copy of the master tab. Populate B:D from the signed ITR only to the
depth it supports and head B4 "FY {Y-1} (per signed ITR)" via a cell entry.

## Queries

```json
{"issue": "Interest income", "description": "Pre-fill carries no bank data. Please confirm interest received in FY26 (PY $412).",
 "reference": {"sheet": "Summary", "cell": "H16"}}
```
The engine writes the row, links column D to the awaiting cell, and writes a `Query n` back-link
into that cell's source column (Summary I / Rental H) if it is empty. Set `"backlink": false` or
`"backlink_cell"` to override.

## Review (Phase E)

```json
"review": {
  "summary": {"bottom_line": "...", "waiting": "...", "fixed": "...", "outside": "..."},
  "sections": [
    {"title": "INCOME — by label (10 interest, 11 dividends, 13 distributions, 18 CGT, 20 foreign)",
     "findings": [{"sheet": "Summary", "cell": "H16", "point": "...", "action": "...",
                   "status": "QUERY", "impact": "~$130", "source": "2026 ATO Pre-filling report"}]},
    {"title": "RENTAL PROPERTY — in rental schedule order", "findings": []},
    {"title": "DEDUCTIONS — D1 to D15 in label order", "findings": []},
    {"title": "OTHER — offsets, levies, disclosures", "findings": []},
    {"title": "WORKPAPER MECHANICS — fixed in this file", "findings": []},
    {"title": "OUTSIDE THIS FILE", "findings": []}
  ]
}
```
Empty sections are skipped. Every finding with a sheet and cell gets a cell comment "Review Notes
row N". Phase B `review_notes` rows are ignored once `review` is present — fold them into the
matching section as `NOTE` rows.

## Commands

```bash
python scripts/build_workpaper.py work/<client>/spec.json --dry-run     # validate
python scripts/build_workpaper.py work/<client>/spec.json               # build (~2 s)
python scripts/verify_workpaper.py "work/<client>/<file>.xlsm" --spec work/<client>/spec.json
python scripts/dump_workpaper.py "work/<client>/<file>.xlsm" --changed > work/<client>/dump.txt
python scripts/verify_workpaper.py "<file>.xlsm" --spec spec.json --claims work/<client>/claims.json
```
