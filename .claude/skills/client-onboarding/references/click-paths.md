# Click paths and logins

Click-level instructions for every runbook step that touches a system. It is the same content as the "How, click by click" blocks in the [Fortis Client Onboarding Runbook](https://claude.ai/artifact/3acCndTsXsiRpbQbhRWzQg), which also carries the annotated screenshots. Checked on 29 September 2026 against the FAP Client Onboarding Guide 300926, the firm’s procedure documents (XPM - Adding an Entity, BGL - How to add an SMSF, Creating New Entities, ASIC & NI - Updating Details, ASIC - Business Name Search, Client Address Update Checklist) and the vendors’ help pages.

How to use it: quote the path, the login and the owner when you hand a task to a person (SKILL.md steps 4, 8 and 9), or when someone asks how to do an onboarding step. Don’t invent a path that isn’t here; say it isn’t captured yet and point to the runbook step.

Conventions: **bold** is the label on screen; *(where)* says where it sits; *(label to confirm)* marks a label nobody has confirmed on screen yet. Keep this file and the runbook in step: change both together.

## Logins and systems

Passwords never go into an output, a chat or an email. Everyone uses their own login; access to each system comes from the admin manager. ATO and ABR portal work is Sydney staff only.

| System | Where | Whose login | Who needs it |
|---|---|---|---|
| XPM (Xero Practice Manager) | login.xero.com, then the Fortis Accounting Partners organisation, top bar **Clients** | Your own Xero user with two-step authentication. Client access follows your staff permissions. | Partner, manager, admin |
| FYI Docs | FYI web app, and the **FYI** add-in inside Outlook | Your own FYI user, signed in with your Fortis Microsoft 365 account (the Outlook add-in asks for the same account the first time). Copy admin@fortisap.com.au on client emails so follow-ups can be snoozed. | Partner, manager, admin |
| Outlook (Microsoft 365) | Your own mailbox, and the shared admin@fortisap.com.au mailbox | Your own Microsoft 365 account. Snooze follow-ups in the admin mailbox so anyone in admin can pick them up. | Everyone |
| Ignition | Ignition web app, main menu **Clients** | Your own Ignition user. | Partner, manager (admin to send forms) |
| monday.com | Board **Annual Compliance 2026-2027** | Your own monday.com user. | Manager, admin |
| NowInfinity | NowInfinity web app, top bar **MENU** | Your own NowInfinity login. ID checks go out under the sender and every completed check is charged. | Admin, manager |
| FuseSign | Started from FYI with the **Signature** button; templates live in the FuseSign web app | Your FYI login for sending; your own FuseSign user for templates. | Admin |
| BGL Simple Fund 360 | BGL web app, left rail **HOME** | Your own BGL login. A subscription error while adding a fund means the firm needs another licence: ask Bernadette, Rehman or Nicole. | Admin (SMSFs) |
| ATO Online services for agents | onlineservices.ato.gov.au (Online services for agents login) | Your own myID at Standard or Strong strength, authorised for FAP in RAM by the practice authorisation administrator, with Online services for agents permissions set in Access Manager. Sydney staff only. Never share a myID or approve a code for someone else. | Admin (Sydney), manager |
| ABR Tax professional’s services | abr.gov.au, Tax professionals | Your own myID linked to FAP in RAM. Sydney staff only. The client must already be linked to FAP in ATO online services. | Admin (Sydney) |
| ASIC Registered agent portal | asic.gov.au, Online services, Registered agent portal | FAP’s registered agent number plus your own username and password (all case-sensitive). Ask the admin manager for a username; access is removed when you leave. | Admin |
| ASIC Connect | connectonline.asic.gov.au | No login to search. Paid extracts go through the site’s checkout with the firm’s payment method. | Admin, manager |
| ABN Lookup | abr.business.gov.au | No login. | Everyone |
| Super Fund Lookup | superfundlookup.gov.au | No login. | Admin, manager |
| DFAT Consolidated List | dfat.gov.au, Sanctions, Consolidated List (Excel download) | No login. | Manager |
| Web search | Any browser, in a private window | No login. | Manager |
| Zoom | Zoom app | The partner’s or senior accountant’s own Zoom account. | Partner, senior accountant |
| The client’s own logins | myID app, Relationship Authorisation Manager (RAM), Online services for business | The client only. Never log in as the client or ask for their myID. | Client |

## Phase 1: Intake and engagement

### 1.1 Capture the brief (Partner)

**Check nothing exists yet**. XPM (Xero Practice Manager), your own Xero login.

1. Run the search in 3.1 for every person and entity you heard about. Claude can run the same check across FYI, Ignition and Monday.

**Create the lead in XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* Click **Clients**.
2. *(top right)* Click **Add client**, the white button left of the blue **Add Xero organisation**.
3. *(New client window)* **Business structure** ▾: **Individual** for the main contact (or the entity’s structure).
4. *(New client window)* **Display name** `SURNAME, First Name`, then **First name** and **Last name**. Add the email and mobile if the window shows those fields; otherwise add them after saving with **Edit details** (top right of the client page).
5. *(bottom of window)* Click **Create**.
- Log your meeting time against the new client in XPM. The timesheet click path is not captured yet (see the runbook’s Screenshots to capture list).

**Put the prospect in Ignition**. Ignition, your own Ignition login.

1. Search Ignition first: clients reach Ignition from XPM in a one-way sync that runs once a day, so a client added to XPM this morning may not be there yet.
2. *(main menu)* **Clients**, then **+ New client** (top right).
3. *(right-hand panel)* **Client name**, **Contact name** and **Contact email** are required; **More details** takes the partner, manager and group. Save *(label to confirm)*.
4. *(if the firm uses Deals)* **Deals**, then **New Deal**, switch on **Existing client**, pick the client, enter the value and close date.
- A client created in Ignition only reaches XPM when its first workflow deploys, so link it to the XPM client when that client appears in Ignition.

### 1.2 Send the Ignition onboarding forms (Partner, Admin)

**Send a form**. Ignition, your own Ignition login.

1. *(main menu)* **Clients**, search the main contact, open the client.
2. *(client page, Summary tab)* Click **Send Form**.
3. *(form picker)* Choose **FAP Onboarding - Group Overview** first; later **FAP Onboarding - Person Details** for each person and **FAP Onboarding - Entity Details** for each entity.
4. *(email)* Set the subject to the person’s or entity’s name, then send *(label to confirm)*.
- Checked on 29 September 2026: the firm’s Ignition forms are New Lead, Lead Qualification and Post Meeting Email - New CLient. The three FAP Onboarding templates still need building with the build guide below.

**Read the answers**. Ignition, your own Ignition login.

1. *(main menu)* **Forms**, select the form to see its submissions. Or open the client, **Summary** tab, **Forms** heading, **Completed**.
2. *(form page)* **Export** emails you a CSV.

**Build a template (once)**. Ignition, your own Ignition login.

1. *(main menu)* **Forms**, then **New form**.
2. *(form editor)* Follow the [Onboarding Forms Build Guide](https://claude.ai/artifact/2YMmZPSMtBSM4N85TwcL3n): it has every name, message, question and choice ready to copy. Use the template names exactly, so Claude can find them.
- Don’t edit a form that already has responses; duplicate it and edit the copy.

### 1.3 Draft the engagement in Ignition (Manager)

**Draft the proposal**. Ignition, your own Ignition login.

1. *(client page, top right)* **+ New**, then **Proposal**. Or **Templates**, **Proposals**, and pick the template.
2. *(proposal editor)* Add the services. In the **Automation** step set up the XPM workflow (one per proposal).
3. *(status)* Leave it as **Draft** for the manager. Sending moves it to **Awaiting acceptance**; the client accepting moves it to **Accepted** and deploys the XPM job.
- Claude’s ignition-proposal-builder drafts this for you and stops at Draft.

**Add the Monday items**. monday.com, your own monday.com login.

1. *(board list)* Open **Annual Compliance 2026-2027**.
2. *(group Proposal, last row)* Click the **+ Add** row *(label to confirm)* at the bottom of the **Proposal** group, type the entity name in capitals as the board does (`TAI, EDWIN`, `TAI & HUI MANAGEMENT PTY LTD`), press Enter.
3. *(item row)* Click each cell and fill it: group name, entity type, manager (People column: search, select), fee (head entity only).
4. *(Status cell)* Pick **To Send Proposal**. Change it to **Proposal Drafted** when the draft exists and **Proposal Sent** once it goes.
- The blue **New Item** button at the top adds to the first group on the board, so use the Proposal group’s own last row.

### 1.4 Decide engagement letter or CU form (Manager)

**Record the choice in XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* **Clients**, search, open the client.
2. *(top right)* **Edit details**; write `EL` or `CU form sent DD/MM/YYYY` in the **01 Notes** section *(label to confirm)*.
3. *(bottom)* **Save**.

**Send a CU form**. FuseSign, sent from FYI with your FYI login.

1. The CU form is a FuseSign template. Sending from FYI is in 4.4; the template clicks inside FuseSign are not captured yet.

## Phase 2: ID verification and AML checks

### 2.1 List everyone who needs verifying (Manager)

**Check each person has an XPM record**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* **Clients**, **Search clients**: search each surname (3.1). Create anyone missing as in 3.3.
2. *(client page)* Open the person and check the custom field **01 Pre-AML Client** *(label to confirm)*. Yes means no new verification unless their situation has changed a lot.

### 2.2 Verify identity (Partner, Manager)

**Send a NowInfinity ID check**. NowInfinity, your own NowInfinity login.

1. *(top bar)* **MENU**, **Identity Verifications**, **Add Identity Verification**.
2. *(service type)* Choose the service type and tick the **Biometric** add-on *(label to confirm)*. **Standard** runs two document checks; **Enhanced** adds PEP and sanctions checks. The firm’s guide only says Biometric, so confirm the service type with the compliance officer.
3. *(recipient)* Name exactly as it appears on the ID, then the mobile and email. Send *(label to confirm)*. The client gets a secure link by email and SMS.
4. *(results)* **MENU**, **Identity Verifications**, **Requests**, click the row. The outcome reads **Confidence**, **Likely** or **Cannot Confirm** (for Cannot Confirm, check what was typed).
5. *(completed check, top right)* Click the **PDF** icon and save the report.
- The link expires after 28 days, or 7 days once the biometric step has been opened.
- Australian ID only. Foreign passports are checked face to face or by video.
- Every completed check is charged, pass or fail: Standard $3, Enhanced $6, Enhanced with 12 months’ monitoring $7, ex GST (NowInfinity price list from 1 July 2026).

**File the report in FYI**. FYI Docs, your own FYI login (Microsoft 365).

1. *(top bar)* Green **+**, **Upload**, **Choose a file** (or drag the PDF onto the person’s Documents list).
2. *(Import drawer)* Client: the person. **Cabinet** Permanent; categories 2027 and **ID TFN/ABN/GST rego etc**. Name it `2027 - ID Verification Report DDMMYYYY - Person`.
3. *(bottom)* Click **Create**.

**Attach it in XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(client page)* Open the person, **Documents** tab.
2. *(Upload a Document)* **Choose File**, **Open**, **Upload** (or drag the file into the shaded area).
- XPM hands documents to the connected document system, so this upload may land in FYI by itself. Check once; if it does, skip the separate FYI upload so there is only one copy.

**Face to face or video**. Zoom, partner’s or senior accountant’s Zoom.

1. Face to face: note the date, the document seen and the risk rating, and give them to admin.
2. *(Zoom)* The client emails a copy of the ID first. On the call they hold the same document next to their face while the partner or senior accountant compares.

### 2.3 Screen names: sanctions, PEP, adverse media (Manager)

**Sanctions: DFAT Consolidated List**. DFAT Consolidated List, no login.

1. *(dfat.gov.au)* International relations, Security, Sanctions, **Consolidated List**. Download the list (Excel) and note its last-updated date.
2. *(Excel)* Ctrl+F, **Options**: **Within** Workbook, untick **Match entire cell contents**.
3. *(Excel)* **Find All** on the surname, then the given names and any other names the person uses.
4. *(any hit)* Compare date of birth, place of birth and citizenship. A possible match: stop and tell Bernadette Pywell straight away.
5. *(Initial CDD form)* Record the date, the list’s version date, what you searched and the result.
- DFAT publishes the list as a download. We found no official name search on the page; if one appears, use it and note it here.

**PEP and adverse media**. Web search, no login.

1. *(browser)* Open a private window so results aren’t tailored to you.
2. *(search box)* Paste the PEP search string (SKILL.md step 3, runbook 2.3) with the full name in quotes; read up to 3 pages of results.
3. *(search box)* Paste the adverse media search string from the same place; read up to 3 pages.
4. *(Initial CDD form)* Record the search terms, sources and outcome.

### 2.6 Record it in XPM (Admin)

**Record verification in XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* **Clients**, **Search clients**, open the person.
2. *(top right)* **Edit details**: **Date Verified** (the completion date) and **Verified By** *(label to confirm)*; the sent date goes in **Notes**. **Save**.
3. *(custom fields)* Open the client’s custom fields *(label to confirm)*: **01 Pre-AML Client**; if No, **02 CDD Created**, **021 CDD Document Type** (for NowInfinity choose NI Digital Report Attached) and **022 Risk Profile**. Only for an issue: **03 CDD Issue Date**, **031 CDD Details and Resolution**, **032 CDD Issue Completed**. **Save**.
- New or changed custom field values can take a while to show in FYI.

## Phase 3: XPM set-up

### 3.1 Search before you create (Admin)

**Search XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* Click **Clients**.
2. *(Clients tab)* In **Search clients** search the surname, then the entity name, then the TFN or ABN. Open any close match and compare TFN, ABN and address.
3. *(tab under the title)* Click **Archived clients** and run the same searches; returning clients are often archived.
4. *(tabs under the title)* **Contacts**: search each person (they may already be a contact of another client). **Groups**: search the family or group name.

### 3.2 Create the XPM group (Admin)

**Create the group and add the clients**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar, then tab)* **Clients**, then the **Groups** tab.
2. *(Groups tab)* **New Group** *(label to confirm)* (Xero’s newer help calls it **Create group**).
3. *(group form)* Name: the same as the Ignition proposal, no trailing spaces or special characters. Leave **Taxable Group** and **Exclude from KPI Reporting** unticked unless the manager says otherwise. Save *(label to confirm)*.
4. *(Clients tab)* Tick each client in the group.
5. *(above the list, right)* **Add to group** ▾, then tick the group.
- Create the group on the Groups tab first; Add to group may not create one.

### 3.3 Create the people first (Admin)

**Create a person**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* Click **Clients**.
2. *(top right)* Click **Add client**.
3. *(New client window)* **Business structure** ▾, choose **Individual**.
4. *(New client window)* **Display name** `SURNAME, First Name`. It is typed by hand, not built from the name fields. Then **First name**, middle names *(label to confirm)* and **Last name** exactly as ATO records.
5. *(bottom of window)* Click **Create**.
6. *(client page, top right)* **Edit details**: date of birth *(label to confirm)*, **Tax file number**, residential address (checked against ATO, ABR and ASIC), and for directors **Place of Birth** and Director ID *(label to confirm)*. Partner and manager: the **Partner** and **Account Manager** fields *(label to confirm)*. **Save**.
7. *(Clients tab)* Add the person to the group (3.2).

### 3.4 Add contact details (Admin)

**Create the contact once**. XPM (Xero Practice Manager), your own Xero login.

1. *(client page)* Open the person, **Contacts** section, **Add Contact**.
2. *(New contact panel)* **Name**, **Salutation** and **Addressee**: first and last name, or the English name if they use one.
3. *(New contact panel)* **Email**, and the mobile in **Phone** as `614xxxxxxxx` (the firm’s guide uses Phone for the mobile).
4. *(New contact panel)* Tick **Set as primary contact for this client** for the main contact.
5. *(bottom right)* Click **Create contact**.

**Attach the same contact to their other entities**. XPM (Xero Practice Manager), your own Xero login.

1. *(entity page)* Open the entity, **Contacts**, add the existing contact *(label to confirm)*. Don’t create a second contact.
2. *(contact on the entity)* Set the **Position** for that entity: Director, Appointer & Beneficiary, Director of Trustee and Member.
3. *(Clients, Contacts tab)* Open the contact to check: it lists every linked client with its position. Change the phone or email once with **Edit details** and it updates everywhere.
- Search the Contacts tab before adding; duplicate contacts are hard to merge.
- A stand-alone individual needs no contact unless they use an English name: put the email and mobile on the client with **Edit details**.

### 3.5 Create each entity with the right structure (Admin)

**Create an entity**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar, top right)* **Clients**, **Add client**.
2. *(Business structure)* **Company** for a company, and to start with for any trust or SMSF with a corporate trustee. **Self Managed Superannuation Fund** or **Trust** come later, after the directors and shareholders are linked.
3. *(New client window)* **Name**: company as ASIC; trust `Trustee Pty Ltd ATF The Trust Name`; SMSF `Trustee Pty Ltd ATF Fund Name`. Click **Create**.
4. *(corporate trustee)* Add the **Director** and **Shareholder** relationships (3.7), then **Edit details**, **Business structure** ▾ to Trust or Self Managed Superannuation Fund, **Save**, and add the appointer, beneficiary or member relationships.
- XPM only offers Director and Shareholder relationships on a Company client, which is why trusts and SMSFs with a corporate trustee start as Company.

### 3.6 Complete the fields (Admin)

**ABN Lookup PDF**. ABN Lookup, no login.

1. *(search box)* Enter the ABN, ACN or name and search.
2. *(results)* Click the ABN. On the current details page check the ABN status is Active, the entity type and GST.
3. *(browser)* Ctrl+P, **Save as PDF**, name it `2027 - ABN Lookup DDMMYYYY - Entity`.
4. *(FYI)* Upload it (see 2.2, File the report) to **Permanent**, 2027, **Entity Set Up**.

**ASIC company check**. ASIC Connect, no login to search.

1. *(top right)* **Search ASIC Registers**: **Within** Organisation & Business Names, **For** the ACN or name, **Go**.
2. *(results)* Click the company name. Check the status is Registered and the ACN matches.
3. *(browser)* Save the page as PDF: `2027 - ASIC Profile DDMMYYYY - Entity`, filed to Permanent, 2027, Entity Set Up.
- ASIC’s new company search (beta since 1 July 2026, service.asic.gov.au/companysearch) shows the same free summary.

**Fill the XPM fields**. XPM (Xero Practice Manager), your own Xero login.

1. *(client page, top right)* **Edit details**.
2. *(details)* **Tax file number**, **ABN**, ACN *(label to confirm)*, **Tax agent** Fortis Accounting Partners, **Balance date**, **Partner** and **Account Manager** *(label to confirm)*. **Save**.
3. *(returns)* Tick **Prepare activity statement** where BAS is in scope, and the income tax return type *(label to confirm)*.
4. *(custom fields)* Note anything still to chase: deed on file, added to BGL, ID pending *(label to confirm)*.
- Leave Active ATO Client, PAYG and GST until the entity is on the portal (Phase 6).

### 3.7 Link relationships and billing (Admin)

**Link a relationship**. XPM (Xero Practice Manager), your own Xero login.

1. *(entity page)* Open the entity, **Relationships**, add a relationship *(label to confirm)*.
2. *(type)* Pick the type: Director, Shareholder (enter the number of shares), Trustee, Beneficiary, Appointer, Member, Partner (enter the percentage), Public Officer, Secretary, Spouse, Parent Of or Child Of.
3. *(related client)* Pick the related client. They must already exist in XPM. Add a start date if you know it, then save *(label to confirm)*.
- XPM adds the reverse link by itself, so enter each relationship once.

**Set the billing entity**. XPM (Xero Practice Manager), your own Xero login.

1. *(client page)* **Edit details**, billing client *(label to confirm)*: the entity the proposal is addressed to. SMSFs bill themselves; a bare trust bills to its SMSF.
- When an Ignition engagement is sent, the client it is addressed to becomes the billing client in XPM. Check it rather than set it twice.

### 3.8 Wait for FYI, then file (Admin)

**File an email from Outlook**. FYI Docs, your own FYI login (Microsoft 365).

1. *(Outlook)* Select the email (the Reading Pane must be on).
2. *(ribbon or message bar)* Click the **FYI** icon (near Reply, under **…**, or in **Apps**). The first time, sign in with the Microsoft 365 account you use for FYI.
3. *(FYI drawer, right)* **Filing**: **Client**, **Cabinet**, then the categories shown (Year and the category). Click **Create**.
4. *(check)* The email gets the blue **Filed in FYI** category. **Pin** keeps the drawer open for the next one.
- The FYI icon greys out when the Reading Pane is off. The category only shows in Inbox and Sent Items.

**Upload a file**. FYI Docs, your own FYI login (Microsoft 365).

1. *(top bar)* Green **+**, **Upload**, **Choose a file** (or drag files onto the client’s Documents list).
2. *(Import drawer)* Client (type 3 letters), **Cabinet**, categories, then **Create**.

**Staple the working documents**. FYI Docs, your own FYI login (Microsoft 365).

1. *(Documents list)* Tick two or more documents, then **Staple** in the toolbar.
2. *(Documents list)* Click the staple icon on a document to see just that set; the yellow **Clear Staple Filter** brings back the full list.

## Phase 4: Information request and e-signs

### 4.1 Prepare a 362 for every company (Admin)

**Read the directors (don’t lodge)**. ASIC Registered agent portal, FAP agent number plus your own username.

1. *(login page)* Registered agent number, your username, your password.
2. *(start)* Enter the company’s **ACN**, pick **362** from the list of forms, choose the appointment option, **Next**.
3. *(company details)* Note every director and update the XPM relationships (3.7).
4. *(stop)* Don’t submit and don’t print. Log out.
- The portal asks for the company’s corporate key, printed on the front of its annual statement. If the client has come from another agent, that key may have been cancelled and a new one needed.
- No corporate key? A paid ASIC extract (5.2) also lists the directors.

**Generate the 362 in NowInfinity**. NowInfinity, your own NowInfinity login.

1. *(top bar)* **MENU**, **Corporate Messenger**, **Appoint an Agent**.
2. *(form)* Enter the ACN. The company name fills in and Fortis shows as the registered agent.
3. *(form)* Select the signing director, name exactly as ASIC holds it, and generate the form *(label to confirm)*.
4. *(Lodgements)* The form waits in **MENU**, **Lodgements**, **Incomplete** as **Waiting for signature**. Use **Actions** to download the PDF.
5. *(FYI)* Save it as `2027 - ASIC 362 Agent Appointment - Company` in Permanent, 2027, Entity Set Up, ready for FuseSign (4.4).
- A company NowInfinity registered for us has **Generate 362 form and add to Corporate Messenger** on its completed documents page.
- Several companies at once: **Bundle Agent Appointment**.

### 4.2 SMSF checks before the email (Admin)

**Find who holds the fund in BGL**. FYI Docs, your own FYI login (Microsoft 365).

1. *(FYI, Work Papers)* Open the fund’s last annual return and find its electronic service address alias. BGLSF360 means SuperStream runs through BGL, usually the previous firm’s BGL.
2. *(manager)* Tell the manager at once so the previous firm transfers the fund to FAP’s BGL before deleting it.
3. *(financial statements)* Property in the assets plus a borrowing: add the bare trust question to the information request (4.3).
- Nothing in the return? Check the fund’s details once it is on the ATO portal (6.2).

### 4.3 Build the information request (Admin, Partner)

**Create the information request in FYI**. FYI Docs, your own FYI login (Microsoft 365).

1. *(client file, tab)* Open the main entity, **Documents**.
2. *(Documents list)* Tick the attachments: the 362(s) and CU form(s). Up to 10 attachments.
3. *(toolbar)* **Share** ▾, **All documents**, **Share** *(label to confirm)* (the firm’s guide; FYI’s help calls this Send Attachments: Email). Or green **+**, **Email**.
4. *(Create Email drawer)* Check **Recipients**: the client, plus admin@fortisap.com.au.
5. *(Create Email drawer)* **Template**: type to search and pick the template for this email *(label to confirm)*. The **Welcome** template now goes with the welcome email at the end (6.7).
6. *(Create Email drawer)* **Name** becomes the subject line. **Cabinet** Correspondence, **Year** 2027, category **Engagement letter**.
7. *(Create Email drawer)* **Save or Send**: **Draft in Outlook**, then **Create**.
8. *(Outlook)* Open the draft in the **FYI - Drafts** folder. Tidy the formatting, delete what doesn’t apply, attach **How to Appoint FAP as your Tax Agent** (FYI, Y2K Procedures and Policies, Permanent). Send it from admin@fortisap.com.au, or the partner sends it with admin copied, so the follow-ups can be set.
- Draft in Outlook marks the email as Sent in FYI straight away and it can’t come back to FYI. If the partner needs to review it in FYI, choose **Draft in FYI** instead.
- Never move or rename the FYI - Drafts folder.
- The guide calls this the response to the initial information gathering email (Part 4 step 3, Part 5 step 5).

### 4.4 Send the e-signs (Admin)

**Send for e-signing from FYI**. FuseSign, sent from FYI with your FYI login.

1. *(FYI, Documents list)* Once the information request (4.3) has gone and the partner has confirmed, tick the PDF(s) for one client (PDFs only).
2. *(toolbar)* Click **Signature**, or right-click the document and choose **Signature**. It isn’t under Share or Delivery.
3. *(Send for Signature drawer)* **Service**: FuseSign. **Recipients**: the client contact is the signer; add others as needed.
4. *(Send for Signature drawer)* **Service Status**: **Send**. Choose **Draft** to finish the bundle in FuseSign, for example to set the signing order.
5. *(check)* The document shows **Pending Client Signature** (list view **Workflow - Pend. Signature**).
- Signers get an email link and then an SMS code. Both come from the XPM contact, so fix the email and mobile in XPM first.
- The signed copy files itself back into FYI in the same cabinet and categories, and a copy goes to the admin mailbox; the original stays.
- The signing name is the name on the recipient’s email, and the address is picked from the XPM contact: check the right one is chosen. You can add extra signatories and send reminders for unsigned documents.
- When a CU form comes back signed, update XPM from it, then ask the partner whether the client can go on the ATO portal (6.2).

### 4.5 Diary the follow-ups (Admin)

**Snooze and diary**. Outlook (Microsoft 365), your mailbox; admin@ for follow-ups.

1. *(admin mailbox)* Select the email you copied to admin, **Home**, **Snooze** *(label to confirm)* (or right-click, **Snooze**), pick the day. It comes back to the Inbox then. Classic Outlook: **Follow Up**, **Add Reminder…**.
2. *(Calendar)* **New event**: title such as `Day 14: check ATO nomination, <client>`, the date, **Reminder**, **Save**.
- Claude can create the calendar entries after your go.

## Phase 5: ASIC

### 5.1 Lodge the signed 362 (Admin)

**Lodge in NowInfinity**. NowInfinity, your own NowInfinity login.

1. *(partner)* Get the partner’s OK to lodge.
2. *(top bar)* **MENU**, **Lodgements**, **Incomplete** tab, find the 362.
3. *(form)* Click the company name, **Amend the Document**: check it matches the signed version.
4. *(row ⋮, right)* **Mark as Signed**, enter the signing date, upload the signed PDF, **Confirm Signing Completed**. A 362 can’t be lodged until it is marked signed.
5. *(list)* Tick the row, **Actions**, **Lodge Selected** (or open the form, **Lodge**).
6. *(status)* Signed Successfully, then Your Message is Pending, Transmitted, Lodged.
7. *(top bar)* **MENU**, **Notification Centre**: the accepted validation, **Expand**, open the Validation Report Accepted PDF. Save it with the 362 in FYI.
- ASIC records the lodgement date as the signing date, and the ASIC to NowInfinity sync can be slow, so lodge each signed 362 as soon as it comes in.
- NowInfinity then lodges an RA61 and RA71 and the company appears on the Corporate Messenger Companies list. Not there after 15 minutes: **Company List Refresh**.

### 5.2 Save the extract and debt report (Admin)

**Debt report**. ASIC Registered agent portal, FAP agent number plus your own username.

1. *(start)* Enter the ACN and choose **RA63 Request for individual company debt report**; submit *(label to confirm)*.
2. *(Inbox)* The report arrives in the portal **Inbox**. Download it as `2027 - ASIC Debt Report DDMMYYYY - Company` and file it to Permanent, 2027, Entity Set Up.
- A company with nothing owing is left off the report. Payments take 24 to 48 hours to show.
- The company owes ASIC? Once the debt has synced from ASIC to NowInfinity, generate the ASIC invoice from NowInfinity (menu not captured yet) and attach it to the welcome email (6.7).

**Current company extract**. ASIC Connect, no login to search.

1. *(results)* Search the company as in 3.6, open it, **Company extract**, **Current company information**.
2. *(cart)* **Add to cart**, **OK**, **Checkout**, **Pay now**. The PDF link comes by email.
3. *(FYI)* Save as `2027 - ASIC Extract DDMMYYYY - Company` in Permanent, 2027, Entity Set Up.
- About $9 to $18; the checkout shows the fee.
- Since 2 February 2026, extracts from the ASIC website no longer show officeholder addresses. Take addresses from the client or the NowInfinity company profile (5.3).
- The firm’s guide says both come from the ASIC portal: confirm whether you buy the extract there, on ASIC Connect or through NowInfinity.

### 5.3 Match XPM to the extract (Admin)

**Compare and update**. NowInfinity, your own NowInfinity login.

1. *(top bar)* **MENU**, Corporate Messenger **Companies** *(label to confirm)*, click the company row, **See Full Profile**.
2. *(profile)* Read the officers, shareholders and addresses. **Actions**, **Force data sync** refreshes it from ASIC.
3. *(XPM)* **Edit details** for addresses; **Relationships** for officeholders and shareholders (3.7).
4. *(list)* Note every address that differs from what the client told us for the welcome email (6.7).

### 5.4 Update the registers (Admin)

**SMSF into Super Comply**. NowInfinity, your own NowInfinity login.

1. *(top bar)* **MENU**, **Super Comply**, **Funds**: search the fund.
2. *(not listed)* **Add an Existing Fund** and follow the prompts with the XPM details.

**Trusts and the ASIC Register**. NowInfinity, your own NowInfinity login.

1. *(NowInfinity)* Trust register: the menu name is not confirmed yet (see the runbook’s Screenshots to capture list).
2. *(ASIC Register)* Add the company, any amount owing and the due dates to the firm’s ASIC Register document. Ask admin for the link if you don’t have it.

## Phase 6: ATO and ABR

### 6.1 Check the nominations (Admin, Manager)

**What the client does**. The client’s own logins, the client’s own, never ours.

1. *(RAM)* Log in with myID, **Link your business**. They must be the principal authority on the ABR.
2. *(Online services for business)* **Profile**, **Agent details**, **Add**, **Search for Agent**: Fortis Accounting Partners, 25220769. Check the details, complete the declaration, **Submit**.
3. *(client tells us)* The nomination lasts 28 days. The client can extend it before then; after that they nominate again.
- Send the client How to Appoint FAP as your Tax Agent (FYI, Y2K Procedures and Policies) rather than retyping these steps.

**Our side: find pending nominations**. ATO Online services for agents, your own myID, Sydney staff only.

1. *(login)* Log in with your myID and pick FAP.
2. *(menu)* **Reports and forms**, **Reports**, request the **Client nominations** report and download it. It lists pending nominations and their expiry dates.
3. *(partner)* The ATO doesn’t notify us. Confirm with the partner and add the client (6.2) before the expiry date.

### 6.2 Add the clients (Admin)

**Add a client**. ATO Online services for agents, your own myID, Sydney staff only.

1. *(menu)* **My practice**, **Client list**, add a client *(label to confirm)*.
2. *(identifier)* Identifier type **TFN**, **Next**. Individuals: TFN and date of birth. Companies, trusts, SMSFs and partnerships: the TFN, never the ABN alone.
3. *(accounts)* Authorise all the client’s accounts *(label to confirm)*.
4. *(check)* The client can take up to 15 minutes to appear in the client list; search by TFN or ABN meanwhile.
- Blocked? There may be no nomination yet, or the TFN is security-assessed or archived: phone the ATO.
- After linking, check the name, TFN, address or date of birth match ATO records.

### 6.3 Update XPM from the portal (Admin)

**Read the ATO details**. ATO Online services for agents, your own myID, Sydney staff only.

1. *(client)* Open the client, **Profile**, **Tax registrations**: note GST, PAYG withholding and PAYG instalments with their dates.
2. *(client)* **Profile**, **Client details**: the mobile and email the ATO holds.
3. *(SMSF)* Check the fund’s ESA in its details *(label to confirm)*. If it isn’t BGL, talk to the accountant about BGL issuing an updated ESA (7.3).

**Update XPM**. XPM (Xero Practice Manager), your own Xero login.

1. *(client page, top right)* **Edit details**: Active ATO Client Yes *(label to confirm)*, GST and PAYG *(label to confirm)*, ABN status, and the ATO’s phone and email if XPM has none (note any difference in Notes). **Save**.

### 6.4 Tidy the ABR details (Admin)

**Update the ABN record**. ABR Tax professional’s services, your own myID, Sydney staff only.

1. *(abr.gov.au)* Tax professionals, log in with your myID.
2. *(client)* Find the client’s ABN, then update the ABN record *(label to confirm)*.
3. *(details)* **Business address**: the street address, matching ASIC. Email: the client’s unless the partner says otherwise.
4. *(contacts)* Contacts: the FAP partner, then the directors or appointers. Authorised contacts: remove the old accountant and add the client *(label to confirm)*.
5. *(finish)* **Next**, submit, save the confirmation as `2027 - ABR Details Update DDMMYYYY - Entity` and file it to FYI.
- Changes are due within 28 days of a change and take effect straight away.

### 6.5 Check the addresses (Admin)

**Check and fix addresses**. ATO Online services for agents, your own myID, Sydney staff only.

1. *(client)* **Profile**, **Client addresses**: **Postal address** and **Business address**, **Filter**, **Edit**.
2. *(address)* Use **Search address** (it predicts as you type) and save. Postal: the client’s own, FAP only for non-residents, overseas clients or when the partner says we manage their ATO mail.
3. *(individuals)* **Profile**, **Client details**, the drop-down next to the address, phone or email.
- A lodged return updates only the income tax account’s address; check the other accounts too.

### 6.6 Save the portal snapshot (Admin)

**Save the snapshot as PDFs**. ATO Online services for agents, your own myID, Sydney staff only.

1. *(Client summary)* **For action** lists overdue and upcoming lodgments and payments. **Print friendly version**, browser print, **Save as PDF**: `2027 - ATO Portal Summary DDMMYYYY - Entity`.
2. *(Accounts and payments)* **Tax accounts**, filter to the income tax account, print friendly, PDF: `2027 - ATO Income Tax Account DDMMYYYY - Entity`. Repeat for the activity statement account.
3. *(amount owing)* **Payment options**: the payment reference (PRN), saved as PDF.
4. *(Lodgments)* The last lodged return *(label to confirm)*, printed to PDF: `2025 - ITR Portal Copy - Entity` (CTR, TTR, PTR or SMSF AR to match).
5. *(FYI)* Return copy to Work Papers, PBC. The summary and account statements aren’t in the filing map yet: confirm the cabinet with the manager.
- The income tax and activity statement account PDFs are for our file only; they don’t go to the client.

### 6.7 Send the welcome email (Admin, Manager)

**Draft the welcome email**. FYI Docs, your own FYI login (Microsoft 365).

1. *(Documents list)* Tick the attachments: each company’s ASIC extract and debt report, any ASIC invoice, and any ATO payment plan or payment advice. Leave the account statements on file.
2. *(toolbar)* **Share** ▾, the email option, as in 4.3.
3. *(Create Email drawer)* **Template**: type `Welcome` and pick the one that matches. **Name**, **Cabinet** Correspondence, 2027.
4. *(Save or Send)* **Draft in Outlook** to finish in Outlook, or **Draft in FYI** if the accountant reviews it in FYI. **Create**.
5. *(Outlook)* For each entity add a picture of the ATO portal summary and accounts summary, TFN redacted: save the page as PDF, redact the TFN, then snip the redacted PDF.
6. *(Outlook)* The accountant approves; send to the client if the partner said so, otherwise to the partner as a draft. Always copy admin.
- The guide calls this the welcome email (Part 4 step 9, Part 5 steps 16 and 17). It goes once every entity is on the ATO and ASIC portals and ID verification is final.

### 6.8 Check the portal against the proposal (Manager)

**Compare the proposal**. Ignition, your own Ignition login.

1. *(client page)* Open the client and its accepted proposal. Compare the services with the For action list from 6.6.
2. *(short scope)* Amend with the partner before work starts: revoking a sent proposal returns it to Draft, then re-send. Claude’s ignition-proposal-builder prices the extra lodgements.
3. *(Monday)* Update the item’s fee and status.

## Phase 7: SMSF in BGL

### 7.1 Add the fund (Admin)

**Add the fund**. BGL Simple Fund 360, your own BGL login.

1. *(before you start)* Confirm with the partner or accountant that the fund is going into BGL. Open the fund and its members in XPM; you will copy from them.
2. *(left rail HOME)* In **Search by Entity Label** type the fund name. Only if it isn’t there: **+ Add New Entity**.
3. *(SMSF Setup)* **Entity Type** SMSF, **Select Badge** Fortis Badge, **SMSF Name** and **Entity Code**, **ABN** and **TFN**, **Are you entering opening balances?** No, **Date Formed** and **Financial Year**. Save *(label to confirm)*.
4. *(SMSF Created)* Click **Enter SMSF Details**, or go back to **HOME** and search the new fund’s name to open its home page.
5. *(fund page)* **FUND DETAILS**, the **SMSF address**, **Save changes**.
6. *(later)* Once signed: **Trust Deed**, **Upload** for the deed and the member declarations. The auditor needs both.

### 7.2 Relationships and members (Admin)

**Relationships**. BGL Simple Fund 360, your own BGL login.

1. *(fund page)* **FUND RELATIONSHIPS** tab.
2. *(cards)* **Accountant**, **Auditor** and **Tax Agent** are standard for John’s team; confirm the HZ team’s. Add **Entity Contacts** and **Trustee** with **+ Add** at the foot of each card.
- Members may sync in from XPM with their TFNs: search before you add.

**Members**. BGL Simple Fund 360, your own BGL login.

1. *(left rail)* **MEMBER**, then **Member List**, or the shortcut **Add Accumulation Member**. A new member is always Accumulation.
2. *(new member)* **Select Member From Contacts**: search and select. **Start Date**: a new fund uses the ABN registration date; for an existing fund ask the manager (or arrange the transfer from the previous firm’s BGL). **Save**.
3. *(prompt)* **Would you like to input opening balances for this member?** Click **No**. The accounting team adds them.

### 7.3 SuperStream and ESA letters (Admin)

**Wait for regulation**. Super Fund Lookup, no login.

1. *(search)* Search the fund, open it and read **Status**. A new fund takes about 28 days; “Election to be regulated is being processed” means not yet.

**Register for SuperStream**. BGL Simple Fund 360, your own BGL login.

1. *(left rail)* **CONNECT**, **SuperStream Dashboard**.
2. *(dashboard)* **All Funds**, search the fund, tick it, **Register** at top left.
3. *(pop-up)* John Kalachian as the accountant, validate. Diary a check for the next day.
- The guide and the BGL procedure say **Register** is at the top right; the firm’s screenshot shows the blue **Register** button at the top left, next to **Change ESA**.

**ESA letters**. BGL Simple Fund 360, your own BGL login.

1. *(fund’s SuperStream page)* **Export** ▾, **Notification Letters (New ESA Registration)**.
2. *(Report Pack List)* **Download**: keep the Trustee Notification Letter, Employer Notification Letter and Super Standard Choice Form.
3. *(FYI)* Name them `2027 - ESA Trustee Notification Letter - Fund` (Employer Notification Letter, Super Standard Choice Form likewise) and file them.
4. *(email)* Send them on the same email chain as the set-up and ask the client to pass them to employers.
- On the ATO portal, make sure BGL is the fund’s nominated SuperStream ESA. The guide says it’s in the fund’s details on the portal *(label to confirm)*.

## Phase 8: Close-out

### 8.1 Check Monday (Manager)

**Check the items**. monday.com, your own monday.com login.

1. *(board)* Open Annual Compliance 2026-2027 and search the group name.
2. *(each item)* Check group name, entity type, fee (head entity) and manager; click the **Status** cell to correct it.
3. *(item)* For a note to the team: the speech-bubble icon beside the item name, **Write an update**, @name, **Update**.

### 8.2 Update the AML/CTF register (Admin)

**Run the AML/CTF report**. XPM (Xero Practice Manager), your own Xero login.

1. *(top bar)* **Reports**, then the **AML/CTF Report** among the saved reports *(label to confirm)*.
2. *(report)* Run it and export it *(label to confirm)*, then update the register with new clients and any open CDD issues.
- New set-ups count as new clients. Run the report regularly, not only at onboarding, so open CDD issues get closed.

### 8.3 File the structure chart (Admin)

**File and tell**. FYI Docs, your own FYI login (Microsoft 365).

1. *(top bar)* Green **+**, **Upload** the chart. Client: the main entity; **Cabinet** Permanent; 2027 and **Structure**. **Create**.
2. *(document)* Open it, **Comment** tab, type **@** and pick the manager and partner, **Comment**. They get an email or Teams notice.

### 8.5 Set the partner's check-ins (Admin)

**Book the check-ins**. Outlook (Microsoft 365), your mailbox; admin@ for follow-ups.

1. *(Calendar)* **New event**: `6-week check-in: <client>`, the date, invite the partner, **Reminder**, **Save**.
2. *(repeat)* Again for 12 and 26 weeks after acceptance.
