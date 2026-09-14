# Preparation rules — item by item

Everything here was learned on a real client run (De Celis FY2026). Ignore at your peril.

## Naming & filing conventions

- Workpaper: `{Y} ITR Workpaper - First Last` · Pre-fill: `{Y} Pre-Filling Report - First Last`.
- The workpaper is a **macro-enabled `.xlsm`** from build to delivery to filing. It carries
  `xl/vbaProject.bin`; a `.xlsx` copy is a broken workpaper, not a convenience.
- Filed in FYI under Client > Work Papers > {year} category, linked to the entity (both spouses on
  a joint file) and the annual compliance job. Upload with `fyi_get_upload_url` + POST of the raw
  bytes, content type `application/vnd.ms-excel.sheet.macroEnabled.12`. Confirm with the user
  before the upload — it writes to production — and file again after a Phase E rebuild. Where the
  session cannot reach the upload host, `fyi_file_document` + `file_base64` carries files under
  ~50 KB; anything larger goes to the user to file, never silently skipped.
- The spec is filed beside it as `{Y} ITR Workpaper Spec - First Last.json` (content type
  `application/json`). It is how the next run picks the job up where this one left off; a workpaper
  filed without its spec costs the next session a reconstruction from the workbook.
- A document the client emails is not a source until it is in FYI — file it, then cite the FYI id.
  A figure resting only on what the client wrote in an email is recorded as that, in the remark.
  Where the assertion *is* the evidence (the client confirming a policy or an account does not
  exist), file a PDF of the email itself so the figure has something to link to, and say in the
  remark that it rests on the client's statement. Check first whether the filing rule has already
  filed the email and its attachments — do not file a second copy.
- Email attachments filed automatically keep the sender's file name. Rename to house convention
  before citing them.
- Client name replaces the "1" placeholder on Summary and Deductions tabs (C3 / B3) and in the
  two sheet names.
- FYI stable document URL: `https://go.fyi.app/search/0/{entity_id}/0/documents/{doc_uuid}/preview`
  — use in `=HYPERLINK()` formulas for every source-document reference (this is FY2025 house style).
  Those links go in the **Hyperlink column** only (Summary I, Rental H), one against each figure the
  document supports. The Summary `Source Documents` block (J1 and below) stays empty — we do not
  link the whole document list there.

## Income items

**Salary / PAYGW / RFB** — from the pre-fill PAYG summary; check STP is *Finalised*. Reportable
fringe benefits go to IT1: label **W** unless the employer is s57A exempt (then N). Flag RFB in
remarks if new versus prior year.

**Interest / dividends** — an early-year pre-fill (July–September) usually contains **no bank or
registry data at all**. That is silence, not nil. Query the client (name any account you know
received money — e.g. sale proceeds), and put a re-run-pre-fill-before-lodgement instruction in
the Review Notes.

**ESS** — Box F of the employer's ESS statement (NAT 75282) is the assessable amount and the
**primary source**; the employer's covering letter is the calculation support — cite both, in that
order. Keep the vesting detail in remarks (units, FMV, FX, AU%). Boxes C/D/E noted if nil.
The ESS assessable value becomes the CGT cost base of those exact shares — record which tranche.

**Foreign dividends (employee plans)** — assessable gross in AUD at the statement FX rate.
FITO only for tax the client was *liable* to pay: cap at the **treaty rate** (AU–Swiss Art 10(2):
15% on portfolio dividends), not the foreign domestic withholding rate. The s 770-75 $1,000
de minimis removes the offset-limit calculation; it does not make excess withholding creditable.
Excess is reclaimable from the source country (Switzerland: Form 82) — tell the client. If the
prior year claimed the full withholding, note the potential amendment; do not repeat the claim.

**CGT — shares/RSUs** — event date = contract/execution date (decides the year, whatever the
filename says). Proceeds net of incidental costs at sale-date FX; cost base at acquisition-date FX
(vested RSUs: the ESS value at vesting, of the *correct tranche*). **Build or update a
tranche-by-tranche register on the Share Register tab** — the prototype found the prior year had
costed a sale from a tranche that had not yet vested at the sale date, corrupting the loss
carried forward. Apply current-year then carried-forward losses **before** any discount; 50%
discount only if held ≥ 12 months; losses are never discounted. Tie total losses c/f to the ATO
pre-fill's 18V; if they don't tie, the prior year is wrong — mark the register PROVISIONAL and
raise a query for the historical statements. Maintain the loss c/f register at Summary N2:P6,
formula-linked to the current CGT working.

**Rental (per property tab)** — columns: B:D prior year (Total / Agency / Owner), E:G current,
H source ref, I remarks. Rules:
- Agency column figures come only from the agent's annual summary, written as **in-cell sums of
  the individual monthly statements** (e.g. `=3900+2600+...`) so completeness is visible on the
  cell face. Split rent from reimbursements (water usage etc. = Other Income).
- Owner column: everything else, each with a source. Missing recurring owner items (strata,
  council, water, insurance, loan interest) → Query quoting the prior-year amounts.
- Depreciation from the QS report, **correct year column**, split: effective-life Div 40 in the
  rental schedule; **pooled plant to label D6** (via the tab's Low Value Pool row → Deductions D6
  → Summary); Div 43 capital works its own row. Net rent for label 21 = the pre-LVP net; taxable
  income is unchanged by the split but the labels matter to the ATO.
- Weeks rented vs weeks available: derive rent-days from the monthly statements (a short month +
  a letting fee = a re-letting; compute the vacancy). Record both numbers and remark on any rent
  change.
- Repairs > $300: check for capital items → depreciation instead.
- Ownership %: cite the evidence (prior return schedule, QS report) on the tab — agent folios are
  often in joint names for banking only.
- Control rows must be plain differences (`=F53-F54`) and must all read zero before handover.

## Offsets, levies, disclosures

**PHI** — one row per benefit code with premiums, rebate received, claim code, from the pre-fill.

**MLS** — the exemption requires **every** dependant including the spouse to hold complying
hospital cover. The client's own policy on the pre-fill proves nothing about the spouse. If
there is a spouse and their cover is unconfirmed: days-not-liable is PROVISIONAL, raise a
dedicated query (distinct from the spouse-income query), and note the tiered exposure in dollars.

**Div 293** — income > $250k: note it will be assessed separately; flag for the cover letter.

**Spouse** — name/DOB from pre-fill; taxable income is a standing query.

**Deductions** — only with substantiation; roll the prior-year list into a query (WFH,
subscriptions, donations, tax agent fee = last year's invoice, personal super + s 290-170 notice,
income protection). Watch the template's D10 total: it must not sum the non-deductible ATO GIC
row (`=SUM(C72:C73)`, not C71) — known master-template defect.

## Excel mechanics — handled by the engine

`scripts/build_workpaper.py` owns every workbook operation: `keep_vba=True`, the client-tab
renames with formula/hyperlink/defined-name patching, deletion of the master's 288 dead external
names, prior-year tab cloning with E:G → B:D roll and a full clear of the current-year constants,
link styling that keeps the cell's own font, `fullCalcOnLoad` so Excel recalculates on open.
You do not re-solve any of that. What is still yours:

1. **Totals are formulas or in-cell sums, never Python-computed constants** — write them as
   `formula` entries in the spec so the workpaper updates itself when query data lands.
2. Writing a constant over a template formula is warned about by the build; only silence the
   warning (`overwrite_formula: true`) when the template cell is genuinely an input.
3. Distinguish inherited template errors (visible in the master) from introduced ones. Ship with
   zero introduced errors; leave the firm's pro-forma formulas alone.
4. Cloned tabs lose their hyperlinks — cite every source again through `cells`, in the Hyperlink column.
5. Never hand-edit the `.xlsm`. A fix is a spec change and a rebuild.
6. `output` in the spec ends in `.xlsm`; the build refuses anything else.
7. On an update run, amend the filed spec and rebuild. Never start a second workpaper for a job
   that already has one, and never rebuild from the master over a build in progress.
8. The engine only rebuilds files of the bundled master's lineage. A worked workpaper with its own
   tab set, its own Queries columns or no VBA is not one: assess it, hand the preparer the changes,
   and leave the file alone (Phase 0).

## Verification checklist (Phase C)

Scripted — `verify_workpaper.py --spec` covers these:
- [ ] VBA present; every internal hyperlink target exists; FYI links carry the entity id and a
      document uuid
- [ ] Template fidelity (sheets, order, visibility, fonts, fills, formats, widths, merges)
- [ ] Every spec cell holds exactly what the spec says
- [ ] Declared `controls` evaluate as expected; Summary chain consistent (income − deductions =
      taxable; tax − credits = payable)
- [ ] No total row holds a constant

Yours, from the source texts — the script cannot do tax:
- [ ] Agent-summary money-in / money-out re-added independently and tied to the workpaper
- [ ] Every FX conversion recomputed
- [ ] Loss c/f register ties to ATO 18V
- [ ] Tax, Medicare and offsets recomputed at current-year resident rates (the template's tax
      table cells use IF/VLOOKUP and only resolve in Excel or a `--recalc` run)
- [ ] File named per protocol: `{Y} ITR Workpaper - First Last.xlsm`
