# 🩺 Fintech Doctor

A Claude skill (`compliance-doctor`) that deep-scans your codebase for the legal, regulatory, security and money-losing risks in vibe-coded apps. It prints a diagnosis with a severity verdict, real penalties by law, what you could owe, what you did right, and a prescription for what to fix first.

**It diagnoses; it never edits your code.**

## Sample output

```text
||==========================================================================
||
||    🩺  C O M P L I A N C E   D O C T O R
||
||    Patient   ::  vibe-wallet
||    Severity  ::  ▓▓ ROYALLY FUCKED ▓▓
||    Mode      ::  LIVE
||    Stack     ::  Next.js 14 · Prisma · Stripe · Open Payments · Twilio
||
||==========================================================================
||  📊 VITALS                                    19 verified · showing top 5
||==========================================================================
||
||    🔴  Crime              ███                3
||    🟠  Fines              ████████           8
||    🟡  Money bugs         ███████            7
||    🟢  Tech debt          █                  1
||
||==========================================================================
||  💚 HEALTHY VITALS  —  what you did right
||==========================================================================
||
||    ✔  All DB access goes through Prisma; no raw SQL, so no injection paths
||                                                          src/lib/db.ts
||    ✔  Card entry never touches your server; no PAN or CVV anywhere in schema
||                                                          prisma/schema.prisma
||    ✔  Uses the official Open Payments SDK instead of hand-rolled ILP signing
||                                                          package.json:1
||
||==========================================================================
||  🩻 DIAGNOSIS
||==========================================================================
||
||  #1  🔴  THE IRS IS ALREADY LOOKING FOR YOU
||  --------------------------------------------------------------------------
||      Problem  |  Landing page says "Your new bank" and "Your money is FDIC
||               |  insured", but there's no charter and no partner bank.
||      Where    |  src/app/page.tsx:4
||      Penalty  |  18 USC 709 — misusing the FDIC name is a federal crime (fine +
||               |  up to 1 yr); FDIC civil money penalties, 12 USC 1828(a)(4);
||               |  state banking codes bar calling yourself a bank.
||      Fix      |  Delete both claims; later, use your partner's exact "Member FDIC"
||               |  disclosure.
||
||  #2  🔴  THE IRS IS ALREADY LOOKING FOR YOU
||  --------------------------------------------------------------------------
||      Problem  |  User funds sit in `User.balance` and move between users inside
||               |  your own DB. No sponsor bank or licensed processor holds them.
||      Where    |  src/app/api/transfer/route.ts:7-8, prisma/schema.prisma:5
||      Penalty  |  18 USC 1960 — unlicensed money transmission, felony (fines + up
||               |  to 5 yrs); 31 USC 5330 — no FinCEN MSB registration, up to
||               |  $5,000/day; plus state money transmitter penalties.
||      Fix      |  Move custody to a sponsor bank FBO or BaaS partner before taking
||               |  more real deposits.
||
||  #3  🔴  THE IRS IS ALREADY LOOKING FOR YOU
||  --------------------------------------------------------------------------
||      Problem  |  A user-facing alert says the account was "flagged for suspicious
||               |  activity and reported to FinCEN."
||      Where    |  src/lib/alerts.ts:1
||      Penalty  |  31 USC 5318(g)(2) — disclosing a SAR is prohibited; civil
||               |  penalties (31 USC 5321), criminal up to $250k + 5 yrs (§5322).
||      Fix      |  Use neutral copy ("We need more information to complete this
||               |  transfer"); keep flag reasons admin-only.
||
||  #4  🟠  GET A LAWYER ON SPEED DIAL
||  --------------------------------------------------------------------------
||      Problem  |  Transfers run with no sanctions screening of sender or recipient.
||      Where    |  src/app/api/transfer/route.ts:3 → :8 (no SDN check in path)
||      Penalty  |  IEEPA, 50 USC 1705 — strict liability, up to $377,700 per
||               |  violation or 2× the transaction; willful violations are criminal.
||      Fix      |  Screen users at signup and recipients on every transfer via a
||               |  sanctions API; log each result.
||
||  #5  🟠  GET A LAWYER ON SPEED DIAL
||  --------------------------------------------------------------------------
||      Problem  |  Landing page promises "Earn 8% APY on every dollar" with no bank
||               |  interest program or registered broker behind it.
||      Where    |  src/app/page.tsx:5
||      Penalty  |  Securities Act §5 + state securities laws — unregistered yield
||               |  product; BlockFi paid $100M to the SEC and states for this.
||      Fix      |  Remove the APY claim until a bank partner's disclosed interest
||               |  program backs it.
||
||==========================================================================
||  💸 THE BILL          all 19 findings · statutory worst case, not a prediction
||==========================================================================
||
||      Government fines    ||   $560k  –  $5.9M
||      Lawsuit exposure    ||   $5.5k  –  $520k
||      Criminal exposure   ||   YES — #1, #2, #3
||      Direct losses       ||   uncapped: anyone can debit any account (#12),
||                          ||   forged webhooks mint balance (#13)
||
||      Assumed: 250 users · 60 days live · 4 transfers/user/mo · 12% in CA
||
||==========================================================================
||  💊 PRESCRIPTION       next steps in order · nothing has been changed
||==========================================================================
||
||    [ TODAY ]
||      1. Pull "your new bank", "FDIC insured", "8% APY" + countdown   → #1 #5 #6
||      2. Rotate the leaked sk_live_ key; untrack .env; purge git history → #14
||      3. Swap the "reported to FinCEN" alert for neutral copy           → #3
||    [ THIS WEEK ]
||      4. Take sender from the session, not body.userId; scope
||         /api/accounts/[id] to its owner                                → #12 #9
||      5. Pause real-money transfers until a licensed partner holds
||         funds; then register with FinCEN                               → #2
||      6. Add a KYC + sanctions vendor at signup and on every transfer   → #4 #7
||    [ BEFORE YOU SCALE ]
||      7. Verify webhook signatures; integer cents + double-entry ledger
||         + idempotency keys                                    → #13 #15 #16 #17
||
||==========================================================================
||  📋 Want the full report? 14 more findings (6 🟠 · 7 🟡 · 1 🟢)
||     Say "full report".
||  ⚖️  Not legal advice — talk to a fintech lawyer before launch.
||==========================================================================
```

## Install

**Claude Code** (personal skill, available in every project):

```bash
git clone https://github.com/DanielLambo/Fintech_Doctor.git
cp -R Fintech_Doctor/compliance-doctor ~/.claude/skills/
```

Then, in any project, run `/compliance-doctor` or ask something like *"run the doctor on this app"* or *"am I going to get fined for this?"*. Add `full` for the uncut report.

## How it works

1. **Triage.** It asks four questions: does real money move, are there real users, is real personal data collected, is anything public. All "no" means **SANDBOX** mode (top 3 findings plus a "before you flip to live keys" checklist). Any "yes" means **LIVE** mode (top 5 findings, the rest on request).
2. **Scan.** `scripts/scan.py` (stdlib Python, read-only) maps the stack and flags candidate risks with `file:line`. It also checks whether safeguards exist (OFAC screening, idempotency, webhook signatures, RLS, MFA, …) and redacts any secrets it finds.
3. **Examine.** Claude traces every money path, the auth scoping, the data model and the user-facing copy. Nothing becomes a finding without evidence.
4. **Grade.**

   | Tier | Label | Meaning |
   |---|---|---|
   | 🔴 | The IRS is already looking for you | potential crime |
   | 🟠 | Get a lawyer on speed dial | regulatory fines |
   | 🟡 | Future you is crying | bugs that lose money |
   | 🟢 | You're good... mostly | tech debt |

5. **Bill and prescribe.** It estimates government fines and lawsuit exposure (statutory worst case), flags criminal exposure, and gives next steps grouped as TODAY / THIS WEEK / BEFORE YOU SCALE.

## What it checks (~70 risks)

| Area | Highlights |
|---|---|
| **Fintech** | unlicensed money transmission (18 USC 1960), OFAC, BSA/AML & KYC, SAR tipping-off, Reg E disputes, Remittance Rule (Rafiki/ILP), FDIC/"bank" claims, double-entry ledgers, float money, idempotency & races, unverified webhooks, FCRA/ECOA, TILA/usury/EWA, securities & APY claims, unclaimed property, card-network risk, PCI, GLBA Safeguards, UDAAP, Reg S-P |
| **HIPAA & health** | HIPAA vs. FTC Health Breach Notification Rule applicability, BAAs, tracking pixels, PHI to LLMs, audit logs, encryption, breach notice, WA My Health My Data |
| **Privacy & consumer** | COPPA, GDPR (CDN/font leaks), CIPA session replay, BIPA, CCPA/CPRA, TCPA, CAN-SPAM, ADA, ROSCA, E-SIGN, record-keeping, cross-border |
| **Security** | BOLA / Supabase RLS, hardcoded & `NEXT_PUBLIC_` secrets, client-trusted state, plaintext PII, rate limiting, sensitive logging, MFA, incident response |
| **AI / vibe-coding** | hallucinated & typosquatted packages, prompt injection with money tools, agent "god mode", unvetted APIs, duplicated logic, test coverage collapse |

## Layout

```
compliance-doctor/
├── SKILL.md                  workflow, tiers, output format
├── scripts/scan.py           first-pass scanner (read-only, stdlib only)
├── references/
│   ├── fintech.md            F1–F22
│   ├── security.md           S1–S10
│   ├── privacy-consumer.md   P1–P12
│   ├── hipaa.md              H0–H10
│   ├── ai-vibe.md            A1–A10
│   └── exposure.md           how "the bill" is priced
└── examples/sample-report.md
```

## Disclaimer

Penalty figures are statutory maximums as of 2025, and many are adjusted for inflation every year. The bill is a worst-case scale estimate, not a prediction. **This is not legal advice.** Talk to a fintech lawyer before launch.
