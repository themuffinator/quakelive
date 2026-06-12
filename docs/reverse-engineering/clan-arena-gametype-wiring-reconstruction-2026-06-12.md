# Clan Arena Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Clan Arena (`GT_CLAN_ARENA`) path across the qagame
round controller, qagame-to-cgame match-state configstrings, the dedicated
Clan Arena scoreboard/stat transports, the cgame score/stat parsers, and the
HUD feeder consumers. The concrete source reconstruction is the retail compact
Clan Arena round-state payload plus the missing retail round-result prints and
invalid-state fatal diagnostic in the CA controller.

## Evidence Used

- qagame Binary Ninja HLIL:
  - `0x10037FD0` is the Clan Arena damage-score gate reached from damage
    handling. It calls the CA round-state resolver before awarding capped
    damage score.
  - `0x10038230` is the `CA_RoundStateTransition` body. It writes configstring
    `0x295` as `\time\-1\round\0`, `\time\%d\round\%d`, or `\round\%d`
    depending on the round phase.
  - The same controller writes configstring `0x296` with the active round start
    time and later writes `-1` when a completed round schedules the next warmup.
  - The string table preserves the three CA round-result print formats and the
    `CA_RoundStateTransition: invalid state` fatal diagnostic.
- qagame Ghidra `decompile_top_functions.c`:
  - The decompile mirrors the compact `0x295` and `0x296` writes.
  - The active-to-complete block tallies living counts and health, chooses red,
    blue, or draw, increments team score, broadcasts the round win sound, and
    emits one of the survivor/health result prints.
- qagame symbol map:
  - `CA_RoundStateTransition` is promoted as the CA controller.
  - `G_BuildClanArenaScoreboardMessage` owns the `scores_ca` transport.
  - The CA postgame stats publisher owns the `castats` transport.
- cgame symbol map:
  - `CG_ParseClanArenaScores` consumes `scores_ca`.
  - `CG_ParseClanArenaStats` consumes `castats`.
  - `CG_FeederItemTextClanArenaTeamList` and
    `CG_FeederItemTextClanArenaStats` render the CA scoreboard/stat rows.
  - `CG_ParseMatchState` is centered on configstring `0x295` and is called by
    both the configstring update dispatcher and bootstrap path.

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Gametype id | `GT_CLAN_ARENA` owns the CA round controller and the dedicated `scores_ca`/`castats` transports. | Existing factory, scoreboard, and stat parser paths already route CA through the dedicated helpers. |
| Round inactive payload | Retail qagame writes `CS_MATCH_STATE` slot `0x295` as `\time\-1\round\0`. | `G_BuildClanArenaMatchStateInfo` now emits the same compact inactive payload. |
| Round warmup payload | Retail qagame writes `\time\%d\round\%d`, using the warmup transition time and the next round ordinal. | The source publisher now emits only `time` and `round` for CA warmup, with the round ordinal derived from red plus blue team scores plus one. |
| Round active payload | Retail qagame writes `CS_ROUND_START_TIME` slot `0x296` to the current time and `CS_MATCH_STATE` as `\round\%d`. | Active CA rounds now publish the hidden round-start side channel and keep the match-state payload compact. |
| Round complete payload | Retail qagame keeps `CS_MATCH_STATE` at `\round\%d` and clears slot `0x296` to `-1` before returning to warmup. | Complete CA rounds now keep the compact round payload and clear the round-start side channel to `-1`. |
| Client round-state cache | Retail cgame consumes configstring `0x295`, but the compact CA payload has no explicit `state` key. | `CG_ParseMatchState` now infers CA/Freeze/RR compact round state from `time`, `round`, warmup state, and the hidden round-start slot when `state` is absent. |
| Round winner prints | Retail prints survivor health, survivor count, or red-vs-blue health detail depending on elimination/timelimit conditions. | `G_CASendRoundWinnerPrint` reconstructs those three formats and replaces the old source-only centerprint. |
| Invalid controller state | Retail calls the fatal error path with `CA_RoundStateTransition: invalid state`. | The source CA controller now calls `G_Error` for unexpected round-state values. |
| Scoreboard transport | Retail qagame emits `scores_ca`; retail cgame parses it with a CA-specific row shape. | Existing `G_BuildClanArenaScoreboardMessage` and `CG_ParseClanArenaScores` mappings were revalidated. |
| Postgame stat transport | Retail qagame emits `castats`; retail cgame caches damage and per-weapon frag/accuracy pairs by scoreboard row. | Existing `G_SendClanArenaStatsMessage` and `CG_ParseClanArenaStats` mappings were revalidated. |
| HUD feeders | Retail cgame has CA-specific team-list and stats feeders. | Existing CA feeder helpers remain the cgame presentation edge for parsed `scores_ca` and `castats` rows. |

## Source Reconstruction

- Added `G_BuildClanArenaMatchStateInfo` and the CA warmup round helper in
  `src/code/game/g_match_state.c`.
- Changed `G_UpdateMatchStateConfigString` so CA uses the retail compact
  configstring `0x295` payload while the richer SRP match-state payload remains
  available for the other reconstructed round modes.
- Changed `G_UpdateRoundStartConfigString` so CA complete rounds clear
  `CS_ROUND_START_TIME` to `-1`, matching the retail side-channel clear.
- Added compact-payload inference in `src/code/cgame/cg_servercmds.c` so cgame
  keeps a usable round-state cache when the retail payload omits the `state`
  key.
- Added `G_CASendRoundWinnerPrint` in `src/code/game/g_active.c` and wired the
  CA active-to-complete transition to the retail survivor/health print formats.
- Replaced the silent CA controller default case with the retail fatal
  diagnostic.
- Strengthened focused static and harness tests for CA match-state payloads,
  CA round-result prints, cgame compact-state inference, and the hidden
  round-start side channel.

## Open Questions

- The award/stat tail after CA round resolution is still mostly inherited from
  earlier reconstruction. This pass revalidated the adjacent strings and call
  flow, but did not exhaustively rename every award helper below the round
  winner branch.
- Freeze and Red Rover show related compact configstring payloads in the
  qagame corpus. The cgame inference helper deliberately includes those modes,
  but this pass only changed qagame publishing behavior for Clan Arena.
- The CA scoreboard and `castats` transports remain high-confidence through
  symbol maps, Ghidra strings, cgame parser symmetry, and existing tests. A
  future direct HLIL slice focused only on the serializers would let us retire
  the last row-field caveat.

## Parity Estimate

Focused Clan Arena qagame/cgame round, configstring, scoreboard, stat, and HUD
feeder wiring moves approximately **87% -> 96%**. The remaining gap is mostly
tail confidence around CA award/stat side effects rather than the core round
state or transport wiring. Broader gametype parity remains approximately
**99%** because this pass is scoped to Clan Arena and its immediate client/server
edges.
