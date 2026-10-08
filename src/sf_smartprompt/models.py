"""UML data objects for SmartPrompt — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Defect:
    rule: str
    issue: str
    fix: str

@dataclass
class PromptScore:
    clarity: int
    defects: list[Defect]
