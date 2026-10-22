# HIPAA & health data (H0–H10)

Same entry format as `fintech.md`.

## H0 · Decide which regime applies first (don't skip this)

HIPAA applies only to **covered entities** (health plans, clearinghouses, providers who bill insurance electronically) and their **business associates** (vendors handling PHI for them). Ask yourself:

- **Does the app work for or with a provider, insurer, or clinic** (EHR integration, telehealth for a practice, billing, patient portal)? Then it's a covered entity or business associate, and HIPAA applies. Use H1–H9.
- **Is it a consumer app people use on their own** (symptom tracker, period app, therapy marketplace, fitness, HSA/medical-bill fintech)? HIPAA usually does **not** apply. The **FTC Health Breach Notification Rule** (H10), the FTC Act, and state health-privacy laws apply instead, and they're often stricter about sharing with advertisers.

State which regime you applied in the finding's Penalty line. Being wrong about HIPAA applicability is common and expensive in both directions.

**HIPAA civil penalties** (45 CFR 160.404, 2024 inflation-adjusted, per violation):
- Tier 1, didn't know: $141–$71,162
- Tier 2, reasonable cause: $1,424–$71,162
- Tier 3, willful neglect, corrected within 30 days: $14,232–$71,162
- Tier 4, willful neglect, not corrected: $71,162–$2,134,831
- Calendar-year cap per identical provision: $2,134,831 (HHS's enforcement discretion uses lower caps for tiers 1–3)

**HIPAA criminal** (42 USC 1320d-6): knowing disclosure up to $50k and 1 year; under false pretenses up to $100k and 5 years; to sell, for commercial advantage, or to cause harm up to $250k and 10 years.

---

### H1 · No BAA with vendors that touch PHI — 🟠
**Detect:** PHI flows to hosting, DB, email/SMS, error tracking, analytics, or AI vendors (Supabase, Vercel, Firebase, Twilio, SendGrid, Sentry, OpenAI, Anthropic, etc.). Is there any sign of a Business Associate Agreement or a HIPAA-eligible plan? Many vendors sign BAAs only on enterprise or HIPAA add-on tiers, and many never do.
**Not a finding if:** HIPAA doesn't apply (H0), or BAAs exist for every vendor in the PHI path (the user may need to confirm, so ask rather than assume).
**Penalty:** HIPAA Privacy/Security Rules (45 CFR 164.502(e), 164.308(b)): tiered civil penalties above, per vendor per day of disclosure.
**Fix:** List every vendor in the PHI path, sign BAAs or move to HIPAA-eligible tiers, and drop the ones that won't sign.
**Bill:** GOV: tier 2 × vendors without a BAA (low $1,424 each, high the annual cap).

### H2 · PHI to ad/analytics pixels — 🟠
**Detect:** Meta Pixel, Google Analytics/Ads, TikTok, Segment, Mixpanel, or Amplitude on authenticated pages, intake forms, appointment flows, or events carrying condition, medication, or provider data (including URLs like `/conditions/hiv`).
**Not a finding if:** Tracking is removed from authenticated and health-specific pages, and events carry no health data.
**Penalty:** HIPAA: HHS tracking-technology guidance (partly vacated in 2024 for unauthenticated pages, but authenticated pages remain covered). Non-HIPAA: FTC HBNR and the FTC Act (GoodRx $1.5M, BetterHelp $7.8M, Cerebral $7M+). Large class actions under wiretap laws (Advocate Aurora $12.2M settlement).
**Fix:** Remove pixels from authenticated and health pages, and strip health data from analytics events (or use a BAA-backed analytics tool).
**Bill:** GOV: $1.5M–$7.8M FTC-style. LAWSUIT: class settlement range.

### H3 · PHI sent to LLM APIs — 🟠
**Detect:** Prompts containing patient names, conditions, notes, or transcripts sent to an AI API without a BAA or zero-retention terms.
**Not a finding if:** The provider signed a BAA for that endpoint, or the data is de-identified to the HIPAA Safe Harbor standard (164.514(b)) before sending.
**Penalty:** As H1 (an impermissible disclosure to a non-BA). Non-HIPAA apps: FTC Act / HBNR.
**Fix:** Use a BAA-covered AI endpoint or de-identify before sending, and turn off training and retention.
**Bill:** As H1.

### H4 · Weak access control on PHI — 🟠
**Detect:** See security.md S1, applied to PHI tables. Also: staff can see all patients (no minimum-necessary role scoping, 164.502(b)), shared admin logins, no session timeout.
**Penalty:** Security Rule 164.312(a) access control. Combined with S1, this is a reportable breach.
**Fix:** Scope PHI queries by patient relationship and role, use unique user IDs, and add auto-logoff.
**Bill:** GOV: tier 2 per affected record class. LAWSUIT: state-law class claims if breached.

### H5 · No audit logs for PHI access — 🟠
**Detect:** No record of who viewed or changed which patient record and when.
**Penalty:** Security Rule 164.312(b) audit controls (required). Without logs you can't scope a breach, so you must assume all records were exposed.
**Fix:** Log every PHI read and write (user, patient, action, timestamp) to append-only storage and review it regularly.
**Bill:** GOV: tier 2–3.

### H6 · No encryption in transit or at rest — 🟠
**Detect:** PHI in plaintext columns, unencrypted backups or storage buckets, HTTP endpoints, PHI in email bodies or SMS.
**Penalty:** Security Rule 164.312(a)(2)(iv), (e). Encryption is "addressable" but expected in practice. Encrypted data is exempt from breach notification (the safe harbor), so plaintext turns every leak into a reportable breach.
**Fix:** Encrypt PHI columns and backups, enforce TLS, and send "you have a new message" notifications instead of PHI in email or SMS.
**Bill:** Multiplier on H8.

### H7 · PHI in logs or error trackers — 🟠
**Detect:** See security.md S6, for health fields. Sentry or Datadog capturing request bodies with PHI.
**Penalty:** Impermissible disclosure (H1) if the log vendor has no BAA.
**Fix:** Scrub PHI from logs and error payloads, and purge what's already there.
**Bill:** As H1.

### H8 · No breach notification process — 🟠
**Detect:** No incident response plan with HIPAA deadlines.
**Penalty:** Breach Notification Rule (45 CFR 164.400–414): notify individuals within 60 days of discovery. For 500+ people in a state, notify HHS and prominent media within 60 days. Under 500, use the annual HHS log. Late notice is its own violation.
**Fix:** Add HIPAA deadlines and templates to the incident response plan (security.md S9).
**Bill:** GOV: tier 2.

### H9 · Selling, sharing, or knowingly disclosing PHI — 🔴
**Detect:** Code or docs showing PHI sold or shared with data brokers or advertisers, or used for marketing without authorization (164.508(a)(3)–(4)).
**Penalty:** 42 USC 1320d-6 — up to $250k and 10 years if for commercial advantage.
**Fix:** Stop the data flow immediately and get counsel. Authorization requirements apply to any marketing use.
**Bill:** GOV: tier 4. Criminal: yes.

### H10 · Consumer health apps: FTC HBNR + state health-privacy laws — 🟠
**Detect:** A non-HIPAA app with health data (H0) that shares it with third parties (ads, analytics, AI) without express consent, or has no breach-notification process. Also check Washington's My Health My Data Act (and Nevada and Connecticut equivalents): consent before collecting or sharing consumer health data, a separate health privacy policy, and no geofencing near health facilities.
**Penalty:** FTC Health Breach Notification Rule (16 CFR 318, expanded in 2024 to cover health apps and unauthorized disclosures): up to about $53,088 per violation, notice within 60 days. WA MHMDA: enforced through the WA Consumer Protection Act **with a private right of action** (actual damages, trebled up to $25k, plus fees) and AG penalties.
**Fix:** Get opt-in consent before any health data sharing, publish a consumer health data privacy policy, and add HBNR notice deadlines to the incident plan.
**Bill:** GOV: $53k × violations (assume per sharing integration × months). LAWSUIT: WA users × up to $25k (assume WA = 2.5% of users).
