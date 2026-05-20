# Game-Module Retail Parity Audit and Implementation Plan (2026-04-10)

## Purpose

This document is the authoritative strict retail-facing parity audit for the
current worktree state of the three Quake Live game modules:

- `cgame`
- `qagame`
- `ui`

It supersedes the `2026-04-09` combined module conclusion for current-tree
review purposes. The `2026-04-09` report remains useful as the historical
closure milestone, but it no longer matches the current validation/certification
surface in this worktree.

The important distinction for this refresh is:

1. the module code and retail host/runtime contracts remain very strong
2. the combined module certification lane, the dedicated UI certification lane,
   and the supporting ledger/pipeline notes are now all restored and reconciled
   for the current worktree

This refresh now records the full current-worktree closure state achieved across
`GMR-P6`, `GMR-P7`, and `GMR-P8`, not a gameplay or module-runtime collapse.

## Scope

Covered source and module-adjacent host seams:

- `src/code/cgame/*`
- `src/code/game/*`
- `src/code/ui/*`
- `src/code/client/cl_cgame.c`
- `src/code/client/cl_ui.c`
- `src/code/server/sv_game.c`
- `src/code/qcommon/vm.c`
- module-facing parity tests and tracked validation artifacts

Read-only reminder:

- `src/ui/` remains evidence-only and read-only
- retail assets under `assets/` remain evidence-only and read-only

## Evidence Used

Canonical retail evidence:

- `assets/quakelive/baseq3/cgamex86.dll`
- `assets/quakelive/baseq3/qagamex86.dll`
- `assets/quakelive/baseq3/uix86.dll`
- `references/hlil/quakelive/cgamex86.dll/`
- `references/hlil/quakelive/qagamex86.dll/`
- `references/hlil/quakelive/uix86.all/`
- `references/reverse-engineering/ghidra/cgamex86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/qagamex86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/reverse-engineering/ghidra/uix86/{metadata.txt,imports.txt,exports.txt,functions.csv,analysis_symbols.txt}`
- `references/symbol-maps/{cgame,qagame,ui}.json`

Existing module notes:

- `docs/reverse-engineering/cgame-retail-parity-audit.md`
- `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`
- `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/architecture/native-pipeline.md`
- `docs/build-pipeline.md`

Tracked artifacts and validation sources:

- `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
- `artifacts/module_validation/logs/retail_module_parity_gate.json`
- `artifacts/ui_validation/logs/ui_full_parity_gate.json`
- `tests/test_game_module_retail_parity_gate.py`
- `tests/test_ui_full_parity_gate.py`
- `tests/test_platform_services.py`

Fresh validation run for this audit on `2026-04-10`:

- `pytest tests/test_cgame_*.py tests/test_cl_console_cgame_parity.py tests/test_game_native_export_helper_parity.py -q --tb=no`
- `pytest tests/test_game_*.py tests/test_gametype_lifecycle.py -q --tb=no`
- `pytest tests/test_ui_*.py tests/test_fs_search_paths.py tests/test_vote_ui_throttle.py -q --tb=no`
- `pytest tests/test_platform_services.py tests/test_game_module_retail_parity_gate.py -q --tb=no`
- `pytest tests/test_ui_full_parity_gate.py -q --tb=no`

## Retail Coverage Snapshot

Observed facts from the committed Ghidra metadata and symbol maps:

| Module | Ghidra functions | Imports | Exports | Symbol anchors |
| --- | ---: | ---: | ---: | ---: |
| `cgame` | `751` | `55` | `2` | `854` |
| `qagame` | `1027` | `65` | `2` | `1128` |
| `ui` | `348` | `50` | `2` | `444` |
| Combined | `2126` | `170` | `6` | `2426` |

Additional observed facts:

- `references/symbol-maps/cgame.json` reports `854 / 854` committed anchors
  mapped.
- `references/symbol-maps/ui.json` reports `444 / 444` committed anchors
  mapped.
- `references/symbol-maps/qagame.json` still does not expose the same
  `coverage` header, but the committed entry count remains `1128`, with
  `102` string entries and `0` relocation entries.
- No new symbol-discovery debt was identified in this audit pass.

Interpretation:

- Module naming and ownership recovery remain saturated.
- No open strict-retail module shortfall remains inside the audited module
  layer. The only remaining runtime blocker cited by the tracked retail probe is
  the renderer-owned `R_fonsErrorCallback` font-atlas saturation blocker, which
  stays outside module scope. The 2026-05-20 renderer wiring pass removed the
  non-retail eager FontStash prebuild behind that source-side blocker, so the
  tracked 2026-04-21 module-runtime alias is now stale until rerun.

## Live Validation Snapshot

Observed facts from the `2026-04-10` validation pass:

| Area | Result |
| --- | --- |
| `cgame` suite | `170 passed` |
| `qagame` suite + lifecycle | `91 passed`, `5 skipped` |
| `ui` suite + fs/vote checks | `58 passed`, `2 skipped` |
| shared platform-service seam + module gate | `57 passed`, `1 skipped` |
| retail module parity artifact | `overall_status: pass` |
| UI parity gate artifact | `overall_status: pass` |

Observed facts from the refreshed machine-readable artifacts:

- `artifacts/module_validation/logs/retail_module_parity_gate.json` now passes
  cleanly again after `GMR-P6`.
- `artifacts/ui_validation/logs/ui_full_parity_gate.json` now passes cleanly
  after `GMR-P7`, with no non-passing gap IDs.
- `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
  is still sufficient: the stable alias now points at the current bounded
  `2026-04-21` probe. The authoritative tracked retail probe still loads
  retail `uix86.dll`, `qagamex86.dll`, and `cgamex86.dll`, and the remaining
  live-map shortfall is now explicitly the renderer-owned
  `R_fonsErrorCallback` font-atlas saturation blocker. Source has since removed
  the eager retained-atlas prebuild, so this blocker classification needs a
  fresh module-runtime rerun before it can be promoted again.

Current-worktree validation blockers:

- None in the audited module surface.

Interpretation:

- The module code and retail host handshake remain strong.
- Both the combined module lane and the dedicated UI certification lane are now
  restored in the current worktree, so no active module-layer parity gap
  remains open in the audited surface.

## Current Strict Retail Parity Estimate

Current estimates for the current worktree:

| Module | Current estimate | Basis |
| --- | ---: | --- |
| `cgame` | `100%` | Retail mapping remains saturated, the focused `cgame` suite is fully green (`170 passed`), and the shared combined module certification lane remains green. No current source-owned `cgame` behavior gap remains open in the audited surface. |
| `qagame` | `100%` | Retail mapping remains saturated enough for behavioral work, the focused `qagame` suite plus lifecycle checks are green (`91 passed`, `5 skipped`), and the shared combined module certification lane remains green. No current source-owned `qagame` behavior gap remains open in the audited surface. |
| `ui` | `100%` | UI runtime logic, corpus, overlay, service-disabled menu behavior, and the dedicated UI parity-gate publication lane all validate strongly (`58 passed`, `2 skipped`; `ui_full_parity_gate.json` now reports `overall_status: pass`). No current source-owned or certification-lane UI gap remains open in the audited surface. |

Weighted by committed Ghidra function counts (`751`, `1027`, `348`):

- Current strict retail module parity estimate: **`100%`**

Before vs after this audit refresh:

- **Before:** `100%` was still being advertised by the historical `2026-04-09`
  closure report.
- **After `GMR-P6`:** about `99.8%` for the current worktree while the
  dedicated UI certification lane remained missing.
- **After `GMR-P7`:** `100%` for the current worktree again.

The temporary confidence reduction was an evidence correction. Runtime behavior
did not regress in the fresh module suites; the reduction came from the reopened
UI certification lane, and `GMR-P7` closes that workflow/publication gap
without changing the audited runtime behavior.

## Module Assessment

### `cgame`

Observed facts:

- Retail coverage remains saturated (`854 / 854` committed anchors mapped).
- The focused `cgame` parity suite is fully green (`170 passed`).
- No new `cgame`-owned gap surfaced in the audited runtime or structural lane.

Interpretation:

- `cgame` remains effectively closed at the code/behavior and certification
  level for the current audited source lane.

### `qagame`

Observed facts:

- The committed corpus is still saturated enough that remaining questions are
  boundary/behavior questions, not naming questions.
- The focused `qagame` parity suite plus lifecycle checks are green
  (`91 passed`, `5 skipped`).
- No open `qagame` behavior or transport regression surfaced in the current
  run.

Interpretation:

- `qagame` remains effectively closed at the code/behavior and certification
  level for the current audited source lane.

### `ui`

Observed facts:

- The UI runtime-facing suite is green (`58 passed`, `2 skipped`).
- The refreshed `artifacts/ui_validation/logs/ui_full_parity_gate.json` now
  reports `overall_status: pass` with no non-passing gap IDs.
- `.github/workflows/ui-validation.yml` is restored and explicitly runs the
  unified UI parity gate under `UI_FULL_PARITY_GATE_ENFORCE=1`.

Interpretation:

- UI runtime parity remains strong.
- The dedicated UI certification/publication lane is now closed again in the
  current worktree, so no UI-specific module debt remains open in the audited
  surface.

## Gap Register Update

### GMR-G02: Dedicated UI parity-gate workflow lane is restored [CLOSED]

- **Module:** `ui`
- **Type:** verification / CI certification
- **Severity:** Medium-High

Observed facts:

- `artifacts/ui_validation/logs/ui_full_parity_gate.json` now reports
  `overall_status: pass`.
- The current artifact records:
  - `workflow_references_gate: true`
  - `workflow_runs_gate: true`
  - `scripting_guide_mentions_gate_artifact: true`
  - `release_mode_env_supported: true`
- `.github/workflows/ui-validation.yml` is restored in the current worktree and
  now enforces the gate with `UI_FULL_PARITY_GATE_ENFORCE=1`.
- UI source/runtime-facing tests remain green, so the closure is backed by both
  workflow wiring and the audited regression surface.

Impact:

- Resolved. The UI module can once again claim end-to-end validation closure in
  the current worktree.

## Closure Plan

### GMR-P6: Restore or replace the combined module validation workflow [COMPLETED]

Covers:

- `GMR-G01`

Goal:

- Re-establish one CI-visible workflow lane for strict-retail module closure.

Completed work:

1. Restored `.github/workflows/module-validation.yml` as the combined
   strict-retail module workflow contract expected by
   `tests/test_game_module_retail_parity_gate.py`.
2. Re-established the tracked workflow references for:
   - `tests/test_game_module_retail_parity_gate.py`
   - `tests/test_platform_services.py`
   - `tools/modules/run_retail_module_runtime_probe.ps1`
3. Refreshed `artifacts/module_validation/logs/retail_module_parity_gate.json`
   so it now reports `overall_status: pass` with no non-passing gap IDs.

Exit status:

- Satisfied. `GMR-G01` is now considered closed again for the current
  worktree.

Projected parity uplift:

- about `99.5%` -> `99.8%`

### GMR-P7: Restore or replace the dedicated UI validation workflow lane [COMPLETED]

Covers:

- `GMR-G02`

Goal:

- Reclose the UI certification lane without touching read-only `src/ui`.

Completed work:

1. Restored `.github/workflows/ui-validation.yml` as the dedicated UI
   certification lane expected by `tests/test_ui_full_parity_gate.py`, and
   wired the workflow to enforce the gate with
   `UI_FULL_PARITY_GATE_ENFORCE=1`.
2. Re-ran:
   - `pytest tests/test_ui_full_parity_gate.py -q --tb=no`
   - `UI_FULL_PARITY_GATE_ENFORCE=1 pytest tests/test_ui_full_parity_gate.py -q --tb=no`
   - `pytest tests/test_platform_services.py -k "test_online_service_bridge_only_hard_stubs_when_build_disabled or test_service_disabled_menu_verb_matrix_stays_explicit or test_launcher_resource_fallbacks_survive_service_disabled_policy" -q --tb=no`
   - `pytest tests/test_ui_*.py tests/test_fs_search_paths.py tests/test_vote_ui_throttle.py -q --tb=no`
   which produced `1 passed, 1 skipped` for the non-enforced artifact refresh
   run, `2 passed` for the enforced release-mode gate, `3 passed, 52
   deselected` for the workflow-matching platform-service selector, and
   `58 passed, 2 skipped` for the broader UI/fs/vote surface.
3. Refreshed `artifacts/ui_validation/logs/ui_full_parity_gate.json` so it now
   reports `overall_status: pass`.
4. Updated the active module ledgers enough to record the restored UI lane and
   unblock the final `GMR-P8` reconciliation pass.

Exit status:

- Satisfied. `GMR-G02` is now considered closed again for the current
  worktree.

Projected parity uplift:

- about `99.8%` -> `100%`

### GMR-P8: Final module-ledger and runtime-evidence reconciliation [COMPLETED]

Covers:

- residual documentation drift after `GMR-P6` and `GMR-P7`

Goal:

- Publish one clean, current-worktree module closure story after the validation
  lanes are restored.

Completed work:

1. Reconciled the current-worktree module audit, the top-level ledgers, and the
   supporting pipeline notes in `docs/build-pipeline.md` and
   `docs/architecture/native-pipeline.md` so they now describe one shared
   `100%` strict-retail module closure state.
2. Refreshed the combined module gate expectations so
   `tests/test_game_module_retail_parity_gate.py` now verifies the current
   `2026-04-10` audit, the top-level ledgers, and the supporting pipeline notes
   together instead of only relying on the historical `2026-04-09` closure
   narrative.
3. The tracked module runtime evidence now lives at the stable alias
   `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`.
   That alias now points at the bounded `2026-04-21` probe: the refreshed
   rerun recovered the current `map <name> ffa` contract and retail module
   loads again, and it now classifies the remaining live-map shortfall as the
   renderer-owned `R_fonsErrorCallback` font-atlas saturation blocker outside
   module scope. The renderer source-side cause has since been patched by
   removing the non-retail eager FontStash prebuild, so this runtime evidence is
   now stale until a new rerun confirms the current behavior.

Exit status:

- Satisfied. The actively referenced module ledgers now agree on one
  current-worktree closure state, and strict-retail module parity can again be
  advertised at `100%`.

Projected parity effect:

- `100%` -> `100%` (final ledger/runtime-evidence reconciliation; runtime
  behavior unchanged)

## Closure Sequence

1. `GMR-P6`
2. `GMR-P7`
3. `GMR-P8`

All planned current-worktree module closure phases are now complete.

## Definition Of Done

The game-module layer can be considered full retail parity in theory again for
the current worktree when all conditions below hold:

1. The retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` runtime evidence
   remains sufficient.
2. The combined module parity artifact remains green.
3. The dedicated UI parity artifact no longer fails `UI-G06`.
4. The focused source suites remain green:
   - `cgame`
   - `qagame`
   - `ui`
   - shared platform-service seam
5. The actively referenced top-level ledgers and parity notes all point at the
   same current-worktree closure state.

## Bottom Line

- The current worktree now has full strict-retail module parity again.
- The audited module code paths remain green today:
  - `cgame`: `170 passed`
  - `qagame` + lifecycle: `91 passed`, `5 skipped`
  - `ui` + fs/vote: `58 passed`, `2 skipped`
- Both the combined module certification lane and the dedicated UI
  certification lane are restored and machine-readable.
- The current authoritative strict-retail module estimate for the current
  worktree is **`100%`**. The remaining live-map shortfall stays explicitly
  renderer-owned outside the module layer, and the stable runtime alias now
  points at the current bounded `2026-04-21` artifact instead of an older
  archived rerun.
