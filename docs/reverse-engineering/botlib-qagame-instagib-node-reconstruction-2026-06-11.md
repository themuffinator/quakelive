# Botlib Qagame Instagib Node Reconstruction - 2026-06-11

## Scope

This pass reconstructs the qagame `AIEnter_InstaGib` and `AINode_InstaGib`
pair and wires `BotDeathmatchAI` into it for retail instagib mode. The owning
retail binary is `qagamex86.dll`; the reconstructed rows are
`0x100133C0..0x10013410`.

## Evidence

- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/symbol-maps/qagame.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `src/code/game/ai_dmnet.c`
- `src/code/game/ai_dmq3.c`
- `src/code/game/ai_main.h`
- `tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py`
- `tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py`
- `tests/test_botlib_qagame_instagib_target_goal_parity.py`

## Source Reconstruction

`AIEnter_InstaGib` now preserves the retail entry writes:

- `ltg_time = FloatTime() + 99999.0f`;
- retail LTG slot `0x15`, now named `LTG_INSTAGIB`;
- `BotRecordNodeSwitch(bs, "insta gib!", "", "")`;
- `bs->ainode = AINode_InstaGib`.

`AINode_InstaGib` now preserves the source-representable retail body:

- calls `BotFindInstaGibTarget` before state exits, matching the HLIL order;
- routes observer, intermission, and dead states through the exact retail debug
  strings;
- exits to seek-LTG when `g_instaGib.integer` no longer matches the retail
  instagib-mode flag;
- hands normal enemy acquisition to `AIEnter_Battle_Fight` after resetting the
  last avoid reach and emptying the goal stack;
- uses the retail travel mask `0x011C0FBE`, then applies lava/slime,
  rocket-jump, and Beyond Reality adjustments;
- builds the transient goal from `BotEntityInfo`, `BotPointAreaNum`, target
  entity number, zeroed metadata, and `[-8, -8, -8]..[8, 8, 8]` bounds;
- empties and pushes the target goal before movement, matching the botlib goal
  stack calls in HLIL;
- preserves close-range/random roam look handling through
  `BotSetIdealViewAnglesToPoint`;
- runs obstacle prediction, movement setup, `trap_BotMoveToGoal`,
  `BotAIBlocked`, `BotClearPath`, movement-view selection, and
  movement-weapon handoff.

`BotDeathmatchAI` now mirrors the retail callsite at `0x1001F359` with the
source guards available in this tree: active `g_instaGib`, not already
`LTG_INSTAGIB`, not ordered, and no current enemy.

## Inference Boundary

The retail intermission/dead exits clear one entity flag bit and two raw
player-state offsets before changing nodes. The current source tree has a
broader training-state helper and a shifted `playerState_t` sidecar layout, so
this pass does not guess those writes. They remain a focused tail-layout task.

The teammate, lead, torment, and fragbait tutorial nodes in the same
`ai_dmnet.c` tail remain mapped-only for the same reason: they use additional
retail tail fields that do not yet have stable source members.

## Tests

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_tutorial_tail_parity.py tests/test_botlib_qagame_ai_dmq3_deathmatch_setup_parity.py tests/test_botlib_qagame_instagib_target_goal_parity.py -q --tb=short
8 passed in 0.29s
```

No runtime launch was needed. `msbuild` and `cl` were not available on PATH in
this environment, so native compile validation could not be run here.

## Parity Estimate

- Focused instagib node alias/source coverage:
  **before 0% -> after 100%** for the two guarded rows.
- Focused instagib node source reconstruction confidence:
  **before 0% -> after 88%**. The stable state, movement, target, and wiring
  behavior is source-backed; the raw cleanup writes remain open.
- Focused qagame botlib movement/import wiring confidence:
  **before 98% -> after 99%**.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 98.9% -> after 99.0%**.
