# Team Deathmatch Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Team Deathmatch (`GT_TEAM`) path across the qagame
rules layer, qagame-to-cgame score transports, cgame scoreboard consumers,
team/ready-up gates, spawn selection, and factory aliasing. The concrete source
reconstruction is the `AddScore` intermission gate: retail blocks score mutation
after the match result is latched, and that guard is part of TDM because
`AddScore` is the only retail `GT_TEAM` team-score forwarding path.

## Evidence Used

- qagame symbol map:
  - `0x1003DD20 -> G_BuildTeamScoreboardMessage`
  - `0x1003E1B0 -> G_SendTDMStatsMessage`
  - `0x10061670 -> Cmd_AddScore_f`
  - `0x100681B0 -> AddTeamScore`
  - `AddScore` comment: gates warmup/intermission scoring, emits the score
    plum, applies the raw delta, forwards `GT_TEAM` score changes into team
    totals, and recalculates ranks.
- qagame Ghidra `decompile_top_functions.c`:
  - `FUN_1003DD20` carries the literal `scores_tdm` format with 28 red/blue
    header fields, score count, red score, blue score, and a 15-field per-client
    row block.
- cgame symbol map:
  - `0x10045F20 -> CG_ParseTdmScores`
  - `0x10046610 -> CG_ParseTDMStats`
  - `CG_ParseTdmScores` consumes the 28-field team header and TDM row block.
  - `CG_ParseTDMStats` clears one `cg.tdmStats[rowIndex]` slab, copies 11
    integer fields, and marks the row valid.
- Existing source cross-checks:
  - `src/code/game/g_cmds.c`
  - `src/code/game/g_combat.c`
  - `src/code/game/g_client.c`
  - `src/code/game/g_team.c`
  - `src/code/game/g_factory.c`
  - `src/code/cgame/cg_servercmds.c`
  - `src/code/cgame/cg_main.c`

## Observed Wiring

| Surface | Retail-backed mapping | Source state after this pass |
| --- | --- | --- |
| Gametype id | `GT_TEAM` is enum slot 3 and maps to `tdm` / `team` aliases. | `bg_public.h`, `g_factory.c`, and bot factory aliases agree on `tdm` -> `GT_TEAM`. |
| Spawn routing | `G_SelectClientSpawnPoint` sends CA/CTF/1F/Overload/Harvester/Freeze/Domination/A-D through team spawn classes; plain TDM is not in that band. | TDM keeps the normal deathmatch spawn picker, matching the recovered retail band. |
| Score mutation | Retail `AddScore` rejects warmup/intermission, then updates the client score, GT_TEAM team score, rank-last-scorer fields, and ranks. | `AddScore` now rejects both `level.warmupTime` and `level.intermissiontime` before score plums or score/team mutations. |
| Team score helper | `AddTeamScore` is for objective team gametypes above `GT_TEAM`; TDM team totals are forwarded from `AddScore`. | Source preserves that split and still keeps AddTeamScore's team lead/tie sound behavior for objective scoring. |
| Exit rules | TDM uses the fraglimit branch with team totals and the shared team mercy/timelimit/overtime flow. | `CheckExitRules` keeps `GT_TEAM` in the fraglimit owner set and team score tie/mercy path. |
| Ready-up/team presence | Retail team warmup paths require both teams before ready-up. | `G_GametypeRequiresBothTeamsPresent` includes `GT_TEAM`; `Team_HasMinimumPlayersForWarmup` handles red/blue counts. |
| Scoreboard command | Retail TDM uses `scores_tdm` instead of legacy `scores` or compact `smscores` when rich output fits. | `DeathmatchScoreboardMessage` selects `scores_tdm` and `G_BuildTeamScoreboardMessage` for `GT_TEAM`. |
| TDM scoreboard header | Retail prefixes 28 team aggregate fields before score count/red score/blue score. | qagame emits `retailTdmTeamStatOrder`; cgame parses it through `cgRetailTdmTeamStatOrder`. |
| TDM row block | Retail row shape is 15 fields: client, team, score, ping, time, kills, deaths, accuracy, best weapon, impressive, excellent, gauntlet, team damage given, team damage received, damage given. | `G_BuildTdmScoreboardRows` and `CG_ParseRetailTdmScoreRows` match this shape. |
| Postgame stats | Retail intermission sends `tdmstats` rows for TDM and Freeze. | `G_SendTDMStatsMessage` runs only under `level.intermissiontime` for `GT_TEAM`/`GT_FREEZE`; cgame caches rows in `cg.tdmStats`. |
| Feeders | Retail shares TDM/Freeze team-list and rich stats feeders. | `CG_FeederItemTextTDMFreezeTeamList` and `CG_FeederItemTextTDMFreezeStats` select `cg.tdmStats[row.scoreIndex]` for the relevant columns. |

## Source Reconstruction

- Added the missing `level.intermissiontime` guard in
  `src/code/game/g_combat.c::AddScore`.
- Added a structural regression in
  `tests/test_game_intermission_stats_parity.py` that pins the guard before:
  - `ScorePlum`
  - personal `PERS_SCORE` mutation
  - `GT_TEAM` team-score mutation

## Open Questions

- The committed qagame HLIL split does not currently include a dedicated
  `g_cmds.c` HLIL dump for `0x1003E1B0`, so the `tdmstats` row order is
  cross-checked through the symbol map, cgame parser evidence, current qagame
  source, and existing tests rather than a direct HLIL text slice.
- `G_BuildTeamScoreboardMessage` remains mostly verified through the Ghidra
  decompile and cgame parser symmetry. A future Binary Ninja export of this
  function would let us retire the remaining row-field confidence caveat.

## Parity Estimate

Focused Team Deathmatch qagame/cgame wiring moves approximately **96% -> 98%**.
The gain is small but real: the remaining retail-mapped TDM scoring side effect
now matches the intermission lockout, while the scoreboard, ready-up, spawn,
factory, and feeder paths were revalidated rather than materially changed.
Broader gameplay/gametype parity remains approximately **99%** because this pass
does not alter the larger CTF, CA, Freeze, Domination, A-D, Race, or Red Rover
surfaces.
