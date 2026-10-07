# Ignition, Monday and Xero mechanics for proposal builds

Hard-won knowledge from live builds (PROP-1591 Penn Property, PROP-1592 JD Refrigeration, PROP-1642 Peter Bijjani, PROP-1570 Kinny Legal revision, PROP-1679 Portquip Group). Follow these exactly; each one was learned from a corrective loop.

## Confirmed house slugs

Verify these still resolve before relying on them; re-read from a recent accepted proposal if a call errors.

| Thing | Slug |
|---|---|
| GST tax | `iatax_micj562adeoaaayaxzaq` |
| Sender user (Rehman) | `user_navlhqeygx7qapqauagq` |
| Engagement letter terms template | `practempl_nbxxmoefb5jaawiahlba` |
| Proposal email template | `practempl_mkz7tnu77fwaa7ifxbqa` |
| Individual Tax Return JK (with quote) template | `pectmp_nb3uhrjml62aakaatm2a` |
| Annual Group Compliance service (library) | `svc_navnvsskmlbqaaiawxgq` |
| Annual Company Financial Report and Tax Return (library) | `svc_na6vp2xd2buaakiafw4q` |
| Individual Tax Return (library) | `svc_nbwlzcgfp3uaaqaaqseq` |
| RAJBANSHI / 2R Design proposal (amend mode + one-line reference) | `prop_njrkshzqmj3aanya47sq` (PROP-1786) |
| Penn Property group compliance proposal (mirror source, monthly instalments) | `prop_nja3kfz7j2xaanyal2aa` (PROP-1591) |
| Portquip Group FY26 proposal (mirror source, 50/50 deposit/balance, DEFAULT) | `prop_njfucjsxhdpqa3aatoua` (PROP-1679) |

## Monday.com Annual Compliance board (fee and group source)

Board: **Annual Compliance 2026-2027**, id `18419272927`, workspace Main (9669172).

| Column | Id | Type |
|---|---|---|
| Group (client group name) | `text_mkshm0f` | text |
| Fees (last FY fee, ex GST) | `numeric_mkshfxes` | numbers |
| Entity Type | `text_mkshd8f3` | text |
| Status | `project_status` | status |
| Manager | `project_owner` | people |
| Accountant | `multiple_person_mksga302` | people |
| Hrs | `numeric_mky1t5vs` | numbers |

Lookup mechanics:

1. `get_board_items_page` with a filter on `text_mkshm0f`, operator `contains_text`, `includeColumns: true`, `columnIds` limited to the table above. One call returns the full entity set and fees together.
2. If the group filter misses (naming drift), retry with `searchTerm` on the entity's legal name before falling back to FYI.
3. **Fees convention**: the group fee sits once on the head entity item, ex GST, last FY. Other entity items are usually blank; that is normal, not missing data. SMSF items carry their own separate fee; ignore it for group proposals.
4. Entity Type values seen: "Australian Private Company", "Discretionary Trust Invest.", "Individual/Sole trader", "Self Managed Super Fund". Use them to drive the per-entity scope bullets and to exclude SMSFs.
5. Board groups run the workflow left to right: IT List, Proposal, To Complete, WIP, In Query, Review, Out, Completed. Fee items are readable regardless of group.

## The 50/50 deposit/balance recipe (default billing, from PROP-1679)

Mirror `assets/prop-1679-example.json` structurally. The load-bearing parts:

1. Service group `billing_mode: "deposit"` with exactly two billing schedules:
   - Position 1 "Deposit": `bill_type: once_off`, `start_type: acceptance`, `start_delay: P0M`.
   - Position 2 "Balance": `bill_type: once_off`, `start_type: date`, `start_date` = 30 June at the end of the engagement term (e.g. `2027-06-30` for an FY26 engagement starting 2026-07-01), `start_delay: P0M`.
2. One proposed service carrying the full fee as a fixed price rule, split into two portions of 50% each:
   - Deposit portion (schedule position 1): `invoice_strategy: automatic`.
   - Balance portion (schedule position 2): `invoice_strategy: manual`. The manual strategy is what makes the balance invoice fire on completion of the work rather than on the schedule date; the date is only the anchor.
3. Fee maths: Monday Fees figure + 5%, rounded to the nearest $50 (midpoints up) = proposal fee ex GST. GST resolves via the tax slug. Then run the pricing check in `references/pricing-reference.md` before confirming. PROP-1679 for reference: 20,500.00 ex, 2,050.00 GST, 22,550.00 inc (built under the old 6% default; Rehman lifted the board 20,000 to 20,500 at confirm). Changed from 6% to 5% with $50 rounding on 2026-09-10.
4. Proposal settings that carried on PROP-1679: `start_on: date` with `start_date` 1 July of the engagement year, `minimum_contract_length: 12`, `payment_method_required: true`, credit card and direct debit accepted, displays all `hide` (these need Rehman's manual click anyway, see quirk 5).
5. Service name pattern: "Annual Group Compliance - Deposit (50% on acceptance)". The personalised message and service-line terms wording are in the asset file; reuse them verbatim, updating only the FY references.
6. Scope description closes with "All other matters as required." followed by `<p>Additional services that are not covered in this proposal will be charged at our hourly rates as listed in the Terms &amp; Conditions on a periodic basis as required.</p>`. The former "Substantially overdue or multi-year catch-up lodgements..." paragraph is retired (2026-09-10); do not write it, and strip it from any older draft you amend.

## Ignition API quirks

1. **Retrieve before you build.** `get_proposal_document` on the source/template proposal returns the full document tree: options, projects, service groups, proposed services, billing rules, all slugs. Capture everything before creating; guessing slugs fails.
2. **Recurring billing rule format** for 12 monthly instalments: `FREQ=MONTHLY;COUNT=12` with `start_type: date` and `start_delay: P0M`.
3. **`tax_exempt: true` false alarm.** `create_proposal` sometimes returns `tax_exempt: true` on a line even when a tax slug was passed. Do not panic and do not rebuild. Immediately call `update_proposed_service` on that line passing the same `tax_slug`; this re-resolves the flag. Then confirm the pricing summary shows GST.
4. **Raw HTML in descriptions.** `update_proposed_service` descriptions take actual HTML characters (`<p>...</p>`). Pre-escaped entities (`&lt;p&gt;`) render literally as double-escaped text and need a corrective call. Send raw HTML the first time.
5. **Display settings need Rehman's click.** `update_proposal` for top-level settings (`service_price_display`, `proposal_value_display`) requires manual approval inside Ignition and will not complete from here. Always list these in the closing summary as "check in Ignition before sending".
6. **`update_proposed_service` cannot change `service_slug`.** It patches text, price, quantity, tax, terms and add-on status only. To move a line onto a different library service you add a new line and remove the old one. Same for changing which service group a line sits in.
7. **`add_proposed_service` copies the library defaults verbatim, and they are stale.** Annual Group Compliance comes in as "Annual Group Compliance (Monthly)", zero dollars, `tax_exempt: true`, description full of "XXX Pty Ltd" placeholders. Patch it in one `update_proposed_service` call straight after adding, before anything else touches the draft.
8. **`add_proposal_service_group` cannot create a deposit group.** `billing_mode` accepts only `once_off` and `recurring`. Deposit billing with two schedules exists only through `create_proposal`, so a draft built with the wrong billing mode has to be rebuilt, not patched.
9. **Removals renumber positions.** After each `remove_proposed_service` the surviving lines shift up. Work off slugs, never positions, and re-read at the end rather than assuming.

10. **Client search is weak.** Ignition's `list_clients` misses company entities whose registered name doesn't contain the search term. Resolve the group via the Monday board first, then FYI (`fyi_list_clients`) if not on the board, then match to the Ignition record.
11. **Structured filters fail from chat (24 Sep 2026).** `list_clients` and `list_proposals` reject every `filter` value with "value at /filter is not an object", whether a single condition or wrapped in `and`/`or`. Unfiltered listing works but the practice has 4,084 clients (mostly XPM-imported leads), so do not page for a name. Fallback: `create_proposal` without `client_slug` (state `new`, deleted after 7 days without a client); Rehman assigns the client in the editor. `get_proposal` by slug still finds it; `list_proposals` does not until a client is attached.

## Xero (Fortis tenant) fee lookups (only on explicit instruction; Monday Fees is the default source)

1. **Tenant id** `93f284aa-7182-4e0c-a164-10bf6dc9472a` must be passed explicitly to `list_contacts` and `list_invoices`. If in doubt, run `current_client` / `select_client` first.
2. **Filtering invoices by contact** uses the `where` parameter with exactly this syntax: `Contact.ContactID==Guid("contact-id-here")`. A bare UUID without the `Guid()` wrapper returns nothing.
3. **Read the invoice lines, not just totals.** Last-year fees are often one combined line covering multiple family members or entities billed under one contact. Identify exactly what the line covered before uplifting, and flag bundles to Rehman (split vs keep combined) before building.

## Known client slugs (for repeat clients)

- Peter Bijjani: Ignition `cli_naxk5rv32csqaaiagogq`, Xero contact `a0f60627-bbd9-4f54-a038-a2ff262d5f45`
- JD Refrigeration Pty Ltd: Ignition `cli_naxk5vieeriaaaialfaa`, FYI group 33821126 (partner JK, manager Rehman)
- Portquip Pty. Ltd.: Ignition `cli_naxk5yne733qaaiawwna`, Monday Group "Portquip Pty Ltd" on board 18419272927 (head entity item 12434121809)
- 2R Design Studio Pty Ltd: Ignition `cli_njqgldhsgf3aa3aamkrq`, Monday Group "RAJBANSHI, Rohit" on board 18419272927 (head entity item 12437491855). Group is the company plus Rohit and Babita Rajbanshi.

- Trojan Medtech group (Troy and Amelia Rose, Bianco & Co Trust): Ignition client slug not yet known. PROP-2055 (`prop_nk2hkgstmmdqaviantca`) built unassigned on 24 Sep 2026, Monday Group "Trojan Medtech Pty Ltd" (head entity item 12437467634, fee 4,600; Troy item 12433826018, fee 1,200).

Add to this table as builds happen; a slug looked up once should not be looked up twice.
