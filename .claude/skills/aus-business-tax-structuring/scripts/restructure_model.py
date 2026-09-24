#!/usr/bin/env python3
"""
Restructure model: what does it cost to move an asset (usually a rental
property) from one owner to another, and does the annual benefit ever pay
that back?

Usage
    python3 restructure_model.py input.json            # markdown report
    python3 restructure_model.py input.json --json     # machine readable

Input: see ../assets/example-wilga-street.json for the full shape. Every
figure must come from the file (FYI) or the client's email; the script does
no guessing. Where a figure is not known, leave it out and the report will
say "not provided" rather than invent it.

What it computes
    1. CGT on the transfer at market value (s 116-30 market value
       substitution), building the cost base from its elements and reducing it
       for Div 43 claimed (s 110-45(2)), with the 50 per cent discount where the
       transferor is an individual or trust and has held the asset 12 months.
       Tax is worked out marginally on top of the owner's other taxable income
       using the 2026-27 resident rates plus 2 per cent Medicare.
    2. Transfer duty in the state where the LAND is (NSW, VIC, QLD modelled;
       other states return "not modelled").
    3. Annual land tax for the current owner and the target owner type
       (NSW, VIC, QLD modelled) so the SPV land tax cost is visible.
    4. Finance: annual interest saving from the refinance, less extra land tax
       and extra compliance, giving a net annual benefit and a payback period.
    5. A sensitivity line for the post 1 July 2027 CGT regime (indexation plus
       a 30 per cent minimum tax) so the reader can see whether timing matters.

Rate tables are 2026-27 as at September 2026. They are marked VERIFY where
they were derived from indexation rather than read from the revenue office
page. Check them against the revenue office before quoting to a client.
"""
import json
import sys
from datetime import date

# ---------------------------------------------------------------------------
# 2026-27 federal rates
# ---------------------------------------------------------------------------
RESIDENT_BRACKETS_2026_27 = [
    # (lower, upper, rate)  upper None = no cap
    (0, 18_200, 0.00),
    (18_200, 45_000, 0.15),
    (45_000, 135_000, 0.30),
    (135_000, 190_000, 0.37),
    (190_000, None, 0.45),
]
MEDICARE = 0.02
COMPANY_RATE_PASSIVE = 0.30     # a pure rental company fails the 80% passive test
COMPANY_RATE_BRE = 0.25
POST_2027_MIN_RATE = 0.30       # Budget 2026-27 minimum tax on net capital gains (announced, not law)

# ---------------------------------------------------------------------------
# Transfer duty tables (general rate, non-foreign). Brackets: (threshold, base, rate_over)
# ---------------------------------------------------------------------------
DUTY = {
    # QLD general rates, unchanged for many years. qro.qld.gov.au/duties/transfer-duty/calculate/rates
    "QLD": [
        (0, 0.0, 0.0),
        (5_000, 0.0, 0.015),
        (75_000, 1_050.0, 0.035),
        (540_000, 17_325.0, 0.045),
        (1_000_000, 38_025.0, 0.0575),
    ],
    # NSW 1 July 2026 to 30 June 2027. Upper brackets confirmed from Revenue NSW
    # ($387,000 to $1,290,000: $11,602 plus 4.5%; premium $3,870,000 = $194,137 plus 7%).
    # Lower brackets DERIVED from CPI indexation of the 2025-26 table. VERIFY.
    "NSW": [
        (0, 0.0, 0.0125),
        (19_000, 238.0, 0.015),
        (38_000, 523.0, 0.0175),
        (103_000, 1_660.0, 0.035),
        (387_000, 11_602.0, 0.045),
        (1_290_000, 52_237.0, 0.055),
        (3_870_000, 194_137.0, 0.07),   # premium duty, residential land only
    ],
    # VIC general rates (long-standing)
    "VIC": [
        (0, 0.0, 0.014),
        (25_000, 350.0, 0.024),
        (130_000, 2_870.0, 0.06),
        (960_000, None, 0.055),          # flat 5.5% of total value
        (2_000_000, 110_000.0, 0.065),
    ],
}
FOREIGN_PURCHASER_SURCHARGE = {"NSW": 0.09, "VIC": 0.08, "QLD": 0.08}

# ---------------------------------------------------------------------------
# Land tax tables. Each entry: list of (threshold, base, rate_over) applied to
# total taxable land value of that owner in that state. Owner types:
#   individual | company | discretionary_trust | unit_trust
# ---------------------------------------------------------------------------
LAND_TAX = {
    "QLD": {
        # qro.qld.gov.au/land-tax/calculate/individual and /company-trust (2026-27)
        "individual": [(600_000, 500.0, 0.01), (1_000_000, 4_500.0, 0.0165), (3_000_000, 37_500.0, 0.0125),
                       (5_000_000, 62_500.0, 0.0175), (10_000_000, 150_000.0, 0.0225)],
        "company": [(350_000, 1_450.0, 0.017), (2_250_000, 33_750.0, 0.015), (5_000_000, 75_000.0, 0.0225),
                    (10_000_000, 187_500.0, 0.0275)],
    },
    "NSW": {
        # 2026 land tax year: general threshold $1,075,000, premium $6,571,000 (thresholds frozen)
        "individual": [(1_075_000, 100.0, 0.016), (6_571_000, 88_036.0, 0.02)],
        # special trust (typical discretionary trust): no threshold, 1.6% from $0, 2% above premium
        "discretionary_trust": [(0, 0.0, 0.016), (6_571_000, 105_136.0, 0.02)],
    },
    "VIC": {
        # 2026 general rates INCLUDING the COVID debt temporary surcharge (2024 to 2033)
        "individual": [(50_000, 500.0, 0.0), (100_000, 975.0, 0.0), (300_000, 1_350.0, 0.003),
                       (600_000, 2_250.0, 0.006), (1_000_000, 4_650.0, 0.009), (1_800_000, 11_850.0, 0.0165),
                       (3_000_000, 31_650.0, 0.0265)],
        # trust surcharge rates (general rate plus 0.375% up to $3m). VERIFY against sro.vic.gov.au
        "discretionary_trust": [(25_000, 82.0, 0.00375), (50_000, 676.0, 0.00375), (100_000, 1_338.0, 0.00375),
                                (250_000, 1_901.0, 0.00675), (600_000, 4_263.0, 0.00975), (1_000_000, 8_163.0, 0.01275),
                                (1_800_000, 18_363.0, 0.011072), (3_000_000, 31_650.0, 0.0265)],
    },
}
# owner type -> which table to use in each state
LAND_TAX_MAP = {
    "QLD": {"individual": "individual", "company": "company", "discretionary_trust": "company", "unit_trust": "company"},
    "NSW": {"individual": "individual", "company": "individual", "discretionary_trust": "discretionary_trust",
            "unit_trust": "individual"},
    "VIC": {"individual": "individual", "company": "individual", "discretionary_trust": "discretionary_trust",
            "unit_trust": "discretionary_trust"},
}
FOREIGN_LAND_TAX_SURCHARGE = {"NSW": 0.05, "VIC": 0.04, "QLD": 0.03}
LAND_TAX_NOTES = {
    "QLD": "Companies, trustees and absentees share the $350,000 threshold; individuals $600,000. "
           "Aggregated across all QLD land of the same owner. Absentee and foreign trust or company surcharge 3%.",
    "NSW": "Special (discretionary) trusts get no threshold and pay 1.6% from the first dollar. "
           "Fixed trusts and companies get the general threshold; related companies are grouped to one threshold. "
           "Foreign owner surcharge 5% on residential land, no threshold. Boarding house exemption (LT rulings) "
           "may be available for genuine boarding houses meeting the tariff limits.",
    "VIC": "Trust surcharge 0.375% applies from $25,000. COVID debt surcharge included in general rates to 2033. "
           "Absentee owner surcharge 4%. Registered rooming houses may be exempt.",
}


def bracket_tax(value, table):
    """Apply a (threshold, base, rate_over) table. Value below the first threshold => 0."""
    if value <= table[0][0]:
        return 0.0
    row = table[0]
    for r in table:
        if value > r[0]:
            row = r
    threshold, base, rate = row
    if base is None:  # flat rate on whole value (VIC 960k to 2m)
        return value * rate
    return base + (value - threshold) * rate


def duty(state, value, foreign=False):
    state = state.upper()
    if state not in DUTY:
        return None, f"Transfer duty for {state} not modelled; look it up on the state revenue office site."
    d = bracket_tax(value, DUTY[state])
    note = ""
    if foreign:
        d += value * FOREIGN_PURCHASER_SURCHARGE[state]
        note = f"includes foreign purchaser surcharge {FOREIGN_PURCHASER_SURCHARGE[state]:.0%}"
    return round(d, 2), note


def land_tax(state, owner_type, land_value, other_land=0.0, foreign=False):
    state = state.upper()
    if state not in LAND_TAX:
        return None, f"Land tax for {state} not modelled."
    key = LAND_TAX_MAP[state].get(owner_type)
    table = LAND_TAX[state].get(key)
    if table is None:
        return None, f"Land tax for owner type {owner_type} in {state} not modelled."
    total = land_value + other_land
    lt = bracket_tax(total, table)
    note = LAND_TAX_NOTES[state]
    if foreign:
        lt += land_value * FOREIGN_LAND_TAX_SURCHARGE[state]
        note += f" Foreign surcharge {FOREIGN_LAND_TAX_SURCHARGE[state]:.0%} added."
    return round(lt, 2), note


def income_tax(taxable):
    tax = 0.0
    for lower, upper, rate in RESIDENT_BRACKETS_2026_27:
        if taxable <= lower:
            break
        top = taxable if upper is None else min(taxable, upper)
        tax += (top - lower) * rate
    return tax + taxable * MEDICARE


def marginal_tax_on(extra, other_income):
    return income_tax(other_income + extra) - income_tax(other_income)


def parse_date(s):
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


def cgt(inputs):
    p = inputs["property"]
    o = inputs["owner"]
    cb = p.get("cost_base", {})
    elements = {
        "Element 1: land": cb.get("land"),
        "Element 1: construction / building": cb.get("construction"),
        "Element 2: acquisition costs (duty, legal, valuation)": cb.get("acquisition_costs"),
        "Element 3: non-deductible holding costs": cb.get("holding_costs_non_deductible"),
        "Element 4: capital improvements": cb.get("other_capital"),
        "Element 5: title costs": cb.get("title_costs"),
    }
    missing = [k for k, v in elements.items() if v is None]
    gross = sum(v for v in elements.values() if v)
    # Plant treatment. Fortis house method ("in_cost_base"): the Div 40 plant stays inside the construction cost
    # and only the Div 40 depreciation already claimed is deducted, so the cost base reflects the plant's written
    # down value. Alternative ("separate"): strip the plant cost out entirely and run each item's balancing
    # adjustment (s 40-285) outside the CGT calculation. Either way the workpaper shows the plant split.
    plant_method = cb.get("plant_method", "in_cost_base")
    if plant_method == "separate":
        less_plant = cb.get("less_depreciating_assets", 0) or 0
        div40 = 0
    else:
        less_plant = 0
        div40 = cb.get("div40_claimed_to_date", 0) or 0
    div43 = p.get("div43_claimed_to_date", 0) or 0            # s 110-45(2): reduce cost base by Div 43 deducted or deductible
    cost_base = gross - less_plant - div43 - div40
    mv = p["market_value"]
    gain = mv - cost_base
    held_days = (parse_date(p["transfer_date"]) - parse_date(p["acquired"])).days
    eligible_discount = o["type"] in ("individual", "discretionary_trust", "unit_trust") and held_days >= 365
    discount = 0.5 if eligible_discount else 0.0
    net_gain = gain * (1 - discount) if gain > 0 else gain
    if o["type"] == "individual":
        tax = marginal_tax_on(max(net_gain, 0), o.get("other_taxable_income", 0))
        tax_basis = "marginal 2026-27 resident rates plus 2% Medicare, stacked on other taxable income"
    elif o["type"] == "company":
        rate = COMPANY_RATE_BRE if o.get("base_rate_entity") else COMPANY_RATE_PASSIVE
        tax = max(net_gain, 0) * rate
        tax_basis = f"company rate {rate:.0%}"
    else:
        tax = None
        tax_basis = "trust: tax depends on who is presently entitled; model at the beneficiary level"
    # sensitivity: post 1 July 2027 regime (announced). Indexation of cost base then 30% minimum on the real gain.
    cpi = inputs.get("assumptions", {}).get("cpi_uplift_to_transfer", 0.0)
    indexed_cb = cost_base * (1 + cpi)
    post_gain = max(mv - indexed_cb, 0)
    post_min_tax = post_gain * POST_2027_MIN_RATE
    return {
        "market_value": mv,
        "elements": elements,
        "missing_elements": missing,
        "gross_cost": gross,
        "plant_method": plant_method,
        "less_depreciating_assets": less_plant,
        "less_div40_claimed": div40,
        "less_div43_claimed": div43,
        "cost_base": cost_base,
        "capital_gain": gain,
        "held_days": held_days,
        "discount_applied": discount,
        "net_capital_gain": net_gain,
        "tax": None if tax is None else round(tax, 2),
        "tax_basis": tax_basis,
        "post_2027_sensitivity": {
            "cpi_uplift_assumed": cpi,
            "indexed_cost_base": round(indexed_cb, 2),
            "real_gain": round(post_gain, 2),
            "minimum_tax_30pc": round(post_min_tax, 2),
            "note": "Announced in the 2026-27 Budget for gains accruing from 1 July 2027; not law at September 2026. "
                    "Gains accrued to 30 June 2027 are to keep the 50% discount under transitional rules.",
        },
    }


def finance(inputs, upfront_total, extra_land_tax):
    f = inputs.get("finance", {})
    cur = f.get("current_loan", 0) * f.get("current_rate", 0)
    new = f.get("new_loan", 0) * f.get("new_rate", 0)
    interest_saving = cur - new
    extra_compliance = f.get("annual_extra_compliance", 0)
    net_annual = interest_saving - extra_land_tax - extra_compliance
    payback = (upfront_total / net_annual) if net_annual > 0 else None
    return {
        "current_annual_interest": round(cur, 2),
        "new_annual_interest": round(new, 2),
        "annual_interest_saving": round(interest_saving, 2),
        "extra_land_tax_pa": round(extra_land_tax, 2),
        "extra_compliance_pa": extra_compliance,
        "net_annual_benefit": round(net_annual, 2),
        "upfront_total": round(upfront_total, 2),
        "payback_years": None if payback is None else round(payback, 1),
    }


def run(inputs):
    p = inputs["property"]
    o = inputs["owner"]
    t = inputs["target"]
    state = p["state"].upper()
    out = {"property": p.get("name"), "state": state}
    out["cgt"] = cgt(inputs)
    d, dnote = duty(state, p["market_value"], foreign=t.get("foreign", False))
    out["duty"] = {"amount": d, "note": dnote}
    lv = p.get("land_value_unimproved")
    if lv is None:
        out["land_tax"] = {"note": "Unimproved land value not provided; read it off the council rates notice or the state valuation."}
        extra_lt = 0.0
    else:
        cur_lt, cur_note = land_tax(state, o["type"], lv, o.get("other_land_in_state", 0), o.get("foreign_person", False))
        new_lt, new_note = land_tax(state, t["entity"], lv, t.get("other_land_in_state", 0), t.get("foreign", False))
        extra_lt = (new_lt or 0) - (cur_lt or 0)
        out["land_tax"] = {"land_value": lv, "current_owner_pa": cur_lt, "target_owner_pa": new_lt,
                           "extra_pa": round(extra_lt, 2), "note": new_note}
    f = inputs.get("finance", {})
    duty_inside = f.get("duty_included_in_transfer_costs", False)
    out["duty"]["included_in_transfer_costs"] = duty_inside
    upfront = ((out["cgt"]["tax"] or 0) + (0 if duty_inside else (d or 0))
               + f.get("transfer_costs_other", 0) + f.get("setup_cost", 0))
    out["finance"] = finance(inputs, upfront, extra_lt)
    out["flags"] = flags(inputs, out)
    return out


def flags(inputs, out):
    fl = []
    p, o, t = inputs["property"], inputs["owner"], inputs["target"]
    if out["cgt"]["missing_elements"]:
        fl.append("Cost base elements not provided: " + "; ".join(out["cgt"]["missing_elements"]) +
                  ". Pull the settlement statement, duty receipt and legal invoices before quoting a CGT figure.")
    if t["entity"] == "company":
        fl.append("Company target: no CGT discount or indexation on a later sale, 30% rate on rent (fails the base rate "
                  "entity passive income test), rental losses trapped in the company, Div 7A on any personal use of "
                  "company cash or refinance proceeds.")
    if t["entity"] == "discretionary_trust":
        fl.append("Discretionary trust target: 30% minimum tax at trustee level announced from 1 July 2028 (credits to "
                  "individual beneficiaries only), rental losses trapped in the trust, adverse land tax in NSW and VIC.")
    if t["entity"] == "unit_trust":
        fl.append("Unit trust target: excluded from the trust minimum tax as a fixed trust, but losses still trapped in "
                  "the trust and the transfer is still a CGT event and dutiable.")
    if p.get("rooming_or_boarding_house"):
        fl.append("Rooming or boarding house: check GST classification (GSTR 2012/6 commercial residential premises). "
                  "If the premises are commercial residential, the transfer itself may be a taxable supply and the "
                  "rent may be taxable supplies over the $75,000 registration threshold. Check state land tax "
                  "boarding house or rooming house exemptions.")
    if p.get("acquired") and parse_date(p["acquired"]) < date(2026, 5, 12):
        fl.append("Property acquired before 12 May 2026: negative gearing is grandfathered while it stays in the "
                  "current owner's hands. A transfer to a new entity is a new acquisition after Budget night, so "
                  "the announced quarantining of rental losses would apply to the new owner from 1 July 2027 "
                  "(new dwellings excepted).")
    if inputs.get("finance", {}).get("current_rate", 0) > inputs.get("finance", {}).get("new_rate", 1):
        fl.append("Confirm the broker's rate differential in writing (approval in principle) and whether the personal "
                  "name rate could be improved with another lender before any transfer is contemplated.")
    return fl


def money(x):
    return "not provided" if x is None else f"${x:,.0f}"


def report(out, inputs):
    c = out["cgt"]
    lines = []
    lines.append(f"# Restructure model: {out['property']} ({out['state']})\n")
    lines.append("## 1. CGT on transfer at market value\n")
    lines.append("| Item | Amount |\n|---|---|")
    lines.append(f"| Market value (deemed capital proceeds, s 116-30) | {money(c['market_value'])} |")
    for k, v in c["elements"].items():
        lines.append(f"| {k} | {money(v)} |")
    if c["plant_method"] == "separate":
        lines.append(f"| Less Div 40 depreciating assets (separate assets) | ({money(c['less_depreciating_assets'])}) |")
    else:
        lines.append(f"| Less Div 40 depreciation claimed to transfer date (plant kept in cost base) | ({money(c['less_div40_claimed'])}) |")
    lines.append(f"| Less Div 43 claimed to transfer date (s 110-45(2)) | ({money(c['less_div43_claimed'])}) |")
    lines.append(f"| **Cost base** | **{money(c['cost_base'])}** |")
    lines.append(f"| **Capital gain** | **{money(c['capital_gain'])}** |")
    lines.append(f"| Held {c['held_days']} days, discount applied | {c['discount_applied']:.0%} |")
    lines.append(f"| Net capital gain | {money(c['net_capital_gain'])} |")
    lines.append(f"| **Tax on the gain** ({c['tax_basis']}) | **{money(c['tax'])}** |")
    s = c["post_2027_sensitivity"]
    lines.append(f"\nPost 1 July 2027 sensitivity (announced, not law): indexed cost base {money(s['indexed_cost_base'])} "
                 f"at {s['cpi_uplift_assumed']:.1%} CPI, real gain {money(s['real_gain'])}, 30% minimum tax "
                 f"{money(s['minimum_tax_30pc'])}. {s['note']}\n")
    lines.append("## 2. Transfer duty\n")
    d = out["duty"]
    inside = " Treated as included in the broker's transfer costs, so not added again in the upfront total." if d.get("included_in_transfer_costs") else ""
    lines.append(f"Duty in {out['state']}: {money(d['amount'])}. {(d['note'] + inside).strip()}\n")
    lines.append("## 3. Land tax, current owner vs target owner\n")
    lt = out["land_tax"]
    if "land_value" in lt:
        lines.append("| | Annual land tax |\n|---|---|")
        lines.append(f"| Unimproved land value used | {money(lt['land_value'])} |")
        lines.append(f"| Current owner ({inputs['owner']['type']}) | {money(lt['current_owner_pa'])} |")
        lines.append(f"| Target owner ({inputs['target']['entity']}) | {money(lt['target_owner_pa'])} |")
        lines.append(f"| Extra per year | {money(lt['extra_pa'])} |")
        lines.append(f"\n{lt['note']}\n")
    else:
        lines.append(lt["note"] + "\n")
    lines.append("## 4. Does the refinance pay for the restructure?\n")
    f = out["finance"]
    lines.append("| | Amount |\n|---|---|")
    lines.append(f"| Current annual interest | {money(f['current_annual_interest'])} |")
    lines.append(f"| New annual interest | {money(f['new_annual_interest'])} |")
    lines.append(f"| Annual interest saving | {money(f['annual_interest_saving'])} |")
    lines.append(f"| Less extra land tax per year | ({money(f['extra_land_tax_pa'])}) |")
    lines.append(f"| Less extra compliance per year | ({money(f['extra_compliance_pa'])}) |")
    lines.append(f"| **Net annual benefit** | **{money(f['net_annual_benefit'])}** |")
    lbl = "CGT + transfer costs incl. duty + setup" if out["duty"].get("included_in_transfer_costs") else "CGT + duty + transfer costs + setup"
    lines.append(f"| Upfront cost ({lbl}) | {money(f['upfront_total'])} |")
    pb = f["payback_years"]
    lines.append(f"| **Payback** | **{'never (net annual benefit is nil or negative)' if pb is None else str(pb) + ' years'}** |")
    lines.append("\n## 5. Flags\n")
    for fl in out["flags"]:
        lines.append(f"- {fl}")
    lines.append("\nRates: 2026-27 tables as at September 2026, some derived and marked VERIFY in the script. "
                 "Confirm against the ATO and the state revenue office before this goes to a client.")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1]) as fh:
        inputs = json.load(fh)
    out = run(inputs)
    if "--json" in sys.argv:
        print(json.dumps(out, indent=2, default=str))
    else:
        print(report(out, inputs))
