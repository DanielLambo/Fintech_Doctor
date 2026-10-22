#!/usr/bin/env python3
"""compliance-doctor first-pass scanner.

A metal detector, not a verdict: it lists *candidate* evidence (file:line) and
whether common mitigations appear anywhere in the repo. Every hit has to be read
in context before it becomes a finding. Read-only, stdlib only.

Usage:
    python3 scan.py [repo_root] [--max-hits N] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "out", ".turbo", ".vercel",
    "coverage", "vendor", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    ".mypy_cache", "Pods", "DerivedData", ".gradle", "target", ".expo",
    ".svelte-kit", ".nuxt", ".cache", ".idea", ".vscode", "storybook-static",
}
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock",
    "Cargo.lock", "Gemfile.lock", "composer.lock", "go.sum", "uv.lock",
}
CODE = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".py", ".rb", ".go", ".java",
        ".kt", ".swift", ".rs", ".php", ".cs", ".dart", ".vue", ".svelte", ".astro",
        ".graphql", ".gql", ".sh"}
SCHEMA = {".prisma", ".sql"}
UI = {".jsx", ".tsx", ".html", ".htm", ".vue", ".svelte", ".astro", ".md", ".mdx",
      ".json", ".txt", ".liquid", ".hbs", ".ejs"}
CONFIG = {".json", ".yaml", ".yml", ".toml"}
ALL = CODE | SCHEMA | UI | CONFIG
MAX_BYTES = 800_000
I = re.IGNORECASE
# Route/file paths that are risk candidates on their own (reported once, at line 1).
PATH_RISKS = {
    "F1": re.compile(r"transfer|withdraw|payout|send-?money|remit|p2p", I),
    "F10": re.compile(r"webhook", I),
}

# --------------------------------------------------------------------------
# Signals: what kind of patient is this? (counted, not reported as findings)
# --------------------------------------------------------------------------
SIGNALS = [
    ("money movement", r"outgoing.?payment|incoming.?payment|send.?money|\bp2p\b|remittan|withdraw|payout|createTransfer|transfer(Funds|Money)|@interledger|rafiki|open.?payments|walletAddress|wallet_address", CODE | SCHEMA),
    ("stored balances", r"\bbalance\b", CODE | SCHEMA),
    ("cards", r"stripe|card.?number|braintree|adyen|checkout\.com|square", CODE),
    ("bank data", r"plaid|mx\.com|finicity|teller\.io|routing.?number|account.?number", CODE | SCHEMA),
    ("lending/credit", r"cash.?advance|\bbnpl\b|earned.?wage|\bapr\b|\bloan\b|credit.?(score|report|line)", CODE | UI),
    ("investing/crypto", r"\bapy\b|brokerage|drivewealth|alpaca|portfolio|staking|crypto|ethers|web3|solana|bitcoin|usdc", CODE | UI),
    ("PII (gov IDs)", r"\bssn\b|social.?security|passport|drivers?.?licen[sc]e|tax.?id|date.?of.?birth|\bdob\b", CODE | SCHEMA),
    ("health data", r"\bpatient|diagnos\w*|medical|prescription|medication|icd-?10|\behr\b|\bemr\b|fhir|hl7|health.?record|symptom|therap(y|ist)|mental.?health|\bhipaa\b|\bphi\b|lab.?result", ALL),
    ("LLM usage", r"openai|@anthropic-ai|\banthropic\b|@ai-sdk|from ['\"]ai['\"]|langchain|llamaindex|chat\.completions|generateText|streamText|gemini|groq", CODE),
    ("email sending", r"\bresend\b|sendgrid|postmark|mailgun|nodemailer|SendEmailCommand|@react-email|mailchimp|loops\.so|customerio|brevo", CODE),
    ("SMS sending", r"twilio|vonage|plivo|messagebird|sinch|sendSms|send_sms|PublishCommand", CODE),
    ("subscriptions", r"subscription|auto.?renew|recurring|free.?trial", CODE | UI),
    ("auth", r"next-auth|@auth/|clerk|supabase\.auth|firebase/auth|lucia|passport\b|jsonwebtoken|bcrypt|argon2", CODE),
]

# --------------------------------------------------------------------------
# Risk candidates: places to go read. (id, label, regex, extensions, flags)
# --------------------------------------------------------------------------
SECRET_RE = (r"sk_live_[0-9A-Za-z]{8,}|rk_live_[0-9A-Za-z]{8,}|AKIA[0-9A-Z]{16}"
             r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}"
             r"|xox[baprs]-[A-Za-z0-9-]{10,}|sk-ant-[A-Za-z0-9_-]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,}"
             r"|AIza[0-9A-Za-z_-]{35}|eyJhbGciOi[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"
             r"|(?:NEXT_PUBLIC|VITE|EXPO_PUBLIC|REACT_APP)_[A-Z0-9_]*(?:SECRET|SERVICE_ROLE|PRIVATE|SK_)[A-Z0-9_]*")

RISKS = [
    ("F1", "money movement / custody — who holds the funds?", r"outgoing.?payment|send.?money|\bp2p\b|remittan|withdraw|payout|createTransfer|transfer(Funds|Money)|@interledger|rafiki|open.?payments", CODE, I),
    ("F3", "possible SAR tipping-off copy", r"suspicious activity|flagged (for|as) (fraud|suspicious|review|aml)|reported (you|your account|this account) to|under (an? )?(aml|fraud|compliance) (review|investigation)|money laundering|reported to (fincen|the authorities|law enforcement)", UI | CODE, I),
    ("F6", "FDIC / 'bank' claims", r"\bfdic\b|federally insured|your (new )?bank\b|(we are|we're) a bank|banking (app|platform|services)|\bneobank\b|online bank|deposits are insured", UI | CODE, I),
    ("F7", "mutable balance writes", r"\bbalance\s*(\+=|-=)|set\s+balance\s*=|balance\s*:\s*\{\s*(increment|decrement)|\.(update|upsert)\([^)]*balance|balance\s*=\s*balance\s*[-+]", CODE | SCHEMA, I),
    ("F8", "floating-point money", r"(parseFloat|Number)\s*\([^)]*(amount|balance|price|total|fee|usd|cents)|\b(amount|balance|price|total|fee)\w*\s+(Float|Double|REAL|FLOAT|DOUBLE)\b|\b(amount|balance|price|total|fee)\w*\s*:\s*(float|double)\b|\.toFixed\(2\)|Math\.round\([^)]*\*\s*100\s*\)", CODE | SCHEMA, 0),
    ("F10", "webhook handlers — verify signatures", r"webhook", CODE, I),
    ("F12", "credit / consumer-report data", r"credit.?(report|score|pull|check|bureau)|experian|equifax|transunion|soft.?pull|hard.?pull|underwrit|creditworth", CODE | UI, I),
    ("F13", "lending / cash advance / BNPL / EWA", r"cash.?advance|buy now,? pay later|\bbnpl\b|earned.?wage|\bewa\b|\bapr\b|line of credit|installment", UI | CODE, I),
    ("F14", "yield / investment claims", r"\bapy\b|guaranteed (return|yield|profit)|earn(s|ing)? (up to )?\d+(\.\d+)?\s?%|passive income|staking rewards|robo.?advis|we recommend (buying|investing)", UI, I),
    ("F19", "raw card data handling", r"card.?number|cardnumber|card_number|\bcvv\b|\bcvc\b|security.?code|\bpan\b", CODE | SCHEMA, I),
    ("F20", "pressure / dark-pattern copy", r"only \d+ (left|spots|remaining)|offer ends|limited.?time|hurry|expires in|countdown|act now|last chance", UI, I),
    ("S1", "record loaded by request id — check ownership scoping", r"params\.(id|accountId|userId|walletId|transactionId)\b|req\.params\.\w+|searchParams\.get\(\s*['\"](id|userId|accountId|walletId)['\"]|request\.args\.get\(\s*['\"](id|user_id|account_id)", CODE, 0),
    ("S1", "Supabase service_role / RLS / permissive rules", r"service_?role|disable row level security|using\s*\(\s*true\s*\)|allow read, write: if true", CODE | SCHEMA | CONFIG, I),
    ("S2", "hardcoded / exposed secrets", SECRET_RE, ALL | {".env"}, 0),
    ("S3", "trusting client-sent privileged fields", r"(req\.body|body|await req\.json\(\)|request\.json)\s*(\.|\[['\"])\s*(role|isAdmin|is_admin|price|balance|userId|user_id|plan|tier)\b", CODE, 0),
    ("S4", "sensitive PII columns — encrypted at rest?", r"\b(ssn|social_?security\w*|tax_?id|passport\w*|drivers?_?licen[sc]e\w*|account_?number|routing_?number|date_?of_?birth|dob|plaid_?access_?token|access_?token)\b", SCHEMA, I),
    ("S6", "logging sensitive data", r"(console\.(log|info|debug|warn|error)|logger\.\w+|\bprint|logging\.\w+)\s*\([^\n]*(password|passwd|\bssn\b|social.?security|\bcvv\b|\bcvc\b|card.?number|secret|token|routing|account.?number|\bdob\b|diagnos|req\.body|request\.body)", CODE, I),
    ("P2", "third-party CDN / fonts (EU IP leak)", r"fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|use\.typekit\.net|kit\.fontawesome\.com", UI | CODE, I),
    ("P3", "session replay / recording", r"hotjar|fullstory|logrocket|mouseflow|smartlook|clarity\.ms|@microsoft/clarity|\brrweb\b|session.?recording|sessionReplay|replayIntegration|replaysSessionSampleRate|disable_session_recording", CODE | UI, I),
    ("P4", "biometrics", r"biometric|face.?id|touch.?id|LocalAuthentication|expo-local-authentication|react-native-biometrics|face-api|rekognition|liveness|selfie|voiceprint|fingerprintjs", CODE, I),
    ("P6", "SMS sending — consent + STOP?", r"twilio|vonage|plivo|messagebird|sinch|sendSms|send_sms|PublishCommand|messages\.create", CODE, I),
    ("P7", "email sending — unsubscribe?", r"\bresend\b|sendgrid|postmark|mailgun|nodemailer|SendEmailCommand|@react-email|mailchimp|loops\.so|customerio|brevo", CODE, I),
    ("P8", "images without alt text", r"<img(?![^>]*\balt=)[^>]*>|<Image(?![^>]*\balt=)[^>\n]*/>", UI, 0),
    ("P9", "subscriptions / auto-renew", r"subscriptions?\.create|auto.?renew|recurring|free.?trial|billing.?cycle|mode:\s*['\"]subscription", CODE | UI, I),
    ("H2", "ad / analytics pixels (PHI or CIPA leakage)", r"fbq\(|connect\.facebook\.net|facebook.?pixel|gtag\(|googletagmanager|google-analytics|analytics\.track|mixpanel|amplitude|tiktok.?pixel|snaptr|linkedin.?insight|posthog", CODE | UI, I),
    ("A3", "LLM calls — check prompt injection & tool scope", r"openai|@anthropic-ai|@ai-sdk|langchain|llamaindex|chat\.completions|generateText|streamText|tools\s*:\s*\[|tool_choice", CODE, I),
    ("A4", "agent / automation with broad permissions", r"dangerously-?skip-?permissions|bypassPermissions|--yolo|auto.?approve|\"Bash\(\*\)\"|claude-code-action", CODE | CONFIG, I),
]

# --------------------------------------------------------------------------
# Mitigations: if NONE of these appear anywhere, the matching risk is a strong
# candidate. If they DO appear, check they're actually on the right path.
# --------------------------------------------------------------------------
MITIGATIONS = [
    ("F1", "licensed partner / BaaS / processor holds funds", r"unit\.co|@unit-finance|synctera|treasury.?prime|column\.com|stripe.?treasury|stripe.?connect|connected.?account|accounts\.create\(|modern.?treasury|increase\.com|lithic|marqeta|dwolla|currencycloud|transferwise|wise\.com|bridge\.xyz|circle\.com|sponsor.?bank|\bfbo\b|for benefit of|\bmoov\b|rapyd|galileo|bond\.tech"),
    ("F2", "OFAC / sanctions screening", r"\bofac\b|sanction|\bsdn\b|complyadvantage|comply.?advantage|sardine|alloy|middesk|watchlist|world.?check|chainalysis|trm.?labs|elliptic"),
    ("F18", "KYC / identity verification", r"\bkyc\b|know.?your.?customer|persona|onfido|jumio|veriff|socure|alloy|stripe.*identity|sumsub|idnow|footprint|identity.?verif"),
    ("F4", "dispute / error-resolution flow", r"dispute|error.?resolution|provisional.?credit|unauthori[sz]ed.?transfer|chargeback"),
    ("F5", "remittance disclosures / cancellation window", r"remittance.?(disclosure|receipt)|pre.?payment.?disclosure|cancel(lation)?.?window|30.?minute|exchange.?rate.?disclos|fx.?disclos"),
    ("F7", "double-entry ledger", r"\bledger|journal.?entr|double.?entry|\bpostings?\b|tigerbeetle|formance|\bblnk\b"),
    ("F8", "decimal / integer-cents money", r"decimal\.js|big\.js|bignumber|dinero|Prisma\.Decimal|@db\.Decimal|\bDecimal\b|numeric\(|NUMERIC|BigInt|_cents\b|amount_?in_?cents|amountCents|minor.?units|currency\.js"),
    ("F9", "idempotency / row locking", r"idempoten|FOR UPDATE|forUpdate|isolationLevel|serializable|advisory.?lock|optimistic.?lock|\$transaction"),
    ("F10", "webhook signature verification", r"constructEvent|verifyWebhook|webhooks?\.verify|svix|x-signature|x-hub-signature|stripe-signature|plaid-verification|createHmac|timingSafeEqual|compare_digest|verify_?signature|http-?signature"),
    ("F12", "FCRA adverse action / permissible purpose", r"adverse.?action|permissible.?purpose|reasons? for (denial|decline)"),
    ("F15", "dormancy / unclaimed property handling", r"dormant|escheat|unclaimed|abandoned.?property|last.?activity"),
    ("F17", "written security program / incident response", r"incident.?response|information.?security.?program|security\.txt|SECURITY\.md|\bwisp\b"),
    ("S1", "RLS / ownership scoping", r"enable row level security|create policy|auth\.uid\(\)|userId:\s*(session|user|ctx|auth)|\.eq\(\s*['\"]user_id|owner_?id|assertOwner|authorize\("),
    ("S4", "field-level encryption", r"encrypt|pgcrypto|pgsodium|\bkms\b|vault|createCipheriv|aes-?256|fernet|libsodium"),
    ("S5", "rate limiting", r"rate.?limit|ratelimit|express-rate-limit|throttl|slowapi|limiter|rack-attack"),
    ("S7", "MFA / 2FA", r"\bmfa\b|\btotp\b|two.?factor|\b2fa\b|webauthn|passkey|otplib|speakeasy|multi.?factor"),
    ("S8", "backups / disaster recovery", r"backup|\bpitr\b|point.?in.?time|failover|disaster.?recovery"),
    ("P1", "age gate / date of birth", r"date.?of.?birth|\bdob\b|birth.?date|age.?(gate|verif|check)|minimum.?age|over (13|18)"),
    ("P5", "Do Not Sell / GPC", r"do.?not.?sell|do.?not.?share|privacy.?choices|globalPrivacyControl|sec-gpc"),
    ("P3", "consent banner / CMP", r"cookie.?consent|consent.?banner|cookiebot|onetrust|osano|termly|iubenda|klaro|hasConsent|analytics.?consent|opt_?in_?capturing"),
    ("P6", "SMS consent / STOP handling", r"sms.?consent|\btcpa\b|consentToSms|sms_?opt|\bSTOP\b"),
    ("P7", "email unsubscribe", r"unsubscribe|list-unsubscribe|email.?preferences"),
    ("P9", "online cancellation", r"cancel.?subscription|cancelSubscription|billing.?portal|billingPortal|customer.?portal|cancel_at_period_end|subscriptions\.(cancel|del)"),
    ("P10", "consent / e-sign audit trail", r"consent.?(log|record|event)|consented_?at|consentedAt|agreed_?at|accepted_?at|terms_?version|termsVersion|\besign\b|e-sign"),
    ("P11", "audit log", r"audit.?log|audit_?trail|auditLog|append.?only"),
    ("H1", "BAA / business associate", r"\bbaa\b|business.?associate"),
    ("A3", "LLM guardrails", r"guardrail|moderation|prompt.?injection|requires?.?approval|human.?in.?the.?loop|allowed_?tools"),
]


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            p = Path(dirpath) / name
            ext = ".env" if name.startswith(".env") else p.suffix.lower()
            if ext not in ALL and ext != ".env":
                continue
            try:
                if p.stat().st_size > MAX_BYTES:
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            yield p, ext, text


def is_test(rel: str) -> bool:
    low = rel.lower()
    return bool(re.search(r"(^|/)(tests?|__tests__|spec|e2e|cypress|playwright)/|\.(test|spec)\.|_test\.|(^|/)test_", low))


def redact(s: str) -> str:
    return re.sub(SECRET_RE, lambda m: m.group(0)[:4] + "…[redacted]", s)


def snippet(line: str, ext: str) -> str:
    if ext == ".env":  # never echo env values
        return line.split("=", 1)[0].strip() + "=…[redacted]"
    s = redact(line.strip())
    return s if len(s) <= 160 else s[:157] + "..."


def stack_summary(root: Path) -> list[str]:
    found: list[str] = []
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            known = ["next", "react", "react-native", "expo", "vue", "svelte", "express", "fastify",
                     "@nestjs/core", "prisma", "@prisma/client", "drizzle-orm", "@supabase/supabase-js",
                     "firebase", "stripe", "plaid", "@interledger/open-payments", "@clerk/nextjs",
                     "next-auth", "openai", "@anthropic-ai/sdk", "ai", "twilio", "resend", "@sendgrid/mail",
                     "@upstash/ratelimit", "@sentry/nextjs", "posthog-js"]
            found += [f"{k}@{deps[k]}" for k in known if k in deps]
            found.append(f"({len(deps)} npm deps total)")
        except (ValueError, OSError):
            found.append("package.json (unparseable)")
    for f in ["requirements.txt", "pyproject.toml", "Gemfile", "go.mod", "Cargo.toml", "pubspec.yaml"]:
        if (root / f).exists():
            found.append(f)
    for d in ["prisma/schema.prisma", "supabase", "firebase.json", "vercel.json", "Dockerfile", ".github/workflows"]:
        if (root / d).exists():
            found.append(d)
    return found


def hygiene(root: Path, n_src: int, n_test: int) -> list[str]:
    out = [f"test files: {n_test} vs source files: {n_src} (ratio {n_test / max(n_src, 1):.2f})"]
    envs = [p.name for p in root.glob(".env*") if p.is_file()]
    gi = (root / ".gitignore").read_text(errors="ignore") if (root / ".gitignore").exists() else ""
    ignored = bool(re.search(r"^\s*\.env", gi, re.M))
    if envs:
        out.append(f"env files present: {', '.join(envs)} · .gitignore covers .env: {'yes' if ignored else 'NO'}")
    if (root / ".git").exists():
        try:
            tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, timeout=20).stdout.split()
            bad = [t for t in tracked if re.search(r"(^|/)\.env(\.|$)", t) and not t.endswith((".example", ".sample", ".template"))]
            if bad:
                out.append(f"TRACKED env files in git: {', '.join(bad[:10])}")
        except (OSError, subprocess.SubprocessError):
            pass
    lock = any((root / f).exists() for f in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "poetry.lock", "uv.lock"])
    out.append(f"lockfile committed: {'yes' if lock else 'NO'}")
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = sorted({**data.get("dependencies", {}), **data.get("devDependencies", {})})
            out.append("npm deps (eyeball for hallucinated/typosquat names): " + ", ".join(deps))
            scripts = data.get("scripts", {})
            risky = {k: v for k, v in scripts.items() if re.search(r"skip-permissions|--yolo|curl .*\|\s*(ba)?sh", v)}
            if risky:
                out.append(f"risky npm scripts: {risky}")
        except (ValueError, OSError):
            pass
    req = root / "requirements.txt"
    if req.exists():
        names = [re.split(r"[<>=~!\[; ]", l.strip())[0] for l in req.read_text(errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
        out.append("pip deps (eyeball for hallucinated names): " + ", ".join(names))
    return out


def scan(root: Path, max_hits: int) -> dict:
    risk_res = [(rid, label, re.compile(rx, fl), exts) for rid, label, rx, exts, fl in RISKS]
    sig_res = [(name, re.compile(rx, I), exts) for name, rx, exts in SIGNALS]
    mit_res = [(mid, label, re.compile(rx, I)) for mid, label, rx in MITIGATIONS]

    hits: dict[tuple[str, str], list[str]] = {(r[0], r[1]): [] for r in risk_res}
    counts: dict[tuple[str, str], int] = {k: 0 for k in hits}
    signals: dict[str, set[str]] = {s[0]: set() for s in sig_res}
    mitig: dict[tuple[str, str], str | None] = {(m[0], m[1]): None for m in mit_res}
    n_src = n_test = 0

    for p, ext, text in iter_files(root):
        rel = str(p.relative_to(root))
        test = is_test(rel)
        if ext in CODE:
            n_test += test
            n_src += not test
        lines = text.splitlines()
        for name, rx, exts in sig_res:
            if ext in exts and not test and (rx.search(text) or (name == "money movement" and PATH_RISKS["F1"].search(rel))):
                signals[name].add(rel)
        for mid, label, rx in mit_res:
            if mitig[(mid, label)] is None and ext != ".env":
                m = rx.search(text)
                if m:
                    ln = text.count("\n", 0, m.start()) + 1
                    mitig[(mid, label)] = f"{rel}:{ln}"
        if test:
            continue  # risk hits in tests are noise
        for rid, label, rx, exts in risk_res:
            if ext not in exts:
                continue
            path_hit = rid in PATH_RISKS and ext in CODE and bool(PATH_RISKS[rid].search(rel))
            for i, line in enumerate(lines, 1):
                if rx.search(line) or (path_hit and i == 1):
                    counts[(rid, label)] += 1
                    if len(hits[(rid, label)]) < max_hits:
                        hits[(rid, label)].append(f"{rel}:{i}  {snippet(line, ext)}")
                    if path_hit:
                        path_hit = False

    return {
        "root": str(root),
        "stack": stack_summary(root),
        "signals": {k: sorted(v)[:5] + ([f"(+{len(v) - 5} more)"] if len(v) > 5 else []) for k, v in signals.items() if v},
        "risks": [{"id": k[0], "label": k[1], "count": counts[k], "hits": v} for k, v in hits.items() if v],
        "mitigations": [{"id": k[0], "label": k[1], "found_at": v} for k, v in mitig.items()],
        "hygiene": hygiene(root, n_src, n_test),
    }


def print_text(r: dict) -> None:
    bar = "=" * 72
    print(bar)
    print(f" compliance-doctor scan :: {r['root']}")
    print(" Candidates only. Read each one in context before calling it a finding.")
    print(bar)
    print("\n[STACK]")
    for s in r["stack"] or ["(nothing recognized)"]:
        print(f"  {s}")
    print("\n[SIGNALS] what this app touches (files)")
    for k, v in r["signals"].items():
        print(f"  {k}: {', '.join(v)}")
    print("\n[RISK CANDIDATES]")
    if not r["risks"]:
        print("  (none)")
    for item in r["risks"]:
        more = f" (showing {len(item['hits'])} of {item['count']})" if item["count"] > len(item["hits"]) else ""
        print(f"\n  {item['id']} · {item['label']} — {item['count']} hit(s){more}")
        for h in item["hits"]:
            print(f"    {h}")
    print("\n[MITIGATIONS] FOUND = keyword exists somewhere (verify it's on the right path)")
    for m in r["mitigations"]:
        status = f"FOUND     {m['found_at']}" if m["found_at"] else "NOT FOUND"
        print(f"  {m['id']:<4} {status:<60} {m['label']}")
    print("\n[HYGIENE]")
    for h in r["hygiene"]:
        print(f"  {h}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--max-hits", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = scan(root, a.max_hits)
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
