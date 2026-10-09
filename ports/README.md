# SmartPrompt \u2014 language ports

Native Go / Node / Java / PHP re-implementations of `lint(text) \u2192 PromptScore`.
Each reproduces the Python reference (`src/sf_smartprompt/core.py`) exactly \u2014 same rule
IDs, issue/fix strings, ordering, weights, and clarity score \u2014 verified by
`conformance/run.sh` against `conformance/expected.json`.

## Verify
```bash
cd conformance && ./run.sh
```
Regenerate the reference after changing rules: `python conformance/gen_expected.py`.
