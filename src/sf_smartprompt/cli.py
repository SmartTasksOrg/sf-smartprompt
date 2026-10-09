"""SmartPrompt CLI — run `sf-smartprompt --demo`."""
import os, sys, json
from . import core
from ._version import __version__


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartPrompt {__version__}"); return 0
    demo = "--demo" in argv or not argv
    print(f"\n🦔 SmartPrompt {__version__}  ·  IAIso §4 · Context")
    result = core_demo()
    print(result)
    print(f"\nBacked by IAIso §4 · Context · part of the Smart* family · https://smarttasks.cloud\n")
    return 0


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
