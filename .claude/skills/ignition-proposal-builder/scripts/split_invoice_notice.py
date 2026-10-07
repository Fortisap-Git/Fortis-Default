#!/usr/bin/env python3
"""Build the client-facing split-invoice wording for an Ignition proposal.

Every Fortis proposal tells the client that the fee arrives as more than one
invoice and what the total is. This script produces all of those pieces from
one fee figure so the amounts can never disagree with each other or with the
price on the service line.

Background: client feedback relayed by Freya Croft (email 7 October 2026,
Teams 28 September 2026). Long-standing clients used to one invoice were
confused by the deposit and balance invoices, the pricing page showed no
total, and the balance invoice said only "(Balance)". Rehman's review of the
first build (PROP-2097, 7 October 2026): keep it to one highlighted line in
the intro, do not repeat it in the services section, greet by first name.

Usage:
    python3 split_invoice_notice.py --fee-ex 400 --service "Individual Tax Returns" --fy 2026 \
        --first-names Bijit Rashmi --covering "your individual income tax returns for the year ended 30 June 2026"
    python3 split_invoice_notice.py ... --new-client
    python3 split_invoice_notice.py ... --billing monthly --instalments 12

Prints one JSON object. Paste each field into the matching create_proposal or
update_proposal / update_proposed_service field exactly as given.
"""

import argparse
import json
import sys

FREYA_SENTENCE = (
    "Please note: Your fee is split into two invoices. The first invoice is for "
    "the 50% deposit, and the second invoice is for the remaining 50% balance, "
    "payable when your work is completed."
)
SERVICE_NAME_LIMIT = 100  # Ignition proposed service name limit


def money(cents):
    return "${:,.2f}".format(cents / 100)


def gst(cents):
    return (cents + 5) // 10  # 10%, half up, in cents


def inc(cents):
    return money(cents + gst(cents))


def ex_inc(cents):
    return f"{money(cents)} + GST ({inc(cents)} inc GST)"


def marked(text):
    return f'<p><mark class="marker-yellow"><strong>{text}</strong></mark></p>'


def join_names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def message(greeting, covering, note_html, new_client):
    opener = ("Thank you for choosing Fortis Accounting Partners. We have prepared this engagement"
              if new_client else
              "Thank you for continuing to work with us. We&rsquo;ve prepared your engagement")
    closer = ("We look forward to working with you for years to come." if new_client
              else "We look forward to continuing our work with you for years to come.")
    return (
        f"<p>{greeting}</p>"
        f"<p>{opener} covering {covering}.</p>"
        f"{note_html}"
        f"<p>Please find the scope of works and fees set out below for your review and approval. {closer}</p>"
        "<p>Best regards,</p><p>{{ practice.admin }}</p>"
    )


def deposit(fee_cents):
    half = fee_cents // 2
    note = marked(f"{FREYA_SENTENCE} Your total fee is {ex_inc(fee_cents)}.")
    terms = (
        "<p><strong>Basis of fee and payment</strong></p>"
        "<p>The fee for this engagement is a fixed fee for the work set out above. A deposit of 50% is payable "
        "on acceptance of this proposal, with the remaining 50% invoiced on completion of the work.</p>"
        "<p>The deposit secures your place in our workflow and covers the initial work on your file. If the "
        "engagement is ended after work has commenced, the deposit is not refundable to the extent the related "
        "work has been performed, and any further work completed up to the date of termination will be invoiced.</p>"
    )
    next_steps = (
        "<p><strong>Your proposal was successfully accepted. Thank you.</strong></p>"
        + marked(f"Reminder: your total fee of {inc(fee_cents)} inc GST is split into two invoices, the 50% deposit "
                 f"of {inc(half)} inc GST now and the 50% balance of {inc(fee_cents - half)} inc GST when your "
                 "work is completed.")
        + "<p>{{ practice.payment_verification_message }}</p>"
    )
    return {
        "billing_schedule_names": ["Invoice 1 of 2: 50% deposit", "Invoice 2 of 2: 50% balance"],
        "portion_cents": [half, fee_cents - half],
        "note_html": note,
        "terms_html": terms,
        "next_steps_message_html": next_steps,
        "must_appear": [FREYA_SENTENCE, inc(fee_cents)],
    }


def monthly(fee_cents, instalments):
    if fee_cents % instalments:
        sys.exit(f"Fee {money(fee_cents)} does not divide into {instalments} equal instalments to the cent. "
                 "Agree the instalment amount with Rehman first.")
    each = fee_cents // instalments
    sentence = f"Please note: Your fee is split into {instalments} monthly invoices of {inc(each)} inc GST each."
    note = marked(f"{sentence} Your total fee is {ex_inc(fee_cents)}.")
    terms = (
        "<p><strong>Basis of fee and payment</strong></p>"
        f"<p>The fee for this engagement is an annual fee for the work set out above, billed in {instalments} equal "
        f"monthly instalments of {ex_inc(each)}.</p>"
    )
    next_steps = (
        "<p><strong>Your proposal was successfully accepted. Thank you.</strong></p>"
        + marked(f"Reminder: your total fee of {inc(fee_cents)} inc GST is split into {instalments} monthly "
                 f"invoices of {inc(each)} inc GST each.")
        + "<p>{{ practice.payment_verification_message }}</p>"
    )
    return {
        "billing_schedule_names": [f"{instalments} monthly instalments"],
        "portion_cents": [each],
        "note_html": note,
        "terms_html": terms,
        "next_steps_message_html": next_steps,
        "must_appear": [sentence, inc(fee_cents)],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fee-ex", type=float, required=True, help="Total fee ex GST in dollars, already rounded to $50")
    p.add_argument("--service", required=True, help='Service name stem, e.g. "Annual Group Compliance"')
    p.add_argument("--fy", type=int, help="Income year the engagement covers, e.g. 2026. Omit for non-annual work")
    p.add_argument("--first-names", nargs="+", required=True,
                   help="First names only of the people being greeted, e.g. Bijit Rashmi")
    p.add_argument("--covering", required=True,
                   help='What the engagement covers, e.g. "the annual compliance for your group for the year ended 30 June 2026"')
    p.add_argument("--new-client", action="store_true", help="Use the new-client opening and closing lines")
    p.add_argument("--billing", choices=["deposit", "monthly"], default="deposit")
    p.add_argument("--instalments", type=int, default=12, help="Monthly billing only")
    a = p.parse_args()

    fee_cents = round(a.fee_ex * 100)
    if fee_cents % 5000:
        sys.exit(f"Fee {money(fee_cents)} is not rounded to the nearest $50. Round it first (SKILL.md step 2).")
    names = [n.strip(" ,") for n in a.first_names if n.strip(" ,")]
    if any("," in n or (n.isupper() and len(n) > 2) for n in names):
        sys.exit("Pass first names only, in normal case (Bijit, not KHATIWADA, Bijit).")

    total_inc = inc(fee_cents)
    stem = f"{a.service} FY{a.fy}" if a.fy else a.service
    service_name = f"{stem} (total fee {total_inc} inc GST)"
    if len(service_name) > SERVICE_NAME_LIMIT:
        sys.exit(f"Service name is {len(service_name)} characters, over Ignition's {SERVICE_NAME_LIMIT}. Shorten --service.")

    out = deposit(fee_cents) if a.billing == "deposit" else monthly(fee_cents, a.instalments)
    greeting = f"Hi {join_names(names)},"

    result = {
        "fee": {
            "total_ex": money(fee_cents),
            "total_gst": money(gst(fee_cents)),
            "total_inc": total_inc,
            "total_cents": fee_cents,
        },
        "service_name": service_name,
        "billing_name": service_name,
        "billing_schedule_names": out["billing_schedule_names"],
        "portion_cents": out["portion_cents"],
        "display_settings": {
            "proposal_value_display": "show",
            "service_price_display": "show",
            "one_time_date_display": "hide",
        },
        "personalised_message_html": message(greeting, a.covering, out["note_html"], a.new_client),
        "terms_html": out["terms_html"],
        "next_steps_message_html": out["next_steps_message_html"],
        "must_appear": out["must_appear"] + [greeting, service_name],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
