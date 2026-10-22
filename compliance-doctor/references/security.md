# Security & infrastructure risks (S1–S10)

Same entry format as `fintech.md`. These apply to almost every app. For financial apps they also back up GLBA (F17). For health apps they back up the HIPAA Security Rule (H4–H7).

### S1 · Broken object-level auth / Supabase RLS off — 🟠
**Detect:** Routes that load a record by an ID from the URL or body (`params.id`, `req.params.accountId`, `searchParams.get('id')`) without scoping the query to the signed-in user (`where: { id, userId: session.user.id }`) or checking ownership after loading. With Supabase, look for tables without `ENABLE ROW LEVEL SECURITY`, policies like `using (true)`, the `service_role` key used in client code or `NEXT_PUBLIC_*`, and `anon` grants on sensitive tables. Firebase: rules with `allow read, write: if true` or only `request.auth != null`. Try the mental test "change 123 to 124 in the URL". Would it return someone else's data?
**Not a finding if:** Every query is scoped by the authenticated principal, or RLS is on with owner policies and only the anon key reaches the browser.
**Penalty:** This is the most common real-world leak in vibe-coded apps. It triggers state breach-notification laws in all 50 states (per-state AG penalties, often up to $500k–$750k per breach, e.g., NY SHIELD up to $250k). For financial apps, the FTC Safeguards Rule requires notifying the FTC within 30 days if 500+ customers are affected (16 CFR 314.4(j)). Under CCPA, consumers can sue for $100–$750 each per incident (Cal. Civ. Code 1798.150).
**Fix:** Scope every query by `session.user.id` (or turn on RLS with `auth.uid() = user_id` policies), and keep `service_role` server-only.
**Bill:** LAWSUIT: $100–$750 × users (CCPA, CA users only. Assume 12% of users are in CA if unknown). GOV: state AG $10k–$250k.

### S2 · Hardcoded or exposed secrets — 🟡 (🟠 if they unlock PII or money)
**Detect:** Live keys in source (`sk_live_`, `rk_live_`, `AKIA…`, private keys, `ghp_`, `xox*`, `sk-ant-`, `service_role` JWTs), secrets in `NEXT_PUBLIC_*`/`VITE_*`/`EXPO_PUBLIC_*` (these ship to the browser), `.env` files tracked by git, or secrets in git history. **Never print values.** Redact to the first 4 characters + `…`.
**Not a finding if:** The value is a publishable key (`pk_`) or a documented test key, or the value is a placeholder.
**Penalty:** Scraper bots find keys pushed to public repos within minutes. Exposure means drained Stripe balances, cloud bills, or full DB dumps, and a breach of any PII behind the key (see S1 penalties).
**Fix:** Rotate the key now, move it to server-only env vars or a secrets manager, and purge it from git history.
**Bill:** LOSS: whatever the key unlocks (Stripe balance, cloud spend cap).

### S3 · Trusting client-side state — 🟡
**Detect:** The server reads `role`, `isAdmin`, `plan`, `price`, `balance`, or `userId` from the request body or from client-set cookies/localStorage instead of from the session or DB. Price or amount is computed on the client and charged as-is. Admin checks happen only in React.
**Not a finding if:** The server re-derives identity, role, plan, and price from trusted sources.
**Penalty:** Users edit the JSON payload to become admin, pay $0, or move money as another user. Losses are uncapped.
**Fix:** Derive identity and privileges from the server session, and look up prices server-side by ID.
**Bill:** LOSS: uncapped.

### S4 · Unencrypted sensitive data at rest — 🟠
**Detect:** Plaintext columns for SSN, tax ID, passport/DL numbers, bank account and routing numbers, DOB, or health fields. Plaid access tokens stored in plaintext. No field-level encryption, KMS, or pgsodium.
**Not a finding if:** Sensitive fields are encrypted at the application level (or tokenized by a vault provider), and keys are held outside the DB.
**Penalty:** Most state breach laws exempt encrypted data, so plaintext turns any leak into a notifiable breach. GLBA Safeguards requires encryption of customer information (16 CFR 314.4(c)(3)). GDPR fines scale with security failures (Art. 32/83).
**Fix:** Encrypt sensitive columns with app-level encryption (KMS-managed keys) or tokenize them through a vault, and store only last-4 where possible.
**Bill:** Multiplies the S1 bill (breach notification becomes mandatory).

### S5 · Missing rate limiting — 🟡
**Detect:** No rate limiting on login, OTP/SMS send, password reset, signup, transfer, or LLM endpoints.
**Not a finding if:** A middleware or edge limiter (Upstash, Cloudflare, express-rate-limit) covers these routes.
**Penalty:** Credential stuffing and account takeovers. SMS-pumping fraud (toll fraud) bills you per text. LLM-cost abuse. Takeovers of financial accounts also raise Reg E unauthorized-transfer liability (F4).
**Fix:** Add per-IP and per-account limits to auth, OTP, money, and AI routes.
**Bill:** LOSS: SMS pumping is commonly $1k–$50k per incident.

### S6 · Logging sensitive data — 🟠
**Detect:** `console.log`, logger, `print`, Sentry breadcrumbs, or analytics events containing passwords, tokens, SSNs, card data, account numbers, full request bodies on auth or payment routes, or health data. Verbose logging left on in production.
**Not a finding if:** Logs are scrubbed (Sentry `beforeSend`, pino redact paths) and bodies aren't logged on sensitive routes.
**Penalty:** Card data in logs is a PCI violation (F19). PII in third-party log tools is a disclosure under GDPR/CCPA and can be a breach. PHI in logs without a BAA is a HIPAA violation (H7).
**Fix:** Remove the log lines, add redaction config to your logger and error tracker, and purge the existing logs.
**Bill:** See F19 / H7 depending on the data.

### S7 · Missing MFA — 🟠 (financial or health apps) / 🟢 (others)
**Detect:** Username and password only for users, and especially for admin dashboards, with no TOTP, passkeys, or SMS second factor on login or on sensitive actions (new payee, large transfer, changing payout bank).
**Not a finding if:** MFA is enforced for staff/admin access and offered or required for users on high-risk actions.
**Penalty:** GLBA Safeguards requires MFA for anyone accessing customer information systems (16 CFR 314.4(c)(5)). Account takeovers create Reg E liability. HIPAA requires reasonable access controls (45 CFR 164.312(d)).
**Fix:** Enforce MFA for all admin/staff access, and require step-up auth for payouts, payee changes, and large transfers.
**Bill:** Folded into F17/F4.

### S8 · No backups / failover — 🟢
**Detect:** No point-in-time recovery, a single region, no restore test, no runbook.
**Penalty:** SLA penalties, churn, and lost transaction records. Financial record retention is required (BSA: 5 years, 31 CFR 1010.430).
**Fix:** Turn on PITR, test one restore, and write a one-page runbook.
**Bill:** None direct.

### S9 · No incident response plan — 🟠 (financial or health apps) / 🟢 (others)
**Detect:** No documented way to detect, contain, and notify. No security contact (`security.txt`, `SECURITY.md`).
**Penalty:** Missed deadlines: FTC 30 days (GLBA), HIPAA 60 days, GDPR 72 hours, state laws 30–60 days. Each missed deadline is its own violation.
**Fix:** Write a one-page incident response plan listing the notification deadlines that apply to you and who is on call.
**Bill:** Folded into the breach bills above.

### S10 · Insecure defaults — 🟢/🟡
**Detect:** CORS `*` on authenticated APIs, cookies without `HttpOnly`/`Secure`/`SameSite`, no CSRF protection on cookie-auth POSTs, missing security headers, debug mode in prod, open admin routes, public storage buckets.
**Fix:** Lock CORS to your origins, set secure cookie flags, close public buckets, and turn off debug.
**Bill:** None direct, unless it enables S1 or S3.
