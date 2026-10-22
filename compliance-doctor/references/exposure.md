# Discussing exposure honestly

Help the user understand the stakes without pretending a code scan can calculate a legal bill. This policy overrides any numerical **Bill** recipes in other references. Those entries are research leads, not verified estimates.

## Evidence before arithmetic

- Never invent user counts, days live, transaction counts, message volumes, net worth, jurisdiction shares, or the likelihood of enforcement. A first commit does not establish a launch date.
- Mark missing inputs `unknown`. Ask for the specific input only when needed; continue the technical review independently.
- State which law could apply, why, and what remains unconfirmed. Missing controls do not establish that a breach, unlawful transaction, or crime occurred.
- Verify current penalty amounts, effective dates, applicable jurisdiction, and statutory caps against an authoritative regulator or statute before quoting them. Include the source URL and date checked. If verification is unavailable, omit the number and say it is unverified. Reference files contain historical figures and are not current legal authority.

## Reporting amounts

Default to `Not quantified — applicability and counts need confirmation`. This is not $0 and is not a clean bill of health.

A numerical illustration is allowed only when the user requests one and supplies its inputs, or when the relevant counts are directly verified. Label it `Illustrative scenario, not a liability estimate`, show the formula, inputs, source, applicable caps, and uncertainty. Keep statutory ceilings separate from expected outcomes; do not invent a realistic floor, settlement likelihood, arbitrary $1M cap, or claim participation rate. If a net-worth cap cannot be evaluated, retain the symbolic formula.

Discuss each finding separately. Do not sum overlapping statutory theories or unrelated hypothetical maximums into a grand total. Keep government penalties, private claims, contractual processor fees, and direct technical losses separate. Never label card-network fees as government fines.

Flag potential criminal applicability conditionally and identify the missing factual elements. Do not declare the user criminally liable from code or assign a dollar value to criminal exposure. Avoid fear-based labels or promises of legal clearance.

## Total you owe: confirmed obligations

Always render this section, separately from potential exposure. A code defect or statutory maximum is not proof of an amount owed.

- Include only obligations established by supplied evidence, such as an assessed fine, executed settlement, outstanding invoice, or verified payable/refund ledger. Identify the liable entity, source (file:line or document reference), currency, amount, and evidence date. A demand or disputed claim is not a confirmed debt; list it separately.
- Calculate each outstanding item as the documented obligation minus verified payments and credits. Do not count both a ledger entry and its invoice, combine overlapping penalties, or add remediation budgets, hypothetical losses, or amounts already paid.
- Sum distinct confirmed outstanding items in each currency. Do not convert currencies without an explicit dated exchange-rate source. Use exact decimal or integer minor-unit arithmetic, not floating point.
- State the scope and as-of date. Call the result `Confirmed subtotal — incomplete` if any relevant balances, payments, or obligations remain unknown. A numerical total is complete only for a clearly bounded scope with all its items reconciled.
- When no debt is established, print `Total you owe: Not established from available evidence`. Print zero only when reconciled evidence actually confirms no outstanding amount in the stated scope. Do not ask users to share secret values or unnecessary personal details to establish balances.

Example with fictional supplied documents: an outstanding USD 1,000 invoice, a verified USD 200 payment against it, and a separate USD 300 refund payable yield **USD 1,100** (1,000 − 200 + 300). Cite all three records and their dates. An unassessed potential fine stays outside that total. If other obligations are unknown, label USD 1,100 a confirmed subtotal, not the user's entire debt.

## Example

```text
||  EXPOSURE — what we can support
||      Government penalties | Not quantified; licensing status unconfirmed
||      Private claims       | Not quantified; affected users unknown
||      Contractual fees     | Not assessed; processor agreement unavailable
||      Direct losses        | Duplicate payouts possible; amount unknown
||      Criminal provisions  | Applicability requires legal review
||      Known inputs         | Webhook replay protection absent in traced path
||      Missing inputs       | Actual duplicate events, amounts, jurisdiction
```

A useful next step is concrete: “Your payment flow is easy to follow. Let's verify the processor agreement before attaching a licensing claim or a price tag to it.” Only praise qualities you actually verified.
