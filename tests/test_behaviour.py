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


import pytest


@pytest.mark.parametrize("leak,kind", [
    ("sk-ant-api03-abcdefghijklmnop", "Anthropic key"),
    ("ghp_" + "a" * 36, "GitHub token"),
    ("AIza" + "b" * 35, "Google API key"),
    ("-----BEGIN PRIVATE KEY-----", "private key"),
    ("password: hunter22", "password"),
    ("postgres://app:s3cret@db:5432/x", "connection string"),
    ("alice@example.com", "email address"),
    ("13800138000", "China mobile number"),
    ("11010519491231002X", "China resident ID"),
    ("4111 1111 1111 1111", "payment card"),
])
def test_secrets_and_personal_data_are_found(leak, kind):
    s = core.lint(GOOD + " " + leak)
    assert [d.rule for d in s.defects] == ["PROMPT-PII"]
    assert kind in s.defects[0].issue and s.clarity == 65


def test_numbers_that_fail_the_card_checksum_are_not_cards():
    assert "payment card" not in core.find_secrets("order 1234 5678 9012 3456")


def test_broke_adds_background_and_examples():
    s = core.lint(GOOD, framework="broke")
    assert [d.rule for d in s.defects] == ["PROMPT-BACKGROUND", "PROMPT-EXAMPLES"]
    assert s.clarity == 100 - 8 - 6
    full = ("We are a sports-drink brand planning a summer campaign. You are a creative director. "
            "Write 5 posts as a markdown table, under 200 words each. Example: 'Beat the heat...'")
    assert core.lint(full, framework="broke").clarity == 100
    with pytest.raises(ValueError):
        core.lint(GOOD, framework="other")


def test_cli_lints_a_file_and_sets_the_exit_code(tmp_path, capsys):
    from sf_smartprompt import cli
    f = tmp_path / "prompt.txt"
    f.write_text(GOOD)
    assert cli.main([str(f)]) == 0
    assert cli.main([str(f), "--framework", "broke", "--min", "90"]) == 1
    f.write_text(GOOD + " key sk-abcdefghijklmnop")
    assert cli.main([str(f), "--min", "0", "--json"]) == 1      # a leak always fails
    assert "PROMPT-PII" in capsys.readouterr().out
