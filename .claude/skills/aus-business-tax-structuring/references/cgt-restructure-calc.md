# CGT on a restructure: how to calculate it properly

A transfer of an asset from an individual to a company or trust they control is a disposal. The law taxes it as if sold at market value. This file sets out the calculation so the figure that goes to the client is built, not estimated.

## 1. The event and the proceeds

- CGT event A1 (s 104-10) on change of ownership. Timing is the contract date, or the transfer date where there is no contract.
- Capital proceeds: what is received. Where the parties are not dealing at arm's length, or no consideration passes, the market value substitution rule (s 116-30) deems proceeds equal to market value at the time of the event. A transfer to a related company or trust is always in this territory, so **use market value**.
- Market value needs evidence. A bank or broker "indicative valuation" is a starting point. For duty the revenue office wants a valuation or appraisal under three months old; the ATO expects the same on audit. Recommend a formal valuation before contracts.

## 2. The cost base, element by element (s 110-25)

| Element | What goes in | Where to find it on the file |
|---|---|---|
| 1. Acquisition cost | Land price; construction cost (for a build); purchase price of an existing building | Contract, settlement statement, builder's contract, depreciation schedule (construction cost) |
| 2. Incidental costs of acquisition and disposal | Duty paid on purchase, legal and conveyancing, valuation, building and pest inspection, agent commission and marketing on sale | Settlement statement, duty receipt, invoices |
| 3. Non-deductible costs of ownership (assets acquired after 20 August 1991) | Interest, rates, insurance, repairs that were **not** deducted (eg while not rented). Cannot create or increase a loss | Rarely for a rental that was let from day one |
| 4. Capital improvements | Renovations and capital works not deducted as repairs | Invoices, depreciation schedule updates |
| 5. Title costs | Legal costs to establish or defend title | Rare |

Then the reductions:

- **Div 43 capital works deducted or deductible** reduce the cost base and reduced cost base for assets acquired after 7.30pm on 13 May 1997 (s 110-45(2)). Sum every year's claim from the first rented date to the transfer date, including the part year. The depreciation schedule gives the annual figure (eg $9,208 a year on a $368,319 Div 43 base at 2.5 per cent). "Deductible" means amounts that could have been claimed even if they were not (TD 2005/47), so a client who skipped claims does not escape the reduction.
- **Div 40 depreciating assets are separate CGT assets**, not part of the property's cost base. Take their cost out of the property cost base. On transfer each plant item has a balancing adjustment event (s 40-295): termination value (its share of the market value, or the agreed allocation) less adjustable value is assessable or deductible income, not a capital gain. For second-hand residential plant the 2017 rules deny the transferee entity any further Div 40 deductions on those existing items (s 40-27), so the new entity loses that deduction stream.
- **GST**: exclude input tax credits claimed from the cost base.

Reduced cost base (for a loss) excludes element 3 and Div 43 amounts.

## 3. The gain and the discount

Capital gain = capital proceeds (market value) less cost base.

- Held 12 months or more, transferor an individual or trust: 50 per cent discount (Div 115), until the announced regime replaces it for gains accruing from 1 July 2027 (see `law-changes-2026.md`).
- Transferor a company: no discount, ever.
- Complying super fund: one third discount.
- Non-resident individuals: no discount for the period of non-residency after 8 May 2012.

Tax: an individual's net gain sits on top of other taxable income and is taxed marginally, plus Medicare. A gain of $357,000 on top of $190,000 of other income is taxed at 47 per cent almost throughout. Model with `restructure_model.py`, which stacks it correctly.

## 4. Post 1 July 2027 (announced)

For gains accruing after 30 June 2027: index the cost base by CPI from acquisition (or from 1 July 2027 for the pre-existing portion under the transitional rules), take the real gain, and pay the greater of tax at marginal rates and 30 per cent. Gains accrued to 30 June 2027 keep the discount. Until the apportionment method is legislated, model two cases (time-based apportionment and valuation-based apportionment) if a client is deciding whether to transact before or after 1 July 2027, and recommend a valuation as at 30 June 2027.

## 5. Rollovers and concessions: which apply to a related party transfer

| Provision | Applies? | Effect and catch |
|---|---|---|
| Subdiv 122-A, individual or trustee to a wholly owned company | Yes, if the transferor owns all the shares and the company is not exempt | Gain disregarded; company inherits the cost base and acquisition date for the 12 month test but **never gets the discount or indexation**; the transferor's shares take the asset's cost base. Duty still payable. Depreciating assets and trading stock excluded. Usually worse than paying the discounted gain if the asset will ever be sold |
| Subdiv 122-B, partners to company | Yes for partnership assets | As above |
| Subdiv 124-N, unit trust to company | Only where a trust already holds the asset | Not for individual to trust |
| Div 615, interposing a company between owner and asset | Only for shares or units, not land | |
| Subdiv 328-G, small business restructure rollover | Only where a small business entity carries on a business and the asset is an active asset; genuine restructure; ultimate economic ownership unchanged | A passive rental property is not an active asset. A discretionary trust can qualify via a family trust election. No duty relief |
| Div 152 small business CGT concessions | Only for active assets of a CGT small business entity or one meeting the $6m net asset test | Residential rental fails the active asset test; a business premises used by a connected entity's business passes |
| Transfer to a discretionary trust | No rollover exists | Full gain at market value |
| Trust restructure rollover (announced, 1 July 2027 to 30 June 2030) | Discretionary trust to company or fixed trust | Income tax relief only; no duty relief |
| Marriage or relationship breakdown rollover (Subdiv 126-A) | Only under a court order or binding financial agreement | Not a planning tool |
| Main residence exemption | Not for a rental; partial if it was once the home | Check the ownership history |

## 6. Depreciating assets on transfer

For each Div 40 item on the schedule: termination value less adjustable value. On a market value transfer of a furnished rooming house the plant is usually near its written down value, so the adjustment is small, but it must be shown. The transferee cannot claim Div 40 on second-hand residential plant acquired after 9 May 2017 (s 40-27), which permanently loses the remaining Div 40 deductions to the group. Div 43 continues in the transferee's hands on the original construction cost.

## 7. Layout for the file note

```
Market value (s 116-30)                                      1,475,000
Cost base
  Element 1  land                                              424,676
  Element 1  construction (builder's contract and fit-out)     437,824
  Element 2  duty, legal, valuation on acquisition          [settlement statement]
  Element 4  capital improvements since                     [invoices]
  Less Div 40 plant (separate assets)                          (68,005)
  Less Div 43 deducted or deductible to transfer date          (34,000)
Cost base                                                      760,495
Capital gain                                                   714,505
Discount 50% (held > 12 months, individual, pre 1 July 2027)  (357,252)
Net capital gain                                               357,252
Tax at marginal rates plus Medicare on top of $190k income     167,909
Div 40 balancing adjustments                                  [per item]
```

Every line carries the FYI document it came from. Where an element is missing, name the document that would supply it and give the figure as a range.

## 8. Common errors this file exists to stop

- Using the client's "purchase price" without splitting out Div 40 plant and without the Div 43 reduction.
- Forgetting that a transfer to a family trust has no rollover.
- Offering Subdiv 122-A without pointing out the permanent loss of the discount and indexation.
- Assuming small business concessions on a passive rental.
- Ignoring the depreciating asset balancing adjustments and the s 40-27 denial for the transferee.
- Quoting "CGT" without the marginal stacking, which understates the tax by tens of thousands at Katya's income level.
- Treating the announced 2027 regime as law, or ignoring it when the client's timeline runs past 1 July 2027.
