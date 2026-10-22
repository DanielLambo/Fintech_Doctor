# Example report (fictional codebase)

All paths and observations below illustrate formatting; they are not findings about this repository.

Nice, your amounts are already stored in integer cents (`src/payments.ts:12`). That's a good foundation. One thing I'd tighten before launch: make sure a webhook retry can't credit the same payment twice.

```text
||==========================================================================
||    🩺  C O M P L I A N C E   D O C T O R
||    Patient   ::  example-wallet (fictional)
||    Severity  ::  ▓▓ COULD IMPROVE ▓▓
||    Mode      ::  SANDBOX
||==========================================================================
||  📊 VITALS                                   1 verified · showing 1
||    🔴  Legal review                         0
||    🟠  Regulatory risk                      0
||    🟡  Money bugs               █           1
||    🟢  Tech debt                            0
||==========================================================================
||  💚 HEALTHY VITALS — what you did right
||    ✔  Amounts are stored and calculated in integer cents.
||                                                          src/payments.ts:12
||    ✔  Webhook signatures are checked before processing events.
||                                                          src/webhook.ts:8
||==========================================================================
||  🩻 DIAGNOSIS
||  #1  🟡  FIX THIS MONEY RISK
||  --------------------------------------------------------------------------
||      Problem  |  Replaying a signed event credits the wallet again.
||      Where    |  src/webhook.ts:8 → src/payments.ts:24
||      Penalty  |  Direct loss risk; actual duplicate events and amounts unknown.
||      Fix      |  Enforce a unique event ID atomically with the wallet credit.
||==========================================================================
||  💸 BEFORE LAUNCH — OPEN QUESTIONS
||      Government penalties | Not quantified; no violation established
||      Private claims       | Not quantified; real users unconfirmed
||      Contractual fees     | Not assessed; agreement unavailable
||      Direct losses        | Duplicate credits possible; amount unknown
||      Criminal provisions  | None identified in examined path
||      Known / unknown      | Sandbox; live volume and jurisdiction unknown
||==========================================================================
||  🧾 TOTAL YOU OWE — confirmed outstanding obligations only
||      Total you owe       | Not established from available evidence
||      Completeness        | No obligation or payment records supplied
||      As of / scope       | Fictional sandbox review; code only
||      Excluded            | Potential duplicate-credit losses; not a debt
||==========================================================================
||  ✅ BEFORE YOU FLIP TO LIVE KEYS
||      [ ]  Add atomic event deduplication and test repeated delivery.
||      [ ]  Confirm the processor agreement and responsibility for disputes.
||==========================================================================
```

You've already got signature verification in place. Adding deduplication will cover the retry case too. Want me to start on that?
