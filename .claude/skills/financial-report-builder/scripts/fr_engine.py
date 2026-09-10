#!/usr/bin/env python3
"""
fr_engine.py - the "Xero ledger" behind the Financial Reports pack.

Given a list of accounts (code, name, type, report_code, cy, py) this module
derives everything the report pack needs, the same way Xero's report templates
derive a pack from account types + report codes:

  * Profit and Loss Statement sections and sub-totals
  * Balance Sheet lines (grouped by 3-segment report code) with note references
  * Movements in Equity (opening, profit, other movements, closing)
  * Notes to the Financial Statements (numbered, tiered by report code)
  * Depreciation schedule totals
  * A validation report (balance, roll-forward, ties, unmapped accounts)

Nothing in here knows about PDF layout - see render_pack.py for that.
The layout rules (labels, ordering, which code goes where) live in
assets/report-map.json so they can be edited without touching code.
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
# Whole-dollar source figures (a rounded PDF or workpaper) can leave footing differences of a few
# dollars; cents-level Xero/workpaper exports should reconcile to $0.  Differences inside this
# tolerance are reported as INFO (rounding), anything larger is a real error.
ROUNDING_TOL = 5.0
DEFAULT_MAP = SKILL_DIR / "assets" / "report-map.json"
DEFAULT_COA = SKILL_DIR / "assets" / "chart-of-accounts" / "company-default.csv"
DEFAULT_BOILERPLATE = SKILL_DIR / "assets" / "boilerplate.json"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def rnd(x: Any) -> int:
    """Round half away from zero to whole dollars (Xero report convention)."""
    if x is None or x == "":
        return 0
    x = float(x)
    if math.isnan(x):
        return 0
    return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)


def fmt(n: int | float | None) -> str:
    """Xero number format: 1,234 / (1,234) / '-' for nil."""
    n = rnd(n)
    if n == 0:
        return "-"
    s = f"{abs(n):,}"
    return f"({s})" if n < 0 else s


def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_map(path: str | Path | None = None) -> dict:
    return load_json(path or DEFAULT_MAP)


def load_boilerplate(path: str | Path | None = None) -> dict:
    return load_json(path or DEFAULT_BOILERPLATE)


def segs(code: str) -> list[str]:
    return [s for s in (code or "").split(".") if s]


def strip_code(label: str) -> tuple[str | None, str]:
    """'200 - Sales' -> ('200', 'Sales'); 'Sales' -> (None, 'Sales')."""
    m = re.match(r"^\s*([0-9][0-9A-Za-z\-/]{1,9})\s*[-:]\s+(.*\S)\s*$", label or "")
    if m:
        return m.group(1), m.group(2)
    return None, (label or "").strip()


# --------------------------------------------------------------------------- #
# chart of accounts + mapping
# --------------------------------------------------------------------------- #
@dataclass
class COA:
    by_code: dict[str, dict] = field(default_factory=dict)
    by_name: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "COA":
        coa = cls()
        p = Path(path or DEFAULT_COA)
        if not p.exists():
            return coa
        with open(p, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
                if not row.get("report_code"):
                    continue
                if row.get("code"):
                    coa.by_code[row["code"]] = row
                if row.get("name"):
                    coa.by_name[row["name"].lower()] = row
        return coa


# Keyword rules, applied top-down; first hit wins.  (regex, report_code, note)
# They only *refine* - the statement side (P&L vs BS, current vs non-current)
# comes from the Xero account type / section header, and a rule is only used
# when it is compatible with that side.
KEYWORD_RULES: list[tuple[str, str, str]] = [
    # ---- balance sheet: cash
    (r"cash (in|on) hand|petty cash|till float|undeposited", "ASS.CUR.CAS.OTH", "cash on hand"),
    (r"term deposit|short.?term deposit", "ASS.CUR.FIN", "term deposit shown as financial asset"),
    (r"\bbank\b|account\s*#|\*{3}\d|savings|saver|cheque|transaction acc|business acc|westpac|anz|nab|cba|commonwealth|macquarie|bankwest|st ?george|\bing\b|amex|mastercard|visa|credit card|paypal|stripe bal", "BANK", "bank / card account (side decides asset or liability)"),
    # ---- balance sheet: receivables & tax assets
    (r"accounts? receivable|trade debtors?|debtors?", "ASS.CUR.REC", "trade debtors"),
    (r"loan to|loans? - .*(director|shareholder|related|trust|pty)|loan.*receivable|amount owing from|related party receivable|intercompany rec", "ASS.CUR.REC", "loan receivable"),
    (r"deposit paid|bond paid|rental bond", "ASS.CUR.REC", "deposit/bond paid"),
    (r"prepay", "ASS.CUR.PRE", "prepayment"),
    (r"inventory|stock on hand|closing stock|trading stock", "ASS.CUR.INV.INV", "inventory"),
    (r"work in progress|\bwip\b", "ASS.CUR.INV.WIP", "WIP"),
    # ---- fixed assets (cost + accumulated depreciation, by class)
    (r"leasehold|fit.?out|improvements", "ASS.NCA.PPE.LEA", "leasehold improvements"),
    (r"land|building|property at", "ASS.NCA.PPE.LAN", "land & buildings"),
    (r"motor vehicle|vehicles?\b|\bcar\b|\bute\b|truck", "ASS.NCA.PPE.MOT", "motor vehicles"),
    (r"furniture|fixtures?|fittings", "ASS.NCA.PPE.FUR", "furniture & fixtures"),
    (r"office equip", "ASS.NCA.PPE.OFF", "office equipment"),
    (r"computer|laptop|it equip|software.*(cost|depn|deprec)", "ASS.NCA.PPE.COM", "computer equipment"),
    (r"low value pool|\blvp\b", "ASS.NCA.PPE.LVP", "low value pool"),
    (r"plant|equipment|machinery|tools", "ASS.NCA.PPE.PLA", "plant & equipment"),
    # ---- intangibles
    (r"goodwill", "ASS.NCA.INT.GOO", "goodwill"),
    (r"formation|establishment cost|borrowing cost", "ASS.NCA.INT.OTH", "formation/borrowing costs"),
    (r"trademark|brand|patent|licen[cs]e.*(asset|cost)|website.*(cost|asset)|intangible|bank guarantee", "ASS.NCA.INT.OTH", "other intangible"),
    (r"shares in|investment in|units in|managed fund|portfolio|crypto", "ASS.NCA.INV", "investment"),
    # ---- liabilities: tax
    (r"\bgst\b|goods and services tax", "LIA.CUR.TAX", "GST"),
    (r"payg ?w|payg withholding|withholding payable|payg - w", "LIA.CUR.TAX", "PAYG withholding"),
    (r"payg ?i|payg instal|instalment payable|installment", "LIA.CUR.TAX", "PAYG instalment"),
    (r"income tax payable|provision for (income )?tax|tax payable|ito payable|fbt payable|fringe benefits tax payable|ato integrated|integrated client|running balance|\bica\b|\bita\b", "LIA.CUR.TAX", "income tax / ATO account"),
    # ---- liabilities: personnel
    (r"superannuation payable|super payable|super clearing|superannuation liability|sgc payable", "LIA.CUR.EMP", "superannuation payable"),
    (r"wages payable|payroll (clearing|liabilit)|salaries payable|accrued wages|net pay|employee (reimb|deduct)|child support|payroll tax payable", "LIA.CUR.EMP", "payroll liability"),
    # ---- liabilities: provisions
    (r"provision for (annual|holiday|long service|employee|bonus|rent|make ?good|doubtful|warranty)|leave provision|holiday pay provision|annual leave|long service leave", "LIA.CUR.PRO", "provision"),
    # ---- liabilities: payables
    (r"accounts? payable|trade creditors?|creditors?|accrued expenses|accruals|sundry payable|client control|trust liabilit|revenue owned|unearned|income in advance|deposits held|customer deposits|clearing|suspense|rounding|historical adjustment", "LIA.CUR.PAY", "trade / other payable"),
    # ---- liabilities: loans
    (r"hire purchase|chattel|equipment finance|lease liabilit|\bhp\b", "LIA.NCA.FIN.SEC", "secured finance"),
    (r"loan|borrowings|mortgage|line of credit|overdraft|finance", "LIA.NCA.FIN.UNS", "loan (defaults to non-current unsecured)"),
    # ---- equity
    (r"dividend", "EQU.DIV", "dividends paid"),
    (r"current year earnings|current year profit|profit for the year|net income", "EQU.CYE", "current year earnings"),
    (r"retained (earnings|profits)|accumulated (losses|profits)", "EQU.RET", "retained earnings"),
    (r"share capital|paid.?up|ordinary shares|issued capital|contributed equity", "EQU.SHA", "share capital"),
    (r"reserve", "EQU.RES", "reserve"),
    (r"drawings", "EQU.DRA", "drawings"),
    (r"capital account|settled sum|trust capital|partner.*capital|beneficiar", "EQU.CAP", "capital / beneficiary account"),
    # ---- P&L: income
    (r"interest (received|income|earned)|bank interest", "REV.OTH", "interest received"),
    (r"dividends? (received|income)|distribution(s)? (received|income)|trust distribution", "REV.OTH", "dividends/distributions received"),
    (r"rent(al)? (received|income)|rent income", "REV.OTH", "rent received"),
    (r"fbt (employee )?contribution|employee contribution", "REV.OTH", "FBT employee contribution"),
    (r"gain on|profit on (sale|disposal)|currency gain|forex gain|exchange gain", "REV.OTH", "gains"),
    (r"grant|subsid|cash ?flow boost|jobkeeper|refund|other income|sundry income|recover|reimburse|overrides?|rebate|commission(s)? (received|collected|income)?$", "REV.OTH", "other income"),
    (r"sales|revenue|fees? (collected|income|received)?|income|commission|consulting|services|turnover|takings|charges", "REV.TRA", "trading income"),
    # ---- P&L: cost of sales
    (r"opening stock|closing stock|purchases|cost of (goods|sales)|direct (cost|labour|wages|material)|subcontract|freight in|materials|stock adjust|cogs", "EXP.COS", "cost of sales"),
    # ---- P&L: tax & dividends
    (r"income tax( expense)?$|income tax expense|tax expense|company tax", "EXP.TAX", "income tax expense"),
]

SIDE_OF = {
    "REV": "pl", "EXP": "pl",
    "ASS": "bs", "LIA": "bs", "EQU": "bs",
}

# Xero section headers (as they appear in P&L / BS exports) -> Xero account type
SECTION_TO_TYPE = {
    "trading income": "Revenue", "income": "Revenue", "revenue": "Revenue", "sales": "Revenue",
    "cost of sales": "Direct Costs", "less cost of sales": "Direct Costs", "cost of goods sold": "Direct Costs",
    "other income": "Other Income", "plus other income": "Other Income",
    "operating expenses": "Expense", "less operating expenses": "Expense", "expenses": "Expense",
    "bank": "Bank", "current assets": "Current Asset", "inventory": "Inventory", "prepayments": "Prepayment",
    "fixed assets": "Fixed Asset", "non-current assets": "Non-current Asset", "non current assets": "Non-current Asset",
    "current liabilities": "Current Liability", "liabilities": "Liability",
    "non-current liabilities": "Non-current Liability", "non current liabilities": "Non-current Liability",
    "equity": "Equity",
}

TYPE_SIDE = {
    "Revenue": "pl", "Sales": "pl", "Other Income": "pl", "Direct Costs": "pl", "Expense": "pl",
    "Overheads": "pl", "Depreciation": "pl",
    "Bank": "bs", "Current Asset": "bs", "Inventory": "bs", "Prepayment": "bs", "Fixed Asset": "bs",
    "Non-current Asset": "bs", "Current Liability": "bs", "Liability": "bs", "Non-current Liability": "bs",
    "Equity": "bs",
}


def infer_report_code(name: str, acct_type: str | None, coa: COA, rmap: dict, code: str | None = None,
                      balance_hint: float | None = None) -> tuple[str, str, str]:
    """
    Returns (report_code, confidence, reason).
    confidence: 'coa' (explicit chart), 'rule' (keyword rule), 'type' (type default), 'none'.
    """
    # 1. explicit chart of accounts match (by code, then by name)
    row = None
    if code and code in coa.by_code:
        row = coa.by_code[code]
    elif name and name.lower() in coa.by_name:
        row = coa.by_name[name.lower()]
    if row:
        return row["report_code"], "coa", f"chart of accounts ({row.get('code') or 'name match'})"

    lname = (name or "").lower()
    side = TYPE_SIDE.get(acct_type or "", None)
    type_default = rmap["type_defaults"].get(acct_type or "", None)

    # 2. keyword rules compatible with the side we know
    for pattern, rcode, why in KEYWORD_RULES:
        if not re.search(pattern, lname):
            continue
        if rcode == "BANK":
            # a bank/card account: asset if debit balance (or Bank type), liability if credit card
            if acct_type in ("Current Liability", "Liability") or re.search(r"credit card|mastercard|visa|amex", lname):
                return "LIA.CUR.PAY", "rule", f"{why} -> card/overdraft shown in payables"
            return "ASS.CUR.CAS.BAN", "rule", why
        rside = SIDE_OF.get(segs(rcode)[0])
        if side and rside != side:
            continue  # e.g. 'Depreciation' expense must not map to the PPE asset rule
        # keep current/non-current from the type when the type says so
        if acct_type == "Non-current Liability" and rcode.startswith("LIA.CUR.") and not rcode.startswith("LIA.CUR.TAX"):
            rcode = rcode.replace("LIA.CUR.", "LIA.NCA.", 1)
        if acct_type in ("Current Liability", "Liability") and rcode.startswith("LIA.NCA.FIN"):
            rcode = rcode.replace("LIA.NCA.", "LIA.CUR.", 1)
        if acct_type == "Non-current Asset" and rcode.startswith("ASS.CUR."):
            rcode = rcode.replace("ASS.CUR.", "ASS.NCA.", 1)
        if acct_type == "Fixed Asset" and not rcode.startswith("ASS.NCA.PPE"):
            rcode = rmap["type_defaults"]["Fixed Asset"]
        return rcode, "rule", why

    # 3. type default
    if type_default:
        return type_default, "type", f"Xero account type '{acct_type}' default"
    return "", "none", "no chart match, no keyword rule, no account type"


# --------------------------------------------------------------------------- #
# the pack builder
# --------------------------------------------------------------------------- #
class Pack:
    def __init__(self, data: dict, rmap: dict | None = None):
        self.src = data
        self.map = rmap or load_map(data.get("report_map"))
        self.entity = data["entity"]
        self.options = {
            "sort": "alpha",                  # alpha | source
            "cost_of_sales_label": "Cost of Sales",
            "keep_nil_accounts": False,
            "show_current_heading": True,
            "include_inventory_policy": None,  # None = auto (only when inventory exists)
            "depreciation_layout": None,       # simple | standard | register
            "report_order": None,
        }
        self.options.update(data.get("options") or {})
        self.accounts = [dict(a) for a in data.get("accounts", [])]
        self.extra_equity_movements = data.get("equity_movements") or []
        self.depreciation = data.get("depreciation")
        self.validation: list[dict] = []
        self._normalise_accounts()
        self.pnl = self._build_pnl()
        self.equity_lines = self._equity_lines()
        self.notes = self._build_notes()
        self.bs = self._build_bs()
        self.equity = self._build_equity_statement()
        self.depn = self._build_depreciation()
        self._validate()

    # ---- accounts ------------------------------------------------------- #
    def _normalise_accounts(self):
        for a in self.accounts:
            a["cy"] = float(a.get("cy") or 0)
            a["py"] = float(a.get("py") or 0)
            a["report_code"] = (a.get("report_code") or "").upper()
            a.setdefault("name", "")
            a["display_name"] = a.get("display_name") or a["name"]
            if not a["report_code"]:
                self.validation.append({"level": "error", "check": "mapping",
                                        "detail": f"Account '{a['name']}' has no report code - map it before rendering."})
        if not self.options["keep_nil_accounts"]:
            self.accounts = [a for a in self.accounts if rnd(a["cy"]) != 0 or rnd(a["py"]) != 0 or a.get("keep")]

    def _accts(self, prefix: str) -> list[dict]:
        rows = [a for a in self.accounts if a["report_code"] == prefix or a["report_code"].startswith(prefix + ".")]
        if self.options["sort"] == "alpha":
            rows.sort(key=lambda a: a["display_name"].lower())
        return rows

    @staticmethod
    def _sum(rows: list[dict]) -> dict:
        return {"cy": sum(r["cy"] for r in rows), "py": sum(r["py"] for r in rows)}

    # ---- profit and loss ---------------------------------------------- #
    def _build_pnl(self) -> dict:
        out = {"sections": [], "totals": {}}
        t: dict[str, dict] = {}
        for sec in self.map["pnl_sections"]:
            key = sec["key"]
            if sec.get("computed"):
                if key == "gross":
                    val = {c: t["income"][c] - t["cos"][c] for c in ("cy", "py")}
                elif key == "total_income":
                    val = {c: t["gross"][c] + t["other"][c] for c in ("cy", "py")}
                elif key == "pbt":
                    val = {c: t["total_income"][c] - t["expenses"][c] for c in ("cy", "py")}
                elif key == "npat":
                    val = {c: t["pbt"][c] - t["tax"][c] for c in ("cy", "py")}
                elif key == "npat_div":
                    val = {c: t["npat"][c] - t["dividends"][c] for c in ("cy", "py")}
                else:
                    val = {"cy": 0, "py": 0}
                t[key] = val
                out["sections"].append({"key": key, "computed": True, "label": sec["label"], **val})
                continue
            rows = self._accts(sec["code"])
            total = self._sum(rows)
            t[key] = total
            heading = sec["heading"]
            total_label = sec["total"]
            if key == "cos":
                heading = self.options["cost_of_sales_label"] or heading
                total_label = sec.get("alt_headings", {}).get(heading, total_label)
            show = bool(rows) and not (sec.get("hide_if_nil") and total["cy"] == 0 and total["py"] == 0)
            out["sections"].append({
                "key": key, "computed": False, "heading": heading, "total_label": total_label,
                "lines": [{"label": r["display_name"], "cy": r["cy"], "py": r["py"], "code": r.get("code")} for r in rows],
                "show": show, **total,
            })
        out["totals"] = t
        return out

    # ---- equity helper -------------------------------------------------- #
    def _equity_lines(self) -> dict:
        ret = self._sum(self._accts("EQU.RET"))
        cye = self._accts("EQU.CYE")
        div = self._sum(self._accts("EQU.DIV"))
        npat = self.pnl["totals"]["npat"]
        if cye:
            cye_tot = self._sum(cye)
            for c in ("cy", "py"):
                if abs(cye_tot[c] - npat[c]) > 0.5:
                    self.validation.append({"level": "error", "check": "current_year_earnings",
                                            "detail": f"Current Year Earnings on the Balance Sheet ({c.upper()}: {fmt(cye_tot[c])}) does not equal Net Profit After Tax per the P&L ({fmt(npat[c])})."})
        else:
            cye_tot = dict(npat)
        return {
            "retained_prior": ret, "cye": cye_tot, "dividends": div,
            "retained_display": {c: ret[c] + cye_tot[c] - div[c] for c in ("cy", "py")},
            "share_capital": self._sum(self._accts("EQU.SHA")),
            "reserves": self._sum(self._accts("EQU.RES")),
            "drawings": self._sum(self._accts("EQU.DRA")),
            "capital": self._sum(self._accts("EQU.CAP")),
            "other": self._sum(self._accts("EQU.OTH")),
        }

    # ---- notes ---------------------------------------------------------- #
    def _note_key_for(self, code: str) -> str | None:
        s = segs(code)
        if len(s) < 3 or s[0] not in ("ASS", "LIA"):
            return None
        info = self._bs_line_info(code)
        return info["note"] if info else None

    def _bs_line_key(self, code: str) -> str | None:
        """4-segment override if report-map has one, else the 3-segment line."""
        s = segs(code)
        if len(s) >= 4 and ".".join(s[:4]) in self.map["bs_lines"]:
            return ".".join(s[:4])
        if len(s) >= 3 and ".".join(s[:3]) in self.map["bs_lines"]:
            return ".".join(s[:3])
        return None

    def _bs_line_info(self, code: str) -> dict | None:
        k = self._bs_line_key(code)
        return self.map["bs_lines"].get(k) if k else None

    def _build_notes(self) -> list[dict]:
        notes_cfg = self.map["notes"]
        by_note: dict[str, list[dict]] = {k: [] for k in self.map["notes_order"]}
        for a in self.accounts:
            k = self._note_key_for(a["report_code"])
            if k is None:
                if a["report_code"].startswith(("ASS", "LIA")):
                    self.validation.append({"level": "error", "check": "mapping",
                                            "detail": f"Account '{a['name']}' report code {a['report_code']} is not a Balance Sheet line in report-map.json."})
                continue
            by_note.setdefault(k, []).append(a)

        notes: list[dict] = []
        number = 2
        for key in self.map["notes_order"]:
            rows = by_note.get(key) or []
            if not any(rnd(r["cy"]) or rnd(r["py"]) for r in rows):
                continue
            cfg = notes_cfg[key]
            tiers = self._tier_rows(key, cfg, rows)
            total = self._sum(rows)
            notes.append({"key": key, "number": number, "title": cfg["title"], "total_label": cfg["total"],
                          "rows": tiers, **total})
            number += 1
        return notes

    def _tier_rows(self, key: str, cfg: dict, rows: list[dict]) -> list[dict]:
        """Turn accounts into display rows: heading / line / total tiers."""
        levels = cfg.get("levels", "flat")
        out: list[dict] = []

        def lines_for(rs: list[dict], indent: int) -> list[dict]:
            rs = sorted(rs, key=lambda a: a["display_name"].lower()) if self.options["sort"] == "alpha" else rs
            # cost lines before their accumulated depreciation, Xero style
            rs = sorted(rs, key=lambda a: 1 if re.search(r"accum|amortis|deprec", a["display_name"].lower()) else 0) if key in ("ppe", "intangibles") else rs
            return [{"kind": "line", "label": a["display_name"], "cy": a["cy"], "py": a["py"], "indent": indent} for a in rs]

        if levels == "flat":
            out += lines_for(rows, 1)
            return out

        if levels == "class":
            groups: OrderedDict[str, list[dict]] = OrderedDict()
            for label in cfg["classes"].values():
                groups[label] = []
            for a in rows:
                s = segs(a["report_code"])
                cls = s[3] if len(s) > 3 and s[3] in cfg["classes"] else cfg.get("default_class")
                groups[cfg["classes"][cls]].append(a)
            for label, rs in groups.items():
                if not rs:
                    continue
                out.append({"kind": "heading", "label": label, "indent": 1})
                out += lines_for(rs, 2)
                st = self._sum(rs)
                out.append({"kind": "total", "label": f"Total {label}", "indent": 2, **st})
            return out

        if levels == "cur_ncu":
            if not self.options["show_current_heading"]:
                out += lines_for(rows, 1)
                return out
            for seg, label in (("CUR", cfg["cur_label"]), ("NCA", cfg["ncu_label"])):
                rs = [a for a in rows if segs(a["report_code"])[1] == seg]
                if not rs:
                    continue
                out.append({"kind": "heading", "label": label, "indent": 1})
                l2 = cfg.get("level2") or {}
                sub: OrderedDict[str, list[dict]] = OrderedDict()
                for a in rs:
                    s = segs(a["report_code"])
                    sub.setdefault(l2.get(s[3]) if len(s) > 3 else None, []).append(a)
                for l2label, l2rows in sub.items():
                    if l2label:
                        out.append({"kind": "heading", "label": l2label, "indent": 2})
                        out += lines_for(l2rows, 3)
                        out.append({"kind": "total", "label": f"Total {l2label}", "indent": 3, **self._sum(l2rows)})
                    else:
                        out += lines_for(l2rows, 2)
                out.append({"kind": "total", "label": f"Total {label}", "indent": 2, **self._sum(rs)})
            return out

        if levels == "payables":
            order = cfg["subgroup_order"]
            groups: OrderedDict[str, list[dict]] = OrderedDict((k, []) for k in order)
            for a in rows:
                code = a["report_code"]
                match = None
                for k in sorted(order, key=len, reverse=True):  # longest prefix first
                    if code == k or code.startswith(k + "."):
                        match = k
                        break
                groups[match or "LIA.CUR.PAY"].append(a)
            for k, rs in groups.items():
                if not rs:
                    continue
                label = cfg["subgroups"][k]
                out.append({"kind": "heading", "label": label, "indent": 1})
                out += lines_for(rs, 2)
                out.append({"kind": "total", "label": f"Total {label}", "indent": 2, **self._sum(rs)})
            return out

        out += lines_for(rows, 1)
        return out

    # ---- balance sheet -------------------------------------------------- #
    def _build_bs(self) -> dict:
        note_no = {n["key"]: n["number"] for n in self.notes}
        cfg = self.map["balance_sheet"]

        def lines(prefix: str) -> list[dict]:
            groups: OrderedDict[str, list[dict]] = OrderedDict()
            for a in self.accounts:
                s = segs(a["report_code"])
                if len(s) >= 3 and ".".join(s[:2]) == prefix:
                    k = self._bs_line_key(a["report_code"])
                    if k:
                        groups.setdefault(k, []).append(a)
            # keep report-map order
            ordered = [k for k in self.map["bs_lines"] if k in groups]
            out = []
            for k in ordered:
                info = self.map["bs_lines"][k]
                tot = self._sum(groups[k])
                if rnd(tot["cy"]) == 0 and rnd(tot["py"]) == 0:
                    continue
                # merge same-label lines (e.g. two codes both labelled Financial Liabilities)
                existing = next((o for o in out if o["label"] == info["label"]), None)
                note = note_no.get(info.get("note"))
                if existing:
                    existing["cy"] += tot["cy"]; existing["py"] += tot["py"]
                    if note and str(note) not in existing["note"].split(", "):
                        existing["note"] = ", ".join(filter(None, [existing["note"], str(note)]))
                else:
                    out.append({"label": info["label"], "note": str(note) if note else "", **tot})
            return out

        assets_cur, assets_ncu = lines("ASS.CUR"), lines("ASS.NCA")
        liab_cur, liab_ncu = lines("LIA.CUR"), lines("LIA.NCA")
        ta = {c: sum(x[c] for x in assets_cur + assets_ncu) for c in ("cy", "py")}
        tl = {c: sum(x[c] for x in liab_cur + liab_ncu) for c in ("cy", "py")}
        na = {c: ta[c] - tl[c] for c in ("cy", "py")}

        eq = self.equity_lines
        equity_rows = []
        for key, lab in (("retained_display", "Retained Earnings"), ("reserves", "Reserves"),
                         ("share_capital", "Share Capital"), ("capital", "Capital Accounts"),
                         ("drawings", "Drawings"), ("other", "Other Equity")):
            v = eq[key]
            if rnd(v["cy"]) or rnd(v["py"]) or key == "retained_display":
                equity_rows.append({"label": lab, "note": "", **v})
        te = {c: sum(x[c] for x in equity_rows) for c in ("cy", "py")}
        return {
            "assets": {"current": assets_cur, "non_current": assets_ncu, "total": ta},
            "liabilities": {"current": liab_cur, "non_current": liab_ncu, "total": tl},
            "net_assets": na, "equity": {"rows": equity_rows, "total": te}, "cfg": cfg,
        }

    # ---- movements in equity -------------------------------------------- #
    def _build_equity_statement(self) -> dict:
        eq = self.equity_lines
        te = self.bs["equity"]["total"]
        profit = self.pnl["totals"]["npat_div"]
        moves: list[dict] = [{"label": self.map["equity_statement"]["profit"], "cy": profit["cy"], "py": profit["py"]}]
        # movements derived from the balance sheet (CY only - PY needs prior-prior data)
        for key, label in (("share_capital", "Share Capital"), ("reserves", "Reserves"),
                           ("capital", "Capital Accounts"), ("drawings", "Drawings"), ("other", "Other Equity")):
            delta = eq[key]["cy"] - eq[key]["py"]
            if rnd(delta):
                names = [a["display_name"] for a in self._accts("EQU." + {"share_capital": "SHA", "reserves": "RES", "capital": "CAP", "drawings": "DRA", "other": "OTH"}[key])]
                moves.append({"label": names[0] if len(names) == 1 and key in ("reserves", "other") else label, "cy": delta, "py": 0, "derived": True})
        # retained earnings roll-forward residual (direct postings to RE)
        expected_ret_cy = eq["retained_prior"]["py"] + eq["cye"]["py"] - eq["dividends"]["py"]
        residual = eq["retained_prior"]["cy"] - expected_ret_cy
        if 0.5 < abs(residual) <= ROUNDING_TOL:
            self.validation.append({"level": "info", "check": "retained_earnings_rollforward",
                                    "detail": f"Retained Earnings roll-forward differs by {fmt(residual)} - rounding of whole-dollar source figures; no movement line added."})
        elif abs(residual) > ROUNDING_TOL:
            moves.append({"label": "Retained Earnings", "cy": residual, "py": 0, "derived": True})
            self.validation.append({"level": "warning", "check": "retained_earnings_rollforward",
                                    "detail": f"Retained Earnings moved by {fmt(residual)} beyond profit and dividends (direct posting / prior period adjustment). It is shown as a 'Retained Earnings' movement - confirm the reason and label."})
        # user-supplied movements (e.g. PY share issue) - merge by label
        for m in self.extra_equity_movements:
            ex = next((x for x in moves if x["label"] == m.get("label")), None)
            if ex:
                ex["py"] = rnd(m.get("py", ex["py"])) if "py" in m else ex["py"]
                if "cy" in m:
                    ex["cy"] = rnd(m["cy"])
            else:
                moves.append({"label": m["label"], "cy": rnd(m.get("cy", 0)), "py": rnd(m.get("py", 0))})
        moves = [m for m in moves if rnd(m["cy"]) or rnd(m["py"]) or m["label"] == self.map["equity_statement"]["profit"]]
        total_inc = {c: sum(m[c] for m in moves) for c in ("cy", "py")}
        opening = {"cy": te["py"], "py": te["py"] - total_inc["py"]}
        if "opening_py" in self.src.get("equity", {}):
            opening["py"] = float(self.src["equity"]["opening_py"])
            diff = rnd(opening["py"] + total_inc["py"] - te["py"])
            if diff and abs(diff) <= ROUNDING_TOL:
                self.validation.append({"level": "info", "check": "equity_opening_py",
                                        "detail": f"Prior-year opening equity rolls to PY closing equity within rounding ({fmt(diff)})."})
            elif diff:
                self.validation.append({"level": "warning", "check": "equity_opening_py",
                                        "detail": f"Prior-year opening equity supplied ({fmt(opening['py'])}) plus PY movements does not roll to PY closing equity ({fmt(te['py'])}); difference {fmt(diff)}. Add the missing PY movement to equity_movements."})
        else:
            self.validation.append({"level": "info", "check": "equity_opening_py",
                                    "detail": "Prior-year opening equity was derived as PY closing equity less PY profit and supplied PY movements. Check it against the prior-year report's Movements in Equity."})
        return {"opening": opening, "movements": moves, "total_increases": total_inc, "total": te}

    # ---- depreciation --------------------------------------------------- #
    def _build_depreciation(self) -> dict | None:
        d = self.depreciation
        if not d or not d.get("groups"):
            return None
        num_cols = ["cost", "opening_accum", "opening_value", "purchases", "disposals", "depreciation",
                    "closing_accum", "closing_value"]
        groups = []
        grand = {k: 0 for k in num_cols}
        for g in d["groups"]:
            assets = []
            gt = {k: 0 for k in num_cols}
            for a in g.get("assets", []):
                row = dict(a)
                for k in num_cols:
                    row[k] = float(a.get(k) or 0)
                    gt[k] += row[k]
                if "closing_value" not in a and ("opening_value" in a or "purchases" in a):
                    row["closing_value"] = row["opening_value"] + row["purchases"] - row["disposals"] - row["depreciation"]
                    gt["closing_value"] += row["closing_value"]
                assets.append(row)
            for k in num_cols:
                grand[k] += gt[k]
            groups.append({"name": g["name"], "assets": assets, "totals": gt})
        layout = d.get("layout") or self.options["depreciation_layout"] or "simple"
        return {"layout": layout, "title": d.get("title") or ("Accounting Depreciation Schedule" if layout == "simple" else "Depreciation Schedule"),
                "groups": groups, "totals": grand}

    # ---- validation ----------------------------------------------------- #
    def _validate(self):
        v = self.validation
        for c in ("cy", "py"):
            na, te = self.bs["net_assets"][c], self.bs["equity"]["total"][c]
            if abs(na - te) > ROUNDING_TOL:
                v.append({"level": "error", "check": "balance_sheet_balances",
                          "detail": f"{c.upper()}: Net Assets {fmt(na)} does not equal Total Equity {fmt(te)} (difference {fmt(na - te)}). Check the P&L ties to Current Year Earnings, and dividends/RE coding."})
            elif abs(na - te) > 0.005:
                v.append({"level": "info", "check": "balance_sheet_balances",
                          "detail": f"{c.upper()}: Net Assets and Total Equity differ by {fmt(na - te)} - within rounding tolerance for whole-dollar source figures (Xero shows the same small footing differences)."})
        # PY comparatives present?
        if all(rnd(a["py"]) == 0 for a in self.accounts):
            v.append({"level": "warning", "check": "comparatives", "detail": "No prior-year figures found - the pack will print '-' in the comparative column."})
        # depreciation ties
        if self.depn:
            pl_depn = sum(l["cy"] for s in self.pnl["sections"] if not s.get("computed") for l in s["lines"]
                          if re.search(r"deprec|amortis|write.?off", l["label"].lower()))
            if abs(pl_depn - self.depn["totals"]["depreciation"]) > ROUNDING_TOL:
                v.append({"level": "warning", "check": "depreciation_ties_pl",
                          "detail": f"Depreciation schedule total {fmt(self.depn['totals']['depreciation'])} vs P&L depreciation/amortisation/write-off lines {fmt(pl_depn)}."})
            ppe = next((n for n in self.notes if n["key"] == "ppe"), None)
            if ppe and abs(ppe["cy"] - self.depn["totals"]["closing_value"]) > ROUNDING_TOL:
                v.append({"level": "warning", "check": "depreciation_ties_ppe",
                          "detail": f"Depreciation schedule closing value {fmt(self.depn['totals']['closing_value'])} vs Property, Plant and Equipment note {fmt(ppe['cy'])}. Land or intangibles may explain the gap."})
        # GST in refund position
        for a in self._accts("LIA.CUR.TAX"):
            if rnd(a["cy"]) < 0 and "gst" in a["name"].lower():
                v.append({"level": "info", "check": "gst_refund",
                          "detail": f"'{a['name']}' is a debit balance {fmt(a['cy'])} - printed as a negative liability, the Xero convention. Reclassify to Receivables only if the firm template requires it."})
        # income tax expense with no tax liability / vice versa
        tax_exp = rnd(self.pnl["totals"]["tax"]["cy"])
        tax_liab = [a for a in self._accts("LIA.CUR.TAX") if re.search(r"income tax|provision for", a["name"].lower())]
        if tax_exp and not tax_liab:
            v.append({"level": "info", "check": "income_tax", "detail": "Income tax expense is booked but no Income Tax Payable / Provision account was found on the Balance Sheet."})
        # entity fields
        for f_ in ("name", "abn", "fy_end"):
            if not self.entity.get(f_):
                v.append({"level": "error", "check": "entity", "detail": f"entity.{f_} is missing."})
        if not self.entity.get("directors"):
            v.append({"level": "warning", "check": "entity", "detail": "No directors listed - the Directors Declaration will have no signature blocks."})

    # ---- output --------------------------------------------------------- #
    def has_errors(self) -> bool:
        return any(x["level"] == "error" for x in self.validation)

    def validation_markdown(self) -> str:
        if not self.validation:
            return "All checks passed."
        order = {"error": 0, "warning": 1, "info": 2}
        rows = sorted(self.validation, key=lambda x: order[x["level"]])
        out = ["| Level | Check | Detail |", "|---|---|---|"]
        for r in rows:
            out.append(f"| {r['level'].upper()} | {r['check']} | {r['detail']} |")
        return "\n".join(out)

    def summary(self) -> dict:
        t = self.pnl["totals"]
        return {
            "entity": self.entity.get("name"),
            "fy_end": self.entity.get("fy_end"),
            "total_income": t["total_income"], "expenses": t["expenses"], "npat": t["npat"],
            "dividends": t["dividends"], "npat_after_div": t["npat_div"],
            "total_assets": self.bs["assets"]["total"], "total_liabilities": self.bs["liabilities"]["total"],
            "net_assets": self.bs["net_assets"], "total_equity": self.bs["equity"]["total"],
            "notes": [(n["number"], n["title"]) for n in self.notes],
            "errors": sum(1 for x in self.validation if x["level"] == "error"),
            "_note": "amounts are unrounded; fmt() rounds at display",
            "warnings": sum(1 for x in self.validation if x["level"] == "warning"),
        }


def fy_labels(entity: dict) -> dict:
    """'2026-06-30' -> {'cy': '2026', 'py': '2025', 'long': '30 June 2026', 'long_py': '30 June 2025'}"""
    import datetime as dt
    end = dt.date.fromisoformat(entity["fy_end"])
    try:
        py_end = end.replace(year=end.year - 1)
    except ValueError:  # 29 Feb
        py_end = end.replace(year=end.year - 1, day=28)
    return {
        "cy": str(end.year), "py": str(py_end.year),
        "long": f"{end.day} {end.strftime('%B %Y')}", "long_py": f"{py_end.day} {py_end.strftime('%B %Y')}",
        "period": entity.get("period_label") or f"For the year ended {end.day} {end.strftime('%B %Y')}",
        "as_at": f"As at {end.day} {end.strftime('%B %Y')}",
        "col_cy": f"{end.day} {end.strftime('%B %Y')}".upper(), "col_py": f"{py_end.day} {py_end.strftime('%B %Y')}".upper(),
    }


if __name__ == "__main__":  # quick smoke test:  python fr_engine.py pack.json
    import sys
    p = Pack(load_json(sys.argv[1]))
    print(json.dumps(p.summary(), indent=2, default=str))
    print(p.validation_markdown())
