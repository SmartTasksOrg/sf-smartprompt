#!/usr/bin/env python3
"""SmartPrompt integration adapter — the single source of truth for every
framework wrapper in this folder. Exposes TOOL_NAME, DESCRIPTION, INPUT_SCHEMA
and run(payload)->dict, plus a CLI:  python adapter.py --file <input>
"""
import argparse
import json
import os
import sys

from smartprompt.core import lint

TOOL_NAME = "smartprompt_lint"
DESCRIPTION = "Lint a prompt for missing role, goal, output format, constraints, and leaked secrets."
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
                "type": "string",
                "description": "The prompt text to lint"
        }
    },
    "required": ["text"],
}


def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def run(payload):
    """Run SmartPrompt on a payload dict and return a compact, JSON-safe result."""
    s = lint(payload.get('text', ''))
    result = {'clarity': s.clarity,
              'defects': [{'rule': d.rule, 'issue': d.issue, 'fix': d.fix} for d in s.defects]}
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=DESCRIPTION)
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--root")
    ap.add_argument("--sources")
    args = ap.parse_args(argv)
    payload = {'text': _read(args.file) if args.file else (args.text or '')}
    print(json.dumps(run(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
