# Pricing the bill

The goal is one honest answer to "what could I owe?": a range for government fines, a range for lawsuit exposure, a criminal-exposure flag, and the assumptions behind them. These are **statutory worst-case figures meant to convey scale, not predictions**. Regulators rarely charge the maximum, and first-time small companies often get consent orders. The output header says this in one line, and nowhere else needs to.

## 1. Set the basis

| Input | Source | Default if unknown |
|---|---|---|
| Users (N) | user's answer, analytics config, seed data, or what they said in chat | LIVE: 100 · SANDBOX: 100 ("if you went live with 100 users") |
| Days live (D) | user, first commit or deploy date | 30 |
| Transfers | per user per month | 4 |
| Marketing emails/texts | per user per month | 4 |
| State shares | CA 12%, IL 4%, WA 2.5%, EU 5% (only if there's EU signup) | as shown |
| Net worth (for class-action caps) | usually unknown | use the dollar cap |

Always print what you assumed on the `Assumed:` line, e.g. `Assumed: 100 users, 30 days live, 4 transfers/user/mo`.

## 2. Price each finding

Use the entry's **Bill** line.

- **Low:** the realistic floor. The minimum statutory amount × the smallest plausible count. Use $0 when the agency typically issues a non-monetary order first (FTC Safeguards, many first-time CFPB matters).
- **High:** maximum per unit × the count from the basis, then apply statutory caps (e.g., EFTA class: lesser of $500k or 1% net worth, so use $500k; TILA class: $1M).
- If a count would explode (CAN-SPAM per email × 10,000 emails = $530M), cap that single finding's high end at a realistic enforcement scale (largest comparable settlement, or $1M for a small app) and note "capped" in your reasoning. Don't print absurd numbers. They make the whole report look unserious.

## 3. Bucket it

- **Government fines:** civil money penalties, FinCEN/OFAC/CFPB/FTC/SEC/HHS/state AG penalties, card-network fines (contractual, but put them here).
- **Lawsuit exposure:** private statutory damages and class actions (EFTA, TILA, FCRA, TCPA, CIPA, BIPA, CCPA breach, ADA, WA MHMDA).
- **Criminal exposure:** list finding numbers (18 USC 1960, 709; 31 USC 5318(g)/5322; IEEPA willful; FCRA 1681q; HIPAA 1320d-6). Never convert to dollars.
- **Plus direct losses:** one line for 🟡 bugs (float drift, duplicate payments, forged webhooks, frozen processor funds). Give a number only if you can compute one from the code (e.g., max transfer limit × duplicates). Otherwise write "uncapped" or "unquantified".

Sum lows and highs within each bucket across **all verified findings**, including any hidden behind "full report".

## 4. Format

- Round to 2 significant figures: `$5,000`, `$38k`, `$1.2M`. Above $100M write `$100M+`.
- A range where low = high: print one number.
- Bucket with nothing in it: `$0`.

## Worked example

LIVE, 250 users, 60 days. Findings: F1 (no partner, custody), F8 (Float balances), F10 (unverified Stripe webhook), F6 ("FDIC insured" on landing page), P6 (marketing SMS, no consent).

- F1: GOV $5,000 × 60 days = $300k (low 30 days = $150k). Criminal: yes.
- F6: GOV $10k–$1M. Criminal: yes.
- P6: LAWSUIT 250 users × 4 texts × 2 months = 2,000 texts × $500–$1,500 = $1M–$3M. Low: assume 10% of recipients sue or are in a class that settles → $100k.
- F8, F10: direct losses. Webhook forgery is uncapped.

```
 💸 THE BILL  (all 5 findings · statutory worst case, not a prediction)
     Government fines  : $160k – $1.3M
     Lawsuit exposure  : $100k – $3M
     Criminal exposure : yes — #1, #2
     Plus direct losses: forged webhooks = uncapped; Float drift on every transfer
     Assumed: 250 users, 60 days live, 4 marketing texts/user/mo
```
