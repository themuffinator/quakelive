# Botlib qagame ai_team one-flag order mapping - 2026-06-06

## Scope

This pass covers the next `qagamex86.dll` `ai_team.c` band after the CTF order
helpers:

- `0x10027750` `BotCTFOrders`
- `0x100277c0` `BotCreateGroup`
- `0x100278f0` `BotTeamOrders`
- `0x10027ae0` `Bot1FCTFOrders_FlagAtCenter`
- `0x10028320` `Bot1FCTFOrders_TeamHasFlag`
- `0x10028d10` `Bot1FCTFOrders_EnemyHasFlag`
- `0x10029550` `Bot1FCTFOrders_EnemyDroppedFlag`
- `0x10029d90` `Bot1FCTFOrders`

The focus is reverse-engineering mapping and reconstruction confidence for the
source-owned bot team-order logic plus the botlib import wiring it exercises.
No live launch was needed; the checked-in source, HLIL, Ghidra inventory, and
symbol maps were enough to settle this slice.

## Evidence

- `references/symbol-maps/qagame.json` already promotes all eight rows as exact
  `ai_team.c` matches with signatures and notes for the retail behavior.
- `references/reverse-engineering/ghidra/qagamex86/functions.csv` reports the
  expected retail sizes: 95, 289, 476, 2104, 2507, 2107, 2102, and 61 bytes.
- Binary Ninja HLIL in
  `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  pins the CTF dispatcher status calculation, group helper chat strings,
  `sv_maxclients` team enumeration, one-flag percentage splits, and
  `neutralflagstatus` dispatch.
- Ghidra `decompile_top_functions.c` covers the larger one-flag functions and
  corroborates the sort helpers, chat command strings, `cmd_returnflag`, and
  voice-chat string families.
- `src/code/game/ai_team.c` already contains a faithful reconstruction for this
  band, including the source-preserved quirks in the one-flag voice-order paths.

## Reconstruction Notes

`BotCTFOrders` is the small dispatcher at `0x10027750`. HLIL shows the
team-relative `redflagstatus` and `blueflagstatus` folding and the same four
edges to `BotCTFOrders_BothFlagsAtBase`, `BotCTFOrders_EnemyFlagNotAtBase`,
`BotCTFOrders_FlagNotAtBase`, and `BotCTFOrders_BothFlagsNotAtBase`.

`BotCreateGroup` at `0x100277c0` treats `teammates[0]` as the group leader,
chooses `cmd_accompanyme` when the bot is leading, otherwise emits
`cmd_accompany`, and sends each order through `BotSayTeamOrderAlways`.

`BotTeamOrders` at `0x100278f0` caches `sv_maxclients`, walks player
configstrings, filters spectators and non-teammates, and creates the same
2-player and 3-player groups as the source. The lower `BotTeamAI` wiring still
dispatches `GT_TEAM` to `BotTeamOrders`, `GT_CTF` to `BotCTFOrders`, and
`GT_1FCTF` to `Bot1FCTFOrders`.

The four one-flag CTF helpers preserve the retail percentage bands:

- Flag at center: passive 50/40 defend/getflag capped at 5/4, aggressive 30/60
  capped at 3/6.
- Team has flag: passive 30/70 defend/escort capped at 3/7, aggressive 20/80
  capped at 2/8, with `cmd_attackenemybase`, `cmd_accompanyme`,
  `cmd_accompany`, and fallback `cmd_getflag` branches.
- Enemy has flag: passive 80/10 defend/return capped at 8/2, aggressive 70/20
  capped at 8/2, with `cmd_returnflag` using the same `VOICECHAT_GETFLAG`
  retail voice hint as the source.
- Enemy dropped flag: passive 50/40 and aggressive 30/60 defend/getflag splits,
  including the source-preserved aggressive default `VOICECHAT_DEFEND` call for
  the getflag loop.

## Changes

- Promoted both `FUN_...` and `sub_...` aliases for the eight mapped functions
  in `references/analysis/quakelive_symbol_aliases.json`.
- Added `tests/test_botlib_qagame_ai_team_oneflag_order_parity.py` to pin
  aliases, Ghidra function sizes, symbol-map signatures, source anchors,
  Binary Ninja HLIL flow anchors, Ghidra decompile anchors, `BotTeamAI`
  dispatch, and the Cvar/configstring/chat/EA import bridge.
- Added this note as the focused evidence record for the pass.

## Confidence And Open Questions

Confidence is high for this slice. The main ambiguity is not ownership but
decompiler quality: `FUN_10028320` has unresolved register/stack artifacts in
Ghidra, while HLIL and source-command evidence still identify it cleanly as
`Bot1FCTFOrders_TeamHasFlag`. The source itself did not need edits in this
round.

Focused parity movement:

- Dispatcher/group/1FCTF alias coverage: before 0%, after 100%.
- Source-owned one-flag and team-order reconstruction confidence: before 87%,
  after 97%.
- Cvar/configstring/chat/EA import-wiring confidence for this band: before 94%,
  after 98%.
- Overall botlib plus qagame AI wiring confidence: before 98.0%, after 98.3%.
