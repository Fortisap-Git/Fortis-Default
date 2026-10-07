#!/usr/bin/env python3
"""Build the client-facing split-invoice notice for an Ignition proposal.

Every Fortis proposal tells the client, in several places they cannot scan
past, that the fee arrives as more than one invoice and what the total is.
This script produces all of those pieces from one fee figure so the amounts
can never disagree with each other or with the price on the service line.

Background: client feedback relayed by Freya Croft (email 7 October 2026,
Teams 28 September 2026). Long-standing clients used to one invoice were
confused by the deposit and balance invoices, the pricing page showed no
total, and the balance invoice said only "(Balance)".

Usage:
    python3 split_invoice_notice.py --fee-ex 2850 --service "Annual Group Compliance" --fy 2026 --existing-client
    python3 split_invoice_notice.py --fee-ex 8000 --service "Annual Group Compliance" --fy 2026 --billing monthly --instalments 12

Prints one JSON object. Paste each field into the matching create_proposal or
update_proposal / update_proposed_service field exactly as given.
"""

import argparse
import json
import sys

ACCENT = "rgb(232,78,44)"  # Fortis orange-red, the colour of the Ignition headings
FREYA_SENTENCE = (
    "Please note: Your fee is split into two invoices. The first invoice is for "
    "the 50% deposit, and the second invoice is for the remaining 50% balance, "
    "payable when your work is completed."
)
EXISTING_CLIENT_SENTENCE = (
    "If you are used to receiving one invoice from us for this work, please note "
    "that this has changed."
)
SERVICE_NAME_LIMIT = 100  # Ignition proposed service name limit


def money(cents):
    return "${:,.2f}".format(cents / 100)


def gst(cents):
    return (cents + 5) // 10  # 10%, half up, in cents


def heading(text):
    return f'<h3><span style="color:{ACCENT};"><strong>{text}</strong></span></h3>'


def marked(text):
    return f'<p><mark class="marker-yellow"><strong>{text}</strong></mark></p>'


def table(rows):
    body = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return f'<figure class="table"><table><tbody>{body}</tbody></table></figure>'


def ex_inc(cents):
    return f"{money(cents)} + GST ({money(cents + gst(cents))} inc GST)"


def deposit(fee_cents, service_name, existing):
    half = fee_cents // 2
    total_row = ("<strong>Total fee for this engagement</strong>", f"<strong>{ex_inc(fee_cents)}</strong>")
    rows = [
        total_row,
        ("Invoice 1 of 2: 50% deposit, issued on acceptance", ex_inc(half)),
        ("Invoice 2 of 2: 50% balance, issued when your work is completed", ex_inc(fee_cents - half)),
    ]
    not_extra = "The two invoices together make up the total fee above. The second invoice is not an additional charge."
    tail = f"<p><strong>{not_extra}</strong>{' ' + EXISTING_CLIENT_SENTENCE if existing else ''}</p>"

    message = heading("PLEASE NOTE: YOUR FEE IS SPLIT INTO TWO INVOICES") + marked(FREYA_SENTENCE) + table(rows) + tail

    description = (
        "<h3>Please note: your fee is split into two invoices</h3>"
        "<blockquote>"
        f"<p><strong>Total fee for this engagement: {ex_inc(fee_cents)}.</strong></p>"
        "<p><strong>Your fee is split into two invoices. The first invoice is for the 50% deposit "
        f"({money(half)} + GST), and the second invoice is for the remaining 50% balance "
        f"({money(fee_cents - half)} + GST), payable when your work is completed. "
        "The two invoices together make up the total fee; the second invoice is not an additional charge.</strong></p>"
        "</blockquote>"
    )

    terms = (
        heading("PLEASE NOTE: YOUR FEE IS SPLIT INTO TWO INVOICES")
        + marked(FREYA_SENTENCE)
        + table(rows)
        + "<p><strong>Basis of fee and payment</strong></p>"
        "<p>The fee for this engagement is a fixed fee for the work set out above. A deposit of 50% is payable "
        "on acceptance of this proposal, with the remaining 50% invoiced on completion of the work.</p>"
        "<p>The deposit secures your place in our workflow and covers the initial work on your file. If the "
        "engagement is ended after work has commenced, the deposit is not refundable to the extent the related "
        "work has been performed, and any further work completed up to the date of termination will be invoiced.</p>"
    )

    total_inc = money(fee_cents + gst(fee_cents))
    next_steps = (
        "<p><strong>Your proposal was successfully accepted. Thank you.</strong></p>"
        + heading("A reminder about your two invoices")
        + marked(f"Your total fee of {total_inc} inc GST is split into two invoices.")
        + "<ul>"
        f"<li><strong>Invoice 1 of 2:</strong> the 50% deposit of {money(half + gst(half))} inc GST, raised now on acceptance.</li>"
        f"<li><strong>Invoice 2 of 2:</strong> the remaining 50% balance of {money(fee_cents - half + gst(fee_cents - half))} inc GST, raised when your work is completed.</li>"
        "</ul>"
        "<p>The second invoice is not an additional charge.</p>"
        "<p>{{ practice.payment_verification_message }}</p>"
    )

    return {
        "billing_schedule_names": ["Invoice 1 of 2: 50% deposit", "Invoice 2 of 2: 50% balance"],
        "portion_cents": [half, fee_cents - half],
        "personalised_message_notice_html": message,
        "description_notice_html": description,
        "terms_html": terms,
        "next_steps_message_html": next_steps,
        "must_appear": [
            FREYA_SENTENCE,
            "Invoice 1 of 2",
            "Invoice 2 of 2",
            total_inc,
            money(half),
        ],
    }


def monthly(fee_cents, instalments, existing):
    if fee_cents % instalments:
        sys.exit(f"Fee {money(fee_cents)} does not divide into {instalments} equal instalments to the cent. "
                 "Agree the instalment amount with Rehman first.")
    each = fee_cents // instalments
    sentence = (
        f"Please note: Your fee is split into {instalments} monthly invoices of "
        f"{money(each + gst(each))} inc GST each."
    )
    rows = [
        ("<strong>Total fee for this engagement</strong>", f"<strong>{ex_inc(fee_cents)}</strong>"),
        (f"{instalments} monthly invoices, each", ex_inc(each)),
    ]
    not_extra = f"The {instalments} invoices together make up the total fee above. None of them is an additional charge."
    tail = f"<p><strong>{not_extra}</strong>{' ' + EXISTING_CLIENT_SENTENCE if existing else ''}</p>"
    title = f"PLEASE NOTE: YOUR FEE IS SPLIT INTO {instalments} MONTHLY INVOICES"
    message = heading(title) + marked(sentence) + table(rows) + tail
    description = (
        f"<h3>Please note: your fee is split into {instalments} monthly invoices</h3>"
        "<blockquote>"
        f"<p><strong>Total fee for this engagement: {ex_inc(fee_cents)}.</strong></p>"
        f"<p><strong>{sentence} {not_extra}</strong></p>"
        "</blockquote>"
    )
    terms = heading(title) + marked(sentence) + table(rows)
    total_inc = money(fee_cents + gst(fee_cents))
    next_steps = (
        "<p><strong>Your proposal was successfully accepted. Thank you.</strong></p>"
        + heading(f"A reminder about your {instalments} monthly invoices")
        + marked(f"Your total fee of {total_inc} inc GST is split into {instalments} monthly invoices "
                 f"of {money(each + gst(each))} inc GST each.")
        + "<p>None of them is an additional charge.</p>"
        "<p>{{ practice.payment_verification_message }}</p>"
    )
    return {
        "billing_schedule_names": [f"{instalments} monthly instalments"],
        "portion_cents": [each],
        "personalised_message_notice_html": message,
        "description_notice_html": description,
        "terms_html": terms,
        "next_steps_message_html": next_steps,
        "must_appear": [sentence, total_inc],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fee-ex", type=float, required=True, help="Total fee ex GST in dollars, already rounded to $50")
    p.add_argument("--service", required=True, help='Service name stem, e.g. "Annual Group Compliance"')
    p.add_argument("--fy", type=int, help="Income year the engagement covers, e.g. 2026. Omit for non-annual work")
    p.add_argument("--existing-client", action="store_true", help="Add the 'this has changed' sentence")
    p.add_argument("--billing", choices=["deposit", "monthly"], default="deposit")
    p.add_argument("--instalments", type=int, default=12, help="Monthly billing only")
    a = p.parse_args()

    fee_cents = round(a.fee_ex * 100)
    if fee_cents % 5000:
        sys.exit(f"Fee {money(fee_cents)} is not rounded to the nearest $50. Round it first (SKILL.md step 2).")

    total_inc = money(fee_cents + gst(fee_cents))
    stem = f"{a.service} FY{a.fy}" if a.fy else a.service
    service_name = f"{stem} (total fee {total_inc} inc GST)"
    if len(service_name) > SERVICE_NAME_LIMIT:
        sys.exit(f"Service name is {len(service_name)} characters, over Ignition's {SERVICE_NAME_LIMIT}. Shorten --service.")

    out = deposit(fee_cents, service_name, a.existing_client) if a.billing == "deposit" \
        else monthly(fee_cents, a.instalments, a.existing_client)

    result = {
        "fee": {
            "total_ex": money(fee_cents),
            "total_gst": money(gst(fee_cents)),
            "total_inc": total_inc,
            "total_cents": fee_cents,
        },
        "service_name": service_name,
        "billing_name": service_name,
        "display_settings": {
            "proposal_value_display": "show",
            "service_price_display": "show",
            "one_time_date_display": "hide",
        },
    }
    result.update(out)
    result["must_appear"].append(service_name)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
