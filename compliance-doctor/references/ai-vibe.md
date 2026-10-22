# AI & vibe-coding risks (A1–A10)

Same entry format as `fintech.md`. These are mostly 🟡/🟢 engineering risks, but they're often the *cause* of the regulatory findings, so connect them in the Fix line when it helps ("This is why F9 happened: three copies of the transfer logic").

### A1 · Hallucinated / slopsquatted dependencies — 🟡 (🟠 if the package runs in a money or PII path)
**Detect:** Look at `package.json` / `requirements.txt` / `pyproject.toml` for unfamiliar names, near-miss names of popular packages (`reqeusts`, `stripe-node-sdk`), very new packages, or packages with install scripts. If network access is allowed, `npm view <pkg> time.created maintainers repository` or `pip index versions <pkg>` shows age and ownership. Also flag imports of packages that aren't declared at all.
**Not a finding if:** It's a well-known package with a long history and its real maintainers.
**Penalty:** Supply-chain compromise. A malicious install script runs with your env vars, which means stolen keys (S2) and a breach of everything behind them.
**Fix:** Remove or replace suspicious packages, commit a lockfile, and use `npm ci` / `--ignore-scripts` in CI.
**Bill:** LOSS: everything the build environment can reach.

### A2 · GPL / copyleft code pulled in silently — 🟢 (🟡 if distributed)
**Detect:** GPL/AGPL dependencies or copied code blocks with license headers in a closed-source app. AGPL matters even for SaaS. Use `npx license-checker --summary` if available.
**Penalty:** Copyleft obligations: you may have to release source, or rip the code out. Litigation is rare but possible.
**Fix:** Replace AGPL/GPL dependencies with permissive alternatives, or comply with the license.
**Bill:** None direct.

### A3 · Prompt injection with real permissions — 🟡 (🟠 if it can move money or read others' PII)
**Detect:** LLM features (support bot, agent, "AI assistant") that have tools able to issue refunds, transfer funds, change accounts, or query other users' data, or whose system prompt contains secrets. User-controlled or retrieved text (emails, documents, web pages, transaction memos) goes into the prompt without isolation.
**Not a finding if:** Tools are read-only and scoped to the current user, money actions need human or step-up confirmation, and outputs are treated as untrusted.
**Penalty:** Direct loss (e.g., unauthorized refunds), data leaks (S1 penalties), and liability for what the bot says. In Moffatt v. Air Canada (2024) the airline had to honor its chatbot's made-up refund policy. Tipping-off risk (F3) if the bot can see AML flags.
**Fix:** Scope AI tools to the signed-in user and read-only by default, require confirmation for money actions, and keep AML/fraud flags out of the model's context.
**Bill:** LOSS: max refund/transfer the tool allows × volume.

### A4 · Agentic "god mode" — 🟡
**Detect:** CI/CD workflows or agent configs that let an AI agent deploy to production, run migrations, or push to main without review. Look for `.claude/settings*.json` with `bypassPermissions` or broad `Bash(*)` allows, `--dangerously-skip-permissions` in scripts, and production secrets available to agent jobs.
**Penalty:** Unreviewed outages, destroyed data, or backdoors shipped straight to production.
**Fix:** Require human review for production deploys and migrations, scope agent permissions, and keep production secrets out of agent environments.
**Bill:** None direct.

### A5 · Unvetted third-party APIs — 🟠 if PII is sent / 🟢 otherwise
**Detect:** "Free" APIs (geolocation, enrichment, OCR, translation, AI wrappers) receiving user PII or financial data, with no DPA and unknown retention.
**Penalty:** You're liable for your vendors: GLBA vendor oversight (16 CFR 314.4(f)), GDPR Art. 28 processor contracts, HIPAA BAAs (H1).
**Fix:** Inventory every third-party call that carries user data, and sign a DPA/BAA or remove it.
**Bill:** As the matching privacy entry.

### A6 · Shadow AI exfiltration — 🟢
**Detect:** Hard to see in code. Look for scripts that send DB dumps, customer CSVs, or the codebase to public LLM endpoints, and for real customer data in prompts or fixtures.
**Fix:** Use synthetic data in prompts and fixtures, and set a team policy on what can be sent to AI tools.
**Bill:** None direct (breach if PII).

### A7 · "Local correctness" / duplicated logic — 🟢 (🟡 if duplicated in money paths)
**Detect:** The same business rule (fee calculation, balance check, transfer flow, auth check) implemented in several places with slight differences. Several API routes doing the same thing.
**Penalty:** A fix lands in one copy and not the others. Inconsistent fees create UDAAP/Reg E exposure (F20/F4).
**Fix:** Consolidate each money and auth rule into one module, and route every caller through it.
**Bill:** None direct.

### A8 · Testing coverage collapse — 🟢 (🟡 if money paths are untested)
**Detect:** The scanner reports a test-to-source ratio. Check whether transfer, webhook, ledger, auth, and fee logic have tests for failure paths (insufficient funds, duplicates, retries, negative or huge amounts, concurrency).
**Fix:** Write tests for the money and auth edge cases first, before adding more features.
**Bill:** None direct.

### A9 · Client-side state & insecure state management — 🟡
See security.md S3. Mention it here only if the pattern is everywhere (a systemic vibe-coding smell).

### A10 · The 90-day refactoring wall — 🟢
**Detect:** Giant files (1,000+ lines), no module boundaries, business logic in React components, no types on money values, no architecture notes.
**Fix:** Write a short architecture note for the money path, and pull money logic out of UI components.
**Bill:** None direct.
