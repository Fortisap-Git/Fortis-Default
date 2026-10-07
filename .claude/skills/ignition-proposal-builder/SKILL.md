---
name: "ignition-proposal-builder"
description: Builds and amends draft Ignition engagement proposals for Fortis clients. Resolves the group from the Monday.com Annual Compliance board, falling back to FYI. Default fee is the Monday Fees column (last FY fee) plus 5%, rounded to the nearest $50; blank means ask Rehman, never estimate. Every fee is checked against the firm's pricing reference (component build-up plus comparable accepted FY26 proposals) and a higher or lower fee is recommended when out of line; Rehman decides. Default billing 50% deposit, 50% on completion. One consolidated service line per group, scope closing with the house additional-services sentence. Always stops at DRAFT. ALWAYS trigger for "Ignition proposal", "create a proposal for [client]", "last year's fee plus [X]%", "mirror [proposal]", "renew [client]'s engagement", "amend [client]'s proposal", "is this fee right", "what should we charge", "price check", or any request to price, build or change a client engagement. NOT for invoice wording, the proposal email, or template admin.
---

# Ignition Proposal Builder

You build and amend draft Ignition proposals for Rehman at Fortis Accounting Partners. Every build and every amendment ends at a draft for his review in Ignition. You never send a proposal and never change its state beyond draft.

Read these before your first Ignition write call:

1. `references/ignition-mechanics.md`, which carries the slugs, formats, Monday column ids, and known API quirks.
2. `assets/prop-1679-example.json`, the accepted Portquip Group proposal (PROP-1679) captured in full. It is the canonical example of the default build: structure, billing schedules, portion strategies, scope wording pattern, and house settings. Mirror it unless Rehman directs otherwise.
3. `assets/prop-1786-example.json`, the RAJBANSHI/2R Design proposal (PROP-1786) captured immediately after amendment. It is the canonical example of **amend mode** and of the **one service line rule**, and carries the consolidation recipe and the post-amend consistency checks. Read it for any amend, and any time a group build is heading towards one line per entity.
4. `references/pricing-reference.md`, the component rate card, the comparable accepted FY26 proposals, and the build-compare-recommend mechanism. Read it at step 2 of every build so the fee is checked against what Fortis has actually agreed this season, not just uplifted from last year.

## Mode selection

- **Default build (Monday fee + 5%, rounded to $50, 50/50 billing)**: Rehman names a client or group ("build the FY26 proposal for Portquip"). Resolve the group from Monday, price from the Fees column plus 5% rounded to the nearest $50, run the pricing consistency check, and bill 50% deposit on acceptance with 50% on completion. This is the standard path; use it whenever no other basis is given.
- **Price check only**: Rehman asks whether a fee is right or what to charge ("is 4,500 right for the Smith group", "what should we charge a new client with a company and two returns"). Run steps 1 and 2 only, present the reference fee, comparables and recommendation, and stop. No draft is built unless he then asks for one.
- **Mirror mode**: Rehman names a source proposal or client to copy ("mirror Penn Property for JD Refrigeration"). The source proposal's structure, billing rules, terms, and email templates carry across; only the client, entities, and fee change.
- **Custom fee basis**: Rehman states a different uplift, a flat fee, or asks for Xero-derived pricing. Only pull Xero invoices when he explicitly asks; the Monday Fees column is the default source.
- **Amend mode**: Rehman names an existing draft and a change to it ("amend the 2R Design proposal to have one service line", "add the wife's return", "drop the trust", "reword the scope"). Do not rebuild. Read the current document, apply the smallest set of write calls that achieves the change, hold the total constant unless he asks otherwise, then re-read and run the consistency checks in `assets/prop-1786-example.json`. Report anything else that looks wrong; fix only what he asked for. Amend mode also covers proposals that are already awaiting acceptance only to the extent Ignition allows: if the proposal is not in draft, stop and tell him it must be recalled first.

## Workflow

### 1. Resolve the client group (Monday first, FYI fallback)

- **Monday first**: search the Annual Compliance 2026-2027 board (id `18419272927`) for the client group. Filter the Group column (`text_mkshm0f`) with `contains_text`; if that misses, retry on item name via `searchTerm`. Pull every item in the group with Group, Entity Type, Status, and Fees columns. This one call gives you the entity list and the fee basis together.
- **FYI fallback**: if the group is not on the Monday board, resolve via `fyi_list_clients` by surname or group name, which carries the entity_group, partner and manager.
- **Then Ignition**: find the Ignition client record and its `cli_` slug. Use, in order: the known slugs table in `references/ignition-mechanics.md`; the `client_slug` on any earlier proposal for the group you already have (FY25 proposal number from Monday, FYI or Rehman); `list_clients` with a name filter. **Do not stall if none of these works.** The `filter` argument is rejected from chat ("value at /filter is not an object") and the client list holds 4,000+ records, so paging is not an option. Build the proposal with no client (`create_proposal` without `client_slug`), which Ignition allows: it is created in `new` state, valid and fully priced, and Rehman attaches the client in the editor. Say plainly in the summary that the client must be assigned within 7 days or Ignition deletes the draft, give the date, and add the slug to the known-slugs table once Rehman supplies it. If the client genuinely does not exist in Ignition, flag it and ask before creating one.
- For group proposals, list every entity in scope and confirm the set with Rehman before building. Name exclusions explicitly, and always exclude SMSFs (separate engagements, standing rule), dormant entities (in scope but no fee, ASIC review only), and archived entities, so he can veto in one pass.

### 2. Establish the fee (Monday Fees column + 5%, rounded to the nearest $50)

- Read the Fees column (`numeric_mkshfxes`) across the group's items. Convention: the group fee usually sits once on the head entity item, ex GST; other entity items are blank; SMSF items carry their own separate fee which you ignore for a group proposal.
- The board figure is the **last FY fee**. Apply a **5% uplift** by default (a different % only if Rehman states one), then **round to the nearest $50** (midpoints round up). Treat all amounts as ex GST; GST resolves via the tax slug in Ignition.
- Show the working: last FY fee per Monday, uplift %, unrounded figure, rounded fee ex GST, fee inc GST. Example: 20,000 + 5% = 21,000, no rounding needed, 23,100 inc GST. Example: 2,344 + 5% = 2,461.20, rounds to 2,450 ex GST, 2,695 inc GST.
- **If the Fees column is blank** for every non-SMSF entity in the group: for an existing client, stop and ask Rehman for the fee. For a new client, build the reference fee from `references/pricing-reference.md` (step 2a) and present it as the proposed fee with its comparables; do not estimate any other way, and do not silently fall back to Xero.
- If several non-SMSF entities each carry a fee, present the per-entity figures and the sum, and confirm which basis he wants before building.
- **Mirror mode**: read the source proposal with `get_proposal_document` (full document tree). Capture service slugs, billing rules, amounts, terms template, email template, tax slug, sender slug, and display settings. Ask for the new fee if it differs.

### 2a. Check the fee against the pricing reference

Do this on every build, including mirror mode and custom fee basis, before the confirmation. `references/pricing-reference.md` carries the full mechanism; the short form:

- **Build the reference fee** by summing the Reference column for every entity and schedule in the resolved group (company by size, trust by type, individuals, rentals, sole trader, CGT, and so on). Where a detail that changes the number is unknown, assume the standard row and say so.
- **Compare**: ratio = proposed fee divided by reference fee. Between 0.85 and 1.20 is consistent. Below 0.85, recommend higher and state the reference fee, the dollar gap, and for an existing client also the halfway step. Above 1.20, look for the complexity drivers listed in the reference (payroll and STP, R&D, business-sale CGT, three or more rentals, first-year or part-year entities, large trading company); if they explain the gap say so and treat as consistent, otherwise recommend lower or ask what is driving the premium.
- **Quote two or three comparables** from the reference table by proposal number and fee, choosing the closest entity mix. If nothing in the table resembles the group, say so and offer to read one of the named proposals with `get_proposal_document`.
- **Recommend, never substitute.** The proposed fee stays the Monday-plus-5% figure (or Rehman's number) until he picks the recommendation at the confirm step. Every recommended figure is rounded to the nearest $50.

### 3. Confirm before build

One consolidated confirmation covering: entity list with named exclusions, fee working (last FY fee, uplift, rounded fee ex and inc GST), the pricing check from step 2a (reference fee, ratio, two or three comparables by number, and the recommendation in one or two sentences), billing model (state "50% deposit on acceptance, 50% on completion" unless directed otherwise), and proposal name. The accepted PROP-1679 fee was set above the raw board figure at this step, so treat the calculated fee as the starting proposal, not a locked number; Rehman chooses between the proposed and recommended figures here. For a simple single-client mirror where the check comes back consistent, a one-line "building now on this basis, fee consistent with reference" is enough.

### 4. Build the draft (50/50 default billing)

Follow the PROP-1679 recipe in the asset file exactly:

- **One service line for the whole group.** A group proposal carries a single consolidated service line on the Annual Group Compliance library service (`svc_navnvsskmlbqaaiawxgq`), with each entity appearing as a bolded heading inside that one description. Never build one line per entity, and never split the individuals out from the company. Both worked examples follow this; PROP-1786 was amended back to it after being built the wrong way, and the duplicate lines had already produced a mislabelled return in the process. If Rehman wants per-entity pricing visible he will say so.
- One option, one project named "[Group Name] FY[YYYY]", one service group with `billing_mode: deposit`.
- Two billing schedules on the service group: schedule 1 "Deposit" (`once_off`, `start_type: acceptance`, `start_delay: P0M`) and schedule 2 "Balance" (`once_off`, `start_type: date`, start date 30 June at the end of the engagement term).
- One proposed service on the group's compliance service (see slugs table), full fee as a fixed price rule, split into two 50% portions: the deposit portion with `invoice_strategy: automatic`, the balance portion with `invoice_strategy: manual` (invoiced on completion of the work).
- Service name pattern: "Annual Group Compliance - Deposit (50% on acceptance)". Proposal name pattern: "[Client/Group Name] - FY[YY] [Engagement type]".
- Scope description follows the pattern documented in the asset: period-covered block, then straight into the per-entity bolded headings with entity-type-standard bullets, dormant entities as a single no-fee bullet, no SMSFs, closing with "All other matters as required." followed by the house closing sentence.
- **No catch-up paragraph.** The former "Substantially overdue or multi-year catch-up lodgements that fall outside the normal annual cycle will be confirmed with you and quoted separately." paragraph is retired (Rehman, 2026-09-10). Do not write it between the period-covered block and the first entity heading, and remove it when amending an older draft that still carries it.
- **Every quote ends with the additional-services sentence.** The last paragraph of every service line description, on every proposal type (group, individual, SMSF, mirror, amend), is exactly: `<p>Additional services that are not covered in this proposal will be charged at our hourly rates as listed in the Terms &amp; Conditions on a periodic basis as required.</p>`. It sits after "All other matters as required." This is the same sentence the library service `svc_newomsxb3ovaaqiawgka` and PROP-1922, PROP-1725 and PROP-1984 already carry, so it is house wording, not new wording. If a proposal has more than one service line, the sentence goes on the last line only, unless the lines sit in separate projects, in which case each project's last line carries it.
- **Activity statements are NOT in scope by default.** The period-covered block carries an amendment bullet only: the June quarter activity statement (BAS) amended where required to correct the GST position for the year of compliance, followed by a sentence stating that ongoing preparation and lodgement of quarterly activity statements (BAS and IAS) is not included and will be quoted separately. Never write a default bullet promising quarterly BAS or IAS lodgement across the term, and apply the same rule inside the per-entity bullets: the company bullet reads "Amendment to the June [YYYY] quarter activity statement (BAS) where required, to correct the GST position for the year of compliance." If Rehman says an engagement does include ongoing activity statements, add them and note it in the summary.
- **Other associated lodgements defaults to exactly three things**: the ASIC annual review, correspondence with the ATO on the client's behalf, and limited advisory during the year. PAYG instalments, STP finalisation and similar are not default inclusions; add them only on instruction, and flag them in the summary when you do.
- Service line terms carry the house "Basis of fee and payment" wording from the asset (50% deposit, balance on completion, deposit non-refundable to the extent work performed).
- Create with `create_proposal` (or `create_proposal_using_template` where a proper Ignition template exists), then verify every line with `get_proposal_document`. Remove template line items that don't apply and confirm removals in the summary.
- Apply the mechanics in the reference file exactly: GST tax slug on every line, raw HTML in descriptions, sender slug, and the tax_exempt false-alarm fix.

### 4a. Amending an existing draft

`assets/prop-1786-example.json` carries the full recipe. The load-bearing parts:

- **Add before you remove.** `update_proposed_service` cannot change `service_slug`, so converting per-entity lines into one group line means `add_proposed_service` on the right library service, then one `update_proposed_service` to set name, billing name, description, terms, price, quantity, tax and invoice strategy, then `remove_proposed_service` on each old line. Price the new line fully before deleting anything, so a failed call never leaves the draft gutted.
- **The library service arrives dirty.** Adding `svc_navnvsskmlbqaaiawxgq` returns it named "Annual Group Compliance (Monthly)" at zero dollars with `tax_exempt: true` and an XXX-placeholder description. Expected, not an error; the single patch call clears all of it and re-resolves the tax flag.
- **Hold the total.** Consolidation is presentational. The new line equals the sum of the lines it replaces unless Rehman asked for a fee change. Check the pricing summary before and after.
- **Run the consistency checks and report, do not fix.** Billing mode against the deposit wording in the message and terms, promises in the personalised message with no matching service line, entity names consistent across name/billing name/description, total unchanged, fee rounded to $50, closing additional-services sentence present, catch-up paragraph absent. Flag failures in the summary and offer to fix them. A once_off group cannot be converted to deposit billing through the API, so that one needs a rebuild via `create_proposal`; offer it, never do it unasked.
- **Fee changes in amend mode go through step 2a too.** If Rehman asks to change the fee while amending, round the new figure to $50 and run the pricing check before writing it.

### 5. Verify and summarise

After building, re-read the proposal and confirm:
- every service line has the right amount, rounded to $50, and GST resolving (pricing summary shows GST)
- both billing portions exist, split 50/50, deposit automatic and balance manual
- the scope closes with "All other matters as required." then the additional-services sentence, and carries no catch-up paragraph
- terms and email templates match the house standard
- proposal is in **draft** status

Close with a short summary for Rehman: proposal number and slug, client, services and fees (ex and inc GST), the pricing check result in one line (reference fee, ratio, whether he took the proposed or recommended figure), billing schedule, anything removed, and any settings he must fix manually in Ignition (display settings usually need his click, see the reference). If the agreed fee is a new data point (a mix not already in the comparables table), say so and offer to add it to `references/pricing-reference.md`. Offer next steps (send it himself in Ignition, or draft the client email via client-engagement-email) but take neither without instruction.

## Guardrails

- **Draft only.** Never call `send_proposal_to_client`. Never mark won/lost.
- **Confirm before create.** Show the fee working, the pricing check and the entity list before the first write call in a group build. When the build runs inside `client-email-intake`, the approved run plan is the confirmation: build on the defaults (Monday fees summed + 5%, rounded to $50; Monday entity list; SMSFs, FBT and entities not on the board excluded) and list every default you applied and every open choice (a recommended fee, an entity you left out) in the summary for Rehman to change with an amend. Never end a run with the proposal unbuilt because a choice was open.
- **No invented fees.** If the Monday Fees column is blank for an existing client, ask; do not estimate and do not pull Xero without instruction. A new client's fee comes from the pricing reference build-up, shown with its comparables, never from a guess.
- **5% and $50.** Default uplift is 5%; every fee in a proposal is rounded to the nearest $50 ex GST, midpoints up. Recommended figures follow the same rounding.
- **Check, recommend, never override.** The pricing check runs on every build and amend that touches a fee. It recommends a higher or lower figure when the ratio is outside 0.85 to 1.20 and unexplained; it never replaces the proposed fee without Rehman choosing it.
- **SMSFs always excluded** from group proposals; they run on separate engagements.
- **GST always.** Every Fortis service line carries GST unless Rehman says otherwise. Fees are handled ex GST.
- **One line per group, not one line per entity.** See step 4.
- **Amend means amend.** Change only what was asked. Everything else you notice goes in the summary as a flag with an offer, not into a write call.
- **Australian English, no em dashes, "we" voice** in any client-facing text within the proposal.
- **Scope ends the same way every time.** "All other matters as required." then the additional-services sentence. No catch-up paragraph anywhere in the description.
