"""SmartPrompt core — deterministic prompt linter.

`lint(text)` checks the basics every prompt needs (role, goal, output format,
constraints) and blocks secrets and personal data before they reach a model.

`lint(text, framework="broke")` adds the two BROKE checks the basics skip:
Background (context for the task) and Evolve (worked examples).
"""
from __future__ import annotations

import re

from .models import Defect, PromptScore

# Secrets and personal data. A prompt containing any of these should not be sent.
SECRET_PATTERNS = [
    ("OpenAI key", r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{12,}"),
    ("Anthropic key", r"\bsk-ant-[A-Za-z0-9_\-]{12,}"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{12,}"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_\-]{30,}"),
    ("Slack token", r"\bxox[baprse]-[A-Za-z0-9\-]{10,}"),
    ("Stripe key", r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}"),
    ("private key", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ("JWT", r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    ("password", r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*\S{4,}"),
    ("connection string", r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s:@/]+:[^\s:@/]+@"),
    ("email address", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b"),
    ("China mobile number", r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    ("China resident ID", r"(?<![0-9Xx])\d{17}[\dXx](?![0-9Xx])"),
    ("US SSN", r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"),
    ("payment card", r"\b(?:\d[ -]?){13,19}\b"),
]
_SECRETS = [(name, re.compile(p)) for name, p in SECRET_PATTERNS]


def _luhn(digits: str) -> bool:
    nums = [int(d) for d in digits][::-1]
    total = sum(n if i % 2 == 0 else (n * 2 - 9 if n * 2 > 9 else n * 2) for i, n in enumerate(nums))
    return total % 10 == 0


def find_secrets(text: str) -> list[str]:
    """Names of the kinds of secret or personal data found in `text`."""
    found = []
    for name, pat in _SECRETS:
        for m in pat.finditer(text):
            if name == "payment card":
                digits = re.sub(r"\D", "", m.group(0))
                if not (13 <= len(digits) <= 19 and _luhn(digits)):
                    continue
            found.append(name)
            break
    return found


RULES = [
    ("PROMPT-ROLE", "No role/persona set", lambda t: not re.search(r"\b(you are|act as|role:)\b", t, re.I),
     "Open with a role: 'You are a <expert> ...'."),
    ("PROMPT-GOAL", "Vague or missing goal", lambda t: not re.search(r"\b(write|summariz|analyz|list|compare|generate|fix|explain|classif|draft|review|translate|extract|rewrite|plan)", t, re.I),
     "State one concrete verb+object."),
    ("PROMPT-FORMAT", "No output format", lambda t: not re.search(r"\b(json|markdown|table|bullet|list|format|schema|csv|yaml)\b", t, re.I),
     "Name the output shape."),
    ("PROMPT-CONSTRAINTS", "No constraints", lambda t: not re.search(r"\b(word|sentence|tone|audience|concise|under \d|at most|no more than|limit|avoid|do not|don't|must)", t, re.I),
     "Add limits: length, tone, audience."),
    ("PROMPT-PII", "Secret/PII in prompt", lambda t: bool(find_secrets(t)),
     "Remove the secret or personal data — see SmartPangolin."),
]
WEIGHT = {"PROMPT-PII": 35, "PROMPT-GOAL": 20, "PROMPT-ROLE": 12, "PROMPT-FORMAT": 12, "PROMPT-CONSTRAINTS": 10}

# BROKE adds Background and Evolve (examples) to the basics above.
BROKE_RULES = [
    ("PROMPT-BACKGROUND", "No background or context",
     lambda t: not re.search(r"\b(background|context|we are|our (company|team|product|customers)|the situation|for a|this is for)\b", t, re.I),
     "Say what the task is for and who it serves."),
    ("PROMPT-EXAMPLES", "No examples",
     lambda t: not re.search(r"\b(example|e\.g\.|for instance|sample|like this|such as)\b|```|^\s*(input|output)\s*:", t, re.I | re.M),
     "Give one or two examples of a good answer."),
]
BROKE_WEIGHT = {"PROMPT-BACKGROUND": 8, "PROMPT-EXAMPLES": 6}

FRAMEWORKS = ("basic", "broke")


def lint(text: str, framework: str = "basic") -> PromptScore:
    """Score a prompt 0-100 and list what to fix. `framework`: "basic" or "broke"."""
    if framework not in FRAMEWORKS:
        raise ValueError(f"framework must be one of {FRAMEWORKS}")
    rules = RULES + (BROKE_RULES if framework == "broke" else [])
    weights = {**WEIGHT, **BROKE_WEIGHT}
    defects = []
    for rid, issue, test, fix in rules:
        if test(text):
            if rid == "PROMPT-PII":
                issue = f"{issue}: {', '.join(find_secrets(text))}"
            defects.append(Defect(rid, issue, fix))
    score = max(0, 100 - sum(weights.get(d.rule, 6) for d in defects))
    return PromptScore(score, defects)
