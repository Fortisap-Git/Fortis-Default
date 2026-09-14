# Phase D — tiered review, four lenses, scripted consolidation

## What every reviewer receives

The same context block, and **nothing that requires opening the workbook**:

- client, year, and `work/<client>/dump.txt` (from `dump_workpaper.py --changed`: every cell the
  preparer entered with its formula, link and comment, plus the row labels for context);
- the extracted source-document texts (`work/<client>/text/*.txt`) — name each file and what it is;
- the prior-year dump if there is one (`dump_workpaper.py <prior>.xlsm --changed`);
- the list of already-open queries (from the spec) with the instruction **not to re-report them**;
- the instruction: *"Report only real, verifiable defects. Quote the tab and cell. For every
  finding list the cell assertions it rests on as `claims`. If you find nothing in your lane,
  return an empty list — do not invent problems to look useful."*

Findings schema (JSON, one array per reviewer):

```json
{"title": "...", "detail": "... with figures ...", "location": "Tab!Cell",
 "severity": "high|medium|low", "expected_treatment": "...",
 "claims": [{"sheet": "Rental Property - 12 Smith St", "cell": "F27", "expect": "=280+190+190+190"},
            {"sheet": "Summary", "cell": "H16", "expect": "blank"}]}
```

`expect` is a number, a formula string, `"blank"`, or `"nonblank"`. Claims are what makes a
finding checkable in one script run instead of a second agent pass.

## Tiering

| Return | Reviewers | Why |
|---|---|---|
| Salary/interest/dividends/deductions only | **1** agent, all four lenses in one prompt | the lanes overlap almost entirely on a simple file; four agents find the same three things |
| Any rental, CGT, ESS, foreign, business schedule | **4** agents in parallel, blind to each other | independence is the point: on the prototype the two most valuable catches each came from a single lens |
| No prior-year workpaper | drop Lens 3 (so 1 or 3 agents) | label totals give a variance lens nothing to work against; it returns noise |

Never skip the claims verification step — it is where false findings die.

## Lens 1 — Completeness
Work from the source documents INWARD. Every pre-fill item in the Summary or deliberately
excluded with a remark; every source document used somewhere (an unused document is a finding);
income categories present last year that vanished unexplained; disclosure items (RFB, PHI rows
and codes, MLS days, spouse, income tests); pre-fill warnings implying uncaptured sources.

## Lens 2 — Technical treatment
Tax law only, ignore presentation. CGT cost base derivation and FX at each leg, holding period,
loss-before-discount ordering, 18V tie-out; ESS year of assessability and cost-base linkage;
FITO versus the treaty rate actually creditable; depreciation year-column and Div 40/43/pool
split; Medicare, MLS, Div 293, PHI codes; the tax calculation's rates and thresholds for the year.

**Arming.** Before spawning, invoke the firm's micro-skills for the domains present via the Skill
tool — `anthropic-skills:itr-income-dividends`, `itr-income-cgt`, `itr-income-ess`,
`itr-income-rental` + `itr-capital-allowance`, `itr-income-foreign`, `itr-income-managed-funds`,
`itr-income-interest`, `itr-income-salary-wages`, `itr-income-government`, `itr-income-business-psi`,
`itr-deductions-home-office`, `itr-deductions-investment`, `itr-deductions-personal` — and paste
each returned body into this lens's prompt under a heading. They are the firm's own checklists,
far sharper than general knowledge. Domains with no evidence in the return get no micro-skill.

## Lens 3 — Prior-year variance
Line-by-line against the prior-year dump. Material movements without an explanatory remark;
recurring items present last year, absent this year, and **not covered by an existing query**.
Before flagging a vanished item, explain it from this year's own facts (deposit consumed by a
settlement, account closed, term deposit matured, one-off first-letting cost). Where the facts
explain it, the finding is "add a remark", not "query the client". Also: whether the comparatives
copied in actually match the prior-year figures; whether a big swing is fully explained by the
known outstanding items.

## Lens 4 — Substantiation
Every populated figure carries a source reference; hyperlinks point at documents that contain
what they claim; agency versus owner columns correctly attributed; re-add the source documents
independently and compare; hardcoded numbers that should be formulas; formula ranges off by a
row; control rows.

Proportionality — the lens most likely to over-fire. We are the client's accountant, not their
auditor: the test is whether the *claim* stands up, not whether the *paperwork* would satisfy an
auditor. A renewal notice due before year end on a mortgaged property was paid; a bank's own
email saying a fee "will be charged on 21 May" means it was charged; a rates notice evidences
rates. Reserve findings for things that could change the return and cannot be resolved by
thinking: characterisation, apportionment, ownership share, a missing tax statement whose
components can't be derived, a figure that contradicts its own source.

Vouching discipline: every judgement call — ownership split, business-use %, WFH hours and method,
6-year main-residence election, bring-forward super — must be backed by a **written client
instruction** on file, not the preparer's assumption. Never infer or back-solve a source figure to
make it tie — an unreachable source is an Unsubstantiated finding. Variances of $2 or less are
never findings (all lenses).

## Consolidation — done by you, with the script

1. Pool every `claims` entry into `work/<client>/claims.json` and run
   `python scripts/verify_workpaper.py <file> --spec spec.json --claims claims.json`. Any finding
   with a FALSE claim is discarded outright.
2. Merge duplicates; a point raised independently by 2+ lenses ranks higher.
3. Discard restatements of open queries, style preferences, speculation without evidence.
4. Rank by monetary effect and lodgement risk.
5. Categorise per the Review Points Register: Error Category (tax/accounting treatment · missed
   checklist step · data entry · formatting · other) × Root Cause (training gap · process gap ·
   template issue · care & attention · unclear instructions). A point the checklist should have
   caught = missed checklist step / care & attention; a point the checklist doesn't cover = process
   gap / template issue.
6. Anything that contradicts a Phase C verification gets re-checked against the source text.
   Reviewers state falsehoods confidently; never publish unverified agent output.

## Output — the review lives in the workpaper

Write it through the spec's `review` block (see `references/fill-spec.md`): manager summary block
(plain English — no statute cites, no lens names, no cell references), then the findings register
grouped **by nature in ITR label order** with Status AMEND / QUERY / FIXED / NOTE. One or two
sentences per point. Rows the verification killed simply don't appear. The engine adds a cell
comment "Review Notes row N" at every flagged cell.

In chat, two lines at most: findings count, dollars at stake, sign-off readiness.
