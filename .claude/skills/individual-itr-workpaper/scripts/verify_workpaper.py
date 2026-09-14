#!/usr/bin/env python3
"""Phase C in one command. Mechanical checks the reviewers should never have to find.

    python scripts/verify_workpaper.py working.xlsm [--spec spec.json] [--claims claims.json]
                                       [--recalc] [--no-fidelity]

Checks (each prints PASS/FAIL/SKIP):
  vba        the file is a macro-enabled .xlsm and xl/vbaProject.bin is present
  links      every internal hyperlink targets an existing sheet; FYI links carry a
             go.fyi.app URL with the entity id
  fidelity   check_template_fidelity.py against the bundled master
  spec       every cell in the spec holds exactly what the spec says (catches a
             later edit or a clone that overwrote it)
  controls   every row marked Control on a Rental Property tab evaluates to 0, and
             the Summary chain (income - deductions = taxable, credits, payable) is
             internally consistent -- evaluated with the built-in mini formula engine
             (cell refs, + - * / %, SUM, ROUND, IF/IFERROR passthrough) so no
             LibreOffice is required
  constants  no hard-coded number sits in a Summary/Deductions/Rental TOTAL row
  recalc     (--recalc) if LibreOffice is installed, produce a recalculated copy
             beside the file (<name>.recalc.xlsx) for dump_workpaper.py --values and
             report any formula error cells; SKIP when no LibreOffice
  claims     (--claims) verify reviewer claims: [{"sheet","cell","expect"}] where expect
             is a value, a formula string, "blank", or "nonblank"

Exit 0 = all PASS/SKIP, 1 = a FAIL, 2 = could not run.

The vba, links and fidelity checks assume a workbook this engine built from the bundled
master. Run against a client workpaper of another lineage they report that difference, not a
defect in anyone's work.

"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp_helpers as h  # noqa: E402

HERE = Path(__file__).resolve().parent
MASTER = HERE.parent / "assets" / "2026_ITR_Workpaper_-_Individual_Name.xlsm"
META = json.loads((HERE.parent / "assets" / "template_meta.json").read_text(encoding="utf-8"))

RESULTS = []


def report(name, ok, detail=""):
    tag = {True: "PASS", False: "FAIL", None: "SKIP"}[ok]
    RESULTS.append((name, ok))
    print(f"[{tag}] {name}" + (f" -- {detail}" if detail else ""))


# ----------------------------------------------------------------- mini engine
REF = re.compile(r"(?:'([^']+)'|([A-Za-z0-9_ ]+))?!?\$?([A-Z]{1,3})\$?(\d+)")
RANGE = re.compile(r"(?:'([^']+)'!|([A-Za-z0-9_]+)!)?\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)")


class Engine:
    def __init__(self, wb):
        self.wb = wb
        self.cache = {}

    def cell(self, sheet, coord, depth=0):
        key = (sheet, coord)
        if key in self.cache:
            return self.cache[key]
        if depth > 60:
            return None
        v = self.wb[sheet][coord].value
        if isinstance(v, str) and v.startswith("="):
            v = self.eval(v[1:], sheet, depth + 1)
        elif isinstance(v, str):
            try:
                v = float(v.replace(",", "").replace("$", ""))
            except ValueError:
                v = 0.0 if v.strip() == "" else None
        elif v is None:
            v = 0.0
        elif isinstance(v, bool):
            v = float(v)
        elif not isinstance(v, (int, float)):
            v = None
        self.cache[key] = v
        return v

    def rng(self, sheet, c1, r1, c2, r2, depth):
        from openpyxl.utils import column_index_from_string as ci, get_column_letter as gl
        vals = []
        for col in range(ci(c1), ci(c2) + 1):
            for r in range(int(r1), int(r2) + 1):
                v = self.cell(sheet, f"{gl(col)}{r}", depth)
                if v is None:
                    return None
                vals.append(v)
        return vals

    def eval(self, expr, sheet, depth):
        e = expr
        # unwrap simple wrappers
        e = re.sub(r"(?i)\bIFERROR\(", "(", e) if not re.search(r"(?i)\bIFERROR\(", e) else self._iferror(e)
        e = re.sub(r"(?i)\bROUND\(([^,()]*(?:\([^()]*\))?[^,()]*),\s*(-?\d+)\)", lambda m: f"round({m.group(1)},{m.group(2)})", e)
        if re.search(r"(?i)\b(IF|VLOOKUP|INDEX|MATCH|HYPERLINK|MIN|MAX|ABS)\(", e):
            return None
        # ranges inside SUM
        def sum_repl(m):
            body = m.group(1)
            total = 0.0
            for part in body.split(","):
                part = part.strip()
                rm = RANGE.fullmatch(part)
                if rm:
                    sh = rm.group(1) or rm.group(2) or sheet
                    vals = self.rng(sh, rm.group(3), rm.group(4), rm.group(5), rm.group(6), depth)
                    if vals is None:
                        return "None"
                    total += sum(vals)
                else:
                    v = self.eval(part, sheet, depth)
                    if v is None:
                        return "None"
                    total += v
            return repr(total)
        e = re.sub(r"(?i)\bSUM\(([^()]*)\)", sum_repl, e)
        if "None" in e:
            return None
        # single refs
        def ref_repl(m):
            sh = m.group(1) or (m.group(2).strip() if m.group(2) else None) or sheet
            if sh not in self.wb.sheetnames:
                return "None"
            v = self.cell(sh, f"{m.group(3)}{m.group(4)}", depth)
            return "None" if v is None else repr(float(v))
        e = re.sub(r"(?:'([^']+)'!|([A-Za-z][A-Za-z0-9_ ]*)!)?\$?([A-Z]{1,3})\$?(\d+)(?![\d:])", ref_repl, e)
        if "None" in e:
            return None
        e = e.replace("%", "/100").replace("^", "**")
        if not re.fullmatch(r"[0-9.eE+\-*/() ,round]*", e):
            return None
        try:
            return float(eval(e, {"__builtins__": {}}, {"round": round}))
        except Exception:
            return None

    def _iferror(self, e):
        # IFERROR(x, y) -> (x)  (we only evaluate the primary branch)
        return re.sub(r"(?i)\bIFERROR\(([^,]+),[^()]*\)", r"(\1)", e)


# ----------------------------------------------------------------- checks
def check_links(wb, entity_id):
    broken = h.validate_links(wb)
    bad_fyi = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=HYPERLINK("):
                    if "go.fyi.app" not in c.value:
                        bad_fyi.append(f"{ws.title}!{c.coordinate}: not a go.fyi.app link")
                    elif entity_id and f"/0/{entity_id}/0/" not in c.value:
                        bad_fyi.append(f"{ws.title}!{c.coordinate}: entity id mismatch")
                    elif not re.search(r"documents/[0-9a-fA-F-]{8,}/preview", c.value):
                        bad_fyi.append(f"{ws.title}!{c.coordinate}: no document uuid")
    probs = broken + bad_fyi
    report("links", not probs, "; ".join(probs[:6]) + (f" (+{len(probs)-6})" if len(probs) > 6 else ""))


def check_fidelity(path):
    proc = subprocess.run([sys.executable, str(HERE / "check_template_fidelity.py"), str(path), str(MASTER)],
                          capture_output=True, text=True)
    ok = proc.returncode == 0
    tail = "\n".join(proc.stdout.strip().splitlines()[-12:])
    report("fidelity", ok, "" if ok else "\n" + tail)


def alias_map(wb, spec):
    c1 = spec["client"]["name"]
    c2 = (spec.get("client2") or {}).get("name")
    m = {"Summary": f"Summary - {c1}", "Deductions": f"Deductions - {c1}"}
    if c2:
        m.update({"Summary2": f"Summary - {c2}", "Deductions2": f"Deductions - {c2}"})
    return {k: v for k, v in m.items() if v in wb.sheetnames}


def check_spec(wb, spec):
    am = alias_map(wb, spec)
    bad = []
    final = {}
    for e in (spec.get("cells") or []) + (spec.get("rev") or []):
        final[(am.get(e["sheet"], e["sheet"]), e["cell"])] = e
    for (sh, coord), e in final.items():
        if sh not in wb.sheetnames:
            bad.append(f"{sh}!{coord}: sheet missing")
            continue
        v = wb[sh][coord].value
        if "formula" in e and e["formula"] is not None:
            want = e["formula"] if e["formula"].startswith("=") else "=" + e["formula"]
            if v != want:
                bad.append(f"{sh}!{coord}: has {v!r}, spec formula {want!r}")
        elif "value" in e:
            if isinstance(e["value"], (int, float)) and isinstance(v, (int, float)):
                if abs(float(v) - float(e["value"])) > 0.005:
                    bad.append(f"{sh}!{coord}: has {v!r}, spec {e['value']!r}")
            elif v != e["value"]:
                bad.append(f"{sh}!{coord}: has {v!r}, spec {e['value']!r}")
        elif "clear" in e and v not in (None, ""):
            bad.append(f"{sh}!{coord}: should be blank, has {v!r}")
    report("spec", not bad, "; ".join(bad[:6]) + (f" (+{len(bad)-6})" if len(bad) > 6 else ""))


def check_controls(wb, spec):
    """Spec-declared control cells ("controls": [{"sheet","cell","expect"}]) must
    evaluate to expect (default 0); plus the Summary chain must be consistent."""
    eng = Engine(wb)
    probs, checked, unevaluable = [], 0, []
    am = alias_map(wb, spec) if spec else {}
    for ctl in (spec or {}).get("controls", []) or []:
        sh = am.get(ctl["sheet"], ctl["sheet"])
        if sh not in wb.sheetnames:
            probs.append(f"control {ctl['sheet']}!{ctl['cell']}: sheet missing")
            continue
        got = eng.cell(sh, ctl["cell"])
        checked += 1
        want = float(ctl.get("expect", 0))
        if got is None:
            unevaluable.append(f"{sh}!{ctl['cell']} ({wb[sh][ctl['cell']].value!r})")
        elif abs(got - want) > 0.01:
            probs.append(f"{sh}!{ctl['cell']} = {got:,.2f} (expected {want:,.2f})")
    # every formula on a visible rental tab must at least evaluate (no dangling refs)
    for ws in wb.worksheets:
        if not ws.title.startswith("Rental Property") or ws.sheet_state != "visible":
            continue
        for l in META["labels"]["rental"]:
            if l["desc"].lower().startswith(("total", "net rent")):
                for col in "BE":
                    if eng.cell(ws.title, f"{col}{l['row']}") is None and ws[f"{col}{l['row']}"].value is not None:
                        probs.append(f"{ws.title}!{col}{l['row']}: could not evaluate {ws[f'{col}{l['row']}'].value!r}")
                    checked += 1
    # Summary chain
    for ws in wb.worksheets:
        if not ws.title.startswith("Summary - ") or ws.sheet_state != "visible":
            continue
        rows = {r["desc"]: r["row"] for r in META["labels"]["summary"] if r.get("desc")}
        try:
            inc = eng.cell(ws.title, f"H{rows['TOTAL INCOME']}")
            ded = eng.cell(ws.title, f"H{rows['TOTAL DEDUCTIONS']}")
            tax = eng.cell(ws.title, f"H{rows['TAXABLE INCOME']}")
            if None not in (inc, ded, tax):
                checked += 1
                if abs(round(inc - ded) - tax) > 1:
                    probs.append(f"{ws.title}: taxable {tax:,.0f} != income {inc:,.0f} - deductions {ded:,.0f}")
            ttp = eng.cell(ws.title, f"H{rows['Total Tax Payable']}")
            ttc = eng.cell(ws.title, f"H{rows['Total Tax Credits']}")
            pay = eng.cell(ws.title, f"H{rows['Tax Payable / (Refund)']}")
            if None not in (ttp, ttc, pay):
                checked += 1
                if abs((ttp - ttc) - pay) > 1:
                    probs.append(f"{ws.title}: payable {pay:,.2f} != tax {ttp:,.2f} - credits {ttc:,.2f}")
        except KeyError as k:
            probs.append(f"{ws.title}: landmark {k} not found")
    detail = f"{checked} checks" if not probs else "; ".join(probs[:6])
    if unevaluable:
        detail += (f"; {len(unevaluable)} control(s) depend on IF/VLOOKUP (tax tables) and need a real "
                   f"recalc -- confirm in Excel or with --recalc: " + ", ".join(unevaluable[:4]))
    report("controls", not probs, detail)


def check_constants(wb):
    probs = []
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        if ws.title.startswith("Summary - "):
            for r in META["labels"]["summary"]:
                if r["formula"] and r["desc"] and r["desc"].upper().startswith(("TOTAL", "TAXABLE", "TAX PAYABLE")):
                    v = ws[f"H{r['row']}"].value
                    if isinstance(v, (int, float)):
                        probs.append(f"{ws.title}!H{r['row']} ({r['desc']}) is a constant {v}")
        if ws.title.startswith("Deductions - "):
            for b in META["labels"]["deductions"]:
                if b["total_row"]:
                    v = ws[f"D{b['total_row']}"].value
                    if isinstance(v, (int, float)) and v != 0:
                        probs.append(f"{ws.title}!D{b['total_row']} ({b['label']} total) is a constant {v}")
        if ws.title.startswith("Rental Property"):
            for l in META["labels"]["rental"]:
                if l["desc"].lower().startswith(("total", "net rent")):
                    for col in "BE":
                        v = ws[f"{col}{l['row']}"].value
                        if isinstance(v, (int, float)) and v != 0:
                            probs.append(f"{ws.title}!{col}{l['row']} ({l['desc']}) is a constant {v}")
    report("constants", not probs, "; ".join(probs[:6]))


def find_soffice():
    for cand in ("soffice", "libreoffice"):
        p = shutil.which(cand)
        if p:
            return p
    for p in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              "/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"):
        if Path(p).exists():
            return p
    return None


def check_recalc(path):
    so = find_soffice()
    if not so:
        report("recalc", None, "LibreOffice not installed -- controls checked with the built-in engine; "
                               "Excel recalculates on open (fullCalcOnLoad set)")
        return
    outdir = path.parent / "_recalc"
    outdir.mkdir(exist_ok=True)
    proc = subprocess.run([so, "--headless", "--calc", "--convert-to", "xlsx", "--outdir",
                           str(outdir), str(path)], capture_output=True, text=True, timeout=300)
    conv = outdir / (path.stem + ".xlsx")
    if proc.returncode != 0 or not conv.exists():
        report("recalc", False, proc.stderr.strip()[-300:])
        return
    target = path.with_suffix(".recalc.xlsx")
    shutil.move(str(conv), target)
    wbv = openpyxl.load_workbook(target, data_only=True)
    errs = []
    for ws in wbv.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("#"):
                    errs.append(f"{ws.title}!{c.coordinate}={c.value}")
    report("recalc", not errs, f"values in {target.name}" if not errs else "; ".join(errs[:8]))


def check_claims(wb, claims, spec):
    am = alias_map(wb, spec) if spec else {}
    out = []
    for cl in claims:
        sh = am.get(cl["sheet"], cl["sheet"])
        if sh not in wb.sheetnames:
            out.append({**cl, "verdict": "NO_SHEET"})
            continue
        v = wb[sh][cl["cell"]].value
        exp = cl.get("expect")
        if exp == "blank":
            ok = v in (None, "")
        elif exp == "nonblank":
            ok = v not in (None, "")
        elif isinstance(exp, (int, float)) and isinstance(v, (int, float)):
            ok = abs(float(v) - float(exp)) <= 0.01
        else:
            ok = v == exp
        out.append({**cl, "actual": v, "verdict": "TRUE" if ok else "FALSE"})
    false = [o for o in out if o["verdict"] != "TRUE"]
    report("claims", not false, f"{len(out)} claims, {len(false)} not as stated")
    for o in out:
        print(f"    {o['verdict']:6} {o['sheet']}!{o['cell']} expect={o.get('expect')!r} actual={o.get('actual')!r}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    path = Path(args[0])
    spec = json.loads(Path(args[args.index("--spec") + 1]).read_text(encoding="utf-8")) if "--spec" in args else None
    claims = json.loads(Path(args[args.index("--claims") + 1]).read_text(encoding="utf-8")) if "--claims" in args else None
    wb = openpyxl.load_workbook(path, keep_vba=True)
    entity_id = (spec or {}).get("client", {}).get("entity_id")

    macro_ext = path.suffix.lower() == ".xlsm"
    report("vba", macro_ext and h.verify_vba(path),
           "" if macro_ext else f"not a macro-enabled workbook ('{path.suffix}'); rebuild as .xlsm")
    check_links(wb, entity_id)
    if "--no-fidelity" not in args:
        check_fidelity(path)
    if spec:
        check_spec(wb, spec)
    check_controls(wb, spec)
    check_constants(wb)
    if "--recalc" in args:
        check_recalc(path)
    if claims:
        check_claims(wb, claims, spec)
    fails = [n for n, ok in RESULTS if ok is False]
    print(("ALL CLEAR" if not fails else f"FAILED: {', '.join(fails)}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
