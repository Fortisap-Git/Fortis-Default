---
name: individual-itr-workpaper
description: Prepares AND reviews the Fortis Individual ITR Excel workpaper from documents filed in FYI, on the bundled master template with structure, fonts and colours untouched. Data-driven: you write a JSON fill spec, bundled scripts build, verify and dump the workbook in seconds. Rolls forward the prior year (or builds comparatives from the prior-year signed ITR for a new client), parses the ATO pre-fill, populates income/deductions/rental/CGT/ESS/foreign workings, raises client queries, runs a tiered review (one reviewer for simple returns, four blind lenses for complex ones), writes the review summary and findings register into the Review Notes tab, and files the finished macro-enabled `.xlsm` to FYI (Work Papers, year category) after confirmation. Invoked again for a client whose current-year workpaper this skill already built, it updates that file rather than starting a second one: it reads the filed spec, gathers what has arrived in FYI and in Outlook since the last build, re-runs the pre-fill, answers the open queries, and rebuilds and re-files. ALWAYS trigger for "prepare workpaper", "prepare the workpaper for [client]", "start [client]'s tax return", "do [client]'s ITR", "[year] workpaper for [client]", "finalise the workpaper", "review [client]'s ITR workpaper", "update [client]'s workpaper", "[client] has sent their information", "[client] has replied to the queries", "add the new documents to [client]'s workpaper", or "refresh [client]'s workpaper". Do NOT trigger for company/trust/SMSF jobs, BAS/IAS, pre-June planning, or the cover letter alone.
---

# Individual ITR Workpaper — Prepare & Review

Produce a manager-ready `.xlsm` workpaper for an Australian individual tax return, built entirely
from the client's file in FYI, reviewed independently, with every surviving finding either fixed or
turned into a query. The workpaper is the supporting reconciliation behind XPM — XPM entry and
lodgement stay with the preparer.

**How the work is split.** You do the tax thinking and write **data**: a JSON fill spec (which
cell gets which figure, formula, source, remark), a query list, a review register. The bundled
scripts do every Excel operation — load, rename, neutralise, clone, write, link, verify, dump — in
a few seconds each, deterministically. **Never write per-client Python against the workbook and
never hand-edit the `.xlsm`.** If the engine cannot express something, say so in Review Notes as a
template issue; do not work around it in code.

Read before Phase B: `references/fill-spec.md` (the spec format and the cell map) and
`references/preparation-rules.md` (item-by-item tax rules). Read before Phase D:
`references/review-lenses.md`. `references/template-fidelity.md` is enforced by the verify
script — open it only when the fidelity check fails and you need to know why.

## Inputs

Only a client name (and optionally a year — default: the most recent 30 June). Everything else
comes from FYI. If the FYI connector is down, stop and say so — never prepare from memory or
invent figures.

## Phase 0 — New build, or update the one already on foot?

A client's information arrives in instalments. The first build almost always ships with open
queries, and the answers land days or weeks later. So a second invocation on the same client and
year is normally an **update**, not a new build — decide which before anything else.

**Detect.** `fyi_find_documents` by `entity_id` for the current year's Work Papers:

- `{Y} ITR Workpaper - First Last.xlsm` **with its spec beside it** (`{Y} ITR Workpaper Spec -
  First Last.json`) → a build by this skill. The spec is the state of that build: sources cited,
  cells written, queries raised, review register, `run.round` and `run.built`. Work from it.
- The workpaper is populated (current-year columns filled, Queries rows, a Review Notes register)
  but no spec is filed → built in a session that did not file its spec. Reconstruct the spec from
  the file (`dump_workpaper.py --changed` gives every cell, formula, link and comment) before
  changing anything, and file it this time.
- An untouched roll-forward from admin — current-year columns empty, no queries — is not a build
  in progress. That is a new build: Phase A.
- **A worked workpaper that is not of the master's lineage** — a different tab set (its own rental
  tabs, extra schedules), a Queries tab with different columns, an `.xlsx` with no VBA, or a
  fidelity check that fails on styles and widths rather than on anything you did. Check before you
  plan a rebuild: `verify_workpaper.py <file> --no-fidelity` on the `vba` line, and the tab list
  against the master. The engine cannot rebuild such a file — its landmarks, its Queries columns
  and the fidelity check are all defined against the bundled master, and a rebuild would restate a
  file someone has worked for days. **Do not rebuild it, do not convert it to `.xlsm`, and do not
  hand-edit it.** Do the Phase A′ assessment and hand the preparer the list: query by query, what
  the client answered, which cells it touches and what each one should become. Say plainly in chat
  that the file is outside the engine's lineage, so the update is theirs to key in.

**Never** start a second workpaper for a job that already has one, and never rebuild from the
master when a build exists. The client's answers, the review register, the preparer's remarks and
every judgment call already made live in that file.

## Phase A′ — Update run (what has arrived, and what it changes)

1. **Cut-off.** The last build: `run.built` in the spec, else the filed date of the workpaper in
   FYI. Everything after it is new information.
2. **FYI.** `fyi_find_documents` by `entity_id` again. New is anything filed or modified since the
   cut-off, plus anything the prior spec's `sources` does not already carry. Download and extract
   with `gather.py` exactly as in Phase A — the cache makes already-seen documents free.
3. **Outlook — in scope on an update run** (the one exception to Phase A step 5; the client's reply
   is the whole point). Search the client's address and the query-email thread since the cut-off.
   An emailed document is **not a source until it is in FYI**: a workpaper hyperlink needs a stable
   FYI target, so file the attachment first (SUGGEST → CONFIRM, same cabinet rules as the
   workpaper) and cite the FYI id. Where the answer is prose and no document exists, record the
   client's words in the query's `client_reply` and in the cell remark, and say on the face of the
   workpaper that the figure rests on the client's statement.
4. **Re-run the pre-fill.** It fills in through the year — bank interest, dividends and health
   cover that were absent in July are usually there by October. Reconcile the new pre-fill against
   what is already in the file before touching anything else.
5. **Assess, item by item.** For every open query: answered, partly answered, or still open? For
   every new document: which cells does it touch, and does it confirm a figure, change one, or add
   one? Does anything contradict a remark, a PROVISIONAL position, or a review finding? A document
   that changes nothing is still worth a source link on the figure it supports.
6. **Apply to the same spec, in place.** Add the new `sources`; add or amend `cells`; set
   `client_reply` (and `reply` where we answered) on the queries that came back; leave unanswered
   queries standing. Move review findings the new information resolves to FIXED and add rows for
   anything it raises. Bump `run.round` and set `run.built`. Then Phase B's one command, Phase C's
   verify — a rebuild, not a patch.
7. **Re-review in proportion.** Re-run only the lenses whose domains the new information touches: a
   rental agent summary or a share sale confirmation earns its full lens, a confirmed interest
   figure does not. Findings in untouched areas stand as they are.
8. **Deliver and re-file** per Phase E — same name, replacing the version on file, spec beside it.
   In chat: what arrived, what changed and by how many dollars, which queries closed, which are
   still open. On a file outside the engine's lineage there is nothing to rebuild or re-file: the
   assessment itself is the deliverable, and the attachments still get filed to FYI so the
   preparer can link them.

**Never close a query silently.** One answered with "nothing to add" is closed with the client's
own words recorded; one that is still open stays open and stays on the list for the next chase.

## Phase A — Gather (target: under 3 minutes)

1. Resolve the client: `fyi_list_clients` (search surname). Note entity id, manager, partner. On a
   joint file resolve both spouses' ids.
2. Enumerate documents with `fyi_find_documents` by `entity_id` (never name wildcards). You need:
   the current-year workpaper template rolled forward by admin (`{Y} ITR Workpaper - First Last`),
   the prior-year workpaper, the ATO pre-fill, the prior-year signed ITR, and every current-year
   statement (dividends, ESS statement + letter, share sale confirmations, agent rental summary,
   QS depreciation report, bank/loan statements, Content Snare exports).
3. Get a presigned URL for each with `fyi_download_document`, write them to
   `work/<client>/manifest.json` as `[{"id","name","url"}]`, and run
   `python scripts/gather.py work/<client>/manifest.json work/<client>/` **immediately** (URLs
   live ~15 min). It downloads in parallel, extracts text (pdftotext → PyMuPDF → pypdf) and caches
   by document id, so a re-run is free. Read the `text/*.txt` files, not the PDFs.
4. Judge each document's **tax year by its event dates, not its filename** — a "July 2026 Share
   Sale" executed 24/07/2025 is an FY2026 CGT event.
5. Outlook is **not** part of the default gather on a first build. Check it when the user asks,
   when a document the pre-fill implies is clearly absent from FYI, or on an update run, where the
   client's reply is the point (Phase A′). Anything found unfiled is a flag to the manager, and
   never a working source until it is filed in FYI.
6. Data the prior year expected that has not arrived (owner rental expenses, deduction evidence)
   becomes a Query — never a silent zero, never an estimate.

**No prior-year workpaper (client new to the firm).** Confirm it is genuinely absent (a workpaper
filed under an odd name is still a workpaper). Then the prior-year signed ITR is the comparative
source: populate B:D only to the depth the ITR supports (label totals, rental-schedule lines — never
apportion a label across holdings) and head those columns "FY{Y-1} (per signed ITR)". Raise as
Queries the balances only the previous accountant holds: Div 40 opening values and effective lives,
low-value pool balance, Div 43 cost base and construction dates, property cost bases and
acquisition dates, unused-cap or election history. **Never restart a depreciation schedule from
scratch** — an invented opening value is a wrong deduction every year after. No prior ITR either →
ask the client for it before building.

## Phase B — Build (target: one spec, one command)

1. Write `work/<client>/spec.json` per `references/fill-spec.md`. Template: the client's
   rolled-forward copy from FYI if it exists, else `null` for the bundled master. The engine
   renames the client tabs, patches every formula and hyperlink, deletes the master's 288 dead
   external names, clones and rolls prior-year tabs, and writes your cells, links, queries and
   notes. Use the cell map in fill-spec.md — do not open the workbook to find rows.
2. Populate per `references/preparation-rules.md`: pre-fill items reconciled to statements (never
   trusted alone); rental agency column as in-cell sums of the monthly statements, owner column
   everything else; Div 40 effective-life vs pooled split, weeks rented; CGT with event dates,
   ESS-linked cost base, losses before discount, 18V tie; ESS statement primary, letter support;
   foreign dividends gross at statement FX with FITO at the treaty rate; PHI/MLS/spouse; deductions
   only with substantiation.
3. Every figure: a live formula where derived, an in-cell sum where it aggregates statements, a
   `source` on every populated cell, a `remark` wherever a reader would ask why. Declare the
   cells that must tie in `controls` (rental control rows, Summary Variance once per-ITR is keyed).
   Source documents are linked **only in the Hyperlink column** (Summary I, Rental H), against the
   figure each one supports — never listed as a block of links under the Summary `Source Documents`
   heading, and never linked for a document no figure cites.
4. Queries: one entry per open item quoting prior-year amounts; the engine links both ways and
   leaves the awaiting cell blank so totals recompute when data lands.
5. `review_notes`: judgment calls, provisional positions, anything the manager must decide.
6. Run `python scripts/build_workpaper.py work/<client>/spec.json`. Read its warnings — a
   "template formula replaced by constant" warning is usually a mistake.

## Phase C — Self-verify (one command, loop until ALL CLEAR)

```
python scripts/verify_workpaper.py "work/<client>/<file>.xlsm" --spec work/<client>/spec.json
```
Checks VBA, every hyperlink target, FYI link shape, template fidelity, spec-vs-file, declared
controls and the Summary chain (built-in formula engine — no LibreOffice needed), and that no total
row holds a constant. A FAIL means fix the **spec** and rebuild; never patch the file. Then, from
the source texts, independently re-add the agent-summary money in/out, recompute each FX leg, and
tie the loss schedule to 18V — those are tax checks the script cannot do. Add `--recalc` only if
LibreOffice is installed (it produces a recalculated copy for the dump); otherwise Excel
recalculates on open (`fullCalcOnLoad` is set) and the tax-table cells are confirmed there.

## Phase D — Review (tiered; reviewers read a dump, not the workbook)

1. `python scripts/dump_workpaper.py "<file>.xlsm" --changed > work/<client>/dump.txt` — every
   cell the preparer entered, with formulas, links and comments, plus row labels. This is the only
   workbook artefact a reviewer receives. No reviewer opens Excel or runs Python.
2. **Tier by complexity.** Salary, interest, dividends and deductions only → **one reviewer** agent
   whose prompt carries all four lenses. Any rental, CGT, ESS, foreign income or business schedule
   → **four reviewers in parallel, blind to each other**, one per lens (`references/review-lenses.md`).
   No prior-year workpaper → drop the variance lens (three reviewers) and tell the consolidation
   step there is no baseline.
3. **Arm the technical lens** with the firm's micro-skills for the domains actually present: invoke
   `anthropic-skills:itr-income-dividends`, `itr-income-cgt`, `itr-income-ess`, `itr-income-rental`
   + `itr-capital-allowance`, `itr-income-foreign`, `itr-deductions-home-office` etc. via the
   Skill tool and paste the returned body into that reviewer's prompt. Skip domains with no
   evidence; if a micro-skill is unavailable, the lens reviews from general knowledge — say so.
4. Every reviewer returns JSON findings, each with `claims: [{"sheet","cell","expect"}]` — the
   concrete cell assertions the finding rests on. Collect all claims into
   `work/<client>/claims.json` and run `verify_workpaper.py ... --claims work/<client>/claims.json`.
   **A finding whose claim comes back FALSE is discarded**, whatever the reviewer's confidence.
5. **You consolidate** (no separate consolidator agent): merge duplicates (2+ lenses = stronger
   signal), drop restatements of already-open queries and anything under $2, rank by dollars and
   lodgement risk, categorise per the Review Points Register (Error Category × Root Cause). Any
   finding contradicting something you verified in Phase C gets re-checked against the source text,
   not accepted.

## Phase E — Apply and deliver (one rebuild)

1. Add a `rev` section to the spec for every accepted fix and a `review` block per fill-spec.md:
   manager summary (plain English — no statute cites, no lens names, no cell refs: bottom line,
   waiting on the client with dollars, fixed during review, outside this file), then the findings
   register grouped **by nature in ITR label order** with Status AMEND / QUERY / FIXED / NOTE.
   Fold the Phase B `review_notes` rows into the matching sections. Judgment items you cannot
   decide become new Queries plus PROVISIONAL rows — not silent choices. Keep each review point to
   one or two sentences.
2. Rebuild once, verify once (`--spec`, and `--claims` for the fixed cells). The engine flags every
   register cell with a comment "Review Notes row N".
3. Deliver the `.xlsm` the engine built, unchanged. The workpaper carries VBA: it is macro-enabled
   `.xlsm` at every step — never converted to `.xlsx`, never re-saved through another tool, never
   handed over as a stripped copy. `verify_workpaper.py` fails the file if the extension or the
   macros are gone. (This governs what the engine builds. A client file of another lineage already
   on foot as `.xlsx` is not converted — see Phase 0.) In chat, two lines at most: findings count, dollars at stake, sign-off
   readiness. Everything else lives in the file.
4. **File the workpaper to FYI.** Part of the job, not an optional extra — the build is not
   delivered until it is on the client's file. It writes to production, so SUGGEST → CONFIRM: one
   line naming the file, cabinet and categories, then upload on a yes.
   - Name `{Y} ITR Workpaper - First Last.xlsm`, linked to the entity (both spouses on a joint
     file) and to the annual compliance job if one exists.
   - Cabinet **Work Papers**, categories **Year = {Y}** (plus the firm's ITR category where the
     cabinet uses one). Replace the admin-rolled-forward copy rather than filing a second document.
   - `fyi_get_upload_url`, then POST the raw bytes with content type
     `application/vnd.ms-excel.sheet.macroEnabled.12`. `fyi_file_document` with `file_base64` is
     only for files under ~50 KB — a workpaper never is.
   - **If the POST cannot leave the session** (a sandboxed or proxied session may refuse the upload
     host outright: a 403 on CONNECT, not a bad URL — re-minting the URL will not help), say so
     rather than pretending it filed. Small companion files (a query-email PDF, a client's emailed
     receipt) still go up through `fyi_file_document` with `file_base64`; the workpaper itself is
     too large for that, so hand it to the user to drop into FYI and name the cabinet, categories
     and links they should set.
   - Rebuilt in Phase E after review fixes? File that version, so FYI holds the reviewed file and
     not the pre-review one.
   - **File `spec.json` beside it** as `{Y} ITR Workpaper Spec - First Last.json`, same cabinet and
     categories. It is the audit trail of the build and the state the next run reads (Phase 0):
     without it, a later session has to reconstruct the build from the workbook.
5. Offer the client query email (Outlook draft) — draft only, never send.
6. Master-template defects belong to the Y2K master — report them, do not fix the copy.

## Judgment principles

- Follow prior-year treatment for layout and mechanics; **do not follow it into a wrong tax
  position** — flag with authority instead (FITO at withholding rate and RSU cost base from an
  unvested tranche were both "consistent with PY").
- Absence of data in the pre-fill is not evidence of nil — early-year pre-fills carry no bank
  data. Always instruct: re-run the pre-fill before lodgement.
- A recurring item missing this year is a query **only if there is reason to think it still
  exists**. First explain it from the year's own facts (deposit consumed by a settlement, account
  closed, term deposit matured); write the explanation in the remark and move on. Chase only when
  something contradicts the explanation.
- When a figure cannot be verified, say so on the face of the workpaper.
- **We are the client's accountant, not their auditor.** The standard is a reasonable belief the
  return is correct. A renewal notice due before year end on a mortgaged property was paid; a
  bank's own email saying a fee "will be charged" means it was charged; a rates notice evidences
  rates. Ask the client only where the answer could change the return and you cannot reason to it
  from the file. A padded query list is a worse review, not a more thorough one.

## Time budget

| Phase | Expected | If it runs longer |
|---|---|---|
| A gather | 2-3 min | you are reading PDFs instead of `text/*.txt`, or downloading serially |
| A′ update | 3-5 min | you are rebuilding from the master instead of editing the filed spec |
| B spec + build | 5-10 min thinking, 2 s build | you are exploring the workbook instead of using the cell map |
| C verify | 30 s per loop, 1-3 loops | you are patching the file instead of the spec |
| D review | 3-5 min simple, 6-10 min complex | reviewers were handed file paths instead of the dump |
| E apply | 2 s rebuild + one verify | you rebuilt more than once |
