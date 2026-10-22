# Privacy & consumer-protection risks (P1–P12)

Same entry format as `fintech.md`. Federal FTC civil penalties are about $53,088 per violation (2025, inflation-adjusted every January).

### P1 · COPPA (no age gate) — 🟠
**Detect:** Signup collects no DOB or age attestation and the product could attract under-13s (games, teen finance, allowance apps, schools), or the code has "actual knowledge" signals (age fields allowing <13, kid accounts).
**Not a finding if:** The product is clearly adult-only (most fintech requires 18+ for KYC anyway) and signup enforces 18+. Flag it only if a minors' path exists.
**Penalty:** COPPA (15 USC 6501; 16 CFR 312) — up to about $53,088 per violation (per child). Epic Games paid $275M.
**Fix:** Add a neutral age screen (DOB, not "Are you 13?"), block under-13s or collect verifiable parental consent.
**Bill:** GOV: $53k × under-13 users (assume 0–1% of users when there's a kids' angle).

### P2 · GDPR — third-party CDN / font leaks — 🟠 (only with EU/UK users)
**Detect:** `fonts.googleapis.com`, `fonts.gstatic.com`, `cdnjs`, `unpkg`, `jsdelivr`, Typekit, or embedded third-party widgets loaded before consent. Analytics loaded without consent. No privacy policy or lawful-basis notice.
**Not a finding if:** There are no EU/UK users, fonts are self-hosted (`next/font/google` downloads at build and self-hosts, so it's fine), or loading waits for consent.
**Penalty:** GDPR Art. 83 — up to €20M or 4% of global annual revenue. In 2022 a Munich court (LG München I, 3 O 17493/20) awarded €100 per visitor for Google Fonts IP leakage, which set off waves of demand letters.
**Fix:** Self-host fonts and assets, and gate analytics and third-party embeds behind a consent banner.
**Bill:** LAWSUIT: €100 × EU visitors (assume 5% of users if unknown). GOV: rarely maxed for small apps.

### P3 · CIPA — session replay without consent — 🟠
**Detect:** Hotjar, FullStory, LogRocket, Microsoft Clarity, PostHog/Sentry session replay, Mouseflow, or rrweb running for all visitors without opt-in consent. Chat widgets that record. "Keystroke" capture on forms.
**Not a finding if:** Replay loads only after explicit consent, or replay is off, or inputs are fully masked *and* there are no California users (still risky).
**Penalty:** California Invasion of Privacy Act, Cal. Penal Code 631/637.2 — $5,000 per violation (plaintiffs argue per session) in private suits. This is a very active class-action area.
**Fix:** Load session replay only after explicit opt-in, mask all inputs, and disclose it in the privacy policy.
**Bill:** LAWSUIT: $5,000 × CA sessions (assume CA = 12% of users, 1 session each).

### P4 · BIPA — biometrics without written release — 🟠
**Detect:** Face/fingerprint templates processed server-side, selfie liveness/face match done in-house, voiceprints. Note: device-native Face ID/Touch ID through `LocalAuthentication` or `BiometricPrompt` never gives you the biometric. That's generally not BIPA, so check whether the template leaves the device.
**Not a finding if:** Only on-device OS biometrics are used, or a KYC vendor collects the biometric under its own BIPA consent and retention schedule and you never receive it.
**Penalty:** Illinois BIPA (740 ILCS 14/20) — $1,000 per negligent violation, $5,000 per intentional or reckless one. After the 2024 amendment, that's one violation per person per collection method, not per scan. Texas (CUBI) and Washington have their own laws, enforced by the AG.
**Fix:** Get a written release before collecting, publish a retention and destruction schedule, and prefer on-device biometrics.
**Bill:** LAWSUIT: $1,000–$5,000 × IL users (assume 4% of users).

### P5 · CCPA/CPRA (no opt-out) — 🟠
**Detect:** Ad pixels or data sharing (Meta Pixel, TikTok, Google Ads, data brokers) with no "Do Not Sell or Share My Personal Information" link, no Global Privacy Control handling, and no privacy policy listing categories. Applies if the business has more than $25M revenue (2025: about $26.6M), handles data on 100k+ consumers, or makes 50%+ of revenue from selling or sharing data.
**Not a finding if:** Below the thresholds (say so and drop it to a checklist item), or opt-out and GPC are honored. Note: GLBA-covered *financial* data is exempt, but marketing and web data are not.
**Penalty:** Cal. Civ. Code 1798.155/1798.199.90 — $2,500 per violation, $7,500 if intentional or involving minors (about $2,663/$7,988 after the 2025 adjustment). Sephora paid $1.2M over GPC alone.
**Fix:** Add the "Do Not Sell or Share" link, honor the `Sec-GPC` header, and list data categories and recipients in the policy.
**Bill:** GOV: $2,500 × CA users affected (cap the estimate at realistic settlement scale).

### P6 · TCPA — automated SMS without consent — 🟠
**Detect:** Marketing or promotional texts sent through Twilio etc. without stored prior express written consent (checkbox + disclosure + timestamp). No STOP handling. Texts sent to numbers imported from elsewhere.
**Not a finding if:** Only transactional or OTP texts are sent (informational texts need lighter consent), or written consent is stored and STOP is honored.
**Penalty:** TCPA (47 USC 227(b)(3)) — $500 per text, trebled to $1,500 if willful or knowing, with no cap. This is a class-action magnet.
**Fix:** Capture and store express written consent with a timestamp and the disclosure text, honor STOP/HELP, and keep marketing texts separate from OTP.
**Bill:** LAWSUIT: $500–$1,500 × marketing texts sent (assume 4 per user per month).

### P7 · CAN-SPAM — no unsubscribe — 🟠
**Detect:** Marketing emails without a working unsubscribe link, no `List-Unsubscribe` header, no physical postal address, misleading subject or from lines. Note: Gmail and Yahoo have required one-click unsubscribe for bulk senders since 2024.
**Not a finding if:** Emails are purely transactional (receipts, OTP, statements).
**Penalty:** CAN-SPAM (15 USC 7706) — up to about $53,088 per email.
**Fix:** Add a one-click unsubscribe (link + `List-Unsubscribe-Post`) and a postal address, and process opt-outs within 10 business days.
**Bill:** GOV: low $53k × 1, high $53k × emails sent (cap the estimate at $1M for small apps; FTC settlements are far below the theoretical max).

### P8 · ADA / accessibility — 🟠
**Detect:** Images without `alt`, clickable `<div>`s without role or keyboard support, inputs without labels, low contrast, focus outlines removed, modals that trap focus, CAPTCHAs without alternatives.
**Not a finding if:** It's a minor issue. Report only systemic patterns as findings.
**Penalty:** ADA Title III suits (thousands per year, mostly settled for about $5,000–$20,000+ plus plaintiff's attorney fees). California's Unruh Act adds $4,000 per visit. The DOJ's 2024 Title II rule sets WCAG 2.1 AA for public entities.
**Fix:** Run axe or Lighthouse, then add alt text, labels, keyboard handlers, and visible focus. Target WCAG 2.1 AA.
**Bill:** LAWSUIT: $5k–$25k per suit (assume 1).

### P9 · ROSCA — negative option / hard-to-cancel subscriptions — 🟠
**Detect:** Paid subscriptions or trials that auto-renew with no clear terms before billing, no express consent to the recurring charge, or cancellation that needs a call or email or is harder than signup.
**Not a finding if:** Terms are shown next to the pay button, consent is explicit, and online cancellation (a billing portal) is as easy as signup.
**Penalty:** ROSCA (15 USC 8403), enforced as an FTC rule violation — up to about $53,088 per violation, plus refunds (the FTC's Amazon Prime case settled for $2.5B in 2025). State auto-renewal laws (CA ARL) add more. Note: the FTC's 2024 "click-to-cancel" rule was vacated by the 8th Circuit in 2025, but ROSCA itself still applies.
**Fix:** Show renewal terms and price before payment, get an explicit checkbox, and add a one-click online cancel.
**Bill:** GOV: $53k × an assumed 1–10 violations. LOSS: refunds.

### P10 · E-SIGN Act consent / contract validity — 🟠 (financial apps) / 🟢 (others)
**Detect:** For financial apps that deliver legally required disclosures (Reg E, TILA, privacy notices) electronically: check for E-SIGN consumer consent (15 USC 7001(c): a disclosure plus an affirmative consent that shows the user can access electronic records). For all apps, check whether terms acceptance is a plain checkbox with no stored record (user, timestamp, IP, terms version).
**Not a finding if:** The consent and acceptance events are logged immutably with the version.
**Penalty:** Disclosures not validly delivered count as not delivered, so every downstream Reg E/TILA disclosure violation follows. Clickwrap without proof is unenforceable, so arbitration clauses and class waivers fail (which inflates every LAWSUIT number above).
**Fix:** Add an E-SIGN consent step before delivering disclosures electronically, and log every acceptance with user, timestamp, IP, and document version.
**Bill:** Multiplier on F4/F5/F13. No standalone figure.

### P11 · Poor record-keeping — 🟡
**Detect:** No immutable log of transactions, consent events, KYC results, and admin actions. Records can be edited or hard-deleted. No retention policy.
**Penalty:** BSA requires 5-year retention (31 CFR 1010.430). Reg E requires 2 years (1005.13). Without records you can't defend chargebacks, disputes, or audits.
**Fix:** Write append-only audit records for money, consent, and admin actions, and set retention to match the longest rule that applies.
**Bill:** LOSS: lost chargebacks or disputes.

### P12 · Cross-border bleed — 🟠
**Detect:** Global signup with no geo restrictions while the app offers regulated features (payments, lending, investing, crypto) licensed for only one country. No localization of required disclosures. Data stored outside the region with no transfer mechanism (GDPR Ch. V).
**Not a finding if:** Signup is restricted to supported jurisdictions.
**Penalty:** Foreign regulators' cease-and-desist orders and local licensing violations. GDPR transfer fines (Meta: €1.2B).
**Fix:** Geo-restrict regulated features to licensed jurisdictions, and localize disclosures and data residency where you expand.
**Bill:** GOV: unquantified. Note it.
