# Freeze Tag Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Freeze Tag (`GT_FREEZE`) gametype from the server round
controller through the cgame scoreboard/event consumers. The owning retail
binary for gameplay behavior is `qagamex86.dll`; cgame evidence was used for
the `scores_ft`, thaw event, and UI feeder wiring.

## Evidence

- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part02.txt`
  - `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt`
- Companion Ghidra corpus:
  - `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
  - `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- Symbol support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `references/symbol-maps/qagame.json`
  - `references/symbol-maps/cgame.json`
- Existing source targets:
  - `src/code/game/g_active.c`
  - `src/code/game/g_client.c`
  - `src/code/game/g_freeze.c`
  - `src/code/game/g_cmds.c`
  - `src/code/cgame/cg_servercmds.c`
  - `src/code/cgame/cg_main.c`
  - `src/code/cgame/cg_event.c`

## Retail Wiring Map

| Surface | Retail evidence | Source reconstruction status |
| --- | --- | --- |
| Gametype ownership | Symbol aliases promote `G_FreezeResolveRoundState`, `G_FreezeSetClientFrozenState`, `G_FreezeResetClientForRound`, `G_FreezeTeamIsFullyFrozen`, `G_FreezeEvaluateRoundWinner`, `Freeze_RoundStateTransition`, `G_FreezeRunFrame`, `G_FreezeClientEndFrame`, and `G_FreezeCanSeeThawProgressEvent`. | The source keeps those boundaries split across `g_active.c`, `g_client.c`, and `g_freeze.c`, with `GT_FREEZE` included in the shared round-controller predicate. |
| Death interception | `G_FreezeHandlePlayerDeath` replaces ordinary death with freeze state during active Freeze rounds, then calls the shared last-alive path. | `g_combat.c` routes fatal damage to `G_FreezeHandlePlayerDeath`; `g_client.c` logs the kill, awards the attacker, drops flags/powerups, applies frozen state, and notifies last alive. |
| Frozen marker | Retail writes the synthetic client marker at `client + 0x17c` and mirrors it into entitystate powerups. | `G_FreezeSetClientFrozenPowerupMarker` uses `ps.powerups[PW_NUM_POWERUPS]` and `ent->s.powerups = ( 1 << PW_NUM_POWERUPS )`; cgame reads the same bit for frozen sprites and team overlay state. |
| Thaw helper scan | `G_FreezeClientEndFrame` uses `trap_EntitiesInBox`, helper retention by client number, line-of-sight gates, and a remaining-time counter. | `G_FreezeCountThawHelpers`, `G_FreezeFindThawHelperByClientNum`, and `G_FreezeClientEndFrame` preserve the entity-box search, retained helper, tick event, and timer restore behavior. |
| Thaw event layer | HLIL at `0x1004D0A5` sends `"ASSIST"`, then emits `EV_OBITUARY`/`MOD_THAW` with thawed client and helper client, followed by `EV_GLOBAL_TEAM_SOUND`. | `G_FreezeAwardThawAssist` and `G_FreezeEmitThawCompletionEvents` publish the helper medal/count, obituary payload, and return-sound event before the `GibEntity` thaw-respawn tail. |
| Round winner | `G_FreezeEvaluateRoundWinner` compares active-player counts, full-team frozen predicates, and roundtimelimit tie-break settings. | `G_FreezeRunFrame` recounts living players/health, asks `G_FreezeShouldCompleteRound`, resolves the winner, and calls `G_FreezeHandleRoundEnd`. |
| Round-end awards | `Freeze_RoundStateTransition` case 4 resets round counters at `+0xBCC`, `+0xBC8`, and `+0xBC4`, later reads those counters for the `ACCURACY` and `PERFECT` medal strings at `0x1004C92C` and `0x1004C96E`, then calls `FUN_10056070` after the medal pass. | This pass restored the evidenced `CalculateRanks()` call inside `G_FreezeHandleRoundEnd` after team-score updates and round-result prints. The exact medal pass is mapped, but not reconstructed until the round-scoped shot/hit/damage counters are rebuilt. |
| Scoreboard transport | qagame HLIL carries `scores_ft %i ... %i%s`; Ghidra shows 31 header ints plus 17 ints per player. | `G_BuildFreezeScoreboardMessage` emits `scores_ft`; cgame `CG_ParseFreezeScores` consumes the 28-field team-family header plus Freeze's 17-field row block. |
| Intermission stats | Symbol map marks `G_SendTDMStatsMessage` as shared by TDM and Freeze. | `DeathmatchScoreboardMessage` sends `tdmstats` during `GT_TEAM`/`GT_FREEZE` intermission; cgame caches `cg.tdmStats` for shared TDM/Freeze rich feeders. |
| UI/feeders | cgame symbol map routes `CG_FeederItemTextTDMFreezeTeamList` and `CG_FeederItemTextTDMFreezeStats` for both TDM and Freeze. | `CG_FeederItemText` dispatches `GT_FREEZE` to the shared TDM/Freeze feeder leaves and branches inside the team list for Freeze-specific columns. |
| Native export | `G_FreezeCanSeeThawProgressEvent` validates event `0x58` and same-team visibility for thaw progress. | Source export checks `ET_EVENTS + EV_THAW_TICK`, linked target client, active Freeze round, and teammate relation. |

## Source Reconstruction

The confirmed source gap in this pass was the Freeze round-complete rank
bookkeeping tail. Retail does not stop after team-score updates: after the
round-end medal pass it runs the rank recalculation helper, promoted in the
source tree as `CalculateRanks`.

The source now mirrors the evidence-backed rank tail through:

- `CalculateRanks();`

The `ACCURACY` / `PERFECT` medal block is mapped but deliberately left as a
follow-up. Retail does not appear to use the source's match-level
`accuracy_shots`, `accuracy_hits`, or `PERS_KILLED` fields for this pass. It
resets and reads round-scoped client counters at `+0xBC4`, `+0xBC8`, and
`+0xBCC`, with writes coming from weapon-fire, accuracy-hit, projectile-hit, and
damage paths. Reconstructing the medals correctly therefore requires adding
those counters and wiring their producers first.

The patch intentionally leaves the already-recovered thaw respawn and helper
credit flow unchanged. The odd-looking marker-preserving thaw path is still
supported by `G_FreezeClientEndFrame` HLIL and the `GibEntity` thaw-respawn
mapping from 2026-06-06.

## Confidence

Confidence is high for the round-end rank tail: the qagame HLIL exposes
`FUN_10056070` directly after the Freeze controller's round-complete medal pass.
Confidence is high that the `ACCURACY` and `PERFECT` strings belong to Freeze
round completion, but medium for source reconstruction until the surrounding
round counter fields are named and wired through their producer sites.
Confidence is high for the `scores_ft` and cgame feeder wiring because the
transport strings, row widths, symbol-map comments, and source parser/serializer
stride all agree.

Open follow-up: the source round controller remains a cleaner GPL-style
reconstruction rather than a one-for-one state-latch port of retail's internal
states `0..5`; future work could move more of `Freeze_RoundStateTransition`
case 1/3/4 timing into source-local helper boundaries if an exact state layout
is required.

## Parity Estimate

- Focused Freeze Tag gametype/wiring parity: **before 94% -> after 95%**.
- Broader gameplay/gametype parity: **before 99% -> after 99%**.
