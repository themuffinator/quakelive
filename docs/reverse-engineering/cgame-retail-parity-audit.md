# Cgame Retail Parity Audit

Last updated: 2026-04-05

Scope:

- `src/code/cgame/*`
- `src/code/client/cl_cgame.c`
- cgame-focused parity tests under `tests/`

This note separates three different views of parity that were partially conflated in the older top-level audit:

1. retail symbol and mapping coverage
2. writable source-lane closure against the committed retail ledgers
3. current dirty-worktree verification status

## Evidence Used

Retail evidence:

- `references/reverse-engineering/ghidra/cgamex86/metadata.txt`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/analysis_symbols.txt`
- `references/symbol-maps/cgame.json`
- `docs/reverse-engineering/cgame-mapping.md`
- `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

Current-source evidence:

- `src/code/cgame/*`
- `src/code/client/cl_cgame.c`
- `git status --short`

Verification run:

- `pytest tests/test_cgame_*.py tests/test_cl_console_cgame_parity.py tests/test_game_native_export_helper_parity.py -q --tb=no`

## Retail Coverage Stats

Observed facts from `references/symbol-maps/cgame.json`:

| Metric | Value |
| --- | --- |
| Ghidra functions in committed corpus | `751` |
| Ghidra functions mapped | `751 / 751` (`100.0%`) |
| HLIL-only anchors | `103` |
| Combined committed anchors | `854` |
| Combined anchors mapped | `854 / 854` (`100.0%`) |
| Resolved strings | `168 / 168` (`100.0%`) |
| Unresolved relocations | `0` |

Interpretation:

- The retail `cgamex86.dll` naming and ownership map is effectively complete against the committed corpus.
- The remaining cgame questions are no longer "what is this retail function?" questions; they are source-shape, runtime, and regression questions.

## Writable Cgame Lane Status

Observed facts from `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`:

| Lane | Theme | Status |
| --- | --- | --- |
| `CG-A` | Browser, widget, and overlay runtime | `CLOSED` |
| `CG-B` | Configstring, scoreboard, and playerinfo transport | `CLOSED` |
| `CG-C` | Event payload, prediction, and snapshot bridges | `CLOSED` |
| `CG-D` | Draw, POI, world-marker, and effects exactness | `CLOSED` |
| `CG-E` | Social sidecar, native export tail, and command overlay parity | `CLOSED` |

Summary:

- Tracked cgame lanes closed: `5 / 5` (`100.0%`)
- Appendix A browser direct-owner gaps: none
- Appendix B non-browser direct-owner gaps: none

Interpretation:

- The writable cgame parity ledger currently describes no active source-owned retail gap.
- Any remaining parity loss in the current worktree is therefore a regression or drift problem, not a missing-ledger problem.

## Current Worktree Verification

Observed facts from the 2026-04-05 pytest pass:

| Metric | Value |
| --- | --- |
| Tests run | `166` |
| Passed | `140` |
| Failed | `26` |
| Pass rate | `84.3%` |

Failure clustering:

| Test file | Failures |
| --- | --- |
| `tests/test_cgame_displaycontext_parity.py` | `16` |
| `tests/test_cgame_ownerdraw_text_parity.py` | `6` |
| `tests/test_cgame_ad_round_scoreboard_parity.py` | `1` |
| `tests/test_cgame_buffered_chat_parity.py` | `1` |
| `tests/test_cgame_console_surface_parity.py` | `1` |
| `tests/test_cgame_hud_parity.py` | `1` |

Additional current-state context:

- The worktree is dirty.
- `git status --short` reports `17` modified files under `src/code/cgame/`.

## Regression Bands In The Current Worktree

The failing tests cluster into a few clear areas:

1. HUD and ownerdraw text drift
   - Match-state label builders, match-status text families, level or round timer formatting, intro panel text, endgame summary copy, placement score lines, and starting-weapons preview helpers are no longer matching the retail-backed regression expectations.
2. Browser and display-context drift
   - Browser input routing, active-item hit tests, display-context helper ownership, and named wrapper expectations are out of sync with the parity suite.
3. Native bridge and import-table drift
   - Header counts, syscall wrappers, and native import-table ownership for the cgame bridge are no longer matching the locked parity surface.
4. Event and transport drift
   - Damage-plum transport expectations and some event-side retail helper ownership checks are failing again.
5. Buffered chat and HUD sidecar drift
   - The shared buffered print path and the crosshair teammate health or armor readout no longer match the current retail-backed tests.

Interpretation:

- The cgame documentation and symbol map show a fully closed parity ledger.
- The current dirty source tree does not presently validate at that same level.
- The dominant gap is now conformance of live source shape to the already-established retail map, especially in `cg_newdraw.c`, `cg_draw.c`, `cg_event.c`, `cg_servercmds.c`, `cg_public.h`, and `cl_cgame.c`.

## Audit Conclusion

Observed facts:

- Retail cgame mapping coverage is complete in the committed corpus: `854 / 854` anchors mapped.
- The writable cgame parity ledger is fully closed: `5 / 5` tracked cgame lanes closed.
- The current worktree fails `26` cgame-focused parity tests, concentrated in display-context and ownerdraw text coverage.

Inference:

- The cgame subsystem is in the `very high retail coverage / high documented parity` range at the reference and mapping level.
- The current dirty worktree is lower than that documented baseline because it no longer satisfies the full cgame parity regression suite.

Estimated parity versus the retail Quake Live cgame source base:

- Committed cgame reference baseline: about `95%`
- Current dirty worktree: about `92%`

This estimate is an inference from three signals rather than a direct corpus metric:

- `100%` retail symbol coverage
- `100%` tracked writable lane closure
- `84.3%` pass rate on the current cgame-focused parity suite

## Recommended Next Actions

1. Recover the `tests/test_cgame_displaycontext_parity.py` surface first; that one file accounts for most current audit failures.
2. Reconcile `cg_newdraw.c` and `cg_draw.c` with the locked ownerdraw and HUD text helpers before making further cgame feature changes.
3. Revalidate the cgame native import and export bridge surface in `cg_public.h`, `cg_syscalls.c`, and `src/code/client/cl_cgame.c`.
4. Refresh the top-level `AUDIT.md` wording once the dirty worktree is stabilized, because its March 2026 cgame summary now understates the reference-ledger state and overstates source stability at the same time.
