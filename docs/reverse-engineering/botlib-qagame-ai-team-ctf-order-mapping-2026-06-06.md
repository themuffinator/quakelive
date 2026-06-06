# Botlib qagame ai_team CTF order mapping - 2026-06-06

## Scope

This pass maps the `qagamex86.dll` `ai_team.c` prologue and first CTF order
quartet at `0x10025390..0x10026f20`.  The slice is botlib-adjacent rather than
botlib-internal: it consumes AAS route timing, writes bot task preferences, and
emits botlib chat / EA commands through the game import table.

## Evidence

Canonical evidence:

- Binary Ninja HLIL:
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
- Ghidra inventory and decompile hints:
  `references/reverse-engineering/ghidra/qagamex86/functions.csv`
  and `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- Promoted symbol map:
  `references/symbol-maps/qagame.json`
- Reconstructed source:
  `src/code/game/ai_team.c`
- Import wiring:
  `src/code/game/g_public.h`, `src/code/game/g_syscalls.c`,
  `src/code/server/sv_game.c`, and `src/code/server/ql_game_imports.inc`

## Mapped rows

| Address | Retail row | Reconstructed name | Confidence |
| --- | --- | --- | --- |
| `0x10025390` | `FUN_10025390` | `BotNumTeamMates` | High |
| `0x100254a0` | `FUN_100254a0` | `BotClientTravelTimeToGoal` | High |
| `0x100255c0` | `FUN_100255c0` | `BotSortTeamMatesByBaseTravelTime` | High |
| `0x100257c0` | `FUN_100257c0` | `BotSetTeamMateTaskPreference` | High |
| `0x10025820` | `FUN_10025820` | `BotGetTeamMateTaskPreference` | High |
| `0x10025890` | `FUN_10025890` | `BotSortTeamMatesByTaskPreference` | High |
| `0x10025a40` | `FUN_10025a40` | `BotSayTeamOrderAlways` | High |
| `0x10025b20` | `FUN_10025b20` | `BotVoiceChat` | High |
| `0x10025b70` | `FUN_10025b70` | `BotVoiceChatOnly` | High |
| `0x10025bc0` | `FUN_10025bc0` | `BotCTFOrders_BothFlagsNotAtBase` | High |
| `0x10026190` | `FUN_10026190` | `BotCTFOrders_FlagNotAtBase` | High |
| `0x100269d0` | `FUN_100269d0` | `BotCTFOrders_EnemyFlagNotAtBase` | Medium-high |
| `0x10026f20` | `FUN_10026f20` | `BotCTFOrders_BothFlagsAtBase` | High |

`FUN_100269d0` has unresolved stack usage in HLIL, but the row is still
well-supported by the adjacent source order, function size, sort/preference
calls, defend/accompany/getflag command strings, flag-carrier field accesses,
and the `BotCTFOrders` dispatcher edge at `0x10027798`.

## Observed facts

- `BotNumTeamMates` and `BotSortTeamMatesByBaseTravelTime` both cache
  `sv_maxclients` through the game import callback at `data_104b13ac + 0x2c`,
  then walk `CS_PLAYERS + i` through `data_104b13ac + 0x68`.
- `BotClientTravelTimeToGoal` copies the target client state, resolves an AAS
  area, returns `1` when no area is available, and otherwise calls the AAS
  travel-time import at `data_104b13ac + 0x134` with `TFL_DEFAULT`.
- `BotSortTeamMatesByBaseTravelTime` selects CTF / 1FCTF flag goals or obelisk
  goals using gametype plus `BotTeam`, filters same-team non-spectators, and
  insertion-sorts teammates by travel time.
- `BotSetTeamMateTaskPreference` stores a per-client bitfield and snapshots the
  teammate name. `BotGetTeamMateTaskPreference` rejects stale preferences when
  the current client name no longer matches the snapshot.
- `BotSortTeamMatesByTaskPreference` partitions teammates into defender,
  roamer, and attacker buckets via `TEAMTP_DEFENDER` and `TEAMTP_ATTACKER`,
  then rewrites the input array in that order.
- `BotVoiceChat` emits `vsay_team` or `vtell`; `BotVoiceChatOnly` emits
  `vosay_team` or `votell`.  Both paths use the botlib EA command import.
- The four CTF order functions share the travel-time sort and task-preference
  sort prelude, then branch on team size, passive/aggressive strategy, and
  flag-carrier state to generate `cmd_defendbase`, `cmd_getflag`,
  `cmd_accompany`, or `cmd_accompanyme` chat plus matching voice commands.
- The `BotCTFOrders` dispatcher immediately following this slice maps flag
  status `0..3` to both-flags-at-base, enemy-flag-away, own-flag-away, and
  both-flags-away respectively, matching the reconstructed source ordering.

## Reconstruction meaning

The committed source is already close to the retail body shape for this band.
This pass does not need new C code; the useful reconstruction work is making
the evidence discoverable and regression-tested:

- Added raw `FUN_...` and `sub_...` aliases for all thirteen rows in
  `references/analysis/quakelive_symbol_aliases.json`.
- Added
  `tests/test_botlib_qagame_ai_team_ctf_order_parity.py`, which pins aliases,
  function sizes, symbol-map signatures, source anchors, HLIL entry/flow
  anchors, Ghidra decompile anchors, and the botlib/AAS/chat/EA import bridge.
- Preserved the important oddities instead of smoothing them over, including
  the source `sizeof(teammates)` argument to `BotSortTeamMatesByBaseTravelTime`
  and the `CTFS_AGRESSIVE` spelling.

## Import surface

This source slice depends on the following game-side imports:

- `G_QL_IMPORT_CVAR_VARIABLE_INTEGER_VALUE = 11`
- `G_QL_IMPORT_GET_CONFIGSTRING = 26`
- `G_QL_IMPORT_BOTLIB_AAS_AREA_TRAVEL_TIME_TO_GOAL_AREA = 77`
- `G_QL_IMPORT_BOTLIB_EA_COMMAND = 87`
- `G_QL_IMPORT_BOTLIB_AI_QUEUE_CONSOLE_MESSAGE = 119`
- `G_QL_IMPORT_BOTLIB_AI_INITIAL_CHAT = 123`
- `G_QL_IMPORT_BOTLIB_AI_ENTER_CHAT = 127`
- `G_QL_IMPORT_BOTLIB_AI_GET_CHAT_MESSAGE = 128`

The new regression checks each import at the enum, syscall remap, server native
import table, Quake Live direct import table, and source-call layers.

## Remaining questions

- Later `ai_team.c` order families, including 1FCTF, Obelisk, Harvester, and
  team-leader dispatch tails, still deserve the same raw-alias and source-body
  guard treatment.
- `FUN_100269d0` should remain marked medium-high until a future pass resolves
  the HLIL stack model cleanly, even though the mapping is strongly supported
  by independent evidence.

## Parity estimate

- Focused alias coverage for this `ai_team.c` CTF order band:
  **before 0% -> after 100%**.
- Focused source-owned team-order reconstruction confidence:
  **before 88% -> after 97%**.
- Focused AAS/chat/EA import-wiring confidence for this band:
  **before 94% -> after 98%**.
- Overall botlib plus qagame AI wiring confidence:
  **97.6% -> 98.0%**.
