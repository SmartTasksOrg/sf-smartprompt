"""Behaviour of core.lint: each rule, its weight, and the clarity score."""
from sf_smartprompt import core

GOOD = "You are a senior analyst. Summarize this into 5 markdown bullets, under 100 words, for execs."


def rules(text):
    return [d.rule for d in core.lint(text).defects]


def test_a_complete_prompt_scores_100():
    s = core.lint(GOOD)
    assert s.clarity == 100 and s.defects == []


def test_each_missing_part_is_one_defect_with_its_weight():
    s = core.lint("write something about our product")
    assert [d.rule for d in s.defects] == ["PROMPT-ROLE", "PROMPT-FORMAT", "PROMPT-CONSTRAINTS"]
    assert s.clarity == 100 - 12 - 12 - 10


def test_no_goal_verb_is_the_heaviest_ordinary_defect():
    assert "PROMPT-GOAL" in rules("You are a poet. Our product, in a table, under 50 words.")
    assert core.lint("You are a poet. Our product, in a table, under 50 words.").clarity == 80


def test_a_secret_in_the_prompt_costs_35():
    s = core.lint(GOOD + " Use key sk-abcdefghijklmnop.")
    assert [d.rule for d in s.defects] == ["PROMPT-PII"] and s.clarity == 65
    assert "PROMPT-PII" in rules(GOOD + " AKIAABCDEFGHIJKL")


def test_the_worst_prompt_never_goes_below_zero_and_every_defect_has_a_fix():
    s = core.lint("hello sk-abcdefghijklmnop")
    assert s.clarity == 100 - sum(core.WEIGHT.values()) >= 0
    assert all(d.fix for d in s.defects)
