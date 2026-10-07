# Split-invoice notice: the client must not be able to miss it

**Mandatory on every proposal this skill builds or amends, from 7 October 2026.** A client who scans the engagement letter, the pricing page or either invoice must still see three things without reading closely: the fee arrives as **two invoices**, **which invoice this is**, and **the total fee**.

`scripts/split_invoice_notice.py` produces every piece from the one fee figure. Never type the amounts by hand.

## Contents

1. Why this exists (the client feedback)
2. Where the client sees each piece, and the field that controls it
3. How to produce and place it
4. What the client reads (rendered example)
5. Variants: monthly instalments, single invoice, more than one priced line
6. The split-invoice check (after every build and amend)
7. What this skill cannot fix (tell Rehman)

## 1. Why this exists

**Freya Croft, email 7 October 2026, "More client feedback on split invoices"** (to Rehman, Lin and Nicole, cc Bernadette and John). Tracey Twomey (Everett group, PROP-1897) rang, confused by the deposit and balance invoices. She is a long-term client, used to paying one invoice, and scans documents from Fortis rather than reading them. Freya says she is "one of many clients calling with the same confusion". Freya's three asks:

1. A clear statement above the breakdown in the engagement letter, in her words: **"Please note: Your fee is split into two invoices. The first invoice is for the 50% deposit, and the second invoice is for the remaining 50% balance, payable when your work is completed."** This is now house wording. Use it verbatim.
2. The **total fee** on the pricing page.
3. A clearer **invoice**.

**Freya on Teams, 28 to 29 September 2026:** "quite a number of complaints re ignition from your clients". These included clients confused by different platforms for different invoices, and direct debits that failed although the money was in the account.

**What the client actually saw before this change:**

- **Pricing page** (FHS Building Group SGC proposal, screenshot in Freya's email): "Billed on acceptance $990.00, **(Deposit)** Super Guarantee Charge (SGC) Assistance - Deposit (50% on acceptance)" then "Billed on completion $990.00, **(Balance)** Super Guarantee Charge (SGC) Assistance - **Deposit (50% on acceptance)**". There was no total. The balance line contradicted itself because the old service-name pattern ("... - Deposit (50% on acceptance)") put billing words into the service name, which appears on both lines. **That pattern is retired.**
- **Balance invoice** (Xero 2026-3010, Ignition INV-0805, from PROP-1897): "**(Balance)** Annual Group Accounting & Tax Compliance", $1,425.00 + GST. Nothing on it said it was the second of two invoices, or what the total fee was.

## 2. Where the client sees each piece, and the field that controls it

| Client sees | Ignition field | Formatting that survives | What goes there |
|---|---|---|---|
| Intro page, straight after "Hi [name]," (the first thing they read) | `personalised_message` | Full toolbar: font colour, highlight, headings, tables | Orange heading, highlighted house sentence, 3-row table (total, invoice 1, invoice 2), "not an additional charge", plus the "this has changed" sentence for existing clients |
| **Pricing page line labels** | `(` billing schedule `name` `)` + proposed service `name` | Plain text | "(Invoice 1 of 2: 50% deposit) Annual Group Compliance FY2026 (total fee $3,135.00 inc GST)" |
| **Pricing page total** | `proposal_value_display: show` and `service_price_display: show` | Setting | The total fee is shown on the page |
| Scope / services page | Proposed service `description`, **first block** | Headings, bold, blockquote, lists only. No tables, colour or highlight | Heading and blockquote with the total and both halves |
| Engagement letter, service terms | Proposed service `terms` | Full toolbar | Heading, highlight and table, then "Basis of fee and payment" |
| Screen shown after signing | `next_steps_message` | Full toolbar | Reminder with both amounts |
| **Invoice line in Xero** | `(` billing schedule `name` `)` + `billing_name` | Plain text | "(Invoice 2 of 2: 50% balance) Annual Group Compliance FY2026 (total fee $3,135.00 inc GST)" |
| **Invoice line description in Xero** | Proposed service `description`, as plain text | Text only | The notice is the first thing in it |

**Evidence for the invoice rows.** PROP-1897 has billing schedules named "Deposit" and "Balance". Its balance invoice INV-0805 carries `billing_name: "Balance"` on the item. In Xero (2026-3010) that line reads "(Balance) Annual Group Accounting & Tax Compliance", and the line description is PROP-1897's service description word for word. So the bracketed prefix is the **schedule name**, and the description travels to the invoice.

**Evidence for the formatting.** On 7 October 2026 the full build below went through `validate_proposal_document`. It returned valid with no warnings, and the `<mark class="marker-yellow">`, `<figure class="table">` and `<span style="color:...">` markup came back intact. Validation saves nothing. Ignition's editor is CKEditor 5 (note the `data-list-item-id` attributes on stored lists), and that is CKEditor 5's own markup for highlight, tables and font colour.

## 3. How to produce and place it

1. Settle the fee first (SKILL.md steps 2, 2a and 3), rounded to the nearest $50 ex GST.
2. Run:
   ```
   python3 scripts/split_invoice_notice.py --fee-ex 2850 --service "Annual Group Compliance" --fy 2026 --existing-client
   ```
   - `--existing-client` adds "If you are used to receiving one invoice from us for this work, please note that this has changed." Use it for every client who is not new to Fortis.
   - `--service` is the plain service stem: "Annual Group Compliance", "Individual Tax Return", "SMSF Annual Compliance", "Super Guarantee Charge (SGC) Assistance". **Never** put billing words (deposit, balance, 50%, on acceptance) in it.
   - Omit `--fy` for work that is not tied to an income year.
3. Paste the output fields into `create_proposal` exactly as given:

| Script field | Goes into |
|---|---|
| `billing_schedule_names[0]`, `[1]` | `billing_schedules[].name`, positions 1 and 2 |
| `portion_cents[0]`, `[1]` | The two portions' `price_rule.amount_cents` |
| `service_name` | Proposed service `name` |
| `billing_name` | Proposed service `billing_name` (set it explicitly, never leave it blank) |
| `personalised_message_notice_html` | `personalised_message`, **immediately after** the `<p>Hi&nbsp;...</p>` greeting and before every other paragraph |
| `description_notice_html` | The **start** of the proposed service `description`, before "Period covered by this engagement" (or the short lead-in). The closing "All other matters as required." and the additional-services sentence stay last. |
| `terms_html` | Proposed service `terms`, the whole field. It already carries the "Basis of fee and payment" wording. |
| `next_steps_message_html` | `next_steps_message` |
| `display_settings` | The three top-level display settings in `create_proposal` |

4. If the fee changes at any point (Rehman picks the recommended figure, or an amend changes it), **re-run the script** and rewrite every field above. A notice with a stale amount is worse than none.

## 4. What the client reads (rendered example)

Fee $2,850 ex GST, existing client:

> **PLEASE NOTE: YOUR FEE IS SPLIT INTO TWO INVOICES** *(Fortis orange heading)*
>
> **Please note: Your fee is split into two invoices. The first invoice is for the 50% deposit, and the second invoice is for the remaining 50% balance, payable when your work is completed.** *(highlighted yellow)*
>
> | | |
> |---|---|
> | **Total fee for this engagement** | **$2,850.00 + GST ($3,135.00 inc GST)** |
> | Invoice 1 of 2: 50% deposit, issued on acceptance | $1,425.00 + GST ($1,567.50 inc GST) |
> | Invoice 2 of 2: 50% balance, issued when your work is completed | $1,425.00 + GST ($1,567.50 inc GST) |
>
> **The two invoices together make up the total fee above. The second invoice is not an additional charge.** If you are used to receiving one invoice from us for this work, please note that this has changed.

Pricing page:

> Billed on acceptance: $1,567.50 inc $142.50 GST
> (Invoice 1 of 2: 50% deposit) Annual Group Compliance FY2026 (total fee $3,135.00 inc GST)
>
> Billed on completion: $1,567.50 inc $142.50 GST
> (Invoice 2 of 2: 50% balance) Annual Group Compliance FY2026 (total fee $3,135.00 inc GST)
>
> Total shown (proposal value display on)

Balance invoice line in Xero:

> (Invoice 2 of 2: 50% balance) Annual Group Compliance FY2026 (total fee $3,135.00 inc GST)
> Please note: your fee is split into two invoices. Total fee for this engagement: $2,850.00 + GST ($3,135.00 inc GST). ...

## 5. Variants

- **Monthly instalments** (a mirror of PROP-1591 Penn Property, or Rehman asks for monthly): `--billing monthly --instalments 12`. The script refuses a fee that does not split into equal instalments to the cent; agree the instalment with Rehman. One schedule, named "12 monthly instalments".
- **Single invoice** (Rehman directs 100% on acceptance): there is no split to explain. Still use the `service_name` with the total, set both price displays to `show`, and leave the notice out of the message, description and terms.
- **More than one priced line** (rare; only where lines sit in separate projects): run the script once on the proposal total for the message and next steps, and once per line for that line's `service_name`, `description_notice_html` and `terms_html`.

## 6. The split-invoice check (after every build and amend)

Re-read with `get_proposal_document` and confirm every item. Report each failure in the summary.

1. `personalised_message` has the notice immediately after the greeting, including the house sentence verbatim and the total inc GST.
2. The billing schedules are named "Invoice 1 of 2: 50% deposit" and "Invoice 2 of 2: 50% balance".
3. Every line's `name` and `billing_name` equals the script's `service_name`. No line name anywhere contains "Deposit (50% on acceptance)" or any other billing words.
4. `description` opens with the notice block, and still closes with "All other matters as required." then the additional-services sentence.
5. `terms` opens with the notice heading and table.
6. `next_steps_message` carries the reminder with both amounts.
7. `proposal_value_display` and `service_price_display` are `show`. **If either is not, the first line of the summary is a MUST DO for Rehman** (see quirk 5 in `ignition-mechanics.md`).
8. Every dollar figure in the notice agrees with `pricing_summary`: the total ex GST equals `minimum_contract_value_cents`, and the two halves equal the two portions.
9. The highlight markup (`<mark class="marker-yellow">`) survived. If Ignition stripped it, the orange heading and bold text still carry the notice; tell Rehman so he can apply the highlight in the editor.
10. Ask Rehman to open the client preview once before sending and look at the pricing page.

## 7. What this skill cannot fix (tell Rehman, once, in the summary)

- **The proposal email template** (`practempl_mkz7tnu77fwaa7ifxbqa`) is template admin and firm-wide, so it is outside this skill. Suggest Rehman add one line to it: "Please note: your fee is split into two invoices, a 50% deposit on acceptance and the 50% balance when your work is completed."
- **Proposals already sent or accepted** cannot be changed. Freya and the admin team can read the house sentence to clients who call.
- **Billing schedule names on an existing draft** cannot be renamed through the API (quirk 15). An older draft keeps "(Deposit)" and "(Balance)" unless it is rebuilt. The new `service_name` with the total still makes those lines clear.
- **Direct debit failures and timing** (Teams, 28 September) are Ignition payment processing, not proposal wording.
- **Invoices raised outside Ignition** (Xero invoices for ASIC fees and other one-off work) do not come from this skill. The `invoice-description-generator` skill covers that wording.
