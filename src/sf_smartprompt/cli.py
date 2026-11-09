"""SmartPrompt CLI.

    sf-smartprompt --demo
    sf-smartprompt PROMPT [--framework basic|broke] [--min 70] [--json]

PROMPT is a file path, or `-` to read standard input. Exit code 0 when the
score is at least --min and no secret or personal data was found, 1 otherwise.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict

from . import core
from ._version import __version__

BANNER = f"\n🦔 SmartPrompt {__version__}  ·  IAIso §4 · Context"
FOOTER = "\nBacked by IAIso §4 · Context · part of the Smart* family · https://smarttasks.cloud\n"


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartPrompt {__version__}"); return 0
    if not argv or "--demo" in argv:
        print(BANNER); print(core_demo()); print(FOOTER); return 0

    ap = argparse.ArgumentParser(prog="sf-smartprompt")
    ap.add_argument("prompt", help="file containing the prompt, or - for stdin")
    ap.add_argument("--framework", choices=core.FRAMEWORKS, default="basic")
    ap.add_argument("--min", type=int, default=70, help="lowest acceptable clarity score")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    text = sys.stdin.read() if a.prompt == "-" else open(a.prompt, encoding="utf-8").read()
    s = core.lint(text, framework=a.framework)
    if a.json:
        print(json.dumps(asdict(s), indent=2, ensure_ascii=False))
    else:
        print(f"clarity {s.clarity}/100")
        for d in s.defects:
            print(f"  ✗ {d.rule:<18} {d.issue} → {d.fix}")
    leaked = any(d.rule == "PROMPT-PII" for d in s.defects)
    return 0 if s.clarity >= a.min and not leaked else 1


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    good = "You are a senior analyst. Summarize this into 5 markdown bullets, under 100 words, for execs."
    bad = "write something about our product"
    out = []
    for label, p in [("clean", good), ("messy", bad)]:
        s = core.lint(p)
        out.append(f"[{label}] clarity {s.clarity}/100" + ("" if not s.defects else ""))
        for d in s.defects:
            out.append(f"  ✗ {d.rule:<18} {d.issue} → {d.fix}")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
