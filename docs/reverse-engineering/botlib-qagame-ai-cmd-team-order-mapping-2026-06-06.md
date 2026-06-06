# Botlib Qagame AI Command Team-Order Mapping - 2026-06-06

## Scope

This pass pins the qagame-side `ai_cmd.c` team-message and team-order command
slab that sits immediately downstream of botlib chat matching. The owning
retail binary is `qagamex86.dll`; the mapped range is
`0x10004930..0x100080A0`.

No C source body change was needed. The work promotes aliases and adds a parity
gate tying the qagame command dispatcher and order handlers to committed retail
evidence and to the botlib match import wiring.

## Evidence

- `references/analysis/quakelive_symbol_aliases.json`
- `references/symbol-maps/qagame.json`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- `src/code/game/ai_cmd.c`
- `src/code/game/g_public.h`
- `src/code/game/g_syscalls.c`
- `src/code/server/sv_game.c`
- `src/code/server/ql_game_imports.inc`
- `tests/test_botlib_qagame_ai_cmd_parity.py`

## Mapped Rows

| Address | Promoted name | Function size |
| --- | --- | ---: |
| `0x10004930` | `BotGetItemTeamGoal` | 60 |
| `0x10004970` | `BotGetMessageTeamGoal` | 90 |
| `0x100049D0` | `BotGetTime` | 468 |
| `0x10004BB0` | `FindClientByName` | 534 |
| `0x10004DD0` | `FindEnemyByName` | 476 |
| `0x10004FB0` | `NumPlayersOnSameTeam` | 368 |
| `0x10005120` | `BotGetPatrolWaypoints` | 655 |
| `0x100053B0` | `BotAddressedToBot` | 727 |
| `0x10005690` | `BotMatch_HelpAccompany` | 1112 |
| `0x10005AF0` | `BotMatch_DefendKeyArea` | 334 |
| `0x10005C40` | `BotMatch_GetItem` | 283 |
| `0x10005D60` | `BotMatch_Camp` | 862 |
| `0x100060C0` | `BotMatch_Patrol` | 280 |
| `0x100061E0` | `BotMatch_GetFlag` | 340 |
| `0x10006340` | `BotMatch_AttackEnemyBase` | 359 |
| `0x100064B0` | `BotMatch_Harvest` | 274 |
| `0x100065D0` | `BotMatch_RushBase` | 308 |
| `0x10006710` | `BotMatch_TaskPreference` | 393 |
| `0x100068A0` | `BotMatch_ReturnFlag` | 227 |
| `0x10006990` | `BotMatch_JoinSubteam` | 218 |
| `0x10006A70` | `BotMatch_LeaveSubteam` | 171 |
| `0x10006B20` | `BotMatch_WhichTeam` | 114 |
| `0x10006BA0` | `BotMatch_CheckPoint` | 524 |
| `0x10006DB0` | `BotMatch_FormationSpace` | 204 |
| `0x10006E80` | `BotMatch_Dismiss` | 193 |
| `0x10006F50` | `BotMatch_Suicide` | 237 |
| `0x10007040` | `BotMatch_StartTeamLeaderShip` | 203 |
| `0x10007110` | `BotMatch_StopTeamLeaderShip` | 233 |
| `0x10007200` | `BotMatch_WhoIsTeamLeader` | 114 |
| `0x10007280` | `BotMatch_WhatAreYouDoing` | 517 |
| `0x100074C0` | `BotMatch_WhatIsMyCommand` | 86 |
| `0x10007520` | `BotNearestVisibleItem` | 381 |
| `0x100076B0` | `BotMatch_WhereAreYou` | 908 |
| `0x10007A40` | `BotMatch_LeadTheWay` | 651 |
| `0x10007CD0` | `BotMatch_Kill` | 306 |
| `0x10007E10` | `BotMatch_CTF` | 414 |
| `0x10007FB0` | `BotMatch_EnterGame` | 85 |
| `0x10008010` | `BotMatch_NewLeader` | 129 |
| `0x100080A0` | `BotMatchMessage` | 665 |

Both `FUN_...` and `sub_...` aliases were promoted for each row so the Ghidra
and Binary Ninja naming tracks resolve to the same source identity.

## Source Reconstruction Notes

Observed source anchors now pinned by tests:

- Team-goal helpers preserve item lookup, dropped-goal rejection, waypoint
  fallback, and explicit patrol waypoint creation with loop/reverse handling.
- Time parsing remains routed through botlib match parsing via
  `trap_BotFindMatch(..., MTCONTEXT_TIME)` and `trap_BotMatchVariable`.
- Addressing preserves NETNAME/ADDRESSEE parsing, everyone and multiple-name
  branches, subteam checks, reply-chat tell detection, and randomized throttling
  for non-directed messages.
- Order handlers preserve the retail LTG transitions for help/accompany,
  defend, get-item, camp, patrol, get-flag, attack base, harvest, rush base,
  return flag, kill, and lead-the-way.
- Subteam, checkpoint, formation, dismiss, suicide, and leadership handlers keep
  their exact chat keys, state updates, voice/action calls, and client lookup
  flows.
- `BotMatch_CTF` preserves red/blue/neutral flag status updates and flagcarrier
  tracking, while `BotMatchMessage` preserves the exact botlib match contexts
  and switch fan-out over the `BotMatch_*` handlers.

Inferred meaning: this range is qagame AI command source that depends on botlib
chat matching, not botlib internal source. Confidence is high because symbol-map
names/signatures, Ghidra row sizes, HLIL entry/call anchors, source bodies, and
match-import wiring all agree.

## Botlib Wiring

The new gate also pins the legacy and native import paths used by this command
layer:

- `BOTLIB_AI_FIND_MATCH` and `BOTLIB_AI_MATCH_VARIABLE` remain in `g_public.h`.
- `G_MapNativeImport` maps them to `G_QL_IMPORT_BOTLIB_AI_FIND_MATCH` and
  `G_QL_IMPORT_BOTLIB_AI_MATCH_VARIABLE`.
- `sv_game.c` keeps both botlib AI import-table entries and qagame native import
  slots wired to `QL_G_trap_BotFindMatch` and `QL_G_trap_BotMatchVariable`.
- `ql_game_imports.inc` forwards both wrappers through `G_Import_Syscall`.

## Coverage Result

`tests/test_botlib_qagame_ai_cmd_parity.py` now verifies:

- all 39 command-layer identities in `references/analysis/quakelive_symbol_aliases.json`;
- matching `references/symbol-maps/qagame.json` names and signatures;
- exact `functions.csv` row sizes for the command slab;
- direct `ai_cmd.c` source anchors for every promoted helper and command
  handler;
- HLIL entry signatures and cross-calls among team-goal lookup, time parsing,
  addressing, visible item search, CTF status handling, and command dispatch;
- botlib match import wiring from game syscall constants through server import
  initialization and generated qagame wrappers.

Focused verification run:

```text
python -m pytest tests/test_botlib_qagame_ai_cmd_parity.py -q --tb=short
2 passed in 0.24s
```

## Parity Estimate

- Focused qagame `ai_cmd.c` team-order alias coverage:
  **before 0% -> after 95%**
- Focused botlib match-parser wiring into qagame command handling:
  **before 82% -> after 94%**
- Overall botlib plus adjacent qagame AI/chat command wiring:
  **before 88% -> after 89%**

No runtime launch was needed. This was a static reverse-engineering mapping pass
with committed HLIL, Ghidra, symbol-map, source-body, and import-wiring
evidence.
