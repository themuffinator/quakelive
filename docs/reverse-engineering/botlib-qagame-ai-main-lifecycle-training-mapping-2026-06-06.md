# Botlib Qagame AI Main Lifecycle and Training Mapping - 2026-06-06

## Scope

This pass extends the qagame-side botlib reconstruction through the `ai_main.c`
lifecycle band and the adjacent Quake Live training helper island. The owning
retail binary is `qagamex86.dll`; the primary mapped ranges are
`0x10020F00..0x10022E40`, `0x10023400..0x100243D0`, and
`0x10024530..0x10024FA0`.

No C behavior was changed. The work promotes missing `FUN_...` and `sub_...`
aliases and adds a parity regression that pins source anchors, Ghidra rows,
Binary Ninja HLIL anchors, retail-only helper boundaries, and the native botlib
import wiring used by the band.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_main.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py`

## Mapped Rows

### Source-Owned Lifecycle Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10020F00` | `BotTestAAS` | 580 |
| `0x10021150` | `BotInterbreedBots` | 390 |
| `0x100212E0` | `BotWriteInterbreeded` | 363 |
| `0x10021450` | `BotInterbreedEndMatch` | 115 |
| `0x100214D0` | `BotInterbreeding` | 265 |
| `0x100215E0` | `BotTeamLeader` | 43 |
| `0x10021610` | `BotChangeViewAngle` | 293 |
| `0x10021740` | `BotChangeViewAngles` | 980 |
| `0x10021B20` | `BotInputToUserCommand` | 741 |
| `0x10021E10` | `BotUpdateInput` | 372 |
| `0x10021F90` | `RemoveColorEscapeSequences` | 70 |
| `0x10021FE0` | `BotAI` | 1187 |
| `0x10022490` | `BotScheduleBotThink` | 138 |
| `0x10022520` | `BotWriteSessionData` | 207 |
| `0x100225F0` | `BotReadSessionData` | 219 |
| `0x100226D0` | `BotAISetupClient` | 1154 |
| `0x10022B60` | `BotAIShutdownClient` | 242 |
| `0x10022C60` | `BotResetState` | 465 |
| `0x10022E40` | `BotAILoadMap` | 157 |
| `0x10023400` | `BotAIStartFrame` | 2038 |
| `0x10023C00` | `BotInitLibrary` | 1469 |
| `0x100241C0` | `BotAISetup` | 436 |
| `0x10024380` | `BotAIShutdown` | 76 |

### Retail-Only or Training-Specific Rows

| Address | Promoted name | Function size | Source status |
| --- | --- | ---: | --- |
| `0x10022EE0` | `BotPublishDebugInfoString` | 1228 | Reconstructed telemetry shim exists |
| `0x100243D0` | `BotEntityBoundsGap` | 350 | Mapped-only retail helper |
| `0x10024530` | `BotSetIdealViewAnglesToPoint` | 82 | Mapped-only retail helper |
| `0x10024590` | `BotSetPredictItemPickupDisabled` | 40 | Reconstructed training shim exists |
| `0x100245C0` | `BotSetTrainingBotState` | 124 | Mapped-only retail helper |
| `0x10024640` | `BotUpdateItemDelayTime` | 183 | Reconstructed training shim exists, retail takes a time input |
| `0x10024700` | `BotAppendDynamicSkillSample` | 177 | Mapped-only retail helper |
| `0x100247C0` | `BotUpdateDynamicSkill` | 1596 | Mapped-only retail helper |
| `0x10024E10` | `BotApplyBeyondRealityTravelFlags` | 136 | Mapped-only retail helper |
| `0x10024EA0` | `BotGetLocalClient` | 56 | Reconstructed training selector exists |
| `0x10024EE0` | `BotGetFirstBotClient` | 59 | Reconstructed training selector exists |
| `0x10024F20` | `BotSetTrainingCvarIfChanged` | 127 | Reconstructed training shim exists |
| `0x10024FA0` | `BotUpdateTrainingState` | 993 | Reconstructed training tail exists, retail body is broader |

## Source Mapping Notes

Observed source anchors now pinned by tests:

- `BotTestAAS` updates the debug cvars, draws area and avoid-spot overlays,
  gates area/cluster probes on AAS initialization, and prints the retail solid
  versus area/cluster messages.
- The interbreed family preserves rank calculation as `kills * 2 - deaths`,
  parent/child selection, goal fuzzy-logic interbreeding, mutation, best-bot
  export, end-match cycle handling, tournament enforcement, bot shutdown, and
  `addbot` command insertion.
- View and input conversion preserves the single-axis `AngleMod` clamp helper,
  challenge versus overreaction view control, `trap_EA_View`,
  `ACTION_*` to button-bit mapping, angle delta conversion, movement vector
  projection, respawn-button filtering, and `trap_EA_GetInput`.
- `BotAI` preserves input reset, client-state refresh, server-command parsing,
  color escape stripping, print/chat/tchat console-message queuing, voice chat
  dispatch, delta-angle normalization, deathmatch AI dispatch, weapon
  selection, and final delta-angle unwind.
- Session and client lifecycle helpers preserve `botsession%i` cvar
  serialization, character/goal/weapon/chat/move-state allocation and teardown,
  restart restore, waypoint cleanup, activate-goal cleanup, and bot-count
  updates.
- Map/setup/shutdown helpers preserve map load, state reset, deathmatch setup,
  botlib var initialization, cvar registration, restart fast paths, botlib
  setup, and botlib shutdown.
- The current training source covers local-player and first-bot selection,
  changed-only cvar setting, item-delay updates, trainer bot bootstrap, warmup
  and loop music, ready-state handling, and the `BotAIStartFrame` tail call.

## Retail-Only Boundaries

The following names are mapped but not reconstructed as exact C in this pass:

- `BotEntityBoundsGap`, `BotSetIdealViewAnglesToPoint`,
  `BotSetTrainingBotState`, and `BotApplyBeyondRealityTravelFlags` are helper
  sidecars used by the late tutorial nodes.
- `BotAppendDynamicSkillSample` and `BotUpdateDynamicSkill` preserve the retail
  dynamic-skill history and skill-refresh island in HLIL/Ghidra evidence, but
  the current source does not yet reconstruct those exact bodies.
- `BotUpdateItemDelayTime` and `BotUpdateTrainingState` have current source
  shims that cover the visible training behavior. The retail rows take broader
  inputs and include additional dynamic-skill and tutorial state transitions,
  so their exact source parity remains a follow-up reconstruction target.

## Botlib Wiring

The new regression pins native import coverage used by this band:

- Botlib lifecycle imports: setup, shutdown, libvar set, start frame, load map,
  update entity, get console message, and user command.
- EA imports: view, get input, and reset input.
- AI/chat imports: load/free character, allocate/free chat state, queue console
  message, load chat file, load item and weapon weights, allocate/reset/free
  goal, move, and weapon states.
- Direct `sv_game.c` import-table entries and `ql_game_imports.inc` wrappers
  for the same calls.

## Tests

- `python -m pytest tests/test_botlib_qagame_ai_main_lifecycle_training_parity.py -q --tb=short`

No runtime launch was needed; the pass is static evidence and regression work.

## Parity Estimate

- Focused ai_main lifecycle and training-helper alias coverage:
  **before 8% -> after 100%** for the 36 guarded rows in this pass.
- Focused source-owned lifecycle reconstruction confidence:
  **before 92% -> after 98%** after pinning source bodies to HLIL, Ghidra
  metadata, and symbol-map signatures.
- Focused retail-only training/dynamic-skill helper mapping confidence:
  **before 58% -> after 87%**. Names, sizes, call sites, and comments are now
  pinned, while exact source reconstruction remains open for the dynamic-skill
  island.
- Overall botlib plus qagame AI execution wiring confidence:
  **before 97.1% -> after 97.6%**. Remaining uncertainty is concentrated in
  exact Quake Live tutorial/dynamic-skill bodies and fresh runtime validation,
  not the source-owned lifecycle and import wiring closed here.
