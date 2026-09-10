---
name: financial-report-builder
description: Builds the Fortis "Financial Reports" pack (special purpose financial statements - Profit and Loss Statement, Balance Sheet, Movements in Equity, Notes, Depreciation Schedule, Directors Declaration, Compilation Report) as a PDF for a legal entity that has NO Xero file, working from the P&L and Balance Sheet tabs of the Fortis year-end workpaper. Mimics how Xero's report templates work - every workpaper line is posted to an account with a Xero account type and report code, and the pack is derived from the codes - so the output is indistinguishable from a Xero-generated pack. Bundles the report-code map, a default company chart of accounts, the firm's boilerplate wording, five worked example packs and the build/render scripts. Files the finished PDF to FYI (Final Reports & Returns) after confirmation. ALWAYS trigger for "prepare the financial statements for [client]", "financial report for [client]", "create the financials from the workpaper", "special purpose financial statements", "SPFS", "compile the accounts", "Xero-style financial report", "generate the financial report pack", "the entity has no Xero file - do the financials", or when a workpaper is uploaded with a request for financial statements. Do NOT trigger for entities that have their own Xero subscription (use Xero report templates), for SMSFs (smsf-audit-pack), for tax return review (company-tax-reviewer / trust-tax-reviewer), or for building the workpaper itself (company-workpaper-creator).
compatibility: >-
  Needs python3 with reportlab and openpyxl (pip install reportlab openpyxl).
  Uses the FYI MCP to find the entity, pull the workpaper and prior-year pack,
  and to file the finished PDF (SUGGEST → CONFIRM). Optional: Xero MCP is NOT
  used - this skill exists for entities without a Xero file. Pairs with
  company-workpaper-creator (upstream) and company-tax-reviewer /
  tax-cover-letter (downstream).
---

# Financial Report Builder

Produces the Fortis **Financial Reports** pack for a company (and, once the
templates are uploaded, trusts and partnerships) whose accounts live only in a
year-end workpaper. The pack must look and behave exactly like the pack Xero's
report templates produce for clients who *do* have a Xero file, so the firm's
output is consistent across the client base.

Two rules sit above everything:

1. **Every account is mapped explicitly.** A workpaper line that the chart of
   accounts and the keyword rules cannot place with confidence is not guessed
   into a section - it is shown as **REVIEW** in the mapping table and resolved
   with the preparer (or by the rules in `references/account-mapping.md`)
   before anything is rendered.
2. **Nothing is written to FYI without a confirmation.** Rendering the PDF is
   fine; filing it into the client's cabinet is SUGGEST → CONFIRM.

## Why this skill exists

For a Xero client the pack takes two clicks. For an entity without a Xero file
the preparer re-keys the workpaper into a Word/Excel template, hand-edits last
year's notes and boilerplate, and hopes nothing was missed. The five reference
packs show what that costs: a declaration dated the wrong year, a compilation
report referring to the prior balance date, "Accounting Policie", "Capital Loss
Resreve", a note total labelled with the wrong name. This skill makes the pack
a deterministic function of the workpaper figures plus a small set of entity
facts, so the only judgement left is the mapping of accounts - and that is
recorded.

## How it mimics the Xero ledger

```
workpaper 'Profit & Loss' + 'Balance Sheet' tabs
        │  each line → account {type, report_code, cy, py}      (build_pack.py)
        ▼
pack.json  = the ledger                                          (fr_engine.py derives P&L sections,
        │                                                         BS lines, notes, equity movements,
        ▼                                                         validation)
Financial Reports PDF                                            (render_pack.py, Xero look)
```

* **Account type** (Revenue, Other Income, Direct Costs, Expense, Bank, Current
  Asset, Fixed Asset, Current Liability, Non-current Liability, Equity) comes
  from the section header the line sits under in the Xero-style export, or from
  the chart.
* **Report code** (`REV.TRA`, `EXP.COS`, `ASS.CUR.CAS.BAN`, `LIA.CUR.TAX`,
  `LIA.NCA.FIN.UNS`, `EQU.DIV` …) decides the P&L section, the Balance Sheet
  line, the Note and the sub-heading inside the Note. The full hierarchy, the
  "where does this account go" rules and the Xero type defaults are in
  `references/account-mapping.md`; the machine copy is `assets/report-map.json`.
* Everything else - totals, Gross Profit, Net Profit After Tax & Dividend, note
  numbering, nil-line suppression, alphabetical ordering, retained earnings
  (RE + current year earnings − dividends), Movements in Equity - is computed
  the way Xero computes it. `references/xero-ledger-model.md` documents the
  rules and the validation checks.

## What you need

| Input | Where it comes from |
|---|---|
| Workpaper (`.xlsx/.xlsm`) with **Profit & Loss** and **Balance Sheet** tabs (A = label, B = CY, C = PY) | FYI › Work Papers › *Annual Returns & Financials* › year; or uploaded. The raw `PL` / `BS` tabs (Xero-style export with section headers) also work. |
| Entity facts: legal name, ABN, FY end, entity type, director names | FYI entity record, ASIC extract / company statement in the Permanent cabinet, last year's pack. |
| Prior-year opening equity (PY column of Movements in Equity) | Last year's Financial Report in FYI › Final Reports & Returns. Optional but recommended. |
| Depreciation schedule (CSV/JSON) if the pack includes one | Workpaper `Accounting Depn` tab or the asset register (see `references/report-pack-structure.md` for columns). |
| Presentation choices | Prior-year pack: "Cost of Sales" vs "Cost of Goods Sold", report order, whether the Inventories policy prints, FX footnote, depreciation layout. **Follow last year's pack unless told otherwise.** |

## Workflow

Keep a short running todo so the user can see progress. Pause at each
SUGGEST → CONFIRM gate.

### Phase 1 - Scope

1. Resolve the entity in FYI (`fyi_list_clients` / `fyi_get_client`). Confirm
   legal name, ABN, FY end, entity type. **If the entity has its own Xero file,
   stop** - the pack should come from Xero's report templates, not this skill.
2. Get the director names (FYI Permanent › ASIC / Entity Set Up, or last year's
   declaration). One director → singular wording is applied automatically.
3. Pull last year's pack (FYI Final Reports & Returns › *Annual Return/Financials*,
   prior year). Note its presentation choices, its note numbering and its
   closing equity two years back (that becomes `equity.opening_py`).

### Phase 2 - Build the ledger

```bash
cd .claude/skills/financial-report-builder
python3 scripts/build_pack.py \
    --workpaper "2026 Workpaper - Client Pty Ltd.xlsm" \
    --name "Client Pty Ltd" --abn "12 345 678 901" --fy-end 2026-06-30 \
    --directors "Jane Citizen;John Citizen" \
    --opening-equity-py 85089 \
    --cost-of-sales-label "Cost of Sales" \
    [--depreciation depn.csv] [--coa assets/chart-of-accounts/company-default.csv] \
    --out pack.json --mapping-out mapping.md
```

The script prints the **mapping table** (source row, code, account, Xero type,
report code, confidence, reason) and the **validation report**.

4. Work through every **REVIEW** row (confidence `type` or `none`) and any
   mapping you disagree with. Fix by editing `report_code` in `pack.json`, or
   better, add the account to the chart CSV so it maps next time. Use the
   decision table in `references/account-mapping.md`; when the prior-year pack
   shows a different treatment (e.g. a director loan inside the Payables note),
   follow the prior year and code accordingly (`LIA.CUR.PAY.FIN`).
5. Set `options` in `pack.json` to match last year's presentation:
   `cost_of_sales_label`, `sort` (`alpha` default), `include_inventory_policy`,
   `depreciation_layout` (`simple` / `standard` / `register`), `report_order`,
   `fx_rates`, `extra_policies`. Add `equity_movements` for anything in the PY
   column other than profit (a share issue, a reserve transfer).
6. Re-run the validation: `python3 scripts/fr_engine.py pack.json`. Resolve every
   ERROR (the renderer refuses to print with errors). Explain every WARNING - a
   Retained Earnings residual means a direct posting to RE that needs a label
   and a reason; a depreciation tie-out difference means the schedule and the
   ledger disagree.

### Phase 3 - Render and check

```bash
python3 scripts/render_pack.py pack.json "2026 Financial Report - Client Pty Ltd.pdf"
```

7. Rasterise a few pages (pymupdf or the pdf skill) and check against the
   checklist below. Compare the P&L, Balance Sheet and note totals to the
   workpaper's `Profit & Loss` and `Balance Sheet` tabs - they must agree to
   the dollar (the workpaper carries cents, so no rounding gaps should appear).

**QA checklist**

- [ ] Cover: entity name exactly as registered, ABN, correct year.
- [ ] Contents lists exactly the reports in the pack, in order.
- [ ] P&L: Net Profit After Tax equals the workpaper; Income Tax Expense and
      Dividend Paid sections only present when non-nil.
- [ ] Balance Sheet: Net Assets = Total Equity; every line has the right note
      number; nil lines suppressed; GST/ITA debit balances shown in brackets.
- [ ] Movements in Equity: opening = PY total equity; PY opening agrees with last
      year's pack; any "Retained Earnings" movement explained.
- [ ] Notes: numbered from 2 in canonical order; Note 1 policies match last year
      (Inventories policy present/absent as expected); every BS line has a note.
- [ ] Depreciation schedule ties to P&L depreciation and the PPE note.
- [ ] Declaration and Compilation Report show the **current** balance date and
      the right singular/plural wording; one signature block per director.
- [ ] Footer "Financial Reports | Entity" and "Page x of y" on every report page.

### Phase 4 - Deliver (SUGGEST → CONFIRM)

8. Name the file `YYYY Financial Report - <Entity Name>.pdf`.
9. **Suggest** filing to FYI: cabinet **Final Reports & Returns**, categories
   **Year = YYYY** and **Final Reports Category = Annual Return/Financials**,
   linked to the entity (and the annual compliance job if one exists). Show the
   user the name, cabinet and categories and wait for a yes before using
   `fyi_get_upload_url` + upload (or `fyi_file_document` for small files).
10. Also save `pack.json` and `mapping.md` alongside the workpaper (FYI Work
    Papers, *Annual Returns & Financials*) - they are the audit trail for how each
    account was mapped and make next year's roll-forward a re-run.
11. Hand off: the pack goes to `tax-cover-letter` / `company-tax-reviewer` as
    usual; signing is done through FuseSign outside this skill.

## Presentation variants you will meet

| Variant | How to get it |
|---|---|
| "Cost of Goods Sold" instead of "Cost of Sales" | `options.cost_of_sales_label` |
| Movements in Equity before the Balance Sheet (Frontier) | `options.report_order: ["pnl","equity","bs","notes","depreciation","declaration","compilation"]` |
| Receivables listed without a "Current" heading (Capstone) | `options.show_current_heading: false` |
| Director loan shown inside the Payables note (Wisdom) | code it `LIA.CUR.PAY.FIN` |
| "Loan from Shareholders/Associates" note (Capstone) | code it `LIA.NCA.SHA` |
| Inventories policy with no stock (Wisdom, Complex) / omitted (Frontier) | `options.include_inventory_policy: true/false` |
| Foreign-currency rate footnote (Padel) | `options.fx_rates: [{"date": "30 June 2026", "rates": ["0.604121 EUR (Euro)"]}]` |
| Accounting Depreciation Schedule (7 columns) / Depreciation Schedule with rate & method / asset register | `depreciation.layout: simple / standard / register` |
| A nil-both-years P&L line that must still print | `"keep": true` on the account |
| Client-specific wording tweak | `boilerplate_overrides` in `pack.json` (shallow merge over `assets/boilerplate.json`) |

## Extending the skill (when the firm uploads charts and templates)

* **New chart of accounts** for an entity type → `assets/chart-of-accounts/<type>.csv`
  with columns `code,name,type,report_code,notes`. Pass it with `--coa`. The
  bundled `company-default.csv` is the Xero AU default chart plus every account
  seen in the five reference packs.
* **New report template** (trust, partnership) → add the declaration wording under
  `boilerplate.json › declaration.<type>`, and any new lines/sections to
  `assets/report-map.json` (`pnl_sections`, `bs_lines`, `notes`). Set
  `entity.type` accordingly. Stubs and the expected differences are listed in
  `references/account-mapping.md § 5`.
* **Label or order changes** (a renamed note, a different note order) → edit
  `report-map.json` only; no code change.
* After any change, re-render the five fixtures in `assets/examples/` and confirm
  the regression figures in `references/worked-examples.md`.

## Files

| Path | Purpose |
|---|---|
| `scripts/build_pack.py` | Workpaper/CSV → `pack.json` + mapping table + validation |
| `scripts/fr_engine.py` | The ledger engine: mapping rules, statement derivation, validation |
| `scripts/render_pack.py` | `pack.json` → PDF in the Xero report-template look |
| `assets/report-map.json` | Report-code hierarchy → sections, lines, notes, labels, order |
| `assets/chart-of-accounts/company-default.csv` | Default company chart with report codes |
| `assets/boilerplate.json` | Firm details, Note 1 policies, Declaration and Compilation Report wording |
| `assets/fonts/` | Source Sans 3 (OFL) - the Xero template face |
| `assets/examples/*.json` | The five reference packs as ledger fixtures |
| `references/xero-ledger-model.md` | How the derivation works; pack.json schema; validation |
| `references/account-mapping.md` | Report codes, type defaults, decision rules, entity-type stubs |
| `references/report-pack-structure.md` | Page-by-page anatomy, typography, layouts, naming/filing |
| `references/worked-examples.md` | Mapping tables and regression figures for the five packs |
