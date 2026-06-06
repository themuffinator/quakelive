# Botlib Qagame AI DMNet Battle Node Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_dmnet.c` seek and battle node slab that
drives nearby-goal seeking, long-term-goal seeking, fight, chase, retreat, and
battle-nearby-goal behavior. The owning retail binary is `qagamex86.dll`; the
mapped range is `0x1000C6E0..0x1000E700`.

No C source body change was needed. The work fills the missing `AIEnter_*`
aliases in this range and adds a parity gate that keeps the already-promoted
node aliases tied to source, HLIL, Ghidra, symbol-map, and botlib movement
wiring evidence.

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
- `tests/test_botlib_qagame_ai_dmnet_battle_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x1000C6E0` | `AINode_Seek_NBG` | 1089 |
| `0x1000CB30` | `AIEnter_Seek_LTG` | 166 |
| `0x1000CBE0` | `AINode_Seek_LTG` | 1641 |
| `0x1000D250` | `AIEnter_Battle_Fight` | 71 |
| `0x1000D2A0` | `AIEnter_Battle_SuicidalFight` | 65 |
| `0x1000D2F0` | `AINode_Battle_Fight` | 1480 |
| `0x1000D8C0` | `AIEnter_Battle_Chase` | 66 |
| `0x1000D910` | `AINode_Battle_Chase` | 1630 |
| `0x1000DF70` | `AIEnter_Battle_Retreat` | 50 |
| `0x1000DFB0` | `AINode_Battle_Retreat` | 1823 |
| `0x1000E6D0` | `AIEnter_Battle_NBG` | 43 |
| `0x1000E700` | `AINode_Battle_NBG` | 1463 |

Both `FUN_...` and `sub_...` aliases are now promoted for every row so the
Ghidra and Binary Ninja naming tracks resolve to the same source identity. The
six `AINode_*` aliases were already present; this pass completes the enter-node
aliases and gates the whole range.

## Source Reconstruction Notes

Observed source anchors now pinned by tests:

- `AINode_Seek_NBG` preserves observer/intermission/dead exits, timeout back to
  `AIEnter_Seek_LTG`, obstacle prediction, botlib movement, path clearing,
  second-goal view targeting, and fight-vs-battle-NBG transitions.
- `AIEnter_Seek_LTG` preserves top-goal naming, "no goal" fallback logging, and
  the `AINode_Seek_LTG` handoff.
- `AINode_Seek_LTG` preserves random-chat standing, LTG refresh through
  `BotLongTermGoal`, nearby-goal checks, defend/CTF/harvester range clamps,
  movement failure handling, path clearing, and movement-view-target aiming.
- `AIEnter_Battle_Fight` and `AIEnter_Battle_SuicidalFight` preserve the common
  battle-fight node handoff, reset-last-avoid-reach call, and suicidal fight
  flagging.
- `AINode_Battle_Fight` preserves no-enemy and enemy-dead transitions,
  enemy-suicide and kill chat, invisible-enemy loss, battle inventory updates,
  hit chat, chase/seek split for out-of-sight enemies, attack movement,
  aiming, attack checks, and retreat escalation.
- `AIEnter_Battle_Chase` and `AINode_Battle_Chase` preserve chase-time setup,
  last-seen enemy goal construction, timeout handling, battle-NBG diversion,
  movement/view updates, and retreat escalation.
- `AIEnter_Battle_Retreat` and `AINode_Battle_Retreat` preserve retreat entry,
  enemy visibility tracking, chase recovery, retreat LTG refresh, suicidal fight
  fallback when no route is available, battle-NBG diversion, movement, aiming,
  and attack checks while retreating.
- `AIEnter_Battle_NBG` and `AINode_Battle_NBG` preserve battle-nearby-goal
  entry, no-enemy/enemy-dead fallback into seek-NBG, top-goal expiry handling,
  fight-vs-retreat timeout split, movement, battle inventory refresh, movement
  view targeting, and attack checks.

Inferred meaning: this range is qagame AI decision-network source that consumes
botlib goal-stack and movement services. Confidence is high because source
function bodies, retail symbol-map names/signatures, Ghidra row sizes, HLIL
entry/call anchors, and import wiring all agree.

## Botlib Wiring

The new gate pins the legacy and native import paths used by this seek/battle
layer:

- Goal-stack service constants remain present for
  `BOTLIB_AI_EMPTY_GOAL_STACK` and `BOTLIB_AI_GET_SECOND_GOAL`.
- Movement service constants remain present for `BOTLIB_AI_MOVE_TO_GOAL`,
  `BOTLIB_AI_RESET_AVOID_REACH`, `BOTLIB_AI_RESET_LAST_AVOID_REACH`, and
  `BOTLIB_AI_MOVEMENT_VIEW_TARGET`.
- `G_MapNativeImport` maps those legacy syscall IDs to native
  `G_QL_IMPORT_BOTLIB_AI_*` slots, including the Quake Live IDs `142`, `147`,
  `167`, `169`, `170`, and `172`.
- `sv_game.c` keeps both botlib AI import-table entries and native import slots
  wired to the generated `QL_G_trap_Bot*` wrappers.
- `ql_game_imports.inc` forwards movement lookahead through
  `QL_G_PASSFLOAT(lookahead)`, matching the qagame syscall wrapper's
  `PASSFLOAT(lookahead)` path.

## Coverage Result

`tests/test_botlib_qagame_ai_dmnet_battle_parity.py` now verifies:

- all 12 seek/battle node identities in `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the mapped range;
- direct `ai_dmnet.c` source anchors for every promoted helper and node;
- HLIL entry signatures and cross-calls among seek-NBG, seek-LTG, fight, chase,
  retreat, suicidal fight, and battle-NBG transitions;
- botlib goal-stack and movement import wiring from game syscall constants
  through server import initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_dmnet_battle_parity.py -q --tb=short
2 passed in 0.19s
```

## Parity Estimate

- Focused qagame `ai_dmnet.c` seek/battle node alias coverage:
  **before 50% -> after 96%**
- Focused botlib goal-stack/movement import wiring into qagame battle flow:
  **before 88% -> after 96%**
- Overall botlib plus adjacent qagame AI execution wiring:
  **before 90% -> after 91%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
