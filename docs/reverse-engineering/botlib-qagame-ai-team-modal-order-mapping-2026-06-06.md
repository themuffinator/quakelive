# Botlib qagame ai_team modal order mapping - 2026-06-06

## Scope

This pass closes the remaining team-order coordinator band in
`qagamex86.dll` `ai_team.c`:

- `0x10029df0` `BotObeliskOrders`
- `0x1002a630` `BotHarvesterOrders`
- `0x1002ae70` `FindHumanTeamLeader`
- `0x1002aef0` `BotTeamAI`

It follows the earlier CTF and 1FCTF slices by mapping the Overload and
Harvester order helpers plus the top-level team AI dispatcher that elects a
leader and schedules gametype-specific orders.

## Evidence

- `references/symbol-maps/qagame.json` marks all four rows as matched and
  provides the source signatures.
- `references/reverse-engineering/ghidra/qagamex86/functions.csv` reports
  retail function sizes of 2102, 2102, 125, and 2710 bytes for the four rows.
- Binary Ninja HLIL pins the shared teammate sort/preference calls, the
  passive/aggressive percentage bands, `cmd_attackenemybase`, `cmd_harvest`,
  human leader scan, `whoisteamleader`, `iamteamleader`, `startleader`, and
  dispatcher edges to the CTF, 1FCTF, Obelisk, and Harvester order helpers.
- Ghidra `decompile_top_functions.c` corroborates the large Obelisk,
  Harvester, and `BotTeamAI` bodies with command strings and downstream calls.
- The checked-in `src/code/game/ai_team.c` already matches this retail slice.

## Reconstruction Notes

`BotObeliskOrders` and `BotHarvesterOrders` are structurally paired with the
1FCTF helpers. Both sort teammates by base travel time and task preference,
then choose passive or aggressive splits based on `CTFS_AGRESSIVE`.
`BotObeliskOrders` routes attackers through `cmd_attackenemybase`; Harvester
uses `cmd_harvest`. Both retain the 50/40 passive split capped at 5/4 and the
30/70 aggressive split capped at 3/7.

`FindHumanTeamLeader` walks `g_entities`, rejects bots and `notleader` clients,
checks `BotSameTeam`, copies the selected client name into `bs->teamleader`,
and sends the default defend voice order if the player had no remembered task.

`BotTeamAI` is the coordinator. It returns below team gametypes, validates or
elects a leader, asks `whoisteamleader` before self-promoting with
`iamteamleader`, emits the `startleader` voice command, and then dispatches
orders only when the bot's own netname matches `bs->teamleader`.

The dispatcher keeps distinct order cadences:

- Team orders: fire after a 5-second readiness delay, then schedule again 120
  seconds later.
- CTF orders: fire after a 3-second readiness delay and reset the order timer.
- 1FCTF orders: fire after a 2-second readiness delay and reset the order
  timer.
- Obelisk and Harvester orders: fire after a 5-second readiness delay, then
  schedule again 30 seconds later.

CTF and 1FCTF also preserve the 240-second stale-capture strategy shuffle with
a 40% chance of toggling `CTFS_AGRESSIVE`.

## Changes

- Promoted both `FUN_...` and `sub_...` aliases for the four mapped rows in
  `references/analysis/quakelive_symbol_aliases.json`.
- Added `tests/test_botlib_qagame_ai_team_modal_order_parity.py` to pin
  aliases, function sizes, symbol-map metadata, source anchors, HLIL flow,
  Ghidra decompile anchors, and the import bridge used by the order path.
- Added this note as the focused evidence record for the pass.

## Confidence And Open Questions

Confidence is high for this band. The main decompiler limitation is that the
Ghidra `BotTeamAI` output uses raw global names for gametype and timing
constants, but HLIL, command strings, function calls, and source anchors align
cleanly. No C source edits were needed.

Focused parity movement:

- Obelisk/Harvester/leader/BotTeamAI alias coverage: before 0%, after 100%.
- Source-owned modal team-order reconstruction confidence: before 88%, after
  98%.
- Bot leader/chat/EA/import-wiring confidence for this band: before 94%, after
  98%.
- Overall botlib plus qagame AI wiring confidence: before 98.3%, after 98.6%.
