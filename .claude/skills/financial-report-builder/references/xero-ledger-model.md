# How the "Xero ledger" model works

The Financial Reports pack Fortis issues (P&L, Balance Sheet, Movements in
Equity, Notes, Depreciation Schedule, Directors Declaration, Compilation Report)
is Xero's **Report Templates** output. Xero never lays that pack out by hand: it
derives every line from two attributes on each account in the chart of accounts.

| Attribute | What it drives |
|---|---|
| **Account type** (Revenue, Other Income, Direct Costs, Expense, Bank, Current Asset, Fixed Asset, Current Liability, Non-current Liability, Equity ...) | Which statement the account lands on and which broad block (income vs expense, current vs non-current, asset vs liability). |
| **Report code** (`REV.TRA`, `EXP.COS`, `ASS.CUR.CAS.BAN`, `LIA.CUR.TAX` ...) | The exact line on the P&L / Balance Sheet, the Note it is disclosed in, and the sub-heading inside that Note. |

This skill reproduces that mechanism for entities that have **no Xero file**.
The workpaper's P&L and Balance Sheet tabs are treated as a trial balance; each
line is "posted" to an account with a type and a report code; the pack is then
generated from the codes, exactly as Xero would.

```
workpaper P&L + BS tabs ──► build_pack.py ──► pack.json (the ledger) ──► render_pack.py ──► PDF
                             │  chart of accounts CSV                     │  report-map.json (layout rules)
                             │  keyword rules                             │  boilerplate.json (wording)
                             └  Xero account type from section header     └  fonts
```

## The ledger file (`pack.json`)

```json
{
  "entity": {"name": "Wisdom IT Pty Ltd", "abn": "64 165 361 553", "type": "company",
             "fy_end": "2026-06-30", "directors": ["Frank Grippi"]},
  "options": {"sort": "alpha", "cost_of_sales_label": "Cost of Sales",
              "include_inventory_policy": null, "depreciation_layout": "simple",
              "report_order": null, "fx_rates": null, "extra_policies": []},
  "equity": {"opening_py": 85089},
  "equity_movements": [{"label": "Share Capital", "py": 100}],
  "accounts": [
    {"code": "200", "name": "Sales", "type": "Revenue", "report_code": "REV.TRA", "cy": 0, "py": 77000}
  ],
  "depreciation": {"layout": "simple", "groups": [{"name": "Motor Vehicle", "assets": [ ... ]}]}
}
```

* `accounts[].cy / py` are the **closing balances** for the current and prior
  year in their natural sign (see below). Keep cents when you have them.
* `report_code` is the only thing the engine reads to place an account. Every
  other field is descriptive.
* `equity.opening_py` is the prior-year *opening* equity (the closing equity two
  years back) so the PY column of Movements in Equity can be completed.
* `equity_movements` are movements the engine cannot derive from two Balance
  Sheet columns (anything in the PY column other than profit; or a label you
  want to force).

## Sign conventions (Xero's)

| Item | Stored as | Printed as |
|---|---|---|
| Income, other income | positive | positive |
| Cost of sales, expenses, income tax | positive | positive (a credit-balance expense such as Closing stock or a currency gain prints in brackets) |
| Dividends paid (`EQU.DIV`) | positive = amount paid | positive in the P&L "Dividend Paid" section; deducted from Retained Earnings |
| Assets | debit positive | positive; accumulated depreciation negative in brackets |
| Liabilities | credit positive | positive; a debit balance (GST refund due, ITA in credit) prints in brackets as a negative liability |
| Equity | credit positive | positive; accumulated losses in brackets |

`build_pack.py` auto-detects a workpaper that stores expenses as negatives
(`--expenses-negative auto`) and converts dividends taken from the equity
section (debit) into the positive "paid" figure.

## Rounding

Xero calculates every total from unrounded ledger balances and rounds only when
printing, so a column can be out by $1 (Wisdom IT: Total Current Liabilities
8,143 vs 9,691 - 1,547 = 8,144). The engine does the same: amounts stay unrounded,
`fmt()` rounds half-away-from-zero at print time. Validation treats differences
up to `ROUNDING_TOL` ($5) as INFO because whole-dollar inputs (a re-keyed PDF)
cannot foot perfectly; cents-level inputs from a workpaper should reconcile to $0.

## What is printed and what is suppressed

| Rule | Detail |
|---|---|
| Account nil in both years | Dropped (set `"keep": true` on the account to force it, as Frontier's "Discounts given" line). |
| P&L section with no accounts | Section omitted, but the computed lines (Gross Profit from Trading, Total Income, Profit/(Loss) before Taxation, Net Profit After Tax, Net Profit After Tax & Dividend) always print. |
| Income Tax Expense / Dividend Paid sections | Printed only when non-nil in either year. |
| Balance Sheet line nil in both years | Suppressed, even if its Note prints. |
| Note whose accounts are all nil | Suppressed. A Note prints if **any account** in it is non-nil, so a fully written-down asset (cost 489, accumulated (489)) still gets a Note with a nil total - Wisdom IT Note 4, Complex Communicators Note 6, Capstone Notes 5-6. |
| Balance Sheet sub-section (e.g. Non-Current Assets) with no lines | Omitted together with its total. |

## Ordering

* Accounts inside a section print **alphabetically by name** (Xero default,
  `options.sort = "alpha"`). Use `"source"` to keep workpaper order (Wisdom IT's
  pack shows Wages, Superannuation, Telephone out of alphabetical order, so its
  template was manually ordered).
* Inside a PPE / Intangibles Note the cost line prints before its accumulated
  depreciation line.
* Notes are numbered from 2 in the fixed order in `report-map.json`
  (`notes_order`): Cash, Receivables, Inventory, Prepayments, PPE, Intangibles,
  Financial Assets, Investments, Other Assets, Provisions, Payables, Financial
  Liabilities, Loan from Shareholders/Associates, Other Liabilities. Note 1 is
  always the accounting policies.
* Reports print in `options.report_order` (default P&L, BS, Equity, Notes,
  Depreciation, Declaration, Compilation). Frontier Travel's pack puts Movements
  in Equity before the Balance Sheet.

## Equity mechanics

Xero keeps three separate equity balances that the pack collapses into one
"Retained Earnings" line:

```
Retained Earnings (printed) = EQU.RET (prior years)  +  EQU.CYE (current year earnings)  -  EQU.DIV (dividends)
```

* If the Balance Sheet export has a **Current Year Earnings** line, code it
  `EQU.CYE`; the engine checks it equals Net Profit After Tax from the P&L.
  If absent, the engine uses the computed NPAT.
* **Movements in Equity** is derived: Opening = PY Total Equity; Increases =
  Profit for the Period (after dividends) + change in Share Capital + change in
  Reserves + any residual movement in `EQU.RET` (a direct posting, shown as a
  "Retained Earnings" line - Frontier's (125,000)) + user-supplied
  `equity_movements`; Total Equity = CY Total Equity.
* The PY column needs `equity.opening_py`; without it the engine backs the
  opening figure out (PY closing less PY profit less supplied PY movements) and
  flags it INFO so you check it against last year's pack.

## Validation checks (`Pack.validation`)

| Level | Check | Meaning |
|---|---|---|
| ERROR | `mapping` | An account has no report code, or a code not in `report-map.json`. |
| ERROR | `balance_sheet_balances` | Net Assets ≠ Total Equity beyond rounding tolerance (CY or PY). |
| ERROR | `current_year_earnings` | BS Current Year Earnings ≠ P&L NPAT. |
| ERROR | `entity` | Missing name / ABN / FY end. |
| WARNING | `retained_earnings_rollforward` | RE moved beyond profit and dividends; a movement line was added - confirm the label. |
| WARNING | `equity_opening_py` | Supplied PY opening equity does not roll to PY closing. |
| WARNING | `depreciation_ties_pl` / `depreciation_ties_ppe` | Schedule totals do not tie to the P&L depreciation lines / PPE note. |
| WARNING | `comparatives` | No prior-year figures at all. |
| WARNING | `entity` | No directors listed. |
| INFO | `gst_refund`, `income_tax`, rounding notes | Presentation reminders; no action unless the firm template says otherwise. |

`render_pack.py` refuses to render while any ERROR remains (override with
`--allow-errors` for a draft).
