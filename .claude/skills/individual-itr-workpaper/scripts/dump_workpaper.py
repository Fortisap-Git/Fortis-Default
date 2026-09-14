#!/usr/bin/env python3
"""Dump a workpaper to compact text so reviewers read ONE file instead of each
opening the workbook in Python.

    python scripts/dump_workpaper.py working.xlsm [--changed] [--all] [--sheet NAME]...
                                     [--values recalc.xlsx] > dump.txt

Line format:   Sheet!A1 | value-or-formula | =computed (with --values) | link:target | comment:...

--changed      only cells that differ from the bundled master (what the preparer
               entered), plus every row label in column A-C so the reader has context.
               This is the reviewer feed: typically 200-400 lines instead of ~1,700.
--all          include hidden sheets (default: visible only).
--sheet NAME   only this sheet (repeatable; implies hidden sheets allowed).
--values FILE  a recalculated copy (verify_workpaper.py --recalc output) whose cached
               values are shown beside each formula.
"""
import re
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
MASTER = HERE.parent / "assets" / "2026_ITR_Workpaper_-_Individual_Name.xlsm"
CLIENT_TAB = re.compile(r"^(Summary|Deductions) - (.+)$")


def plain(v):
    """ArrayFormula / DataTableFormula objects -> their formula text."""
    if hasattr(v, "text"):
        return v.text if str(v.text).startswith("=") else "=" + str(v.text)
    return v


def fmt(v):
    v = plain(v)
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:,.2f}" if abs(v) >= 1 else f"{v:.4g}"
    return str(v).replace("\n", " ")[:160]


def master_counterpart(name, master_names, taken):
    if name in master_names:
        return name
    m = CLIENT_TAB.match(name)
    if m:
        for n in ("1", "2"):
            cand = f"{m.group(1)} - {n} Client name "
            if cand in master_names and cand not in taken:
                return cand
    for mn in master_names:                       # clone -> parent by prefix
        if name.startswith(mn.rstrip()) and name != mn:
            return mn
    return None


def normalise_formula(v, sheet, msheet):
    """Formulas that only differ by the renamed sheet are 'unchanged'."""
    if isinstance(v, str) and v.startswith("=") and sheet != msheet:
        return v.replace(f"'{sheet}'", f"'{msheet}'")
    return v


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    show_hidden = "--all" in args
    changed = "--changed" in args
    only = [args[i + 1] for i, a in enumerate(args) if a == "--sheet"]
    vals = None
    if "--values" in args:
        vals = openpyxl.load_workbook(args[args.index("--values") + 1], data_only=True)

    wb = openpyxl.load_workbook(path, keep_vba=True)
    mb = openpyxl.load_workbook(MASTER, keep_vba=True) if changed else None
    taken = set()
    out = []
    for ws in wb.worksheets:
        if only and ws.title not in only:
            continue
        if ws.sheet_state != "visible" and not show_hidden and not only:
            continue
        ms = None
        if mb:
            mname = master_counterpart(ws.title, mb.sheetnames, taken)
            if mname:
                taken.add(mname)
                ms = mb[mname]
        out.append(f"## {ws.title} [{ws.sheet_state}] rows={ws.max_row} cols={ws.max_column}"
                   + (f"  (vs master '{ms.title}')" if ms else ""))
        vws = vals[ws.title] if vals and ws.title in vals.sheetnames else None
        renames = {}
        if ms and ms.title != ws.title:
            renames[ws.title] = ms.title

        def differs(c):
            mv = plain(ms.cell(c.row, c.column).value)
            v = plain(c.value)
            for new, old in renames.items():
                v = normalise_formula(v, new, old)
            if isinstance(v, str) and v.startswith("="):
                v = re.sub(r"'(Summary|Deductions) - [^']+'", lambda m: f"'{m.group(1)} - 1 Client name '", v)
                mv = re.sub(r"'(Summary|Deductions) - [^']+'", lambda m: f"'{m.group(1)} - 1 Client name '", mv) if isinstance(mv, str) else mv
            return v != mv or bool(c.comment)

        changed_rows = set()
        if ms is not None:
            for row in ws.iter_rows():
                for c in row:
                    if (c.value is not None or c.hyperlink or c.comment) and differs(c):
                        changed_rows.add(c.row)

        for row in ws.iter_rows():
            for c in row:
                if c.value is None and not c.hyperlink and not c.comment:
                    continue
                if ms is not None:
                    is_label = (c.column <= 3 and isinstance(c.value, str)
                                and not c.value.startswith("=") and c.row in changed_rows)
                    if not differs(c) and not is_label:
                        continue
                parts = [f"{ws.title}!{c.coordinate}", fmt(c.value)]
                if vws is not None and isinstance(c.value, str) and c.value.startswith("="):
                    parts.append("=" + fmt(vws[c.coordinate].value))
                if c.hyperlink:
                    parts.append("link:" + (c.hyperlink.location or c.hyperlink.target or ""))
                if c.comment:
                    parts.append("comment:" + c.comment.text.replace("\n", " ")[:80])
                out.append(" | ".join(parts))
        out.append("")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
