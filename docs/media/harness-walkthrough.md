# Harness Walkthrough – Slide Deck

> **Format:** Use this markdown deck during onboarding or record a voice-over screen
> share to produce a short video. Each heading marks a slide.

## Slide 1 – Why the harness matters
- Ensures deterministic parity between QVM bytecode and native DLL builds.
- Enables automated regression detection for gameplay logic.
- Forms the backbone of CI smoke tests executed through `tools/tests/`.

## Slide 2 – Repository layout
- `tools/tests/match_sim.py` orchestrates deterministic match playback.
- Fixture data lives under `tools/tests/fixtures/` and `src/game/tests/`.
- `docs/testing-strategy.md` documents expectations for adding new suites.

## Slide 3 – Running the harness locally
- Create a virtual environment and install requirements via
  `pip install -r tools/tests/requirements.txt`.
- Invoke the smoke test: `python tools/tests/match_sim.py --demo samples/ffa_8p.dm_73`.
- Watch for diff reports in `artifacts/match-sim/` when results diverge.

## Slide 4 – Extending coverage
- Add scenario-specific fixtures to `tools/tests/fixtures/` and document them.
- Update `match_sim.py` to register new harness arguments or validations.
- Ensure CI parity by updating the GitHub workflow if new dependencies surface.

## Slide 5 – Troubleshooting tips
- Rerun with `--verbose` to inspect per-frame deltas.
- Use Binary Ninja or Ghidra to inspect suspect functions referenced in diffs.
- Escalate persistent mismatches in the #reverse-engineering Slack channel.
