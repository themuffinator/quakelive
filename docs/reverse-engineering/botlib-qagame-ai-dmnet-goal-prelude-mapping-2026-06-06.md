# Botlib Qagame AI DMNet Goal Prelude Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmnet.c` long-term-goal and node-entry
prelude that sits downstream of botlib goal, movement, and item-selection
services. The owning retail binary is `qagamex86.dll`; the mapped range is
`0x100083C0..0x1000C640`.

No C source body change was needed. The work promotes aliases and adds a parity
gate tying the reconstructed goal-selection source to committed retail evidence
and to the botlib goal import wiring.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_dmnet.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_dmnet_goal_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x100083C0` | `BotDumpNodeSwitches` | 146 |
| `0x10008460` | `BotRecordNodeSwitch` | 169 |
| `0x10008510` | `BotGetAirGoal` | 887 |
| `0x10008890` | `BotGoForAir` | 340 |
| `0x100089F0` | `BotNearbyGoal` | 181 |
| `0x10008AB0` | `BotReachedGoal` | 427 |
| `0x10008C60` | `BotGetItemLongTermGoal` | 262 |
| `0x10008D90` | `BotGetLongTermGoal` | 8762 |
| `0x1000AFD0` | `BotLongTermGoal` | 1141 |
| `0x1000B450` | `AIEnter_Intermission` | 93 |
| `0x1000B4B0` | `AINode_Intermission` | 149 |
| `0x1000B550` | `AINode_Observer` | 96 |
| `0x1000B5B0` | `AIEnter_Stand` | 68 |
| `0x1000B600` | `AINode_Stand` | 371 |
| `0x1000B780` | `AIEnter_Respawn` | 268 |
| `0x1000B890` | `AINode_Respawn` | 252 |
| `0x1000B990` | `BotSelectActivateWeapon` | 274 |
| `0x1000BAB0` | `BotClearPath` | 1221 |
| `0x1000BF80` | `AINode_Seek_ActivateEntity` | 1715 |
| `0x1000C640` | `AIEnter_Seek_NBG` | 152 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity.
`BotRecordNodeSwitch` was already present in the alias table and is included in
the gate as an anchor across the surrounding node-enter helpers.

## Source Reconstruction Notes

Observed source anchors now pinned by tests:

- Node-switch diagnostics preserve the overflow print, per-switch dump loop,
  fatal print, active-player netname lookup, and `ainodename` update path.
- `BotGetAirGoal` preserves the retail water-surface probe with the upward
  1000-unit trace, playerclip/solid rejection, liquid-content checks, and
  `GFL_AIR` goal fill.
- `BotGoForAir` preserves the six-second `lastair_time` throttle, direct
  air-goal push path, nearby-goal scan loop, underwater-goal rejection, and
  avoid-goal reset fallback.
- `BotNearbyGoal`, `BotReachedGoal`, and `BotGetItemLongTermGoal` preserve the
  air-priority branch, CTF flag-carrier range clamp, item/air reached checks,
  avoid-time handling, LTG item selection, and avoid-reach reset.
- `BotGetLongTermGoal` preserves the team-help, accompany, defend, kill,
  get-item, patrol, capture-flag, enemy-base, and harvest transitions, including
  the `BotLongTermGoal: go for air` nearby-goal node transition.
- `BotLongTermGoal` preserves the lead/follow wrapper, `lead_stop` and
  `followme` chat paths, teammate entity-state refresh, lead visibility timers,
  and fallback into `BotGetLongTermGoal`.
- The intermission, observer, stand, and respawn enter/node helpers preserve
  node-switch labels, chat timing, enemy discovery, respawn reset calls, and
  `AINode_*` assignments.
- `BotSelectActivateWeapon`, `BotClearPath`, and
  `AINode_Seek_ActivateEntity` preserve the path-clearing weapon fallback,
  kamikaze/proximity-mine handling, activate-goal stack flow, movement
  prediction, activate-entity transitions, and battle handoff.
- `AIEnter_Seek_NBG` preserves top-goal naming, the "no goal" fallback, and
  transition to `AINode_Seek_NBG`.

Inferred meaning: this range is qagame AI decision-network source rather than
botlib internal source. Confidence is high because symbol-map names/signatures,
Ghidra row sizes, HLIL entry/call anchors, reconstructed `ai_dmnet.c` source
bodies, and botlib import wiring all agree.

## Botlib Wiring

The new gate pins the legacy and native import paths used by this goal layer:

- Goal-stack service constants remain present for `BOTLIB_AI_RESET_AVOID_GOALS`,
  `BOTLIB_AI_PUSH_GOAL`, `BOTLIB_AI_POP_GOAL`, and
  `BOTLIB_AI_GET_TOP_GOAL`.
- Goal-choice and reachability constants remain present for
  `BOTLIB_AI_CHOOSE_LTG_ITEM`, `BOTLIB_AI_CHOOSE_NBG_ITEM`,
  `BOTLIB_AI_AVOID_GOAL_TIME`, and `BOTLIB_AI_RESET_AVOID_REACH`.
- `G_MapNativeImport` maps those legacy syscall IDs to native
  `G_QL_IMPORT_BOTLIB_AI_*` slots, including the Quake Live IDs
  `139`, `140`, `141`, `146`, `148`, `149`, `155`, and `169`.
- `sv_game.c` keeps both botlib AI import-table entries and native import slots
  wired to the generated `QL_G_trap_Bot*` wrappers.
- `ql_game_imports.inc` forwards `trap_BotChooseNBGItem` through
  `G_Import_Syscall(..., QL_G_PASSFLOAT(maxtime))`, matching the qagame syscall
  wrapper's `PASSFLOAT(maxtime)` path.

## Coverage Result

`tests/test_botlib_qagame_ai_dmnet_goal_parity.py` now verifies:

- all 20 goal-prelude identities in `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmnet.c` source anchors for every promoted helper and node entry;
- HLIL entry signatures and cross-calls among air-goal selection, nearby-goal
  selection, reached-goal checks, long-term goal selection, node entry, weapon
  selection, path clearing, and activate-entity seeking;
- botlib goal/movement import wiring from game syscall constants through server
  import initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_goal_parity.py -q --tb=short
2 passed in 0.26s
```

## Parity Estimate

- Focused qagame `ai_dmnet.c` LTG/node prelude alias coverage:
  **before 5% -> after 96%**
- Focused botlib goal/movement import wiring into qagame node flow:
  **before 86% -> after 95%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 89% -> after 90%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
