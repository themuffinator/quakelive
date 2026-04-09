# Module Parity Audit (2026-04-06)

Superseded note:

- This document is preserved as the historical 2026-04-06 snapshot only.
- The current combined module audit is
  `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-09.md`.
- Current module-layer validation baseline on 2026-04-09:
  - `cgame`: `170 passed`
  - `qagame`: `91 passed`, `5 skipped`
  - `ui`: `49 passed`, `6 skipped`
  - shared platform-service seam: `41 passed`
- The residual `GM-G01`..`GM-G05` register is now closed, and current
  source-built module parity is treated as effectively `100%`.

## Scope

This audit summarizes current parity for the three source-built gameplay/UI DLLs:

- `cgame`
- `qagame`
- `ui`

It also derives:

- a weighted overall parity estimate for the combined game-module source base
- a broader full-source estimate for the retail Quake Live codebase in theory, with launcher/platform gaps called out explicitly

## Evidence Used

Committed retail evidence:

- `references/reverse-engineering/ghidra/cgamex86/{metadata.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/qagamex86/{metadata.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/uix86/{metadata.txt,functions.csv,analysis_symbols.txt}`
- `references/symbol-maps/{cgame,qagame,ui}.json`
- `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
- `docs/reverse-engineering/cgame-retail-parity-audit.md`
- `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`

Live verification used for this pass:

- `pytest tests/test_cgame_*.py tests/test_cl_console_cgame_parity.py tests/test_game_native_export_helper_parity.py -q --tb=no`
- `pytest tests/test_game_*.py tests/test_gametype_lifecycle.py -q --tb=no`
- `pytest tests/test_ui_*.py tests/test_fs_search_paths.py tests/test_vote_ui_throttle.py -q --tb=no`
- `pytest tests/test_platform_services.py -q --tb=no`

## Mapping Coverage Snapshot

Observed facts:

| Module | Ghidra functions | Symbol-map anchors | Anchors mapped |
| --- | ---: | ---: | ---: |
| `cgame` | `751` | `854` | `854 / 854` (`100.0%`) |
| `qagame` | `1027` | `1128` | `1128 / 1128` (`100.0%`) |
| `ui` | `348` | `444` | `444 / 444` (`100.0%`) |
| Combined | `2126` | `2426` | `2426 / 2426` (`100.0%`) |

Notes:

- `cgame` and `ui` expose their combined committed-corpus coverage directly in the symbol-map header.
- `qagame` does not yet carry the same summary header. The `1128` anchor count above is derived from the current `qagame.json` function-entry count. The `1027` Ghidra-function total comes from `references/reverse-engineering/ghidra/qagamex86/functions.csv`.

Interpretation:

- Naming and ownership recovery for all three DLLs is effectively saturated against the committed corpus.
- The remaining parity gap is not missing symbol discovery. It is source-shape, behavior, transport, packaging, and regression drift.

## Live Verification Snapshot

### `cgame`

Observed facts:

- Tests run: `168`
- Passed: `142`
- Failed: `26`
- Pass rate on executed tests: `84.5%`

Failure concentration:

- `tests/test_cgame_displaycontext_parity.py`: `19` failures
- `tests/test_cgame_ownerdraw_text_parity.py`: `6` failures
- single failures in:
  - `tests/test_cgame_ad_round_scoreboard_parity.py`
  - `tests/test_cgame_buffered_chat_parity.py`
  - `tests/test_cgame_console_surface_parity.py`
  - `tests/test_cgame_hud_parity.py`

Interpretation:

- The committed cgame ledgers still show `5 / 5` writable cgame lanes closed.
- The current source tree is therefore below the documented baseline because retail-backed regressions have reopened in the live source shape, especially around display-context, HUD text, native bridge, and event transport expectations.

### `qagame`

Observed facts:

- Tests run: `84`
- Passed: `77`
- Failed: `7`
- Skipped: `4`
- Pass rate on executed tests: `91.7%`

Current failures:

- `tests/test_game_attack_defend_parity.py::test_attack_defend_round_controller_hooks_use_retail_boundaries`
- `tests/test_game_callvote_option_parity.py::test_cmd_callvote_restores_retail_privileged_bypass`
- `tests/test_game_compact_scoreboard_parity.py::test_cgame_parses_smscores_with_compact_row_stride`
- `tests/test_game_nonteam_scoreboard_helper_parity.py::test_nonteam_scoreboard_helper_family_is_split_from_generic_builder`
- `tests/test_game_nonteam_scoreboard_helper_parity.py::test_deathmatch_scoreboard_dispatch_uses_retail_nonteam_helpers`
- `tests/test_game_round_controller_helper_parity.py::test_red_rover_controller_helpers_match_retail_mapping_surface`
- `tests/test_game_round_controller_helper_parity.py::test_red_rover_autojoin_helper_routes_team_selection`

Interpretation:

- The live failures line up closely with the open `qagame` gap register: round-controller exactness, scoreboard serializer/helper decomposition, and Red Rover controller behavior remain the highest-value open seams.

### `ui`

Pure UI suite observed facts:

- Tests run: `49`
- Passed: `49`
- Failed: `0`
- Skipped: `6`
- Pass rate on executed tests: `100.0%`

Cross-module UI-adjacent platform verification:

- `tests/test_platform_services.py` currently has `1` failure:
  - `test_module_native_export_qboolean_slots_use_explicit_wrappers`
- The failing assertion is not a menu/script/UI-asset regression. It is a shared native export-wrapper drift in `src/code/game/g_main.c`, where the expected `G_NativeClientConnect` wrapper surface is missing.

Packaging/gate detail:

- `artifacts/ui_validation/logs/ui_full_parity_gate.json` currently reports `overall_status: pass`
- `UI-G03` is now passing with the tracked bundle, overlay bundle, metrics artifact, and validation summary all present
- Current recorded bundle-validation details are `glyph_drift_count: 0`, `missing_shader_groups: []`, and `missing_configs: []`

Interpretation:

- Pure UI behavior and content parity remain very strong.
- The published 2026-04-05 UI audit and the current strict artifact-backed gate now agree. UI no longer carries an open packaging/evidence-state tranche.

## Current Parity Estimates

The estimates below are intentionally conservative and distinguish current worktree parity from fully documented baseline parity when those differ.

| Module | Current estimate | Basis |
| --- | ---: | --- |
| `cgame` | `92%` | Inherited from the dedicated cgame audit and still supported by `100%` mapping coverage, `5 / 5` lane closure, and a still-failing regression suite (`142 / 168` passed). |
| `qagame` | `78%` | Matches the dedicated qagame full audit. The live failures are consistent with the published open gap register rather than with a newly closed subsystem. |
| `ui` | `100%` | Pure UI parity checks are fully green and the strict UI parity gate is also green, with `UI-G03` now closed in the tracked artifact set. |

Reference-only baseline estimates if the current regressions/artifact drift were cleared without changing the underlying ledgers:

- `cgame`: `95%`
- `qagame`: `78%`
- `ui`: `100%`

## Overall Module Parity

Weighted by the committed retail Ghidra function counts (`751` `cgame`, `1027` `qagame`, `348` `ui`):

- Current weighted DLL parity: **`86.5%`**
- Reference-baseline weighted DLL parity: **`87.6%`**

Interpretation:

- The source-built DLL layer as a whole is in the high-parity range.
- The weighted overall score is dragged down much more by `qagame`'s still-open behavioral/helper-exactness work than by `ui`.
- `cgame`'s current delta is mostly regression debt, not discovery debt.

## Broader Full-Source Parity Against Retail Quake Live

This section is an inference, not a direct corpus metric.

Observed facts supporting a lower full-source estimate than the DLL-only score:

- Top-level `AUDIT.md` still rates native launcher/platform host parity as low.
- The same audit still rates retail-binary hosting as only medium parity relative to the current source-built DLL path.
- `docs/reverse-engineering/quakelive_steam_mapping_round_99.md` reports only `18.308%` address-backed mapping coverage for the retail `quakelive_steam.exe` host corpus, even though the exact GPL-aligned Win32 wrappers mapped there are individually high confidence.
- `IMPLEMENTATION_PLAN.md` still lists native launcher/platform host reconstruction and strict retail-DLL host validation as open strategic priorities.

Current full-source estimate versus the retail Quake Live source base in theory:

- **`~82%`**

Rationale:

- Start from the weighted current DLL parity (`86.4%`)
- Start from the weighted current DLL parity (`86.5%`)
- Adjust downward for the still-low launcher/platform host parity and the still-incomplete retail-binary host-compatibility surface
- Do not penalize twice for UI behavior, because the remaining UI gap is evidence-packaging rather than live menu/runtime drift

Confidence: medium.

## Bottom Line

- `cgame` is structurally close to retail and fully mapped, but the current source still has enough regression drift to keep it around `92%` instead of the `95%` documented baseline.
- `qagame` remains the main gameplay DLL parity limiter at `78%`, with the open work concentrated in round controllers, scoreboard helper decomposition, and Red Rover exactness.
- `ui` is now fully closed in both behavior and artifact-gated validation terms.
- The combined source-built game DLL layer is currently about **`86.5%`** parity against retail Quake Live.
- The broader full-source tree, including the native launcher/platform host and strict retail-DLL hosting surface, is currently about **`82%`** parity in theory.

## Recommended Next Closures

1. Recover the `cgame` display-context and ownerdraw text surface first; it dominates the current DLL regression debt.
2. Close the `qagame` round-controller and nonteam-scoreboard helper families next; those failures are the clearest remaining gameplay-side exactness gap.
3. Restore the missing `G_NativeClientConnect` wrapper form in `src/code/game/g_main.c`; it currently leaks into the shared platform-service verification surface.
4. Keep the launcher/platform host and strict retail-binary host-validation work separate from the DLL scores; those gaps still dominate the difference between high DLL parity and lower full-source parity.
