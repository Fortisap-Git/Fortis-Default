# FYI, Outlook and Xero: what to pull and what it tells you

The firm already holds most of what a structuring answer needs. This map turns "check the file" into a fixed list of pulls and the field each one yields. Run the pulls in one parallel batch, scoped by entity id.

## 1. Resolve the group

```
fyi_list_clients  search = surname or trading name
```

Take every result that shares the same `entity_group.id`. For each entity note: `id`, `name`, `business_structure` (Individual, Company, Trust, Partnership, Superannuation Fund), `business_number` (ABN), partner and manager, address. That is the group map.

Gaps in the group map are common. XPM only knows entities the firm acts for. A trust or second company the client mentions in an email (the KTV Family Trust, the "second company sitting with ASIC") may not be in FYI at all. Add those to the map from the correspondence and mark them "not on our register".

`fyi_list_resource resource=group search=<name>` returns the group record. `entity_relationship` is not available through the API, so shareholdings and trustee roles come from ASIC extracts and deeds, not from FYI metadata.

`fyi_list_jobs entity_id=<id>` shows the compliance jobs and their state, which tells you whether the latest year is lodged or still in progress.

## 2. Pull the documents

```
fyi_find_documents  entity_id=<id>  per_page=100   (paginate; 63 to 120 documents per entity is normal)
```

Document names rarely contain the client name, so never rely on the `search` wildcard to find a client's documents. Filter the entity's list yourself. The pulls that matter, and what each yields:

| Document (typical FYI name) | Cabinet | What to take from it |
|---|---|---|
| `FY 2025 - ITR - <name>` (signed copy has `(SIGNED)`) | Final Reports & Returns | Taxable income and marginal rate, rental schedule per property with **address and state**, date first rented, ownership %, gross rent, interest, Div 40 and Div 43 claimed, CGT schedule, franking credits received, PAYG instalments |
| `FY 2025 CTR - <company>`, `2025 FR - <company>` | Final Reports & Returns | Retained earnings, franking account, shareholder loans, Div 7A balances, base rate entity status, related party balances, assets held |
| `2025 Workpaper - <name>` (xlsx or xlsm) | Work Papers | Rental tabs per unit or property (address, first available date, agency summary, owner expenses, Div 40 and Div 43), `CGT Property` tab (the cost base template), Review Notes (what the reviewer flagged), dividend decision tab (how income was topped up) |
| `<address> Tax Depreciation Schedule` | Work Papers | Construction cost, Div 43 base and annual claim, Div 40 asset list and written down values, construction start and completion, settlement date, date available for income. This is the backbone of the cost base |
| `Rates - <period>` (council) | Work Papers | Unimproved land valuation and its effective date (the land tax base), real property description, rating category, owner name as registered |
| `Financial_year_statement_<agent>` / `Rental Summary` | Work Papers | Gross rent, agent fees, letting fees, sundry; confirms the property is agent managed and on what terms (matters for the GST classification of a rooming house) |
| Loan statements, `Interest Summary`, `Mortgage Mart` etc | Work Papers | Lender, balance, rate, security, borrower name, interest paid |
| `ASIC Extract <date> - <company>` | ASIC | Directors, shareholders and share classes, registered office, ACN, any second company |
| `Division 7A Loan Agreement`, `Loan Drawdown Acknowledgement`, `Director Resolution`, `Dividend Statement` | Final Reports & Returns | Existing Div 7A loans, terms, minimum yearly repayments, dividends declared |
| `ATO Mail - <type>` and the PDF letters | Correspondence | PAYG instalment position, ATO debt, **ABN cancellation advices** (a cancelled ABN on a landlord with rooming income is a GST flag), NOAs |
| `Email` documents filed by the Outlook add-in | Work Papers / Correspondence | The client's own words. Read them; they carry the intent and often the missing facts |
| `PreJune Workpaper`, `SMSF_vs_Outside_Super_Comparison` and similar | Work Papers | Planning already done this year; do not contradict it without saying why |

Read PDFs and emails with `fyi_read_document`. Download spreadsheets with `fyi_download_document` and open them with openpyxl (`data_only=True`, then dump the rental, CGT and summary tabs).

**Scanned PDFs.** `fyi_read_document` sometimes returns pages with no text (the rates notice and the depreciation schedule did this). Download the file and extract locally:

```python
import pymupdf
doc = pymupdf.open("file.pdf")
for page in doc:
    print(page.get_text())          # most "scans" still carry a text layer
    # page.get_pixmap(dpi=110).save("p.png")  # render to view if there is truly no text
```

## 3. The Outlook thread

Search the mailbox for the client and the subject (`outlook_email_search` with `query`, then `read_resource` on the URI). Read the whole thread: the original ask, every reply Rehman has sent or drafted, and earlier threads on related topics (ASIC transfer, Div 7A, planning meeting recaps). Draft replies show what has already been promised to the client. Do not repeat a promise; deliver on it.

## 4. Xero (where connected)

`select_client` then balance sheet, trial balance and the loan and related party accounts. Gives the live Div 7A balance, retained earnings, franking position and any inter-entity loans. Use the FYI financials where there is no Xero file.

## 5. House constants

| Thing | Id |
|---|---|
| Final Reports & Returns cabinet | 194010 |
| ASIC cabinet | 194011 |
| Work Papers cabinet | 194012 |
| Correspondence cabinet | 194013 |
| Year 2025 category | 6554355 |
| Year 2026 category | 13013940 |
| Year 2027 category | 16270592 |
| PBC / provided by client | 6536465 |
| Annual Return/Financials | 6536450 |
| ATO letters | 6536431 |
| General correspondence | 7852514 |
| Acting user | rehman@fortisap.com.au |

Filing the practitioner note back to FYI follows the fyi-document-filer skill: `fyi_get_upload_url` then POST the bytes, then `fyi_upsert_resource` to set categories and `original_filename`. Confirm with Rehman before any write.

## 6. Fact base checklist

Before analysis, you should be able to fill every cell for every asset and entity. Anything you cannot fill from the file is the client request.

- Legal owner, state of the land, title description
- Acquisition date, contract and settlement dates, price split land and build
- Acquisition costs: duty paid, legal, valuation, inspections (settlement statement)
- Construction or improvement costs and dates (depreciation schedule, invoices)
- Div 43 claimed each year to date; Div 40 assets and written down values
- Current market value and its source; unimproved land value and its date
- Loan balance, rate, lender, security, borrower, guarantees
- Gross and net rent, first rented date, agent, tenancy type (rooming, residential, commercial)
- Each individual's taxable income, marginal rate, residency, citizenship or visa (foreign person tests), spouse and dependants
- Entity registrations: ABN (active or cancelled), TFN, GST, PAYG, payroll tax, land tax
- Dormant entities and what they were set up for
