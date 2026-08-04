"""SmartPrompt core — deterministic prompt linter."""
import re
from .models import Defect, PromptScore

RULES = [
    ("PROMPT-ROLE", "No role/persona set", lambda t: not re.search(r"\b(you are|act as|role:)\b", t, re.I),
     "Open with a role: 'You are a <expert> ...'."),
    ("PROMPT-GOAL", "Vague or missing goal", lambda t: not re.search(r"\b(write|summariz|analyz|list|compare|generate|fix|explain|classif)", t, re.I),
     "State one concrete verb+object."),
    ("PROMPT-FORMAT", "No output format", lambda t: not re.search(r"\b(json|markdown|table|bullet|list|format|schema)\b", t, re.I),
     "Name the output shape."),
    ("PROMPT-CONSTRAINTS", "No constraints", lambda t: not re.search(r"\b(word|sentence|tone|audience|concise|under \d)", t, re.I),
     "Add limits: length, tone, audience."),
    ("PROMPT-PII", "Secret/PII in prompt", lambda t: bool(re.search(r"(sk-[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,})", t)),
     "Remove the secret — see SmartPangolin."),
]
WEIGHT = {"PROMPT-PII": 35, "PROMPT-GOAL": 20, "PROMPT-ROLE": 12, "PROMPT-FORMAT": 12, "PROMPT-CONSTRAINTS": 10}

def lint(text: str) -> PromptScore:
    defects = [Defect(rid, issue, fix) for rid, issue, test, fix in RULES if test(text)]
    score = max(0, 100 - sum(WEIGHT.get(d.rule, 6) for d in defects))
    return PromptScore(score, defects)
