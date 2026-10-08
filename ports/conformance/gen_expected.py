#!/usr/bin/env python3
"""Regenerate expected.json from the Python reference (source of truth)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "src")))
from sf_smartprompt.core import lint  # noqa: E402

def to_dict(name, s):
    return {"name": name, "clarity": s.clarity,
            "defects": [{"rule": d.rule, "issue": d.issue, "fix": d.fix} for d in s.defects]}

v = json.load(open(os.path.join(HERE, "vectors.json"), encoding="utf-8"))
out = {"results": [to_dict(c["name"], lint(c.get("text", ""))) for c in v["cases"]]}
with open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False); f.write("\n")
print(f"wrote expected.json ({len(out['results'])} cases)")
