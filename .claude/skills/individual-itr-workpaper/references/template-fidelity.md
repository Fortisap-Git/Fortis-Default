# The master template, and the rule that its structure never changes

The firm's master Individual ITR workpaper ships with this skill:

```
assets/2026_ITR_Workpaper_-_Individual_Name.xlsm
```

**Read this file before Phase B.** It governs what may and may not be touched in the workbook.

## Which template to load

1. The client's own current-year template rolled forward into FYI by admin
   (`{Y} ITR Workpaper - First Last`) — always first choice.
2. If FYI has none (common for a client new to the firm), copy the bundled asset above and
   work from the copy.

The asset is a read-only master. Copy it into the working folder first; never write to it,
never save a client's figures over it, and never save the external-link neutralisation back
into it.

## Contents of the master

22 sheets, in this order. Hidden sheets are hidden deliberately — they carry working schedules
that only some returns need. Leave them hidden unless the return actually uses one.

| # | Sheet | State |
|---|---|---|
| 1 | Review Notes | visible |
| 2 | Queries | visible |
| 3 | `Summary - 1 Client name ` | visible |
| 4 | `Deductions - 1 Client name ` | visible |
| 5 | Distributions | hidden |
| 6 | `Summary - 2 Client name ` | visible |
| 7 | `Deductions - 2 Client name ` | visible |
| 8 | Home Office Expenses | visible |
| 9 | Depreciation schedule | visible |
| 10 | Dividend Summary Ind | hidden |
| 11 | Income | hidden |
| 12 | Share Register | hidden |
| 13 | `Motor Vehicle ` | hidden |
| 14 | Business Summary | visible |
| 15 | Rental Property | visible |
| 16 | CGT Summary | visible |
| 17 | CGT Property | visible |
| 18 | Other Reconciliation | hidden |
| 19 | Dividend Summary Joint | hidden |
| 20 | BAS Summary | hidden |
| 21 | Client Data | visible |
| 22 | Foreign Income | hidden |

Note the trailing spaces in `Summary - 1 Client name `, `Deductions - 1 Client name ` and
`Motor Vehicle `. They are part of the sheet name and every cross-sheet formula depends on
them. A sheet name containing a space must be quoted in a reference.

The workbook carries `xl/vbaProject.bin` and 25 external-link parts. Load with
`keep_vba=True`, neutralise the external links in the working copy only, and confirm the VBA
part survives every save (Phase C already checks this).

## Landmarks that must stay where they are

- **Header block, rows 1 to 5** on every client-facing tab: `Fortis Accounting Partners`,
  `Client:`, `Period / Year Ended:`, `Workpaper:`. The Deductions, Queries and Review Notes
  tabs pull client and year from the Summary tab by formula. Do not replace those with typed
  text.
- **Summary tab** — row 10 headers: B `ITEM` (ITR label), C `DESCRIPTION`, G `Tax Credits`,
  H `$`, I `Hyperlink`, J `PREPARER'S REMARKS`, K `REVIEWER'S SIGNOFF`; `PY` marker at I8;
  `Source Documents` heading at J1 — the heading stays, the block below it stays empty (document
  links belong in the Hyperlink column, against the figure). Rows follow ITR label order.
- **Rental Property tab** — B4 `FY {Y-1}` over B:D (Total / Agency Rental Summary /
  Owner's Exp/Adj) and E4 `FY {Y}` over E:G with the same three columns, H `Ref/Remark`.
  Prior year on the left, current year on the right. This is the comparative convention the
  other working tabs follow.
- **Queries tab** — row 7 headers: `Sr No`, `Query/Issue`, `Description`, `Reference`,
  `Client's Reply`, `Reply`, numbered rows beneath.
- **Review Notes tab** — numbered rows from row 8. The Phase E manager summary and findings
  register go on this tab without disturbing the header block above them.
- **Client Data tab** — the source index (`Src`, `Client Data Excel`, `Client Data PDF`).

## What must never change

- **Sheet names, sheet order, and hidden/visible state.** The only permitted rename is
  `1 Client name` / `2 Client name` to the actual taxpayer names, and that rename must be
  followed by `patch_renames` so both formula strings and hyperlink locations move with it.
- **Fonts.** Arial 10 is the body font across the workbook; some tabs use Calibri 11, Arial 12
  for headings and Verdana 8 in places. Whatever a cell already has is correct. Write values,
  never fonts. Do not "tidy" a tab to a single typeface.
- **Colours.** The palette in the file is the palette: blue `FF0070C0` for links and input
  text, fills `FFB4FCBB` (light green), `FFDAEEF3` (pale blue), `FF92D050`, `FFFFC000`,
  `FFC00000`, plus theme colours. Introduce no others, and do not recolour cells to mark your
  own work. New hyperlinks match the existing blue/underline styling and nothing else.
- **Number formats.** Accounting currency (`_-"$"* #,##0.00_-;...`), `"$"#,##0.00`, `#,##0`,
  `[$-C09]dd-mmm-yy` and `mmm-yy` for dates, `0%` for percentages. Reuse the format already in
  the cell or the one used by the equivalent cell in the same column.
- **Column widths, row heights, merged ranges, print areas, and the header block layout.**
- **The macros.** Never save without `keep_vba=True`.

## What may change

- Values and formulas in the working cells of the tabs the return actually needs.
- Sheet renames for the taxpayer names, as above.
- Rows added *inside* an existing block where a schedule needs more lines. Insert within the
  block so the block's own totals absorb the new rows, and copy the style of the row directly
  above so the new row inherits font, fill, borders and number format. Never append below a
  total, and re-check every control row afterwards.
- Cloned per-property or per-entity copies of an existing working tab, cloned from the tab in
  this workbook so they carry its formatting.
- Cell comments and Review Notes/Queries content.

## Prove it before delivery

`scripts/verify_workpaper.py --spec` runs the fidelity check as one of its steps; standalone:

```bash
python scripts/check_template_fidelity.py <working-copy.xlsm> assets/2026_ITR_Workpaper_-_Individual_Name.xlsm
```

It compares sheet inventory, order and visibility, fonts, fills, number formats, column widths
and merged ranges against the master. Allowed and not reported as issues: the client-name renames
(`Summary - Jane Smith` maps back to `Summary - 1 Client name `), cloned working tabs (matched to
their parent by name prefix), a hidden master tab made visible because the return uses it, link
colour/underline on hyperlink cells, and the written content of the Review Notes and Queries tabs.
Everything else it reports is a defect: fix the spec and rebuild. If a difference is genuinely
required, say so in Review Notes and treat it as a master-template issue for the Y2K owner.

## Template metadata

`assets/template_meta.json` (generated by `scripts/build_template_meta.py`, rerun only when the
master changes) holds the sheet inventory, the 288 external defined names the engine deletes, and
the cell map — Summary rows by ITR label, Deductions block rows, Rental Property line rows, the
Queries and Review Notes numbered rows. The build and verify scripts read it; so should you, via
`references/fill-spec.md`, instead of opening the workbook to find a row.
