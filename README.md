# 🩺 Fintech Doctor

You vibe-coded an app. It works. But is it *legal*?

Fintech Doctor is an AI skill that reads through your codebase like a very blunt doctor. You get back a diagnosis covering what could get you fined, sued, robbed, or worse, plus what you got right, what the evidence supports about the stakes, and what to fix first.

**It only diagnoses. It never touches your code.**

```text
||==========================================================================
||
||    🩺  C O M P L I A N C E   D O C T O R
||
||    Patient   ::  your-app
||    Severity  ::  ▓▓ ?????????????? ▓▓
||    Mode      ::  LIVE
||
||==========================================================================
||  📊 VITALS  ...
||  💚 HEALTHY VITALS  ...
||  🩻 DIAGNOSIS  ...
||  💸 THE BILL  ...
||  💊 PRESCRIPTION  ...
```

What's behind the `??????`? Run it and find out. 🙃

---

## What it looks at

- **Money:** moving it, holding it, lending it, promising yield on it, storing it as a float
- **Health data:** HIPAA, plus the rules that apply when HIPAA doesn't
- **Privacy:** tracking, session replay, biometrics, kids, texts, emails
- **Consumer law:** subscriptions, dark patterns, accessibility, e-signatures
- **Security:** leaked keys, open databases, anyone-can-see-anyone's-account bugs
- **AI-built code:** made-up packages, prompt injection, agents with too much power

It starts by asking you four quick questions so it knows whether you're still in a sandbox or already live, and it scales its findings to match.

---

## Install it in your harness

The skill is the [`compliance-doctor/`](compliance-doctor) folder: a `SKILL.md`, some reference files, and a small Python scanner. Get it first:

```bash
git clone https://github.com/DanielLambo/Fintech_Doctor.git
```

Then pick your tool below.

### Claude Code

```bash
cp -R Fintech_Doctor/compliance-doctor ~/.claude/skills/
```

In any project, run `/compliance-doctor`, or just ask *"run the doctor on this app."* Add `full` for the uncut report.

To install it for one repo only, copy it to `.claude/skills/` inside that repo instead.

### Claude.ai / Claude Desktop

1. Zip the folder: `cd Fintech_Doctor && zip -r compliance-doctor.zip compliance-doctor`
2. Go to **Settings → Capabilities → Skills** and upload the zip.
3. Attach or connect your repo, then ask *"run the compliance doctor on this."*

### OpenAI Codex (CLI / IDE)

```bash
mkdir -p ~/.codex/skills && cp -R Fintech_Doctor/compliance-doctor ~/.codex/skills/
```

Then ask Codex to *"run the compliance doctor."* If your Codex version doesn't load skills, copy the folder into your repo and add this to `AGENTS.md`:

```markdown
For compliance or pre-launch audits, follow compliance-doctor/SKILL.md exactly.
```

### GitHub Copilot (agent mode / coding agent)

```bash
mkdir -p .github/skills && cp -R Fintech_Doctor/compliance-doctor .github/skills/
```

Commit it, then in Copilot Chat (agent mode) or in an issue assigned to the Copilot coding agent, ask: *"Run the compliance doctor on this repo and post the report."* If skills aren't picked up, add the `AGENTS.md`-style line above to `.github/copilot-instructions.md`, pointing at `.github/skills/compliance-doctor/SKILL.md`.

### Cursor

```bash
cp -R Fintech_Doctor/compliance-doctor ./compliance-doctor
mkdir -p .cursor/rules && cp compliance-doctor/SKILL.md .cursor/rules/compliance-doctor.mdc
```

Then open Agent mode and type *"Run the compliance doctor on this repo."*

### Windsurf / Gemini CLI / other agents

Copy the folder into your repo and point your agent's instruction file at it:

| Tool | Instruction file |
|---|---|
| Windsurf | `.windsurf/rules/compliance-doctor.md` |
| Gemini CLI | `GEMINI.md` |
| Anything that reads `AGENTS.md` | `AGENTS.md` |

Add the line: *"For compliance audits, follow compliance-doctor/SKILL.md exactly."*

### Lovable

Lovable can't run the Python scanner, but it can follow the instructions.

1. Connect your project to GitHub and push the `compliance-doctor/` folder into the repo.
2. Paste this into your project's **Knowledge** / custom instructions:
   > When I say "run the doctor", read compliance-doctor/SKILL.md and the files in compliance-doctor/references/, skip the scanner step, and produce the report exactly as specified. Do not change any code.
3. In chat (Chat mode, not edit mode, so it doesn't start "fixing" things): *"Run the doctor."*

### v0

v0 can't run the scanner either.

1. Add `SKILL.md` and the `references/` files to your project as sources or attachments (or paste `SKILL.md` into the project instructions).
2. Ask: *"Follow SKILL.md and run the compliance doctor on this project. Diagnose only, don't edit code."*

### Bolt / Replit Agent / any chat AI

Run the scanner yourself (below), then give the AI `SKILL.md`, the `references/` folder, the scanner output, and your key files (schema, payment routes, landing page). Say: *"Follow SKILL.md and produce the report."*

### Using something else? Copy this prompt

If your AI tool can open GitHub links and access your project, paste this:

```text
https://github.com/DanielLambo/Fintech_Doctor/tree/main — run this doctor on my project.

Read compliance-doctor/SKILL.md and follow its audit workflow, using the relevant
files in compliance-doctor/references/. Start with the triage questions. Run the
bundled scanner if you can execute Python; otherwise say it wasn't run and
review the project files you can access. Diagnose only—don't change my code.
Be a helpful, honest friend: point out what I did well, explain the risks with
file:line evidence, and tell me what to fix first. Don't expose secrets or
invent findings, usage numbers, or legal costs. If you can't open the link or
see my project, tell me exactly which files you need before making claims.
```

If the tool can't open links, attach `compliance-doctor/SKILL.md`, its `references/`
folder, and the project files you want reviewed. A link alone doesn't give the AI
access to your app.

### No AI at all

The scanner works on its own, with plain Python 3 and no installs:

```bash
python3 Fintech_Doctor/compliance-doctor/scripts/scan.py /path/to/your/repo
```

Add `--json` for machine-readable output and `--fail-on-candidates` for CI triage. Exit codes: `0` = scan completed within its supported scope, `1` = candidates found with the CI flag, `2` = incomplete coverage or invalid invocation. No exit code certifies compliance. Source snippets are omitted to protect credentials; inspect reported file:line locations locally. Coverage reports skipped paths and counts of intentional exclusions (unsupported files, lockfiles, and dependency/build directories). Symlinks are not followed. Python 3.10+ on Linux/macOS is required (safe file opening uses `O_NOFOLLOW`). It lists suspicious lines and missing safeguards, but the verdict, the bill and the prescription need an AI to verify and weigh the findings.

---

## Heads up

- **Works best in tools that can open files and run commands** (Claude Code, Codex, Copilot agent, Cursor). Browser builders like Lovable and v0 can only see what's in the project, so the diagnosis is shallower there.
- **Written for Claude.** Other models usually follow it well but may drift from the format.
- **Not legal advice.** Historical penalty figures in the references require current authoritative verification before use. The report does not invent usage counts or total hypothetical fines. If the doctor says it's serious, talk to a fintech lawyer before launch.

The doctor should sound like a helpful friend: specific praise when earned, clear risks, and a practical next step. “Nice, your amounts are already in cents. Let's make retries safe next.”

Run regression tests with `python3 -m unittest discover -s tests -v`.
