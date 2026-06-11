# Botlib Qagame Instagib Target Goal Reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame-side Instagib target-goal seam that feeds the
tutorial `AINode_InstaGib` flow. The owning retail binary is
`qagamex86.dll`; the reconstructed range is `0x10020200..0x10020730`.

Unlike the previous voice/spawn pass, this round includes source code: the
three retail helpers were named in `references/symbol-maps/qagame.json` but had
no source bodies or alias-corpus entries in the current tree. The new source is
kept narrowly scoped to existing `bot_state_t` fields and the botlib AAS route
bridge.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmq3.c`
- `src/code/game/ai_dmq3.h`
- `src/code/game/ai_main.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_instagib_target_goal_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10020200` | `BotFindInstaGibTarget` | 1018 |
| `0x10020600` | `BotRefreshInstaGibTargetGoal` | 303 |
| `0x10020730` | `BotGetInstaGibTargetGoal` | 585 |

Both `FUN_...` and `sub_...` aliases are now promoted for the three rows so
the Ghidra, Binary Ninja, symbol-map, and source names agree.

## Source Reconstruction

The new helpers use the already-present source layout. No new speculative
`bot_state_t` members were added:

- `0x1794` maps to `bs->ltg_time`.
- `0x196C` maps to `bs->enemy`.
- `0x19C0..0x19FF` maps to the existing `bs->teamgoal` slab.
- `0x19A8` maps to `bs->ltgtype`.
- `0x1A48` maps to `bs->teamgoal_time`.

`BotFindInstaGibTarget` now preserves the retail shape: seed the best distance
with `100000000.0f`, revalidate the cached enemy through full `360` degree
visibility and AAS travel time, scan live non-dead clients for the closest
reachable target through `BotPointAreaNum`, and fall back to
`trap_AAS_PointReachabilityAreaIndex` plus the `+10` unit `trap_AAS_TraceAreas`
probe before accepting a target.

`BotRefreshInstaGibTargetGoal` now preserves the five-second refresh window on
`ltg_time`, the unusual retail invalid-entity success return, dead-target timer
clear, target-origin copy, `BotPointAreaNum` area refresh, `[-8, -8, -8]` to
`[8, 8, 8]` goal bounds, and zeroed goal flags.

`BotGetInstaGibTargetGoal` now preserves the refresh-first flow, nearest
not-same-team fallback, `LTG_KILL` setup, five-second `ltg_time`, sixty-second
`teamgoal_time`, `teamgoal.entitynum` seed, refresh call, and final
`memcpy(goal, &bs->teamgoal, sizeof(bot_goal_t))`.

## Inference Boundary

The retail `AINode_InstaGib` body is now source-backed by the follow-up
`ai_dmnet.c` reconstruction pass. The target-goal helpers in this note remain
the evidence base for the node's target picker, while the node itself builds
the transient movement goal directly from `trap_AAS_EntityInfo` in the
target-present path. The raw retail player-state cleanup writes on the
intermission/death exits remain a separate tail-layout boundary.

`BotGetInstaGibTargetGoal` intentionally follows the HLIL fallback loop shape:
the target-picker helper skips `bs->client`, while the goal fallback is gated by
`BotSameTeam` without adding a separate self-skip that is not visible in the
retail control flow.

## Botlib Wiring

The new regression pins the qagame botlib/AAS imports used by the reconstructed
helpers:

- `trap_AAS_EntityInfo` through `BotEntityInfo`.
- `trap_AAS_PointAreaNum` through `BotPointAreaNum`.
- `trap_AAS_PointReachabilityAreaIndex`.
- `trap_AAS_TraceAreas`.
- `trap_AAS_AreaTravelTimeToGoalArea`.

The same test checks the legacy syscall IDs, native `G_QL_IMPORT_BOTLIB_*`
slots, `sv_game.c` import-table registrations, and generated
`ql_game_imports.inc` wrappers.

## Tests

- `python -m pytest tests/test_botlib_qagame_instagib_target_goal_parity.py -q --tb=short`
- `python -m pytest tests/test_botlib_qagame_instagib_target_goal_parity.py tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_ai_dmq3_team_goal_parity.py tests/test_botlib_qagame_ai_dmq3_support_parity.py tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py tests/test_botlib_qagame_ai_dmq3_aim_attack_parity.py tests/test_botlib_qagame_ai_dmq3_activate_obstacle_parity.py tests/test_botlib_qagame_ai_dmq3_visibility_parity.py tests/test_botlib_residual_promoted_alias_coverage.py -q --tb=short`

`msbuild` and `cl` were not available on PATH in this environment, so a native
qagame compile pass could not be run here. No runtime launch was needed.

## Parity Estimate

- Focused Instagib target-goal alias-corpus coverage:
  **before 0% -> after 100%** for the three guarded rows.
- Focused Instagib target-goal source reconstruction confidence:
  **before 0% -> after 92%**. The helper bodies, field offsets, route checks,
  and timers are now source-backed; the larger retail tutorial node is now
  separately reconstructed with one documented cleanup-offset boundary.
- Focused botlib AAS route/import wiring confidence:
  **before 94% -> after 98%**.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 98.8% -> after 99.0%**. Remaining uncertainty is concentrated in
  the unreconstructed teammate/lead/torment/fragbait tutorial bodies, the
  instagib node's raw cleanup offsets, and native compile/runtime validation,
  not this helper seam.
