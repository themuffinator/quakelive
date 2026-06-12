# Duel Gametype Wiring Reconstruction - 2026-06-12

## Scope

This pass rechecked the Quake Live Duel gametype, represented in the GPL-derived
source as `GT_TOURNAMENT`, from the qagame lifecycle and queue controller through
the cgame `scores_duel` parser, spectator list, and competitive HUD consumers.
The owning retail binary for gameplay behavior is `qagamex86.dll`; cgame evidence
was used for scoreboard parsing, duel menus, spectator queue metadata, and
scorebox ownerdraw wiring.

## Evidence

- Canonical HLIL:
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil_split/qagamex86.dll.bndb_hlil_part01.txt`
  - `references/hlil/quakelive/qagamex86.dll/qagamex86.dll.bndb_hlil.txt`
  - `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part02.txt`
  - `references/hlil/quakelive/qagamex86.dll/sully_interpreted/structs/level_locals_t.md`
- Companion Ghidra corpus:
  - `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
  - `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- Symbol support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `references/symbol-maps/qagame.json`
  - `references/symbol-maps/cgame.json`
- Existing source targets:
  - `src/code/game/g_cmds.c`
  - `src/code/game/g_main.c`
  - `src/code/game/g_lifecycle.c`
  - `src/code/game/g_team.c`
  - `src/code/game/g_session.c`
  - `src/code/cgame/cg_servercmds.c`
  - `src/code/cgame/cg_main.c`
  - `src/code/cgame/cg_players.c`
  - `src/code/cgame/cg_newdraw.c`

## Retail Wiring Map

| Surface | Retail evidence | Source reconstruction status |
| --- | --- | --- |
| Gametype identity | qagame label helper returns `DUEL` for gametype id 1; UI/cgame token helpers map the same id to `duel` and `DUEL`. | Source preserves the inherited `GT_TOURNAMENT` enum while outward strings, vote tokens, menu names, and HUD labels expose Duel. |
| Lifecycle and spawn loadout | `CheckTournament` owns the Duel warmup state, warmup modification latch, map restart request, and ready-delay helper call. `G_FinalizeSpawnLoadout` applies the Duel grant/select-spawn-weapon tail after `ClientSpawn`. | `g_lifecycle.c` handles Duel init/begin/spawn stages; `g_main.c::CheckTournament` owns live countdown state; tests pin the Duel spawn grant and countdown math. |
| Queue eligibility | Symbol-map aliases promote `G_FindNextTournamentPlayer`, `AddTournamentPlayer`, `RemoveTournamentLoser`, `G_UpdateTournamentQueuePositions`, and `G_SyncTournamentQueueTeamTasks`. HLIL filters scoreboard/follow-only/spectate-only spectators before sorting by spectator time. | `g_main.c` keeps the queue predicate, oldest-spectator promotion, loser demotion, one-based `spectatorQueuePosition`, dirty republish, and `teamtask` userinfo mirror. |
| Spectator metadata transport | qagame session fields at `clientSession_t +0x36C/+0x370` publish the `so` and `pq` Duel sidecars; cgame symbol notes show the spectator cache sorting by those fields. | `g_session.c` persists `spectateOnly` / `spectatorQueuePosition`; `ClientUserinfoChanged` publishes them; cgame `CG_NewClientInfo` parses them and `CG_BuildSpectatorString` renders `(n)` and `(^5s^7)` prefixes. |
| Ready-up delay | HLIL `G_CheckReadyUpDelayAction` requires Duel, warmup enabled, two active duelists, exactly one ready duelist, then arms `CS_READYUP_STATUS` from `level.readyUpDelayDeadline`. On expiry action 1 moves unready players to spectator; action 2 forces ready. | Source keeps `readyUpDelayDeadline`, `G_GetDuelReadyStateCounts`, `G_CheckReadyUpDelayAction`, ready latch clearing, and configstring refreshes. |
| Scoreboard serializer | qagame `G_BuildDuelScoreboardMessage` caches low/high live duel client slots at `level +0x1C08/+0x1C0C`, builds public/private row variants, and emits `scores_duel %i %s`, `scores_duel %i %s %s`, or `scores_duel 2 %s %s`. | Source builds the same row family, preserves the low/high level-tail cache, applies per-viewer public/private item timing visibility, and dispatches through `DeathmatchScoreboardMessage`. |
| Queued intermission detail reveal | HLIL line `0x1003DB06` branches on `data_105de9d4 != 0 || data_105de9d8 != 0`; Sully notes map those to `intermissionQueued` and `intermissiontime`. The branch emits the all-detail two-row literal `scores_duel 2 %s %s`. | This pass extended `G_ShouldRevealDuelScoreboardDetails` to reveal Duel item timing during both `level.intermissionQueued` and `level.intermissiontime`. |
| cgame score consumer | cgame dispatch recognizes `scores_duel` and calls `CG_ParseDuelScores`; symbol-map comments describe the 14 classic-weapon blocks and placement ownerdraw cache. | `CG_ParseDuelScores` consumes the fixed Duel row, stores pickup counts/averages, walks `cg_retailWeaponReloadOrder`, recomputes weapon accuracy, marks `cg.scoreStats[client]` valid, and refreshes score selection. |
| Duel HUD and menus | cgame string tables include `score_menu_duel`, `endscore_menu_duel`, `ui/ingame_scoreboard_duel.menu`, `ui/end_scoreboard_duel.menu`, and `ui/assets/hud/duel.tga`. | Source keeps the Duel menu-selection names, Duel icon registration, placement metric ownerdraws, spectator comparison scorebox, and primary/secondary status labels. |
| Forfeit and match exit | Symbol aliases promote `G_CanForfeit`, `G_ApplyForfeit`, `ScoreIsTied`, `BeginIntermission`, `ExitLevel`, and `RemoveTournamentLoser`. Retail marks the Duel loser with `-999`, recalculates ranks, adjusts tournament wins/losses at intermission, and removes the loser on restart. | Source splits command-side rejection from the shared forfeit gate, applies the Duel loser score marker, calls `CalculateRanks`, adjusts wins/losses in `BeginIntermission`, and demotes the loser in `ExitLevel`. |
| Overtime and tie handling | `ScoreIsTied` compares the top two active non-team scores for FFA/Duel/Race/Red Rover before overtime or exit-rule decisions. | Source preserves the non-team top-two score comparison and Duel participation in time/fraglimit/overtime paths. |

## Source Reconstruction

The concrete source gap closed in this pass was the Duel scoreboard detail reveal
predicate. Retail does not wait for full intermission before exposing both
players' detailed item timing rows. The `scores_duel` serializer checks the
queued-intermission latch (`data_105de9d4`, `level.intermissionQueued`) as well
as the active intermission latch (`data_105de9d8`, `level.intermissiontime`) and
then emits `scores_duel 2 %s %s` from the cached low/high row buffers.

The source now mirrors that retail branch by allowing
`G_ShouldRevealDuelScoreboardDetails` to return true when either
`level.intermissionQueued` or `level.intermissiontime` is set. The dedicated
non-team scoreboard parity test pins:

- the `level.intermissionQueued || level.intermissiontime` predicate,
- the HLIL `data_105de9d4 || data_105de9d8` branch,
- the `scores_duel 2 %s %s` literal,
- and the Sully level-offset mapping for both latches.

No runtime launch was needed; this was a static evidence and regression-test
pass.

## Confidence

Confidence is high for the queued-intermission detail fix because it is anchored
by three independent signals: the HLIL branch, the Sully `level_locals_t` offset
map, and the existing source's already-recovered public/private Duel row builder.
Confidence is also high for the queue, ready-delay, forfeit, and cgame
score-consumer wiring because the promoted symbol-map names, source helpers, and
focused tests all agree on ownership and side effects.

Open follow-up: exact executable validation of a live Duel transition from
fraglimit hit through the 200 ms queued-intermission window would be useful if a
future runtime pass already needs to launch qagame. Static evidence is strong
enough for this reconstruction, so no launch was performed here.

## Parity Estimate

- Focused Duel gametype/wiring parity: **before 96% -> after 97%**.
- Broader gameplay/gametype parity: **before 99% -> after 99%**.
