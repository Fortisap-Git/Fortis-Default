---
name: "client-onboarding"
description: "Onboards a new Fortis client (individual, company, trust, SMSF, partnership or group) step by step: brief, duplicate check, AML screening, ownership map, Ignition onboarding forms, XPM data sheet, proposal, welcome pack, ASIC, ATO and close-out. Gives the owner, login and click-by-click path for the steps people do in XPM, FYI, Ignition, NowInfinity, BGL, ASIC and the ATO portal, and answers how-to questions about them."
---

# Client Onboarding

Brings a new client onto the Fortis books in the same order every time, with a stop at every point where a mistake is expensive. Claude does the looking-up, checking, maths and drafting; people do the verifying, signing and keying into systems Claude can't reach (XPM, ATO portal, ASIC, NowInfinity, BGL, FuseSign). Client information comes in through three Ignition onboarding forms, which Claude creates, sends on approval and reads back.

The human version of this process is the **Fortis Client Onboarding Runbook** artifact: https://claude.ai/artifact/3acCndTsXsiRpbQbhRWzQg. Step numbers below (1.1, 2.4 ...) match it, so you can point staff to the exact step; a step links as `#s-3-3` (step 3.3) on the end of that URL. Each step has a "How, click by click" block: the login, every click and where it sits on screen, with annotated screenshots. The same clicks, without the pictures, are in `references/click-paths.md`.

**Trigger for:** "onboard [client]", "new client", "new company coming on board", "set up [client] in XPM", "onboarding checklist for [client]", "what do we need from [new client]", a partner's meeting notes or a prospect's email with a request to get them set up, and "how do I [onboarding step] in XPM / FYI / NowInfinity / BGL / the ATO portal" (add a client in XPM, send the 362 for signing, lodge the 362, add a client on the portal).
**Do not trigger for:** establishing a brand-new company, trust or SMSF (use `nowinfinity-setup`, then come back here for the onboarding); an existing client's annual pack (use `client-email-intake`); a single proposal (use `ignition-proposal-builder`).

## Hard rules (never broken, whatever the pressure)

1. **CDD before the portal.** Nobody goes on the ATO portal until every person linked to the client is ID verified, screened and recorded in XPM. Claude never marks verification complete; a partner or senior accountant does.
2. **TFN, never ABN only**, when adding to the ATO portal.
3. **Never lodge an ASIC 362 without a signature.**
4. **Search before you create:** FYI (which mirrors XPM), Ignition and Monday, by every person and entity name, before proposing any new record.
5. **Sensitive details come in securely.** Never ask for TFNs, dates of birth or ID details in the body of an email; they come through the Ignition onboarding forms (or NowInfinity for ID). Never write a TFN into Monday, a chat reply or a file name; in chat, show only the last three digits. TFNs go only into the XPM data sheet.
6. **Postal address is the client's own.** FAP's address only for non-residents or overseas clients, or where the partner says we manage their ATO mail.
7. **Drafts only.** Proposals stop at draft, emails are Outlook drafts, nothing is lodged by Claude. The one client-facing send is the Ignition onboarding forms, and only when the approved plan lists them.
8. **One plan, one "go".** Every write (FYI, Monday, Ignition, Outlook) is listed in the Onboarding Plan (step 4 below) and happens only after Rehman or the manager says go. Anything new that turns up later is raised, not done.
9. House style for anything client-facing: Rehman's voice via `email-auto-drafter` and `humanizer`, "we" voice, flat numbered lists, Australian English, no em dashes.
10. **Own logins only.** Name the system and whose login it needs, never the login itself: no password, username or myID detail in a plan, chat, email or file, even if someone pastes one. Everyone uses their own login; access to a system comes from the admin manager. Nobody logs in as the client. ATO and ABR portal work is Sydney staff only.

## How-to questions

When someone asks how to do one onboarding step, skip the workflow and answer from `references/click-paths.md`:

1. The runbook step, who does it and the login it needs (system and whose login, per hard rule 10).
2. The numbered clicks, each with where it sits on screen and the label in bold, as the file gives them.
3. Any warning the file notes under the procedure (charges, expiry dates, "don't lodge").
4. The link to the step in the runbook, which has the screenshots: `https://claude.ai/artifact/3acCndTsXsiRpbQbhRWzQg#s-3-3` for 3.3.

Keep every *(label to confirm)* flag. If the path isn't in the file, say it isn't captured yet and give the runbook step; never guess at a menu.

## Workflow

### 1. Build the brief (runbook 1.1)

From the partner's notes, the prospect's email or the chat, write the **Onboarding Brief**:

| Field | What to capture |
|---|---|
| Client / group name | As the partner refers to it; this becomes the XPM group and Ignition proposal name |
| People | Full name, role(s) in each entity, whether a director, residency, email, mobile |
| Entities | Legal name, type, ABN, ACN, trustee, what it does |
| Structure | Who owns what percentage of what; who controls (directors, trustees, appointers) |
| Services | Returns, financials, BAS, SMSF, advice; first year we act for |
| Partner / manager | Name each; billing entity if known |
| Previous accountant | Name and contact, for the handover (8.4) and BGL transfer |

Ask the user at most one question, and only when the answer changes the plan (for example, which entity pays). Otherwise take the most likely reading and mark it as an assumption in the plan.

### 2. Check what already exists (runbook 3.1)

Run in parallel, for every person and entity in the brief:

- **FYI:** `fyi_list_clients` with `search` on the surname or entity name. FYI syncs from XPM, so a hit means an XPM record exists (active or archived). Note id, partner, manager, group.
- **Ignition:** `list_clients` with `filter: {"property": "name", "rich_text": {"contains": "<SURNAME or entity>"}}`, then `list_proposals` with `filter: {"property": "client_slug", "relation": {"contains": "<cli_ slug>"}}` for any accepted engagement. (If the filter is rejected, scan recent `list_proposals` pages instead.)
- **Monday:** Annual Compliance 2026-2027 board `18419272927`, `get_board_items_page` with `searchTerm` on the name.

Report matches as "existing, update rather than create". A returning client or a lead the partner already made is updated, never duplicated.

### 3. Public register look-ups and AML screening (runbook 2.3, 2.4, 3.6)

This is preparation for the verifier, not the verification itself.

**Registers** (WebFetch; record what you saw and the date):

- ABN Lookup `https://abr.business.gov.au/ABN/View?abn=<11 digits>` or a name search: entity name, ABN status, entity type, GST registration, state and postcode, and the ACN for companies.
- ASIC: company status and registration date where the free search is readable (ASIC Connect, or ASIC's new company search at `https://service.asic.gov.au/companysearch`, in beta). Director and shareholder names come from the admin's draft 362 in the ASIC Registered agent portal (runbook 4.1) or a paid extract, so list them as "to confirm" if unknown. Since 2 February 2026, extracts bought on the ASIC website no longer show officeholder addresses; addresses come from the client's forms or the NowInfinity company profile (runbook 5.3).
- SMSFs: Super Fund Lookup `https://superfundlookup.gov.au` for regulation status and complying status.
- Admin still saves the ABN Lookup and ASIC PDFs to FYI; say so in the plan.

**Screening**, for every individual in the brief (clients, directors, shareholders, trustees, appointers, beneficiaries, anyone controlling money, beneficial owners):

- **Sanctions:** try the DFAT Consolidated List. If you can't search the list itself, say so and leave the check open for the verifier; never report "no match" for a list you didn't read. Prioritise anyone who isn't an Australian citizen.
- **PEP:** WebSearch `"<full name>" AND government OR politics OR parliament OR court OR military OR administration OR diplomat OR state-owned OR international` (add the country for anyone with foreign links).
- **Adverse media:** WebSearch `"<full name>" AND fraud OR corruption OR crime OR arrest OR scandal OR investigation OR lawsuit OR conviction OR bribery OR "money laundering" OR terrorist OR sanctions`.
- The policy asks for up to 3 pages of results. Search tools return fewer, so state how many results you reviewed and that the verifier should complete the 3-page review if anything looks relevant.
- Ignore results that clearly aren't the same person; ignore spent convictions and minor offences. A possible sanctions match or a foreign PEP is flagged at the top of the plan for the AML/CTF compliance officer (Bernadette Pywell), and all work on the client pauses until she clears it.

**Beneficial ownership** (companies, trusts, partnerships, groups):

1. Lay out every layer from the client entity down to individuals, from the structure chart and documents (company extract no more than 6 months old, constitution, trust deed and variations, partnership agreement).
2. For each individual, multiply the percentages along each path and add their paths together. 25% or more = beneficial owner. Show the working, e.g. "Company A 50% owned by Company B; X owns 60% of B; X holds 30% of A".
3. Add controllers who don't own: directors, trustees, appointers, anyone who can appoint or remove them.
4. Nominee holder: record the person behind them and note that a written declaration is needed.
5. No beneficial owner: record why, and flag that the CEO or most senior officer must be verified.

Output the **CDD Worksheet**: one row per person with role(s), beneficial owner yes/no and %, register findings, PEP result, adverse media result, sanctions status (checked / open), suggested risk factors, and "ID verification method: to be chosen by verifier". The verifier completes the Initial customer due diligence form and the risk rating (Low reviews every 3 years, Medium 2, High 1).

### 4. Present the Onboarding Plan and wait for "go"

One message, scannable:

1. **Who and what:** the brief in 5 to 8 lines, with assumptions marked.
2. **Existing records:** FYI, Ignition and Monday matches, or "none found".
3. **Flags:** anything from screening, missing structure information, overseas directors, nominees, trustee companies acting in two roles, SMSF on another firm's BGL.
4. **Forms to send:** which Ignition form goes for whom (one Group Overview; a Person Details per person; an Entity Details per entity), the client each sits under, and the email subject for each. Plus the documents to ask for by email (see "Missing items" below).
5. **Actions on "go"**, in order, each with the skill or tool that runs it:
   - XPM data sheet (Excel, via the `xlsx` skill) for admin to key in
   - Ignition proposal draft via `ignition-proposal-builder` (family group and SMSF separate)
   - Monday items (listed with name, group, entity type, fee, status)
   - Create and send the Ignition onboarding forms (step 7)
   - Welcome email draft via `email-auto-drafter`
   - FYI filing of anything the client already sent, via `fyi-document-filer`
   - Follow-up reminders (optional Outlook calendar entries)
6. **For people to do:** one line per task, in order: owner, runbook step, system and whose login, then the short click path from "People tasks" in Reference, e.g. `Admin, Sydney staff · 6.2 · ATO Online services for agents, own myID · My practice › Client list › add client by TFN`. Usually ID verification, recording it in XPM, keying the data sheet into XPM, the 362s, FuseSign, ASIC lodgement, the ATO and ABR portals and BGL. The full numbered clicks go in the admin checklists (steps 8 and 9).

### 5. XPM data sheet (runbook 3.2 to 3.7)

XPM has no connector, so Claude writes exactly what admin types. Build it from the submitted Ignition forms (step 7) plus the register look-ups, with the `xlsx` skill (house Excel style), in four sheets. If the forms aren't back yet, build it from the brief and mark the gaps:

- **Entities:** one row per XPM entity in creation order (group first, people next, then companies, then trusts and SMSFs), with every field in "XPM fields" below. Leave a cell blank and highlight it in the Missing sheet rather than guessing.
- **Contacts:** one row per person in a group: Name, Salutation, Addressee (first and last name, or English name if used), mobile in 614xxxxxxxx format, email, and the entities to attach the Contact to with the role on each.
- **Relationships:** from-entity, relationship (director, shareholder %, appointer, beneficiary, member, trustee, public officer, spouse), to-entity.
- **Missing:** every blank still needing the client after the forms, feeding the welcome email.

Naming rules: people `SURNAME, First Name` (display) with first, middle and last exactly as ATO records; companies as ASIC; trusts `Trustee Pty Ltd ATF The Trust Name`; SMSFs `Trustee Pty Ltd ATF Fund Name`. A company that trades and is also a trustee gets two XPM entities. Trust or SMSF with a corporate trustee: note in the sheet "create as Company, add directors and shareholders, then switch Business Structure". Mobiles: strip spaces, replace a leading 0 or +61 with 61, check the result is 614 plus 8 digits.

Add a fifth sheet, **How**, first in the workbook: the login line and the numbered XPM clicks for runbook 3.1 to 3.7 from `references/click-paths.md`, so admin keys in from one file.

File it: `fyi-document-filer` rules, name `YYYY - XPM Data Sheet - <Group Name>`, Permanent cabinet `194015`, Year + Entity Set Up `6536498`, against the main entity once it exists in FYI (hold it in the chat until then).

### 6. Engagement and Monday (runbook 1.3, 1.4)

- Run `ignition-proposal-builder`. A new client has no Monday fee, so the builder prices from its pricing reference and shows comparables. Family group and SMSF proposals are separate. If the client isn't in Ignition yet (XPM feeds Ignition), the builder creates it unassigned and says to attach the client within 7 days.
- Monday, board `18419272927`, group **Proposal** (`group_mksngqym`): one item per entity, named in capitals as the board does (`TAI, EDWIN`, `TAI & HUI MANAGEMENT PTY LTD`); columns `text_mkshm0f` group name, `text_mkshd8f3` entity type (`Individual/Sole trader`, `Australian Private Company`, `Discretionary Trust Invest.`, `Self Managed Super Fund`), `project_owner` manager, `numeric_mkshfxes` fee on the head entity only, `project_status` **To Send Proposal** then **Proposal Drafted** once the draft exists. No TFNs on Monday.
- Don't create XPM jobs: Ignition creates the job when the engagement is accepted. New entity establishments use the Establish… job templates (check with the accountant).
- CU form or engagement letter: people named in the engagement letter need no CU form; anyone else with missing details gets one (FuseSign template). Record the choice for XPM 01 Notes in the data sheet.

### 7. Ignition onboarding forms and welcome pack (runbook 1.2, 4.1 to 4.5)

**The forms.** Three templates live in Ignition (designs and questions: runbook section "Ignition onboarding forms", https://claude.ai/artifact/3acCndTsXsiRpbQbhRWzQg#ref-forms):

| Template | Send | What it covers |
|---|---|---|
| `FAP Onboarding - Group Overview` | Once, to the main contact, straight after the meeting | Services, start year, people and roles, entities, ownership, billing entity, previous accountant, nature and purpose, source of funds, PEP and overseas links, documents they'll email |
| `FAP Onboarding - Person Details` | One per person (client, director, shareholder, trustee, appointer, member, beneficial owner) | Names as ATO, other or English name, DOB, place of birth, addresses, mobile, email, TFN, residency, citizenship, occupation, roles, Director ID, sole-trader ABN, ID method and document, PEP, last return lodged |
| `FAP Onboarding - Entity Details` | One per company, trust, SMSF or partnership | Type, legal name, ABN, ACN, TFN, trustee, addresses, directors, shareholders %, appointers, beneficiaries, members, partners, activity, date set up, GST, employees, software, SMSF property and loan, SMSF administrator and BGL, last return, known debts, documents they'll email |

1. **Find the templates:** `list_form_templates` with `filter: {"property": "name", "rich_text": {"contains": "FAP Onboarding"}}`. If any of the three is missing, say which, point the user to the runbook forms section to build it in Ignition, and carry on with the rest of the plan. Never substitute the generic "New Lead" or "Lead Qualification" templates.
2. **Pick the client:** a form belongs to one Ignition client. Use the main contact's Ignition client from step 2. Person and Entity forms for other people and entities sit under that same client unless the person is an Ignition client in their own right. If the main contact isn't in Ignition yet, ask before creating a client (the partner may already have them as a lead in Deals).
3. **Create on "go":** `create_form_using_template` for each form with `form_template_slug`, `client_slug`, `email_subject` (`Fortis onboarding: your group`, `Fortis onboarding: details for Jane Smith`, `Fortis onboarding: details for ABC Pty Ltd`) and a short `email_message` in the partner's voice. The subject is how answers get matched back, so always name the person or entity.
4. **Send on "go":** `send_form_to_client` for each created form, only if the approved plan listed the send. Otherwise report the form slugs so the partner can send them from Ignition.
5. **Read back:** `list_forms` with `filter: {"and": [{"property": "client_slug", "relation": {"contains": "<cli_ slug>"}}, {"property": "state", "select": {"equals": "submitted"}}]}`, then `get_form` for each. Map the answers into the XPM data sheet, the CDD worksheet (PEP answers, citizenship, ID method, overseas links) and the Missing sheet, using the form-to-field map below. Check answers against the register look-ups (legal name vs ABN Lookup, ACN vs ASIC) and list any difference.
6. **Chase:** forms still `awaiting` at day 3: offer to resend with `send_form_to_client`. At day 14, suggest the partner calls.

Ignition forms can't take uploads and have no conditional questions. Documents (deeds, constitution, prior returns, structure chart) come by email to admin@fortisap.com.au, where the FYI add-in files them; `fyi-document-filer` renames and categorises them.

**Welcome email:** draft with `email-auto-drafter` as an Outlook draft in the partner's voice. It lists only what's still outstanding after the forms, says the CU form(s) and 362(s) will arrive by FuseSign, and flags `[ATTACH: How to Appoint FAP as your Tax Agent]` (FYI document `e5780df5-961f-4eda-8518-371a0b3215ef`; tax agent number 25220769; nominations lapse after 28 days) plus `[ATTACH: CU form]` and `[ATTACH: ASIC 362]`. Copy admin@fortisap.com.au. No TFN or date of birth requests in the body.

**SMSF extras:** if the Entity Details form or the last return shows the fund on another firm's BGL, put "arrange BGL transfer now" at the top of the plan; property plus a loan in the fund means a bare trust question in the welcome email.

**Follow-ups** (offer to put them in Outlook with `outlook_create_event` after "go"): form resend day 3 and partner call day 14; e-sign chase day 2 and day 7; ATO nomination check day 14 and day 21; partner check-ins at 6, 12 and 26 weeks after acceptance.

### 8. When documents and signatures come back (runbook Phases 5 and 6)

- File what the client sends with `fyi-document-filer`, using the onboarding names below.
- Give admin the Phase 5 and 6 checklist with the client's names filled in and, under each item, the login and the numbered clicks from `references/click-paths.md`. Mark the ATO and ABR items Sydney staff.
  1. Lodge the signed 362, only after the partner's OK (5.1). In NowInfinity it must be marked signed first: MENU › Lodgements › Incomplete › row ⋮ › Mark as Signed, then Actions › Lodge Selected.
  2. Save the ASIC debt report and current extract (5.2): RA63 in the Registered agent portal; the extract from ASIC Connect (paid).
  3. Match XPM to the extract (5.3), then the ASIC Register and NowInfinity registers (5.4).
  4. Check nominations (6.1): Online services for agents, Reports and forms › Reports › Client nominations.
  5. Add each client by TFN (6.2), then update XPM from the portal (6.3).
  6. Tidy ABR (6.4): email, ABN contacts, remove the old accountant as authorised representative, business address.
  7. Check addresses (6.5) and save the portal snapshot as PDFs (6.6).
- **Portal against the proposal (runbook 6.8):** compare the ATO portal summary with the engagement scope. Overdue returns, activity statements or debts the proposal doesn't cover go back to the manager and partner, with `ignition-proposal-builder` in amend mode, before work starts.
- Draft the ATO summary email (runbook 6.7) for the accountant to approve: balances and payment details if anything is owing, outstanding lodgements, ASIC extract and debt report with address differences, and anything still missing (constitution, stamped deed and variations, signed SMSF deed and member declarations).

### 9. SMSF in BGL (runbook Phase 7)

Give admin the BGL checklist: search first, Add New Entity from XPM, fund address now and signed deed and member declarations later (audit), standard relationships for John's team (confirm HZ team's), members as Accumulation with start date = ABN registration date for new funds (ask the manager for existing funds), opening balances "No", SuperStream registration once regulated (about 28 days for new funds) with John Kalachian as accountant, the three ESA documents, BGL as the nominated SuperStream on the ATO portal, ESA letters sent on the same email chain.

Put the BGL login line and the numbered clicks from `references/click-paths.md` (runbook 7.1 to 7.3) under each item. The key ones: HOME › Search by Entity Label before + Add New Entity; FUND RELATIONSHIPS tab for the standard cards; MEMBER › Member List › Add Accumulation Member, then **No** to opening balances; CONNECT › SuperStream Dashboard › All Funds › Register; Export › Notification Letters (New ESA Registration) for the letters. A subscription error when adding a fund means the firm needs another BGL licence: ask Bernadette, Rehman or Nicole.

### 10. Close-out and report (runbook Phase 8)

Check the definition of done and report in this shape:

- **Existing records found / created:** FYI ids, Ignition proposal number, Monday item ids.
- **CDD:** worksheet filed or held, open checks (sanctions list not read, 3-page reviews, verifications outstanding), any escalation.
- **Forms:** created, sent and submitted counts, with any still awaiting.
- **Drafts staged:** welcome email draft, ATO summary email (when reached).
- **For people to do next,** by owner, with runbook step numbers.
- **Reminders set** (if any) and dates.
- **Offers:** previous accountant handover request (8.4), group structure chart, AML/CTF register update (run the XPM "AML/CTF Report").

## Reference

### People tasks: owner, login, click path

The short path is for the plan (step 4). Checklists and how-to answers use the full numbered clicks in `references/click-paths.md`. `*` marks a label still to confirm on screen.

| Step | Task | Owner | System and login | Short click path |
|---|---|---|---|---|
| 1.2 | Send forms Claude created but didn't send | Partner or admin | Ignition, own login | Clients › open the client › Summary tab › Send Form |
| 2.2 | Verify ID, file the report | Partner or manager | NowInfinity, own login (every completed check is charged); FYI | MENU › Identity Verifications › Add Identity Verification; PDF icon on the completed check; FYI green + › Upload |
| 2.3 | Sanctions list, if Claude couldn't read it | Manager | DFAT Consolidated List, no login | dfat.gov.au › Sanctions › Consolidated List › download; Excel Find All within Workbook |
| 2.6 | Record the verification | Admin | XPM, own Xero login | Clients › Search clients › person › Edit details (Date Verified, Verified By*); custom fields 01 to 032* |
| 3.1 | Search before creating | Admin | XPM | Clients › Search clients, then the Archived clients, Contacts and Groups tabs |
| 3.2 | Create the group | Admin | XPM | Clients › Groups tab › New Group*; tick the clients › Add to group ▾ |
| 3.3 | Create the people | Admin | XPM | Clients › Add client › Business structure Individual › Create › Edit details |
| 3.4 | Contacts | Admin | XPM | person › Contacts › Add Contact › Create contact; the same contact on their other entities, never a second one |
| 3.5 | Create the entities | Admin | XPM | Clients › Add client › Company (also a trust or SMSF with a corporate trustee, switched after 3.7) |
| 3.6 | Fields and register PDFs | Admin | XPM; ABN Lookup and ASIC Connect, no login | Edit details; register page › Ctrl+P › Save as PDF › FYI |
| 3.7 | Relationships and billing | Admin | XPM | entity › Relationships › add*; Edit details › billing client* |
| 4.1 | Prepare the 362s | Admin | ASIC Registered agent portal (FAP agent number, own username) to read the directors only, don't submit; NowInfinity to generate | NowInfinity MENU › Corporate Messenger › Appoint an Agent › ACN |
| 4.4 | E-sign the 362s and CU forms | Admin | FYI, own login (sends through FuseSign) | tick the PDFs › Signature › Service FuseSign › Send |
| 5.1 | Lodge the signed 362 | Admin, after the partner's OK | NowInfinity | MENU › Lodgements › Incomplete › row ⋮ › Mark as Signed › Actions › Lodge Selected |
| 5.2 | Debt report and extract | Admin | ASIC Registered agent portal; ASIC Connect (paid) | portal: ACN › RA63 › Inbox; ASIC Connect: company › Company extract › Current company information › Add to cart |
| 5.3 | Match XPM to ASIC | Admin | NowInfinity; XPM | Corporate Messenger Companies* › See Full Profile; XPM Edit details and Relationships |
| 5.4 | Registers | Admin | NowInfinity | MENU › Super Comply › Funds for an SMSF; trust register menu not captured yet |
| 6.1 | Pending nominations | Admin or manager, Sydney staff | ATO Online services for agents, own myID | Reports and forms › Reports › Client nominations |
| 6.2 | Add the clients | Admin, Sydney staff | ATO Online services for agents, own myID | My practice › Client list › add client* › TFN |
| 6.3 | Update XPM from the portal | Admin, Sydney staff | ATO Online services for agents; XPM | client › Profile › Tax registrations and Client details; XPM Edit details |
| 6.4 | Tidy the ABR | Admin, Sydney staff | ABR Tax professional's services, own myID | abr.gov.au › Tax professionals › client ABN › update the ABN record* |
| 6.5 | Addresses | Admin, Sydney staff | ATO Online services for agents | client › Profile › Client addresses › Edit |
| 6.6 | Portal snapshot | Admin, Sydney staff | ATO Online services for agents | Client summary › Print friendly version › Save as PDF; Tax accounts; Lodgments |
| 7.1 | Add the fund | Admin | BGL Simple Fund 360, own login | HOME › Search by Entity Label, only then + Add New Entity › Enter SMSF Details |
| 7.2 | Relationships and members | Admin | BGL | FUND RELATIONSHIPS tab; MEMBER › Member List › Add Accumulation Member; opening balances No |
| 7.3 | SuperStream and ESA letters | Admin | Super Fund Lookup, no login; BGL | CONNECT › SuperStream Dashboard › All Funds › Register; Export › Notification Letters (New ESA Registration) |
| 8.2 | AML/CTF register | Admin | XPM | Reports › AML/CTF Report* |
| 8.3 | File the structure chart | Admin | FYI | green + › Upload › Permanent, Structure; Comment tab › @ the manager and partner |

### Missing items (asked in the Ignition forms; documents by email to admin@)

| Who | Items |
|---|---|
| Everyone | Full legal name as ATO records, date of birth, residential and postal address, mobile and email, ID for verification, TFN, answers to the AML questions in the forms |
| Directors | Director ID; place of birth (must match the Director ID); at least one director with an Australian residential address |
| Company | ACN and ABN, constitution, last two years' financial statements and returns, share register if it differs from ASIC |
| Trust | Stamped trust deed and every variation, appointer details, trust TFN and ABN, last two years' returns and distribution minutes |
| SMSF | Signed deed and variations, signed member declarations, trustee company constitution, previous accountant and BGL details, bare trust deed if property with a loan |
| Partnership | Partnership agreement and variations, TFN and ABN, last two years' returns |
| Groups | Structure chart showing every entity and percentage |

### Details by role

- **Director:** name as ATO records (must match ATO, ABR and ABRS or ASIC won't recognise the Director ID); Australian residential address (at least one director resident); date of birth; place of birth; TFN; Director ID (personal application, the director sends it to us); email and mobile.
- **Shareholder:** name as ATO records; residential address, or registered address for a corporate shareholder; date of birth for individuals; authorised signatory for corporate shareholders (company: public officer and directors; trust: appointer; SMSF: directors of the trustee); TFN (overseas shareholders without one post 2 certified, translated IDs for manual ABR assessment); email and mobile.
- **SMSF member:** everything a director needs, because every member must be a director of the corporate trustee.

### Form answers to XPM fields

| Form answer | Goes to |
|---|---|
| Person: first, middle, last name | XPM name fields; display `SURNAME, First Name` |
| Person: other or English name | XPM Contact Name, Salutation and Addressee |
| Person: mobile | XPM Contact mobile, converted to 614xxxxxxxx |
| Person: DOB, place of birth, Director ID, TFN, sole-trader ABN | XPM entity fields (place of birth and Director ID for directors) |
| Person: residential and postal address, residency | XPM addresses; postal address rule (hard rule 6) |
| Person: roles; Entity: directors, shareholders %, appointers, beneficiaries, members, partners | XPM relationship links; ownership map |
| Person: ID method and document; PEP; citizenship | CDD worksheet; ID verification (runbook 2.2, 2.3) |
| Entity: type | XPM Business Structure (and the company-first rule for corporate trustees) |
| Entity: name, trustee, ABN, ACN, TFN, addresses | XPM entity fields; checked against ABN Lookup and ASIC |
| Entity: GST, employees | Noted for PAYG and GST (set in XPM only after the portal) and proposal scope |
| Entity: last return, known debts; Group: services, start year | Proposal scope; portal check (runbook 6.8) |
| Group: billing entity | XPM billing link; proposal addressee |
| Group: previous accountant | Handover request (runbook 8.4); BGL transfer |
| Group: purpose, source of funds; all: declaration | CDD worksheet and Initial CDD form |

### XPM fields

Name (as above); date of birth; place of birth (directors); Director ID (directors); email and mobile (on the entity for a stand-alone individual, otherwise on the Contact); address checked against ASIC, ATO and ABR; partner; manager (partner if unknown); ABN (active, ABN Lookup PDF saved); ACN (registered, ASIC profile PDF saved); billing entity (from the proposal; SMSFs bill themselves, a bare trust bills to its SMSF); TFN; Tax Agent = Fortis Accounting Partners; returns to be prepared; custom fields for anything to chase. **Active ATO Client, PAYG and GST are set only after the entity is on the ATO portal.**

### XPM verification fields (feed the AML/CTF register)

| Where | Field | Entry |
|---|---|---|
| Client | Date Verified | Date completed (sent date goes in Notes) |
| Client | Verified By | Who verified or processed the NI check |
| Custom | 01 Pre-AML Client | Yes = no action unless circumstances change a lot; No = complete 02 (and 03 if an issue) |
| Custom | 02 CDD Created | Face to face, video or NI |
| Custom | 021 CDD Document Type | Document seen; NI = NI Digital Report Attached |
| Custom | 022 Risk Profile | Low, Medium or High |
| Custom | 03 / 031 / 032 | Issue date, one-line details and resolution, tick when resolved |

### FYI filing

| Document | Cabinet | Categories |
|---|---|---|
| Set-up: ABN and ASIC PDFs, 362, extracts, deeds, constitution, XPM data sheet | Permanent `194015` | Year + Entity Set Up `6536498` |
| ID verification reports, TFN and registration letters | Permanent `194015` | Year + ID TFN/ABN/GST rego etc `6536499` |
| Structure chart | Permanent `194015` | Year + Structure `6536505` |
| Prior returns and documents for the upcoming return | Work Papers `194012` | Year + PBC `6536465` |
| Welcome email, engagement letter, CU forms | Correspondence `194013` | Year + Engagement letter `6536433` |

Year categories: 2027 `16270592` (filed from 1 July 2026), 2026 `13013940`, 2025 `6554355`.

### Onboarding file names

House format `YYYY - Document Type - Entity Name`, YYYY = financial year of the document date; point-in-time snapshots add the date as DDMMYYYY. Use "and", not "&", in upload names.

| Document | Name |
|---|---|
| ABN Lookup PDF | `2027 - ABN Lookup 29092026 - Entity` |
| ASIC profile / extract / debt report | `2027 - ASIC Profile 29092026 - Entity` (Extract, Debt Report likewise) |
| ABR update | `2027 - ABR Details Update 29092026 - Entity` |
| ATO portal summary and accounts | `2027 - ATO Portal Summary 29092026 - Entity`; `... ATO Income Tax Account ...`; `... ATO Activity Statement Account ...` |
| Last lodged return from the portal | `2025 - ITR Portal Copy - Entity` (year of the return; CTR, TTR, PTR, SMSF AR to match) |
| ID verification report | `2027 - ID Verification Report 29092026 - Person` |
| 362, CU form, structure chart | `2027 - ASIC 362 Agent Appointment - Company`; `2027 - Customer Update Form - Person`; `2027 - Group Structure Chart - Group` |
| ESA letters | `2027 - ESA Trustee Notification Letter - Fund` (Employer Notification Letter, Super Standard Choice Form likewise) |

The September 2026 guide used an older format (`ABN XXXX26 – Client Name`). The runbook recommends the house format above; follow whichever the partners have confirmed, and mention the difference once if a file already uses the old one.

## Judgement calls

- **Lead already in XPM** (partner created it after the first call): update it, fill the gaps; don't create a second.
- **Company that is also a trustee:** two XPM entities, two roles, one 362 (the 362 is per ACN).
- **Overseas director or shareholder:** check the Director ID and TFN position early; they may need to apply by post with certified documents, which takes weeks. Put it at the top of the Missing list.
- **Nominee shareholder or director:** the beneficial owner is the person behind them; flag the declaration needed.
- **Client already has a signed Fortis engagement for another entity:** check whether it names the new people before sending CU forms.
- **Screening result that might be the same person:** don't decide; list it with the source link for the verifier.
- **User asks to skip a hard rule** (for example add to the portal before verification): explain the rule in one line and leave it with the partner; don't do it.

## Sources behind this skill

FAP Client Onboarding Guide 290926 and the Y2K Procedures and Policies documents (XPM - Adding an Entity, Client Onboarding - Individual(s), Client Onboarding - Corporates and Groups, ID Verification, Corporate Role Requirements, How to Appoint FAP as your Tax Agent, How To Set Up New Entities, Client Onboarding - Meeting Notes, Stage 1 Intake & Proposal SOP v0.4), the Fortis AML/CTF Process Procedures v1.0, and Onboarding - Tax Return & ITR Procedures (postal address rule).

The click paths (runbook revision 2 and `references/click-paths.md`, 29 September 2026) also draw on BGL - How to add an SMSF, Creating New Entities, ASIC & NI - Updating Details, ASIC - Business Name Search and the Client Address Update Checklist, and on the vendors' help pages: Xero, the ATO Online services for agents user guide, ASIC's registered agent guides, NowInfinity, FYI, Ignition and monday.com. When a screen changes, update the runbook's click-by-click block and `references/click-paths.md` together.
