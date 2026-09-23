# Worked example: Wilga Street, Wacol (September 2026)

The case this skill was rebuilt around. Kateryna (Katya) Vakulenko, managing director of Soup Agency Pty Ltd, asked whether to move her rooming house from her own name into a company or trust so her broker could refinance it at a lower rate. It shows the full run: file pull, fact base, model, recommendation, file note, email.

## 1. The ask (email 16 September 2026)

Katya's broker says the loan (about $944,000 with WLTH) would roll to about 8.34% interest only in her own name, but a company or trust could refinance with Suncorp at about 6.94% interest only on a $1.475m indicative valuation, borrowing $1.0325m at 70% LVR. Broker's estimate of transfer and refinance costs about $79,000 before CGT and set up. She asked six things: the CGT triggered at $1.475m; the cost base on our records (original land and build about $862,500); any rollover or concession; company versus trust for rooming accommodation income; set up and annual costs; and everything else, including interest deductibility after the transfer and tax when the property is eventually sold. The claimed saving is about $6,900 a year.

## 2. What the file said (FYI, entity 214613933 and 216173648)

| Source | Fact |
|---|---|
| `fyi_list_clients` "Soup" | Group 61319366 "Soup Agency Pty Ltd": Soup Agency Pty Ltd (company, ABN 95 646 832 626) and VAKULENKO, Kateryna (individual). Partner John Kalachian, manager Rehman Khan |
| Outlook thread "ASIC statement" (Aug to Sep 2026) | A second company transferred to Fortis from the old accountant; a **KTV Family Trust** settled "a while ago" with no ABN or TFN, never used, client unsure whether to keep it |
| FY 2025 ITR (signed) | Taxable income $190,720; dividends $140,000 franked from Soup Agency; five rental schedules for **Unit 1 to Unit 5, 60 Wilga St, Wacol QLD 4076**, first rented 25 May 2023, 100% owned, gross rent about $99,000, interest $46,930, capital works $9,208, other deductions $39,564, net rent $3,645 |
| 2025 Workpaper (xlsx) | Rental tabs per unit tie to agent statements; CGT Property tab is empty (no cost base ever built); Review Notes show dividends were set to bring income to $190k |
| 60 Wilga Street Tax Depreciation Schedule (Budget Tax Depreciation, 23 May 2023) | New build: construction commenced 22 March 2022, completed and settled 22 March 2023, construction cost $437,824 (builder's contract $416,900 plus fit-out), Div 40 plant $68,005, Div 43 base $368,319 at 2.5% = $9,208 a year, soft landscaping $1,500 non-depreciable |
| Brisbane City Council rates notice, Oct to Dec 2024 | Lot 1 SP333035 Parish of Oxley; **land valuation $250,000 at 1 July 2024** ($210,000 at 1 July 2022) |
| ATO mail June 2026 | **ABN cancellation advice** for Kateryna, 4 June 2026 |
| Agent statements (WILGA60R2 to R5) | Rooms let individually through an agent on rooming agreements |
| Loan statements (WLTH) | Land settled 16 June 2022 (drawdown $240,100); build progress payments $416,500 reconcile to the builder's contract |
| Soup Agency file | 2025 Div 7A loan agreement, drawdown acknowledgement and resolution; 2025 dividend statement; ASIC extract 18 Aug 2026 |

Two facts the first drafts missed: the property is in **Queensland**, and the file already held enough to build the cost base.

Not on file: the settlement statement and duty receipt from the March 2023 land purchase (element 2 costs), a formal current valuation, and the broker's written terms.

## 3. Fact base

- Owner: Kateryna, individual, resident, top marginal rate (income about $190k and she controls the dividend).
- Asset: 5-room rooming house, Wacol QLD, land about $424,676 (being $862,500 less the $437,824 build) settled June 2022, build $437,824 including $68,005 plant, first rented 25 May 2023, Div 43 claimed $33,628 and Div 40 claimed $41,368 to a December 2026 transfer, land value $250,000, indicative market value $1.475m (broker, not a formal valuation).
- Debt: $944,000 WLTH, moving to interest only at about 8.34%.
- Group: Soup Agency Pty Ltd (trading, pays Katya franked dividends, has a Div 7A loan history), a second dormant company, KTV Family Trust (dormant, no TFN or ABN).
- Registrations: Katya's ABN cancelled June 2026; gross rooming income about $99,000.

## 4. Model output (scripts/restructure_model.py on assets/example-wilga-street.json)

Fortis house method: the Div 40 plant stays in the cost base and only the depreciation already claimed is deducted. The broker's $79,000 is treated as including the QLD transfer duty of about $65,000.

| | Company | Discretionary trust | Unit trust |
|---|---|---|---|
| CGT event at market value | $1,475,000 | same | same |
| Land $424,676 + build including plant $437,824 + estimated duty and legals on the land $15,289 | $877,789 | same | same |
| Less Div 43 claimed (FY23 $2,548, $9,208 a year, FY27 to date) | ($33,628) | same | same |
| Less Div 40 claimed (FY23 $12,765, FY24 $11,165, FY25 $8,591, FY26 $6,848, FY27 to date) | ($41,368) | same | same |
| **Cost base** | **$802,793** | same | same |
| Capital gain | $672,207 | same | same |
| 50% discount (held over 12 months, individual, pre 1 July 2027) | $336,104 net gain | same | same |
| Tax at marginal rates plus Medicare on top of $190k | **$157,969** | same | same |
| Broker's transfer and refinance costs, including QLD duty of about $65,338 | $79,000 | same | same |
| Set up | about $3,500 | about $4,000 | about $4,500 |
| **Upfront total** | **about $240,000** | about $241,000 | about $241,000 |
| QLD land tax: individual nil (under $600k); company or trustee nil (under $350k) at $250k land value | nil now; $1,450 plus 1.7% once land value passes $350k | same | same |
| Annual interest saving ($944k at 8.34% vs $1.0325m at 6.94%) | $7,074 | same | same |
| Extra annual compliance | about $4,000 | about $4,500 | about $4,500 |
| **Net annual benefit** | **about $3,000** | about $2,500 | about $2,500 |
| **Payback** | **about 80 years** | longer | longer |

The $15,289 acquisition cost is an estimate (QLD duty on the land plus $2,000 legals) until the settlement statement is on file. Each $10,000 of price or cost base moves the tax by about $2,350. If the broker's $79,000 turns out to exclude duty, add about $65,000 to the upfront total.

**Sale instead, settling by Christmas 2026.** Selling costs of about $42,375 (agent 2.5%, marketing $3,000, legals $2,500) lift the cost base to $845,168. Gain $629,832, net gain $314,916 after the discount, tax about $148,011 at $190k of other income ($138,400 at $100k, $132,400 at $60k, so the dividend from Soup Agency is a $10,000 to $16,000 lever). Cash after the WLTH loan and tax about $340,600. A foreign resident capital gains withholding clearance certificate is needed before settlement or the buyer withholds 15%.

Post 1 July 2027 sensitivity: if the transfer happened after that date the gain accrued to 30 June 2027 keeps the discount and only the later accrual is indexed with a 30% floor, so waiting does not make a transfer cheaper in any meaningful way; and the extra tax on a company later selling with no discount or indexation is a further cost of the company route.

## 5. Other consequences found

- **Company holding the rooming house**: 30% on net rent (passive, fails the base rate entity test); losses trapped; no discount or indexation on the eventual sale, so a later sale from the company costs more than from her own name; any of the extra $88,500 the company borrows above the $944,000 that reaches Katya personally is a Div 7A loan at 8.77%.
- **Discretionary trust**: from 1 July 2028 the announced 30% minimum tax at trustee level; QLD trustee threshold $350,000 so land tax starts once the land value grows; no rollover into a trust at all.
- **Unit trust**: excluded from the trust minimum tax, but the same CGT, duty and lending profile, and losses trapped.
- **Negative gearing**: the property is grandfathered in Katya's hands (acquired 2023). A new entity acquiring it in 2026 is an acquisition after Budget night, so any future net rental loss in the entity would be quarantined from 1 July 2027.
- **GST**: a furnished five room rooming house let by the room through an agent may be commercial residential premises under GSTR 2012/6. With gross accommodation income around $99,000 the registration threshold is exceeded, and a transfer of commercial residential premises is a taxable supply unless a going concern. Katya's ABN was cancelled in June 2026. This needs a cited answer from tax-guru before the next return, regardless of the restructure.
- **Depreciation**: the plant's written down value is about $26,637 ($68,005 less $41,368 claimed). If the contract allocates the plant at about that figure there is no balancing adjustment. The transferee could not claim Div 40 on the second-hand plant (s 40-27); Div 43 of $9,208 a year continues.
- **Lending**: the rate gap (8.34% own name against 6.94% in an entity) is the whole case for the restructure and it has not been confirmed in writing; rooming houses are often priced as commercial security whoever the borrower is, so the same product may be available to Katya directly or a different lender may price her own name better.
- **Dormant entities**: KTV Family Trust has no reason to exist after the 2028 changes unless a purpose is named; either vest it or keep it with a deed review (foreign beneficiary exclusion, appointor succession). The second company can be deregistered (ASIC Form 6010, $49) if it has no assets or liabilities, or kept as a future trustee.

## 6. Recommendation

Do not transfer. The restructure costs about $240,000 up front to save about $3,000 a year net, so it never realistically pays back, and the company route also raises the tax on the eventual sale. Instead, take the broker's entity rate back to the market as a target for Katya's own name: written approval in principle from Suncorp or another lender pricing rooming house security for an individual borrower, and confirm whether the 8.34% figure is a product choice rather than a borrower-type constraint. Separately, resolve the GST classification of the rooming house, obtain a market valuation as at 30 June 2027 for the CGT transition, and decide the fate of the KTV Family Trust and the dormant company at the planned catch-up.

## 7. Client email (Rehman voice)

Hi Katya,

Thanks for setting this out so clearly, and for the broker's numbers, which made it possible to model the whole thing from our file rather than in the abstract.

The short answer is that moving Wilga Street into a company or trust doesn't stack up. Because you'd be transferring to an entity you control, the tax law treats it as a sale at market value, so at $1.475m we'd be looking at a capital gain of roughly $672,000. Our records give a cost base of about $803,000, being the land at around $425,000, the build at $438,000 including the furniture and fittings, and an estimate of $15,000 for the duty and legals on the land purchase, less the depreciation and capital works we've claimed since 2023. With the 50% discount, the tax on the gain at your marginal rate is about $158,000. Add the broker's $79,000, which we've assumed already includes the Queensland transfer duty of about $65,000, and the set up costs, and you're at roughly $240,000 before anyone has saved a dollar of interest.

Against that, the refinance saves around $7,000 a year, and running a company or trust adds around $4,000 a year in accounts, returns and ASIC fees, so the net benefit is about $3,000 a year. That's a payback of about 80 years, and it gets worse if the property is ever sold from a company, which pays 30% on the whole gain with no discount. There's no rollover that helps here. The small business concessions need a business asset rather than a rental, and the rollover into a wholly owned company gives up the discount permanently, so it would cost more later than it saves now. Of the entity options a unit trust would be the least bad, mainly because the government's new 30% minimum tax on family trusts from July 2028 makes a discretionary trust a poor home for property, but none of them get near paying for themselves.

What we'd suggest instead is to use the broker's 6.94% as a target for your own name. Rooming houses tend to be priced as commercial security regardless of who owns them, so the gap between 8.34% and 6.94% looks like a product or lender difference rather than something only a company can unlock, and we'd like to see the Suncorp terms in writing before anything else. Two housekeeping items came out of the review as well. We want to confirm the GST treatment of the rooming house, since accommodation let by the room can be treated differently from a normal rental and your ABN was cancelled in June, and we'd like to settle what happens with the KTV Family Trust and the second company, both of which are sitting idle and costing you either fees or attention.

Happy to jump on a call with you and the broker to walk through the numbers, and we can pull the cost base together properly in the meantime if you can send through the settlement statement from the land purchase.

Kind regards,
Rehman

## 8. What to file

Practitioner note to FYI Work Papers (Kateryna Vakulenko, 2026 or 2027 category) with the model table, the documents relied on by id, the law applied with the announced measures marked, and the actions: broker terms in writing, GST classification to tax-guru, valuation at 30 June 2027, dormant entities decision, settlement statement request. Confirm with Rehman before filing and before staging the email as an Outlook reply draft.
