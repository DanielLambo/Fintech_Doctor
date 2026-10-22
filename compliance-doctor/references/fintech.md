# Fintech risks (F1–F22)

Each entry: **Tier** · **Detect** (what to read and trace) · **Not a finding if** (false-positive guards) · **Penalty** · **Fix** · **Bill** (how to price it; see `exposure.md`).

Dollar figures are statutory maximums as of 2025 and many are inflation-adjusted every year. Write them as "up to" or "about".

## Contents
- F1 Unlicensed money transmission · F2 OFAC · F3 SAR tipping-off · F4 Reg E errors · F5 Remittance rule
- F6 FDIC/"bank" claims · F7 No ledger · F8 Float money · F9 Idempotency/races · F10 Unverified webhooks
- F11 (see security.md S1) · F12 FCRA/ECOA · F13 TILA/usury/EWA · F14 Securities/advice · F15 Unclaimed property
- F16 Card networks · F17 GLBA Safeguards · F18 BSA/AML program · F19 PCI · F20 UDAAP · F21 AI credit models · F22 SEC / Reg S-P

---

### F1 · Unlicensed money transmission — 🔴
**Detect:** The app holds user funds (a stored balance users can withdraw or send) or moves money between people: P2P, remittance, wallets, Rafiki/ILP outgoing payments, crypto custody. Trace where the money sits. If it's in the company's own bank or crypto account and is tracked in a `balance` column, the app is acting as the transmitter.
**Not a finding if:** A licensed partner holds the funds and is the transmitter of record: a sponsor bank through a BaaS (Unit, Synctera, Treasury Prime, Column, Increase, Lithic, Moov), Stripe Connect or Treasury, Dwolla, Wise Platform, Circle, Bridge, or an FBO account in the partner's name. Also not a finding if the app only initiates payments the user's own bank executes (pure Plaid/Open Banking pay-by-bank with no custody). Mention the partner's agreement terms as a checklist item.
**Penalty:** 18 USC 1960 — operating an unlicensed money transmitting business is a federal felony: fines and up to 5 years in prison. 31 USC 5330 / 31 CFR 1022.380 — failing to register with FinCEN as an MSB: up to $5,000 per violation, and each day is a separate violation. State money transmitter laws require a license in each state you serve, and each state sets its own penalties.
**Fix:** Move custody and transmission to a licensed partner (sponsor bank FBO or licensed processor) before real funds flow, then register with FinCEN if you're still an MSB.
**Bill:** GOV: $5,000 × days operating (low: 30 days). Criminal: yes.

### F2 · No OFAC sanctions screening — 🟠 (🔴 if willful)
**Detect:** Look at signup/KYC and every outgoing transfer, payout, or crypto withdrawal. Is the name, address, country, or wallet address screened against the SDN list? Is there country blocking for comprehensively sanctioned jurisdictions (Cuba, Iran, North Korea, Syria, Crimea/DNR/LNR regions)?
**Not a finding if:** A KYC vendor with sanctions screening runs at onboarding and on transfers (ComplyAdvantage, Alloy, Persona with watchlists, Sardine, Middesk, Chainalysis/TRM/Elliptic for wallets), or the sponsor bank or processor contractually screens every transaction. Ongoing re-screening is still worth a checklist item.
**Penalty:** IEEPA (50 USC 1705) — civil penalty up to about $377,700 per violation or twice the transaction value, whichever is greater. Liability is strict, so intent doesn't matter. Willful violations are criminal: up to $1M and 20 years.
**Fix:** Screen users at signup and counterparties on every transfer through a sanctions API, block sanctioned jurisdictions by IP and address, and log the result of every screening.
**Bill:** GOV low $0 (no sanctioned party found yet), high $377,700 × an assumed 1–3 transactions. Note that the real exposure depends on whether a sanctioned person actually used the app.

### F3 · SAR "tipping off" — 🔴
**Detect:** User-facing strings (toasts, emails, support macros, AI support-bot prompts) that tell a user their account or transaction was flagged as suspicious, is under AML or fraud investigation, or was reported to FinCEN or authorities. Grep UI copy and LLM system prompts for "suspicious activity", "flagged", "reported", "money laundering", "under review".
**Not a finding if:** The copy is neutral and says nothing about suspicion or reporting ("We need a bit more information to complete this transfer", "This transfer couldn't be completed"). Generic fraud alerts sent to the account owner about a third party ("Was this you?") are fine.
**Penalty:** 31 USC 5318(g)(2) prohibits disclosing a SAR or the fact one was filed. Violations bring BSA civil penalties (31 USC 5321) and criminal penalties (31 USC 5322: up to $250k and 5 years, or $500k and 10 years as part of a pattern).
**Fix:** Replace the copy with neutral language that doesn't mention monitoring, flagging, or reporting, and keep the internal flag reason in admin-only fields.
**Bill:** GOV: low $25k, high $250k per message template. Criminal: yes.

### F4 · Reg E error resolution / unauthorized transfers — 🟠
**Detect:** For consumer accounts that move money electronically, check for a way to dispute a transaction, a 10-business-day investigation clock, provisional credit when the investigation runs longer, and limits on consumer liability for unauthorized transfers. Look for a `disputes` table, a support flow, and job timers.
**Not a finding if:** The account is business-only (Reg E covers consumers), or a sponsor bank or processor runs disputes end to end and the app routes users to it.
**Penalty:** EFTA (15 USC 1693m) / Reg E (12 CFR 1005.6, 1005.11) — individual actual damages plus $100–$1,000; class actions up to the lesser of $500,000 or 1% of net worth. Treble damages if provisional credit was withheld in bad faith (1693f(e)). You also absorb the unauthorized-transfer losses above the $50/$500 consumer liability limits. The CFPB can add civil penalties.
**Fix:** Add a dispute intake that timestamps notice, a 10-business-day investigation SLA with provisional credit, and written results to the user.
**Bill:** LAWSUIT: low $1,000 × 1% of users, high min($500k, …) + $1,000 × users disputing. GOV: CFPB tier-1 penalty if the app is large.

### F5 · Remittance Transfer Rule (Reg E Subpart B) — 🟠
**Detect:** Consumer transfers to recipients abroad (cross-border ILP/Rafiki, FX corridors, wallet-to-foreign-wallet). Check for a pre-payment disclosure (exchange rate, fees, taxes, amount received), a receipt with the date funds will be available and error and cancellation rights, a 30-minute cancellation window, and the error-resolution process (12 CFR 1005.33).
**Not a finding if:** The provider made 500 or fewer remittance transfers in both the previous and the current calendar year (the normal-course-of-business safe harbor), or a licensed partner is the remittance provider of record and issues the disclosures. Keep this one in mind for anything built on Rafiki/ILP.
**Penalty:** EFTA damages as in F4 (class actions up to the lesser of $500k or 1% of net worth), refunds of fees and amounts, and CFPB enforcement with civil penalties under 12 USC 5565 (about $7k/day, $36k/day reckless, $1.4M/day knowing).
**Fix:** Show a pre-payment disclosure with the exact received amount, send a compliant receipt, enforce a 30-minute cancellation window, and route errors through a 90-day error-resolution flow.
**Bill:** LAWSUIT: as F4 for international transfers. GOV: tier-1 CFPB penalty × days.

### F6 · "FDIC insured" or "bank" misrepresentation — 🔴
**Detect:** Landing page, app store copy, onboarding, emails, and meta tags that say "FDIC insured", "your money is insured", "bank", "banking", "neobank", or "your new bank" when there is no charter. Also check for missing names: the FDIC's 2024 sign and advertising rule (12 CFR 328) requires naming the insured bank and saying deposits are insured only if the bank fails.
**Not a finding if:** The copy is accurate partner language: "Banking services provided by <Bank>, Member FDIC. <App> is a financial technology company, not a bank. FDIC insurance covers the failure of <Bank> only." Saying "not FDIC insured" is fine.
**Penalty:** 18 USC 709 — misusing the FDIC name or implying insurance is a federal crime (fine and up to 1 year). FDIC civil money penalties and cease-and-desist orders under 12 USC 1828(a)(4) and Part 328 Subpart B. Most states' banking codes make it unlawful to call yourself a "bank" without a charter.
**Fix:** Remove "bank" and "FDIC insured" claims, or replace them with the exact partner disclosure that names the bank and says the company isn't one.
**Bill:** GOV: low $10k, high $1M+ (FDIC CMPs scale with willfulness and duration). Criminal: yes.

### F7 · No double-entry ledger or FBO reconciliation — 🟡
**Detect:** A mutable `balance` column updated directly (`balance: { increment }`, `UPDATE ... SET balance = balance - x`) with no immutable journal of debits and credits. There is also no job that reconciles internal balances against the bank or FBO statement.
**Not a finding if:** Balances are derived from or verified against an append-only ledger (TigerBeetle, Formance, Modern Treasury Ledgers, Blnk, or a `ledger_entries` table with paired debit/credit rows) and a reconciliation job exists. A cached balance column alongside a real ledger is fine.
**Penalty:** No single statute. This is how Synapse collapsed in 2024: tens of millions in end-user funds couldn't be matched to owners. Regulators, the sponsor bank, and auditors require proof of whose money is whose. Without it you can't defend Reg E claims or a state MTL exam.
**Fix:** Add an append-only double-entry ledger, write every balance change as paired entries in one DB transaction, and reconcile daily against the bank or FBO statement.
**Bill:** LOSS: unquantified (money you can't attribute). No direct GOV figure.

### F8 · Floating-point money — 🟡
**Detect:** `Float`, `Double`, `REAL`, or `FLOAT` columns for amounts. `parseFloat`/`Number()` on amounts. JS number arithmetic on currency. `toFixed(2)` used as rounding. `Math.round(x * 100)` scattered around.
**Not a finding if:** Amounts are stored as integer minor units (`BigInt`/`Int` cents) or `Decimal`/`NUMERIC(19,4)`, and math uses a decimal library (decimal.js, big.js, dinero.js, `Prisma.Decimal`). Display-only formatting of an already-correct value is fine.
**Penalty:** Rounding drift breaks reconciliation, and disclosed amounts stop matching charged amounts, which creates Reg E error claims (12 CFR 1005.11) and Remittance Rule accuracy problems (1005.31). You owe restitution to every affected user.
**Fix:** Store integer cents (or `Decimal`) and do all money math in a decimal library. Convert to float only for display.
**Bill:** LOSS: small per transaction but on every one. LAWSUIT: overlaps with F4 if disclosed and charged amounts differ.

### F9 · No idempotency / race conditions — 🟡
**Detect:** POST handlers that move money with no idempotency key, no unique constraint on a request ID, no `SELECT ... FOR UPDATE`, no serializable transaction, and a balance check done separately from the debit (check-then-act). Double-clicking the submit button sends twice. Retried jobs re-pay.
**Not a finding if:** An idempotency key is enforced by a unique index, the debit is atomic (`UPDATE ... SET balance = balance - x WHERE balance >= x` or a row lock), and the processor call passes an idempotency key.
**Penalty:** Direct loss on every duplicate and every overdraft, plus a Reg E error claim each time (12 CFR 1005.11).
**Fix:** Require an `Idempotency-Key` per money request with a unique index, debit atomically inside a locked transaction, and pass idempotency keys to the processor.
**Bill:** LOSS: average transfer × duplicate rate (assume 0.1–1%).

### F10 · Unverified webhooks — 🟡
**Detect:** Webhook routes (Stripe, Plaid, Rafiki, Circle, KYC vendors) that act on the body without verifying a signature. Watch for `JSON.parse(body)` with no `constructEvent`/HMAC check, or a parsed JSON body where the signature check needs the raw body.
**Not a finding if:** Signature verification runs on the raw body with a constant-time compare and secrets kept server-side, and replays are rejected (timestamp tolerance or event ID dedupe).
**Penalty:** An attacker POSTs `payment_succeeded` and credits themselves. The loss is whatever amount they type in. Rafiki webhooks also drive incoming payment state.
**Fix:** Verify the provider signature on the raw body before parsing, dedupe on event ID, and re-fetch the object from the provider API before crediting.
**Bill:** LOSS: uncapped.

### F12 · FCRA / ECOA (credit and alternative data) — 🟠 (🔴 if obtained under false pretenses)
**Detect:** Pulling credit reports or scores, bank-data underwriting (Plaid Assets/Income), or "alternative data" used for eligibility, pricing, limits, or tenant/employment decisions. Check for a permissible-purpose record, consent capture, and adverse-action notices with specific principal reasons (and for an AI model, can it produce those reasons?).
**Not a finding if:** No credit or eligibility decisions are made, or a licensed lender partner makes the decision and sends the notices.
**Penalty:** FCRA 15 USC 1681n — willful violations: $100–$1,000 per consumer plus punitive damages and attorney fees. 1681q — obtaining reports under false pretenses: fine and up to 2 years. ECOA/Reg B (12 CFR 1002.9) — adverse-action notices need specific reasons, and the CFPB (Circular 2022-03) says "the model said no" isn't one. ECOA class actions up to the lesser of $500k or 1% of net worth, plus punitive damages up to $10k per individual.
**Fix:** Record permissible purpose and consent before each pull, and send adverse-action notices with the top specific reasons your model can actually explain.
**Bill:** LAWSUIT: $100–$1,000 × applicants affected. Criminal: only if false pretenses.

### F13 · TILA / Reg Z, state usury, EWA — 🟠
**Detect:** Cash advance, BNPL, earned-wage access, "instant pay" with fees or tips, credit lines, installment plans. Check for APR disclosure, finance-charge math, and state rate caps (often 36%). Expedite fees and "tips" can count as finance charges.
**Not a finding if:** A licensed lender partner originates the loans and issues the disclosures, and the app's copy matches them.
**Penalty:** TILA 15 USC 1640 — individual: twice the finance charge (min $200 / max $2,000 for most closed-end credit); class actions up to the lesser of $1M or 1% of net worth, plus fees. Loans above state usury caps can be void or uncollectible. EWA regulation is unsettled federally, and several states (and the NY AG's enforcement) treat fee/tip EWA as lending.
**Fix:** Run credit products through a licensed lender with Reg Z disclosures, compute and show APR including all fees and tips, and cap rates by state.
**Bill:** LAWSUIT: up to min($1M, 1% net worth). LOSS: void loans = uncollectible principal.

### F14 · Unregistered securities / investment advice — 🟠
**Detect:** "Earn X% APY", "guaranteed yield", interest on crypto, staking-as-a-service, pooled returns, robo-portfolio picks, "we recommend buying".
**Not a finding if:** Deposits sit at a bank partner paying disclosed interest under its own program, or a registered broker-dealer/RIA (e.g., DriveWealth or Alpaca as broker) carries the accounts and the app does no personalized recommending, with the disclosures in place.
**Penalty:** Securities Act §5 and Exchange Act enforcement. BlockFi paid $100M combined to the SEC and states for an unregistered crypto lending product. Giving personalized advice without registering as an adviser (Investment Advisers Act / state law) is a separate violation, with disgorgement and penalties.
**Fix:** Remove yield and return promises, and route investing through a registered broker/adviser with their disclosures, with no personalized picks.
**Bill:** GOV: low $100k, high scales with AUM (BlockFi: $100M).

### F15 · Unclaimed property (escheat) — 🟠
**Detect:** User balances that can sit forever with no dormancy tracking, no last-activity timestamp, no owner outreach, and no escheat reporting.
**Not a finding if:** A sponsor bank holds and escheats the funds, or a dormancy job and state reporting exist.
**Penalty:** State unclaimed property laws — after 3–5 years of inactivity balances belong to the state. Audits bring back-reporting plus interest (often around 12%/yr) and penalties (up to 25–50% of the amount in some states, e.g., Delaware).
**Fix:** Track last owner-initiated activity, send dormancy notices, and report and remit to the owner's state on its schedule.
**Bill:** GOV: dormant balances × (1 + 25% penalty). Usually small for young apps, so mention it, don't lead with it.

### F16 · Card network kill switch — 🟡
**Detect:** High-risk business types (crypto, gambling-adjacent, cash-like P2P, adult, nutraceuticals) on Stripe or a standard processor. Card-funded wallet top-ups. No fraud controls (3DS, Radar rules, velocity limits) on card funding.
**Not a finding if:** The business type is allowed under the processor's terms and fraud controls are on.
**Penalty:** Network monitoring programs (Visa VAMP, Mastercard ECM) bring fines of roughly $1,000s to $100k+/month. The MATCH/TMF list bars you from card processing for about 5 years. Processors (Stripe included) can freeze funds and hold reserves for 90–180 days.
**Fix:** Check the processor's restricted-business list against your model, turn on 3DS and Radar/velocity rules, and track your chargeback ratio monthly (keep it under 0.9%).
**Bill:** LOSS: frozen funds = your monthly volume × hold period.

### F17 · GLBA Safeguards Rule — 🟠
**Detect:** A financial product collecting customer financial information with no written information security program, no designated "qualified individual", no risk assessment, no MFA for anyone accessing customer data (16 CFR 314.4(c)(5)), no encryption, and no written incident response plan (314.4(h)). Look for `SECURITY.md`, `docs/security`, or a policy repo.
**Not a finding if:** A written program exists (even short) and the controls above are in place.
**Penalty:** FTC enforcement under GLBA and the FTC Act: consent orders with about 20 years of mandated security assessments. Since May 2024, 314.4(j) requires notifying the FTC within 30 days of discovering a breach of unencrypted data affecting 500+ customers. Separately, GLBA's pretexting provisions (15 USC 6821–6823) carry fines and up to 5 years (10 if aggravated). Those are the source of the often-quoted "$100k per violation" figure.
**Fix:** Write a 2–5 page infosec program (owner, risk assessment, access controls, MFA, encryption, vendor oversight, incident response) and actually turn on the controls it lists.
**Bill:** GOV: low $0 (first-time FTC orders are usually non-monetary), high: compliance cost of a 20-year order (~$50k+/yr).

### F18 · BSA/AML program (KYC/CIP, monitoring) — 🟠 (🔴 if willful)
**Detect:** An MSB or money-moving app with no identity verification at onboarding, no transaction monitoring rules (velocity, structuring, high-risk corridors), no SAR workflow, no AML officer, and AI-template KYC that only checks "a name and DOB were entered".
**Not a finding if:** The sponsor bank or BaaS runs CIP/KYC and monitoring and the app passes data through correctly.
**Penalty:** 31 CFR 1022.210 requires MSBs to have a written AML program. BSA civil penalties (31 USC 5321) run per violation per day, and fintech settlements reach the millions (e.g., Wise $2.5M multistate 2024, Block/Cash App $80M multistate 2025). Willful violations are criminal (31 USC 5322).
**Fix:** Use a KYC/CIP vendor at onboarding, add monitoring rules with case management and a SAR workflow, and name a BSA officer.
**Bill:** GOV: low $50k, high $1M+ depending on volume.

### F19 · PCI-DSS (storing card data) — 🟠
**Detect:** Card number, CVV, or expiry in your DB, logs, analytics, or your own form posting to your own server. Raw PAN in request bodies.
**Not a finding if:** Card entry happens in processor-hosted fields (Stripe Elements/Checkout, Adyen Drop-in, Braintree Hosted Fields) and you store only tokens and last4.
**Penalty:** Card brand fines passed through by your acquirer: about $5,000–$100,000 per month of non-compliance, plus forensic audit costs and breach liability. Storing CVV after authorization is never allowed.
**Fix:** Switch to processor-hosted card fields, delete stored PAN/CVV, and purge them from logs and backups.
**Bill:** GOV-like (contractual): $5k–$100k × months.

### F20 · UDAAP / dark patterns — 🟠
**Detect:** Fake scarcity or countdown timers, hidden or drip-priced fees, "tips" defaulted on, pre-checked add-ons, misleading APY/fee comparisons, confirmshaming, hard-to-find fee disclosures.
**Not a finding if:** Timers are real deadlines and fees are disclosed upfront next to the action.
**Penalty:** Dodd-Frank 12 USC 5531/5536 enforced under 5565. Civil penalties of about $7k/day, about $36k/day if reckless, and about $1.4M/day if knowing (inflation-adjusted), plus restitution. State UDAP laws stack on top.
**Fix:** Remove fake urgency, default tips to $0, and show every fee before the user confirms.
**Bill:** GOV: low tier-1 × 30 days, high tier-2 × days live.

### F21 · AI / black-box credit decisions — 🟠
**Detect:** An LLM or ML model deciding approval, limits, or pricing using inputs that proxy for protected classes (ZIP, name, language, device). No disparate-impact testing. No explainable reasons.
**Not a finding if:** Decisions use documented, tested features and the model produces specific adverse-action reasons.
**Penalty:** ECOA/Reg B and the Fair Housing Act — disparate-impact liability, CFPB/DOJ settlements in the millions, and class actions (see F12 caps).
**Fix:** Remove proxy features, run disparate-impact tests before launch, and generate reason codes from the model.
**Bill:** LAWSUIT: see F12. GOV: settlement range $1M+.

### F22 · SEC cyber disclosure / Reg S-P — 🟠 (only if it applies)
**Detect:** Only for public companies (Form 8-K Item 1.05: material cyber incidents within 4 business days) or SEC registrants such as broker-dealers and RIAs (Reg S-P as amended 2024: written incident response program and customer notice within 30 days, compliance from Dec 2025 for large entities and Jun 2026 for smaller ones). Most startups: not applicable, so skip.
**Penalty:** SEC enforcement. Penalties in disclosure cases have ranged from about $1M to $35M (e.g., Altaba $35M).
**Fix:** If you're a registrant, write the incident response program and the 30-day notice workflow.
**Bill:** GOV: $1M–$35M range only if a registrant.
