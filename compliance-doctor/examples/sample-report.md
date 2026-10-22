# Sample report

A run against a deliberately broken test wallet app (`vibe-wallet`). Triage answers: real money moves, ~250 real users, SSNs collected, landing page public. That means **LIVE** mode.

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

Want me to start on any of these? Tell me the numbers.
