# Split-invoice notice: say it once, clearly

**Mandatory on every proposal this skill builds or amends, from 7 October 2026.** A client who scans the engagement letter, the pricing page or either invoice must still see three things: the fee arrives as **two invoices**, **which invoice this is**, and **the total fee**. Say it **once** in words, in one highlighted line in the intro. The pricing labels, the total on the pricing page and the invoice lines do the rest. Greet the client by **first name**.

`scripts/split_invoice_notice.py` produces every piece from the one fee figure. Never type the amounts by hand.

## Contents

1. Why this exists (the client feedback and Rehman's review)
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

**Rehman's review of the first build (PROP-2097, 7 October 2026).** The first version put an orange heading, the highlighted sentence, a three-row fee table and an extra paragraph in the intro. It repeated the notice at the top of the services section and in the service terms. Rehman's verdict: "way too much". He also said the notice does not need saying again in the services section. He also asked for **first names only** in the greeting. The placeholder `{{ contact.addressee | default:contact.name }}` printed the XPM-style "KHATIWADA, Bijit". This file and the script now reflect that review.

## 2. Where the client sees each piece, and the field that controls it

| Client sees | Ignition field | What goes there |
|---|---|---|
| **Intro page** | `personalised_message` | "Hi [first names]," then one thank-you line naming what the engagement covers, then **one highlighted, bold line**: Freya's sentence plus "Your total fee is $X + GST ($Y inc GST).", then the usual close. Nothing else. |
| **Pricing page line labels** | `(` billing schedule `name` `)` + proposed service `name` | "(Invoice 1 of 2: 50% deposit) Individual Tax Returns FY2026 (total fee $440.00 inc GST)" |
| **Pricing page total** | `proposal_value_display: show` and `service_price_display: show` | The total fee is shown on the page |
| Services section (scope) | Proposed service `description` | **No notice.** The scope only, closing with the house sentences |
| Engagement letter, service terms | Proposed service `terms` | The plain "Basis of fee and payment" wording (50% deposit on acceptance, 50% on completion) |
| Screen shown after signing | `next_steps_message` | One highlighted reminder line with both amounts |
| **Invoice line in Xero** | `(` billing schedule `name` `)` + `billing_name` | "(Invoice 2 of 2: 50% balance) Individual Tax Returns FY2026 (total fee $440.00 inc GST)" |

**Evidence for the invoice rows.** PROP-1897 has billing schedules named "Deposit" and "Balance". Its balance invoice INV-0805 carries `billing_name: "Balance"` on the item. In Xero (2026-3010) that line reads "(Balance) Annual Group Accounting & Tax Compliance", and the line description is PROP-1897's service description word for word. So the bracketed prefix is the **schedule name**, and the description travels to the invoice. The schedule name and service name together now tell the client which invoice it is and what the total is.

**Evidence for the formatting.** On 7 October 2026 a full build went through `validate_proposal_document` (which saves nothing), and the highlight markup `<mark class="marker-yellow">` came back intact. The same day the first live build, **PROP-2097** (Khatiwada, $400 + GST), was created. Rehman's preview showed the yellow highlight and bold rendering on the intro page. A fresh `get_proposal_document` read confirmed that both display settings took at creation and that the schedule names stuck. Ignition's editor is CKEditor 5 (note the `data-list-item-id` attributes on stored lists), and `<mark class="marker-yellow">` is its native highlight.

## 3. How to produce and place it

1. Settle the fee first (SKILL.md steps 2, 2a and 3), rounded to the nearest $50 ex GST.
2. Run:
   ```
   python3 scripts/split_invoice_notice.py --fee-ex 400 --service "Individual Tax Returns" --fy 2026 \
       --first-names Bijit Rashmi \
       --covering "your individual income tax returns for the year ended 30 June 2026"
   ```
   - `--first-names`: first names only, in normal case. FYI and Monday hold "KHATIWADA, Bijit", so pass `Bijit`. The script refuses a comma or an all-capitals surname. For a company group, pass the first names of the directors or individuals being addressed.
   - `--covering`: what the engagement covers, finishing the sentence "We've prepared your engagement covering ...". For example "the annual compliance for your group for the year ended 30 June 2026", or "your individual income tax returns for the year ended 30 June 2026".
   - `--new-client`: use for clients new to Fortis. It switches to "Thank you for choosing Fortis Accounting Partners..." and "We look forward to working with you...".
   - `--service`: the plain service stem, such as "Annual Group Compliance", "Individual Tax Returns", "SMSF Annual Compliance" or "Super Guarantee Charge (SGC) Assistance". **Never** put billing words (deposit, balance, 50%, on acceptance) in it.
   - Omit `--fy` for work that is not tied to an income year.
3. Paste the output fields into `create_proposal` exactly as given:

| Script field | Goes into |
|---|---|
| `billing_schedule_names[0]`, `[1]` | `billing_schedules[].name`, positions 1 and 2 |
| `portion_cents[0]`, `[1]` | The two portions' `price_rule.amount_cents` |
| `service_name` | Proposed service `name` |
| `billing_name` | Proposed service `billing_name` (set it explicitly, never leave it blank) |
| `personalised_message_html` | `personalised_message`, the whole field |
| `terms_html` | Proposed service `terms`, the whole field |
| `next_steps_message_html` | `next_steps_message` |
| `display_settings` | The three top-level display settings in `create_proposal` |

   The scope `description` gets **nothing** from the script. It is the scope only, as in the asset examples.
4. If the fee changes at any point (Rehman picks the recommended figure, or an amend changes it), **re-run the script** and rewrite the message, next steps message, service name and billing name. A stale amount is worse than none.

## 4. What the client reads (rendered example)

PROP-2097, fee $400 ex GST, existing clients:

> Hi Bijit and Rashmi,
>
> Thank you for continuing to work with us. We've prepared your engagement covering your individual income tax returns for the year ended 30 June 2026.
>
> **Please note: Your fee is split into two invoices. The first invoice is for the 50% deposit, and the second invoice is for the remaining 50% balance, payable when your work is completed. Your total fee is $400.00 + GST ($440.00 inc GST).** *(bold, highlighted yellow)*
>
> Please find the scope of works and fees set out below for your review and approval. We look forward to continuing our work with you for years to come.

Pricing page:

> Billed on acceptance: $220.00 inc $20.00 GST
> (Invoice 1 of 2: 50% deposit) Individual Tax Returns FY2026 (total fee $440.00 inc GST)
>
> Billed on completion: $220.00 inc $20.00 GST
> (Invoice 2 of 2: 50% balance) Individual Tax Returns FY2026 (total fee $440.00 inc GST)
>
> Total shown (proposal value display on)

Balance invoice line in Xero:

> (Invoice 2 of 2: 50% balance) Individual Tax Returns FY2026 (total fee $440.00 inc GST)

## 5. Variants

- **Monthly instalments** (a mirror of PROP-1591 Penn Property, or Rehman asks for monthly): `--billing monthly --instalments 12`. The highlighted line reads "Please note: Your fee is split into 12 monthly invoices of $X inc GST each. Your total fee is ...". The script refuses a fee that does not split into equal instalments to the cent; agree the instalment with Rehman. One schedule, named "12 monthly instalments".
- **Single invoice** (Rehman directs 100% on acceptance): there is no split to explain. Still greet by first name, use the `service_name` with the total, and set both price displays to `show`. Leave the highlighted line out of the message.
- **More than one priced line** (rare; only where lines sit in separate projects): run the script once on the proposal total for the message and next steps, and once per line for that line's `service_name`.

## 6. The split-invoice check (after every build and amend)

Re-read with `get_proposal_document` and confirm every item. Report each failure in the summary.

1. `personalised_message` opens with a first-name greeting ("Hi Bijit and Rashmi,"), not the `{{ contact... }}` placeholder.
2. It carries exactly one highlighted line: Freya's sentence verbatim plus the total ex and inc GST. There is no heading, no table, and no second statement of the split.
3. The billing schedules are named "Invoice 1 of 2: 50% deposit" and "Invoice 2 of 2: 50% balance".
4. Every line's `name` and `billing_name` equals the script's `service_name`. No line name anywhere contains "Deposit (50% on acceptance)" or any other billing words.
5. `description` carries **no** split-invoice notice, and still closes with "All other matters as required." then the additional-services sentence.
6. `terms` is the plain "Basis of fee and payment" wording.
7. `next_steps_message` carries the one-line reminder with both amounts.
8. `proposal_value_display` and `service_price_display` are `show`. **If either is not, the first line of the summary is a MUST DO for Rehman** (quirk 5 in `ignition-mechanics.md`).
9. Every dollar figure agrees with `pricing_summary`: the total ex GST equals `minimum_contract_value_cents`, and the two halves equal the two portions.
10. Ask Rehman to open the client preview once before sending and look at the intro and pricing page.

## 7. What this skill cannot fix (tell Rehman, once, in the summary)

- **The proposal email template** (`practempl_mkz7tnu77fwaa7ifxbqa`) is template admin and firm-wide, so it is outside this skill. Suggest Rehman add one line to it: "Please note: your fee is split into two invoices, a 50% deposit on acceptance and the 50% balance when your work is completed."
- **Proposals already sent or accepted** cannot be changed. Freya and the admin team can read the house sentence to clients who call.
- **Billing schedule names on an existing draft** cannot be renamed through the API (quirk 15). An older draft keeps "(Deposit)" and "(Balance)" unless it is rebuilt. The new `service_name` with the total still makes those lines clear.
- **Direct debit failures and timing** (Teams, 28 September) are Ignition payment processing, not proposal wording.
- **Invoices raised outside Ignition** (Xero invoices for ASIC fees and other one-off work) do not come from this skill. The `invoice-description-generator` skill covers that wording.
