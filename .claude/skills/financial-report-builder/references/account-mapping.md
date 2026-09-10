# Account mapping reference

Every account gets **one report code**. The code decides where the account
prints in each report of the pack. This file is the lookup; the machine copy is
`assets/report-map.json` (labels, order) and the keyword rules in
`scripts/fr_engine.py`.

## 1. Report code hierarchy

Segment 1 = statement side, 2 = current/non-current, 3 = Balance Sheet line /
P&L section, 4 = class or sub-heading inside the Note.

### Profit and Loss Statement

| Report code | P&L section printed | Total line | Typical accounts |
|---|---|---|---|
| `REV.TRA` | **Income** | Total Income | Sales, Sale of goods, Commissions collected, Fees, "Test" (Complex), BAC Wage Subsidies (Frontier) |
| `EXP.COS` | **Cost of Sales** (or "Cost of Goods Sold" via `options.cost_of_sales_label`) | Total Cost of Sales | Opening stock, Purchases, Closing stock (credit), Consultant, Therapy Resource, Assessment Program |
| *(computed)* | **Gross Profit from Trading** | | Income less Cost of Sales - always printed |
| `REV.OTH` | **Other Income** | Total Other Income | Interest received, FBT employee contribution, Consulting Fees Collected (Wisdom), Overrides, Other income & refunds, dividends/distributions received, gains |
| *(computed)* | **Total Income** | | Gross Profit + Other Income |
| `EXP.OPE` | **Expenses** | Total Expenses | every operating expense incl. Depreciation, Amortisation, Instant Write-Off Assets, Interest Expense, PSI Attribution, Realised/Unrealised Currency Gains, Bad Debts, Donation, Fines |
| *(computed)* | **Profit/(Loss) before Taxation** | | |
| `EXP.TAX` | **Income Tax Expense** (hidden when nil) | Total Income Tax Expense | Income Tax Expense, Income tax |
| *(computed)* | **Net Profit After Tax** | | |
| `EQU.DIV` | **Dividend Paid** (hidden when nil) | Total Dividend Paid | Fully Franked Dividends Paid, Unfranked Dividends Paid |
| *(computed)* | **Net Profit After Tax & Dividend** | | = "Profit for the Period" in Movements in Equity |

### Balance Sheet + Notes

| Report code | BS section | BS line label | Note | Sub-heading inside the Note |
|---|---|---|---|---|
| `ASS.CUR.CAS.BAN` | Current Assets | Cash and Cash Equivalents | Cash and Cash Equivalents | Bank Accounts |
| `ASS.CUR.CAS.OTH` | Current Assets | Cash and Cash Equivalents | Cash and Cash Equivalents | Other Cash Items (cash in hand, petty cash; Capstone put its CBA account here) |
| `ASS.CUR.CAS.TRM` | Current Assets | Cash and Cash Equivalents | Cash and Cash Equivalents | Term Deposits |
| `ASS.CUR.REC` | Current Assets | Receivables | Receivables | Current (heading suppressed with `show_current_heading:false` - Capstone) |
| `ASS.NCA.REC` | Non-Current Assets | Receivables | Receivables | Non Current |
| `ASS.CUR.INV.INV` | Current Assets | Inventory | Inventory | Inventories |
| `ASS.CUR.INV.WIP` | Current Assets | Inventory | Inventory | Work in Progress |
| `ASS.CUR.PRE` | Current Assets | Prepayments | Prepayments | *(flat)* |
| `ASS.CUR.FIN` | Current Assets | Financial Assets | Financial Assets | Current (Frontier's bank-guarantee term deposit) |
| `ASS.NCA.FIN` | Non-Current Assets | Financial Assets | Financial Assets | Non Current |
| `ASS.CUR.OTH` / `ASS.NCA.OTH` | Current / Non-Current | Other Current / Non-Current Assets | Other Assets | Current / Non Current |
| `ASS.NCA.PPE.LAN` | Non-Current Assets | Property, Plant and Equipment | Property Plant and Equipment | Land and Buildings |
| `ASS.NCA.PPE.LEA` | " | " | " | Leasehold Improvements |
| `ASS.NCA.PPE.PLA` | " | " | " | Plant and Equipment |
| `ASS.NCA.PPE.MOT` | " | " | " | Motor Vehicles |
| `ASS.NCA.PPE.FUR` | " | " | " | Furniture & Fixtures |
| `ASS.NCA.PPE.OFF` | " | " | " | Office Equipment |
| `ASS.NCA.PPE.COM` | " | " | " | Computer Equipment |
| `ASS.NCA.PPE.LVP` | " | " | " | Low Value Pool |
| `ASS.NCA.INT.GOO` | Non-Current Assets | Intangibles | Intangibles | Goodwill |
| `ASS.NCA.INT.OTH` | Non-Current Assets | Intangibles | Intangibles | Other Intangible Assets (formation costs + amortisation, trademarks, Padel's bank guarantees) |
| `ASS.NCA.INV` | Non-Current Assets | Investments | Investments | *(flat)* |
| `LIA.CUR.PAY` | Current Liabilities | Payables | Payables | Current (trade creditors, credit cards, accruals, client control account, ATO ICA when a liability) |
| `LIA.CUR.PAY.FIN` | Current Liabilities | **Financial Liabilities** | Payables | Financial Liabilities (Wisdom IT: director loan inside the Payables note) |
| `LIA.CUR.EMP` | Current Liabilities | Personnel-related items | Payables | Personnel-related items (super payable, wages payable) |
| `LIA.CUR.TAX` | Current Liabilities | Taxation | Payables | Tax liabilities (GST, PAYG W, PAYG I, Income tax payable) |
| `LIA.CUR.PRO` | Current Liabilities | Provisions | Provisions | *(flat)* |
| `LIA.CUR.FIN` | Current Liabilities | Financial Liabilities | Financial Liabilities | Current (Frontier: Loans - Related party) |
| `LIA.NCA.FIN.UNS` | Non-Current Liabilities | Financial Liabilities | Financial Liabilities | Non Current › Unsecured (director / family-trust loans - Padel, Complex) |
| `LIA.NCA.FIN.SEC` | Non-Current Liabilities | Financial Liabilities | Financial Liabilities | Non Current › Secured (bank loans, HP, chattel mortgage) |
| `LIA.NCA.SHA` | Non-Current Liabilities | Financial Liabilities | **Loan from Shareholders/Associates** | *(flat)* (Capstone) |
| `LIA.NCA.PRO` | Non-Current Liabilities | Provisions | Provisions | *(flat)* (long service leave) |
| `LIA.NCA.PAY` | Non-Current Liabilities | Payables | Payables | Non Current |
| `EQU.SHA` | Equity | Share Capital | - | - |
| `EQU.RES` | Equity | Reserves | - | - |
| `EQU.RET` | Equity | Retained Earnings (combined with CYE and DIV) | - | - |
| `EQU.CYE` | Equity | *(folded into Retained Earnings)* | - | must equal NPAT |
| `EQU.DIV` | Equity | *(folded into Retained Earnings; printed in the P&L)* | - | - |
| `EQU.DRA` / `EQU.CAP` / `EQU.OTH` | Equity | Drawings / Capital Accounts / Other Equity | - | non-company entities |

## 2. Xero account type → default code

Used when an account is not in the chart and no keyword rule fires.
`build_pack.py` reads the type from the **section header** the line sits under
in a Xero export (Trading Income, Cost of Sales, Other Income, Operating
Expenses; Bank, Current Assets, Inventory, Fixed Assets, Non-current Assets,
Current Liabilities, Non-current Liabilities, Equity).

| Xero type | Default report code |
|---|---|
| Revenue / Sales | `REV.TRA` |
| Other Income | `REV.OTH` |
| Direct Costs | `EXP.COS` |
| Expense / Overheads / Depreciation | `EXP.OPE` |
| Bank | `ASS.CUR.CAS.BAN` |
| Current Asset | `ASS.CUR.REC` |
| Inventory | `ASS.CUR.INV.INV` |
| Prepayment | `ASS.CUR.PRE` |
| Fixed Asset | `ASS.NCA.PPE.PLA` |
| Non-current Asset | `ASS.NCA.OTH` |
| Current Liability / Liability | `LIA.CUR.PAY` |
| Non-current Liability | `LIA.NCA.FIN.UNS` |
| Equity | `EQU.OTH` |

A type-default mapping prints as **REVIEW** in the mapping table - confirm or
override it before rendering.

## 3. Where does this account go? (decision rules)

| Account (as it appears in the workpaper) | Code | Why / when to choose differently |
|---|---|---|
| GST (credit) | `LIA.CUR.TAX` | Tax liabilities inside the Payables note. |
| GST (debit / refund due) | `LIA.CUR.TAX` | Xero prints it as a negative liability (Wisdom, Complex, Frontier). Capstone reclassified "GST payments/refunds" to `ASS.CUR.REC` - only do that if the preparer asks. |
| PAYG Withholding Payable, PAYG Instalment Payable, Income Tax Payable, Provision for Income Tax (credit) | `LIA.CUR.TAX` | |
| Provision for income tax in **debit** (refund) | `LIA.CUR.TAX` (negative) or `ASS.CUR.REC` | Capstone shows it in Receivables. Follow the prior-year pack for the client. |
| ATO Integrated Client Account | `LIA.CUR.PAY` when a liability (Padel, Frontier), `ASS.CUR.REC` when in credit (Capstone) | Not a tax liability sub-group in any of the five packs. |
| Superannuation Payable, Wages Payable, payroll clearing | `LIA.CUR.EMP` | Personnel-related items. |
| Provision for holiday pay / annual leave / bonuses / rent / make-good | `LIA.CUR.PRO` | Long service leave → `LIA.NCA.PRO`. |
| Credit cards (AMEX, Mastercard) in credit | `LIA.CUR.PAY` | Frontier. If the card is in debit and set up as a Bank account, `ASS.CUR.CAS.BAN` (Wisdom's Mastercard***0401). |
| Client control / trust monies liability | `LIA.CUR.PAY` | Frontier. |
| Revenue received in advance / unearned income | `LIA.CUR.PAY` | |
| Director / shareholder / family-trust loan, credit, no fixed repayment | `LIA.NCA.FIN.UNS` | Padel, Complex. Use `LIA.NCA.SHA` if the client's prior pack used the "Loan from Shareholders/Associates" note (Capstone). Use `LIA.CUR.FIN` if repayable within 12 months (Frontier's "Loans - Related party"). `LIA.CUR.PAY.FIN` reproduces Wisdom's presentation inside the Payables note. |
| Director loan in **debit** (company owed money) | `ASS.CUR.REC` | Padel "Loan to Directors" - flag Division 7A to the reviewer. |
| Loan to a related company | `ASS.CUR.REC` | Padel "Loan - Padel Point Rosehill Pty Ltd". Non-current if not repayable within 12 months → `ASS.NCA.REC`. |
| Bank loan, HP, chattel mortgage, equipment finance | `LIA.NCA.FIN.SEC` (current portion `LIA.CUR.FIN`) | |
| Bank guarantee / term deposit held as security | `ASS.CUR.FIN` | Frontier. Padel coded its bank guarantees to Intangibles (`ASS.NCA.INT.OTH`) - keep whatever the prior year did. |
| Deposits / bonds paid | `ASS.CUR.REC` | |
| Trade debtors / Accounts Receivable | `ASS.CUR.REC` | |
| Inventory / stock on hand | `ASS.CUR.INV.INV` | Also triggers the Inventories accounting policy. |
| "... at Cost" and "Accumulated Depreciation ..." pairs | same `ASS.NCA.PPE.<class>` | Both lines in the same class so the class total is the written-down value. Class from the name: leasehold/fit-out → LEA, motor/vehicle → MOT, furniture/fixtures → FUR, office equipment → OFF, computer → COM, else PLA. |
| Formation costs (+ accumulated amortisation) | `ASS.NCA.INT.OTH` | Prints even when fully amortised. |
| Trademark, brand deposit, website cost | `ASS.NCA.INT.OTH` | |
| Goodwill | `ASS.NCA.INT.GOO` | |
| Cash in hand, petty cash | `ASS.CUR.CAS.OTH` | |
| Depreciation, Amortisation, Instant Write-Off Assets | `EXP.OPE` | They are ordinary expenses in the pack; the depreciation schedule tie-out finds them by name. |
| Realised / Unrealised Currency Gains | `EXP.OPE` | Xero default codes 498/499 are expense-type; a gain prints in brackets. Padel. |
| Interest received / income | `REV.OTH` | |
| FBT employee contribution | `REV.OTH` | |
| Consulting fees **collected** | `REV.OTH` if the client's prior pack did so (Wisdom); otherwise `REV.TRA` | |
| Commissions collected / Overrides | `REV.TRA` / `REV.OTH` respectively | Frontier convention. |
| Government subsidies / grants | `REV.OTH` (Frontier coded BAC Wage Subsidies to `REV.TRA` - follow prior year) | |
| Income Tax Expense | `EXP.TAX` | |
| Dividends paid (franked / unfranked) | `EQU.DIV` | Enter as a positive "paid" amount. |
| Current Year Earnings | `EQU.CYE` | Only if the BS export shows it; validated against NPAT. |
| Retained Earnings | `EQU.RET` | Prior-years balance (Xero system account). |
| Capital loss / capital profits reserve | `EQU.RES` | Padel's PY movement was posted to RE; supply it in `equity_movements`. |
| Share Capital | `EQU.SHA` | |
| Suspense, Clearing, Historical Adjustment, Rounding, Tracking Transfers | `LIA.CUR.PAY` | Should be nil at year end - raise a query if not. |

## 4. Keyword rules (summary)

`fr_engine.KEYWORD_RULES` is scanned top to bottom; the first pattern that
matches the account name and is compatible with the statement side wins. The
important ones, in priority order: cash on hand → term deposit → bank/card names
→ receivables/loans receivable → prepayments → inventory → PPE classes
(leasehold, land, motor, furniture, office, computer, LVP, plant) → intangibles
→ investments → GST / PAYG / income tax / ATO accounts → super & payroll
liabilities → provisions → payables & clearing accounts → HP/secured finance →
loans (default non-current unsecured) → equity (dividends, CYE, RE, share
capital, reserves, drawings, capital accounts) → other income (interest,
dividends received, rent, FBT contribution, gains, grants/refunds/overrides) →
trading income (sales, revenue, fees, income, commission, consulting, services)
→ cost of sales (stock, purchases, direct costs, subcontractors) → income tax.

Rules never move an account across statements: a P&L line can only become
`REV.*`, `EXP.*` or `EQU.DIV`; a Balance Sheet line only `ASS.*`, `LIA.*`,
`EQU.*`. The account type also pins current vs non-current where it says so.

## 5. Other entity types (stubs until the templates are uploaded)

| Entity | Differences the mapping must support |
|---|---|
| **Trust** | No Share Capital / dividends. Equity = Settled sum (`EQU.CAP`), Trust capital reserves (`EQU.RES`), Undistributed income (`EQU.RET`); distributions to beneficiaries replace dividends (add `EQU.DIS` to `pnl_sections` as "Distribution to Beneficiaries"); beneficiary loan / UPE accounts → `LIA.CUR.PAY` or `ASS.CUR.REC`; Declaration becomes a Trustee Declaration (stub in `boilerplate.json`). |
| **Partnership** | Partners' capital and current accounts (`EQU.CAP`, `EQU.DRA`); profit distributed to partners; "Statement of Distribution" report. |
| **Sole trader** | Owner's capital, drawings (`EQU.DRA`), funds introduced (`EQU.CAP`); no income tax expense. |
| **SMSF** | Different pack entirely (Operating Statement, Statement of Financial Position, member statements) - out of scope; use `smsf-audit-pack`. |

To add an entity type: drop the chart in `assets/chart-of-accounts/<type>.csv`,
add the declaration wording under `boilerplate.json › declaration.<type>`, and
extend `report-map.json` (`pnl_sections`, `bs_lines`) if new lines are needed.
Set `entity.type` in the pack to pick them up.
