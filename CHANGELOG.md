# Changelog

## Unreleased

### Security
- Install instructions no longer name packages the maintainers have not
  published. Until the first release, install from a clone (README, "Install").
- New `SECURITY.md` (private vulnerability reporting), `names.json` (the only
  official package names) and a CI check that fails when a document names any
  other package.
- Releases are built and published only by `.github/workflows/release.yml`
  through PyPI trusted publishing, with provenance attestations.

### Changed
- **Renamed (breaking), `sf-` = Smart Family:** repository `SmartTasksOrg/sf-smartprompt`, PyPI package `sf-smartprompt`, command `sf-smartprompt`, import package `sf_smartprompt`, MCP server `io.github.smarttasksorg/sf-smartprompt`. The unprefixed names are not used any more, so nobody can be sent to a look-alike.
- README: "Install" and "Status" sections; the MCP marker on line 1 is the bare server name.
- `pyproject.toml`: SPDX licence, `NOTICE` in the wheel, "3 - Alpha" classifier, Source/Issues/Security/Changelog URLs.
- `make test` runs pytest (it ran a file that executed no test).
- `MARKETING.md` moved out of the public repository.
- `ports/node/package.json`: repository, files and publishConfig (still unpublished).
- Java port writes UTF-8, so its output matches the reference on Windows consoles too.

## 3.0.0 — the family release
- **Joined the Smart\* family**: shared mascot, manifesto, and `PROMPT-*` rule-ID style.
- **IAIso conformance**: implements **§4 · Context**; see `spec/iaiso-map.json`.
- **Cross-tool stacking**: composes with sibling tools via shared receipts + standard.
- **UML data objects** exposed in `src/smartprompt/models.py` and `site/playground.html`.
- **Ships with a synthetic demo** so `smartprompt --demo` works on clone.
- MCP server, pre-commit hook, and multi-language install parity.

## 2.x — standalone tool (pre-family)
## 1.x — initial release
