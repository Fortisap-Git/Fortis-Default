#!/usr/bin/env python3
"""
build_pack.py - turn the workpaper's Profit & Loss and Balance Sheet tabs into a
ledger pack (pack.json) that render_pack.py can print.

This is the "post to the Xero ledger" step: every line on the two tabs becomes an
account with a Xero-style account type and a report code, using (in order)
  1. the chart of accounts CSV (exact code or name match),
  2. keyword rules,
  3. the Xero account type implied by the section header the line sits under.

Usage
-----
  # from the Fortis workpaper (tabs 'Profit & Loss' and 'Balance Sheet'; A=label, B=CY, C=PY)
  python build_pack.py --workpaper "2026 Workpaper - Client.xlsm" \
      --name "Client Pty Ltd" --abn "12 345 678 901" --fy-end 2026-06-30 \
      --directors "Jane Citizen;John Citizen" --out pack.json

  # from two CSV exports instead (label,cy,py)
  python build_pack.py --pl pl.csv --bs bs.csv --entity entity.json --out pack.json

  # optional extras
      --coa assets/chart-of-accounts/company-default.csv   (default)
      --depreciation depn.csv|depn.json                     (see references/report-pack-structure.md)
      --opening-equity-py 85089                             (PY opening equity from last year's pack)
      --expenses-negative auto|yes|no                       (flip sign if the workpaper stores expenses as negatives)
      --mapping-out mapping.md                              (account -> report code table for review)

The script prints the mapping table and the validation report.  Accounts with
confidence 'type' or 'none' MUST be reviewed before the pack is rendered.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fr_engine import (COA, DEFAULT_COA, SECTION_TO_TYPE, Pack, fmt, infer_report_code, load_map,  # noqa: E402
                       rnd, strip_code)

SKIP_LABELS = re.compile(
    r"^(total\b|gross profit|net profit|net loss|operating profit|net assets|net income|profit/\(loss\)|"
    r"profit before|profit after|less |plus |add |ebit)", re.I)
HEADER_HINTS = re.compile(r"^(account( code)?( - name)?|particulars|cy|py|current year|prior year|\d{4})$", re.I)


# --------------------------------------------------------------------------- #
# reading the two statements
# --------------------------------------------------------------------------- #
def _num(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "").replace("$", "")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if s in ("-", "", "–"):
        return 0.0
    try:
        f = float(s)
    except ValueError:
        return None
    return -f if neg else f


def read_rows_xlsx(path: str, sheet_names: list[str]) -> list[list]:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    for name in sheet_names:
        if name in wb.sheetnames:
            ws = wb[name]
            return [list(r) for r in ws.iter_rows(values_only=True)]
    raise SystemExit(f"None of the sheets {sheet_names} found in {path}. Sheets: {wb.sheetnames}")


def read_rows_csv(path: str) -> list[list]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [row for row in csv.reader(fh)]


def parse_statement(rows: list[list], side: str) -> list[dict]:
    """
    Walk the rows of a P&L or BS tab and return account dicts:
      {code, name, section, type, cy, py, row}
    Section headers (label with no numbers) set the Xero account type context.
    Totals / computed lines are skipped - the engine recomputes them.
    """
    out = []
    section = None
    started = False
    for idx, r in enumerate(rows, 1):
        r = list(r) + [None] * (4 - len(r))
        label = (str(r[0]).strip() if r[0] is not None else "")
        cy, py = _num(r[1]), _num(r[2])
        if not label:
            continue
        if not started:
            # header row: 'Account Code - Name | CY | PY' or 'Particulars | CY | PY'
            if HEADER_HINTS.match(label) or (isinstance(r[1], str) and HEADER_HINTS.match(str(r[1]).strip())):
                started = True
                continue
            if cy is None and py is None:
                # pre-header text (titles) - but a section header could also come first
                if label.lower() in SECTION_TO_TYPE:
                    started = True
                    section = label.lower()
                continue
            started = True  # numeric row before any header - just start
        if cy is None and py is None:
            key = label.lower().rstrip(":")
            if key in SECTION_TO_TYPE or key in ("assets", "liabilities", "income", "expenses", "equity"):
                section = key
            continue
        if SKIP_LABELS.match(label) and not re.match(r"^\d", label):
            continue
        code, name = strip_code(label)
        atype = SECTION_TO_TYPE.get(section or "", None)
        if atype is None:
            atype = {"pl": None, "bs": None}[side]
        out.append({"code": code, "name": name, "section": section, "type": atype,
                    "cy": cy or 0.0, "py": py or 0.0, "row": idx})
    return out


# --------------------------------------------------------------------------- #
# mapping
# --------------------------------------------------------------------------- #
def map_accounts(pl: list[dict], bs: list[dict], coa: COA, rmap: dict, expenses_negative: str) -> tuple[list[dict], list[dict]]:
    mapping_rows = []
    accounts = []

    def fallback_type(a: dict, side: str) -> str | None:
        if a["type"]:
            return a["type"]
        # no section header - guess from the side
        if side == "pl":
            return None  # keyword rules will have to decide REV vs EXP
        return None

    for side, rows in (("pl", pl), ("bs", bs)):
        for a in rows:
            atype = fallback_type(a, side)
            rcode, conf, why = infer_report_code(a["name"], atype, coa, rmap, code=a["code"])
            # side sanity: a P&L line must be REV/EXP/EQU.DIV; a BS line must be ASS/LIA/EQU
            if rcode:
                top = rcode.split(".")[0]
                if side == "pl" and top not in ("REV", "EXP") and rcode != "EQU.DIV":
                    rcode, conf, why = ("EXP.OPE" if a["type"] not in ("Revenue", "Sales", "Other Income") else "REV.TRA"), "type", f"P&L line but rule gave {rcode}; defaulted"
                if side == "bs" and top not in ("ASS", "LIA", "EQU"):
                    rcode, conf, why = "", "none", f"Balance Sheet line but rule gave {rcode}"
            if side == "pl" and not rcode:
                # last resort on the P&L: positive amounts under no header -> expense
                rcode, conf, why = "EXP.OPE", "none", "no header, no rule - defaulted to Expenses; REVIEW"
            acct = {"code": a["code"], "name": a["name"], "type": atype or "", "report_code": rcode,
                    "cy": a["cy"], "py": a["py"], "source": f"{side}:row{a['row']}",
                    "mapping": {"confidence": conf, "reason": why, "section": a["section"]}}
            accounts.append(acct)
            mapping_rows.append(acct)

    # sign conventions -----------------------------------------------------
    exp = [a for a in accounts if a["report_code"].startswith("EXP")]
    if exp:
        neg = sum(1 for a in exp if a["cy"] < 0 or (a["cy"] == 0 and a["py"] < 0))
        flip = expenses_negative == "yes" or (expenses_negative == "auto" and neg > len(exp) / 2)
        if flip:
            for a in exp:
                a["cy"], a["py"] = -a["cy"], -a["py"]
                a["mapping"]["reason"] += "; sign flipped (expenses stored as negatives)"
    for a in accounts:
        if a["report_code"] == "EQU.DIV":
            # dividends: printed as a positive 'paid' amount
            if a["source"].startswith("bs") and (a["cy"] < 0 or a["py"] < 0):
                a["cy"], a["py"] = -a["cy"], -a["py"]
                a["mapping"]["reason"] += "; dividends taken from equity (debit) and shown as paid"
    return accounts, mapping_rows


def mapping_markdown(rows: list[dict]) -> str:
    out = ["| Source | Code | Account | Xero type | Report code | Confidence | Why |", "|---|---|---|---|---|---|---|"]
    for a in rows:
        m = a["mapping"]
        flag = " **REVIEW**" if m["confidence"] in ("type", "none") else ""
        out.append(f"| {a['source']} | {a['code'] or ''} | {a['name']} | {a['type']} | `{a['report_code']}`{flag} | {m['confidence']} | {m['reason']} |")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# depreciation input
# --------------------------------------------------------------------------- #
def read_depreciation(path: str) -> dict:
    p = Path(path)
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    groups: dict[str, list] = {}
    with open(p, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            row = {k.strip().lower().replace(" ", "_"): (v or "").strip() for k, v in row.items() if k}
            g = row.pop("group", None) or row.pop("class", None) or "Assets"
            asset = {}
            for k, v in row.items():
                if k in ("cost", "opening_accum", "opening_value", "purchases", "disposals", "depreciation",
                         "closing_accum", "closing_value"):
                    asset[k] = _num(v) or 0.0
                elif v:
                    asset[k] = v
            groups.setdefault(g, []).append(asset)
    layout = "simple"
    cols = set().union(*[set(a) for g in groups.values() for a in g]) if groups else set()
    if "asset_number" in cols or "opening_accum" in cols:
        layout = "register"
    elif "rate" in cols or "method" in cols:
        layout = "standard"
    return {"layout": layout, "groups": [{"name": g, "assets": a} for g, a in groups.items()]}


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_argument_group("source")
    src.add_argument("--workpaper", help="xlsx/xlsm workpaper")
    src.add_argument("--pl-sheet", default="Profit & Loss,PL")
    src.add_argument("--bs-sheet", default="Balance Sheet,BS")
    src.add_argument("--pl", help="CSV: label,cy,py")
    src.add_argument("--bs", help="CSV: label,cy,py")
    ent = ap.add_argument_group("entity")
    ent.add_argument("--entity", help="JSON file with entity fields (name, abn, fy_end, directors, type)")
    ent.add_argument("--name"); ent.add_argument("--abn"); ent.add_argument("--fy-end")
    ent.add_argument("--directors", help="semicolon separated"); ent.add_argument("--type", default="company")
    ap.add_argument("--coa", default=str(DEFAULT_COA))
    ap.add_argument("--map")
    ap.add_argument("--depreciation")
    ap.add_argument("--opening-equity-py", type=float)
    ap.add_argument("--expenses-negative", choices=["auto", "yes", "no"], default="auto")
    ap.add_argument("--cost-of-sales-label", default="Cost of Sales")
    ap.add_argument("--sort", choices=["alpha", "source"], default="alpha")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mapping-out")
    args = ap.parse_args()

    if args.workpaper:
        pl_rows = read_rows_xlsx(args.workpaper, [s.strip() for s in args.pl_sheet.split(",")])
        bs_rows = read_rows_xlsx(args.workpaper, [s.strip() for s in args.bs_sheet.split(",")])
    elif args.pl and args.bs:
        pl_rows, bs_rows = read_rows_csv(args.pl), read_rows_csv(args.bs)
    else:
        ap.error("give --workpaper or both --pl and --bs")

    entity = {}
    if args.entity:
        entity = json.loads(Path(args.entity).read_text(encoding="utf-8"))
    for k, v in (("name", args.name), ("abn", args.abn), ("fy_end", args.fy_end), ("type", args.type)):
        if v:
            entity[k] = v
    if args.directors:
        entity["directors"] = [d.strip() for d in args.directors.split(";") if d.strip()]
    entity.setdefault("type", "company")

    rmap = load_map(args.map)
    coa = COA.load(args.coa)
    pl = parse_statement(pl_rows, "pl")
    bs = parse_statement(bs_rows, "bs")
    accounts, mapping_rows = map_accounts(pl, bs, coa, rmap, args.expenses_negative)

    pack = {
        "_generated_by": "build_pack.py",
        "_source": {"workpaper": args.workpaper, "pl": args.pl, "bs": args.bs, "coa": args.coa},
        "entity": entity,
        "options": {"sort": args.sort, "cost_of_sales_label": args.cost_of_sales_label},
        "accounts": accounts,
    }
    if args.opening_equity_py is not None:
        pack["equity"] = {"opening_py": args.opening_equity_py}
    if args.depreciation:
        pack["depreciation"] = read_depreciation(args.depreciation)

    Path(args.out).write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")

    md = mapping_markdown(mapping_rows)
    if args.mapping_out:
        Path(args.mapping_out).write_text(md, encoding="utf-8")
    print("## Account mapping\n")
    print(md)
    review = [a for a in mapping_rows if a["mapping"]["confidence"] in ("type", "none")]
    print(f"\n{len(mapping_rows)} accounts mapped; {len(review)} need review (confidence type/none).")

    print("\n## Validation\n")
    p = Pack(pack, rmap)
    print(p.validation_markdown())
    s = p.summary()
    print(f"\nNPAT {fmt(s['npat']['cy'])} (PY {fmt(s['npat']['py'])}) | Net Assets {fmt(s['net_assets']['cy'])} "
          f"(PY {fmt(s['net_assets']['py'])}) | Notes: {', '.join(f'{n}. {t}' for n, t in s['notes'])}")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
