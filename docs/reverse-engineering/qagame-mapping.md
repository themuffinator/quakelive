# Qagame Mapping Ledger

This ledger tracks recurring high-confidence passes over the retail
`qagamex86.dll` against `src/code/game/` using the committed Ghidra corpus in
`references/reverse-engineering/ghidra/qagamex86/` and the Binary Ninja HLIL
dump in `references/hlil/quakelive/qagamex86.dll/`.

Observed facts come from exports, `functions.csv`, native dispatch-table slots,
log strings, and call flow. Inferred names are only promoted when the retail
behavior and source analogue align cleanly.

## Latest All-Gametype Integration Reconstruction

- Scope: full gametype enum identity, factory defaults, qagame lifecycle
  buckets, runframe hooks, exit-rule ownership, scoreboard command transports,
  team count publishing, flag/objective configstrings, and intermission stat
  publishers.
- Coverage delta: `+0` curated symbol-map entries; the individual gametype
  owners were already promoted, but this pass added a single executable
  cross-mode parity gate over the full retail mode matrix.
- Source delta: no gameplay rewrite was needed. Current qagame source already
  preserves Race as the reused single-player slot, maps shipped factory ids for
  every retail gametype, keeps the `scores_*` command split, delegates CA/A-D/RR
  exit decisions to round controllers, gates Freeze through its round delay,
  and keeps CTF-family stat publishing scoped to CTF, One Flag, Harvester,
  Domination, and Attack and Defend.
- Evidence note: qagame HLIL anchors the scoreboard command family from
  `scores_ffa` through `scores_rr`, the `tdmstats` / `castats` / `ctfstats`
  postgame publishers, and the CA, A/D, Freeze, and RR invalid-state
  controller diagnostics.
- Reconstruction note:
  `docs/reverse-engineering/all-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest CTF And One Flag Wiring Reconstruction

- Scope: `Team_SetFlagStatus`, `Pickup_Team`, `Team_TouchOurFlag`,
  `Team_TouchEnemyFlag`, `Team_ReturnFlagIfMissing`, `CheckAlmostCapture`,
  flag drop/forced-return helpers, legacy `trigger_capturezone`, and the
  CTF-family `scores_ctf` / `ctfstats` transports.
- Coverage delta: `+0` curated symbol-map entries; the CTF and One Flag owners
  were already promoted, but this pass tightened their comments, source
  headers, and parity gates around the compact flag-status and drop/return
  wiring.
- Source delta: `g_team.c` now has corrected reconstruction headers for the
  flag status/reset/return/touch helpers. No qagame gameplay rewrite was needed:
  current source already publishes CTF status as `0/1/*/*/2`, One Flag status
  as `0/1/2/3/4`, routes neutral pickup and enemy-base capture correctly, and
  clears red/blue/neutral carried flags through `G_TossFlag`.
- Evidence note: qagame HLIL anchors `0x10068770 -> Team_SetFlagStatus`,
  `0x10069800 -> Team_TouchOurFlag`, `0x10069E30 -> Team_TouchEnemyFlag`,
  `0x1006A040 -> Pickup_Team`,
  `0x1006BDA0 -> G_DroppedPowerupTouchCaptureZone`, and
  `0x10046F80 -> CheckAlmostCapture`; Ghidra keeps the red/blue/neutral
  missing-objective warnings in `G_CheckTeamItems`.
- Reconstruction note:
  `docs/reverse-engineering/ctf-oneflag-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Harvester Skull-Drop Reconstruction

- Scope: `TossClientCubes`, `G_ApplyTeamChange`, Harvester obelisk validation,
  `scores_ctf` / `ctfstats`, and cgame Harvester skull ownerdraw wiring.
- Coverage delta: `+0` curated symbol-map entries; the Harvester skull-drop,
  obelisk, scoreboard, cgame HUD, and bot goal owners were already promoted,
  but source still used stale `Red Cube` / `Blue Cube` lookup names and did not
  preserve the retail carried-skull drop semantics.
- Source delta: `g_combat.c::TossClientCubes` now reads
  `ps.generic1 & 0x3f`, clears with `ps.generic1 &= 0xc0`, launches the
  generated death skull, and loops carried skulls only while `g_dropSkulls` is
  enabled. Harvester item lookups now use `Red Skull` / `Blue Skull`, and
  `G_ApplyTeamChange` now feeds `MOD_SWITCHTEAM` into `player_die` so the
  recovered Harvester death-path exclusion is effective on team changes.
- Evidence note: qagame Ghidra `FUN_10046970` exposes the count mask, clear
  mask, `g_dropSkulls` branch, team-flipped carried-skull spawnflags,
  `g_cubeTimeout` timeout, and the `GT_HARVESTER && meansOfDeath != 0x1d`
  call gate; `FUN_10040440` passes `0x1d` into `player_die` for team-change
  cleanup, which maps to `MOD_SWITCHTEAM`.
- Reconstruction note:
  `docs/reverse-engineering/harvester-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Domination Point Wiring Recheck

- Scope: `SP_team_dom_point`, `trigger_capturezone`,
  `Team_SelectDominationSpawnPoint`, `Team_RunDomination`,
  `G_UpdateDominationPointCountConfigstrings`, the capture/assist reward fanout,
  and the Domination defense-bonus path.
- Coverage delta: `+0` curated symbol-map entries; the Domination point,
  capture, spawn, reward, count, and defense helpers were already promoted, but
  this pass connects the helpers to explicit source parity gates.
- Source delta: no gameplay-code rewrite was needed. Existing qagame source
  already reconstructs the non-Domination point free path, delayed point
  activation, linked point-spawn selection, per-frame capture/scoring pass,
  capture/assist rewards, defense bonus, and owned-count configstring bridge.
- Evidence note: qagame HLIL pins Domination respawn selection at `0x10038B60`,
  capture/assist rewards at `0x1004AA80`, primary-capturer selection at
  `0x1004ABF0`, point activation/spawn at `0x1004B720`/`0x1004BB10`,
  owned-count publishing at `0x1004B900`, and defense bonus at `0x1004B980`.
- Reconstruction note:
  `docs/reverse-engineering/domination-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Red Rover Round Wiring Reconstruction

- Scope: `RR_RoundStateTransition`, the hidden round-start configstring, the
  compact `CS_MATCH_STATE` payload, RR infection-role helpers, and the
  `scores_rr` qagame scoreboard transport.
- Coverage delta: `+0` curated symbol-map entries; the RR controller,
  infection helpers, exit helper, autojoin helper, death-path helper, and
  scoreboard owner were already promoted, but source still published the
  generic SRP match-state payload on the RR path and silently ignored unknown
  controller states.
- Source delta: `g_match_state.c` now emits the retail compact RR
  configstring forms, active rounds keep the `0x296` start side channel, and
  RR complete/exit states clear that slot to `-1`. `g_active.c` now fatal
  errors unexpected RR controller states with the recovered retail diagnostic.
- Evidence note: qagame HLIL at `0x100649F0` writes `0x295` as
  `\time\-1\round\0`, `\time\%d\round\%d`, or `\round\%d`; the same body
  writes `0x296` with the active start time and later `-1`, and preserves
  `RR_RoundStateTransition: invalid state`.
- Reconstruction note:
  `docs/reverse-engineering/red-rover-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Attack and Defend Round Wiring Reconstruction

- Scope: `AD_RoundStateTransition`, the hidden round-start configstring, the
  compact `CS_MATCH_STATE` payload, the A/D side resolvers, and the
  `scores_ad` qagame history transport.
- Coverage delta: `+0` curated symbol-map entries; the A/D controller,
  side-resolver, score-history, objective, and scoreboard owners were already
  promoted, but source still published a richer SRP match-state payload on the
  A/D path.
- Source delta: `g_match_state.c` now emits the retail compact A/D
  configstring forms, active rounds keep the `0x296` start side channel, and
  complete/exit states clear that slot to `-1` while retaining the completed
  turn's active `turn/state` payload for cgame.
- Evidence note: qagame HLIL at `0x10035B70` writes `0x295` as
  `\time\-1\round\0\turn\0\state\0`,
  `\time\%d\round\%d\turn\%d\state\1`, or `\turn\%d\state\2`; the same body
  writes `0x296` with the active start time and later `-1`, and preserves
  `AD_RoundStateTransition: invalid state`.
- Reconstruction note:
  `docs/reverse-engineering/attack-defend-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Clan Arena Round Wiring Reconstruction

- Scope: `CA_RoundStateTransition`, the hidden round-start configstring, the
  compact `CS_MATCH_STATE` payload, CA winner prints, and the dedicated
  `scores_ca` / `castats` qagame transports.
- Coverage delta: `+0` curated symbol-map entries; the CA controller and
  scoreboard/stat transport owners were already promoted, but source still
  carried an SRP-rich match-state payload and a source-only round centerprint
  on the CA path.
- Source delta: `g_match_state.c` now emits the retail compact Clan Arena
  configstring forms, active rounds publish the `0x296` start side channel, and
  complete CA rounds clear that slot to `-1`. `g_active.c` now emits the retail
  survivor-count, survivor-health, and health-vs-health round-result prints and
  fatal-errors unexpected CA controller states.
- Evidence note: qagame HLIL at `0x10038230` writes `0x295` as
  `\time\-1\round\0`, `\time\%d\round\%d`, or `\round\%d`; the same body writes
  `0x296` with the active start time and later `-1`, and preserves the three
  CA result print strings plus `CA_RoundStateTransition: invalid state`.
- Reconstruction note:
  `docs/reverse-engineering/clan-arena-gametype-wiring-reconstruction-2026-06-12.md`.

## Latest Botlib Debug Visualization Wiring

- Scope: `ai_main.c::BotTestAAS`, qagame native import slots `83/84`, and the
  engine-owned botlib debug helpers `BotDrawDebugAreas` / `BotDrawAvoidSpots`.
- Coverage delta: `+0` curated symbol-map entries; this is source and wiring
  reconstruction against already-named engine-side botlib exports.
- Source delta: `g_public.h` now names `G_QL_IMPORT_BOTLIB_AI_DRAW_DEBUG_AREAS`
  and `G_QL_IMPORT_BOTLIB_AI_DRAW_AVOID_SPOTS`, qagame uses direct native
  wrappers for those retail-only slots, `SV_InitGameImports` fills them from
  `botlib_export->ai`, and `BotTestAAS` performs the retail debug draw pass
  before the solid/cluster AAS diagnostics.
- Evidence note: qagame HLIL at `0x10020F00` updates `bot_testsolid`,
  `bot_testclusters`, and `bot_showAreas`, then calls
  `data_104b13ac + 0x14c` with `(origin, bot_showAreas.integer,
  bot_showAreaNumber.integer)`. The same body reads `bot_showAvoidSpots` as a
  selected bot index and calls `data_104b13ac + 0x150` with the selected
  `bot_state_t::ms` handle, or clears `bot_showAvoidSpots` through `Cvar_Set`
  when the selected bot state is missing.
- Reconstruction note:
  `docs/reverse-engineering/botlib-native-import-compat-bridge-recheck-2026-06-05.md`.

## Latest Mapping Correction

- Scope: botlib obstacle-prediction wiring around
  `ai_dmq3.c::BotAIPredictObstacles`, the qagame `trap_AAS_PredictRoute` import
  call, and the engine-owned `AAS_PredictRoute` result layout.
- Coverage delta: `+0` curated symbol-map entries; corrected one existing
  identity from `BotCheckForGrenades` to `BotAIPredictObstacles`.
- Source delta: none. The current qagame source already carries the retail
  `bot_predictobstacles` gate, six-second goal-area throttle, route-prediction
  constants, mover model lookup, and activation-goal path. The engine
  `AAS_PredictRoute` source already mirrors retail by initializing `endarea`,
  `stopevent`, `endcontents`, `endtravelflags`, `endpos`, and `time` without
  writing `numareas`.
- Evidence note: qagame HLIL at `0x1001DCF0` calls the botlib import slot
  `0x13c` with `100`, `1000`, `RSE_USETRAVELTYPE|RSE_ENTERCONTENTS`,
  `AREACONTENTS_MOVER`, `TFL_BRIDGE`, and `0`, then follows the mover
  activation path. Host HLIL/Ghidra at `0x00494870` pins the matching
  `AAS_PredictRoute` layout. The same round rejected adding HMG/heavy-bullet bot
  inventory wiring because retail `BotUpdateInventory` and
  `BotNormalizeAmmoInventory` stop at the chaingun/belt inventory slab.
- Reconstruction note:
  `docs/reverse-engineering/botlib-obstacle-prediction-mapping-2026-06-05.md`.

## Botlib Import And AI Alias Recheck

- Scope: qagame native botlib import offsets plus the recent bot-AI tranche
  aliases around seek/combat nodes, activate-goal helpers, obstacle prediction,
  snapshot scans, prox-mine/event helpers, and direct AI resource slots.
- Coverage delta: `+44` scoped alias entries in
  `references/analysis/quakelive_symbol_aliases.json` for the paired
  `FUN_`/`sub_` names from `AINode_Seek_NBG` through `BotCheckSnapshot`,
  including the contiguous activate-goal helper run from
  `BotFuncButtonActivateGoal` through `BotRandomMove`.
- Source delta: `BotGetActivateGoal` now checks the fetched classname's first
  byte rather than the stack-array pointer, matching the retail first-byte guard
  before the no-classname error path.
- Evidence note: qagame Ghidra/HLIL pins `BotLibStartFrame` at
  `DAT_104b13ac + 0xd8`, `BotLibUpdateEntity` at `+0xe0`,
  `AAS_PredictRoute` at `+0x13c`, `AAS_AlternativeRouteGoals` at `+0x140`,
  `AAS_Swimming` at `+0x144`, and `AAS_PredictClientMovement` at `+0x148`.
  The same corpus now backs direct bot-AI native imports for character
  load/free, characteristic float/integer, goal-stack diagnostics, item-weight
  loads, fuzzy-logic interbreed/save/mutate, goal-state alloc/free, reset move
  state, and move-state alloc/free.
- Mapping note: no standalone retail `BotCheckForGrenades` owner was promoted,
  and the previous `0x1001D810` `BotPrintActivateGoalInfo` identity was
  corrected to `BotRandomMove`. The retail `BotCheckSnapshot` body carries the
  grenade avoidance flow inline while calling out to `BotCheckEvents` and
  `BotCheckForProxMines`; retail references also omit the GPL debug activate
  speech strings used by `BotPrintActivateGoalInfo`.
- Reconstruction note:
  `docs/reverse-engineering/botlib-snapshot-grenade-inline-reconstruction-2026-06-05.md`,
  `docs/reverse-engineering/botlib-native-import-compat-bridge-recheck-2026-06-05.md`,
  and
  `docs/reverse-engineering/botlib-activate-goal-source-mapping-2026-06-05.md`.

## Latest Source Reconstruction Pass

- Scope: spectator client-state resync across `G_ApplyTeamChange`,
  `ClientSpawn`, `SpectatorClientEndFrame`, `G_SyncSpectatorItemStatesForClient`,
  and the cgame `CG_Respawn` `specresp` handoff.
- Coverage delta: `+0` curated symbol-map entries; the owning functions were
  already mapped, but the source still left the retail `0x4000` spectator
  eFlag write unresolved as a GPL `EF_VOTED` collision.
- Source delta: `EF_SPECTATOR_RESPAWN` now aliases the retail `0x4000`
  playerstate bit. `G_ApplyTeamChange` and `ClientSpawn` set it for
  `TEAM_SPECTATOR` snapshots and clear it for non-spectator snapshots before
  the cgame `CG_Respawn` path answers with `specresp`. `SpectatorClientEndFrame`
  now preserves that observer bit when copying followed-player snapshots, and
  the existing item-state resync/broadcast path remains the server-side
  responder for both `specresp` and direct spectator entry.
- Evidence note: qagame HLIL/Ghidra at `0x10040440` and `0x1003BC30` both show
  the `0x4000` set/clear around spectator team state. cgame HLIL at
  `0x100433D0` reads the same bit before sending `"specresp"`, and qagame
  `0x100462D9` routes that command back into `0x1004ED70`.
- Reconstruction note:
  `docs/reverse-engineering/spectator-client-state-wiring-reconstruction-2026-05-27.md`.

## Previous Source Reconstruction Pass

- Scope: spectator state and movement across `SpectatorThink`,
  `G_TouchTriggers`, `SpectatorClientEndFrame`, `StopFollowing`,
  `Cmd_Follow_f`, `Cmd_FollowCycle_f`, shared qagame/cgame `PM_FlyMove`, and
  `Pickup_Powerup`.
- Coverage delta: `+0` curated symbol-map entries; the owning functions were
  already mapped, but the source still carried Q3/source-only spectator speed,
  unlink ordering, POI camera branches, command-wrapper follow cycling,
  stop-follow fallback policy, and Flight-fuel movement assumptions.
- Source delta: `SpectatorThink` now unlinks before pmove, writes the retail
  `480` spectator speed, touches triggers after moving, returns after
  attack-edge inner follow cycling, and uses the later `BUTTON_ANY` edge to
  drop follow state. `SpectatorClientEndFrame` now mirrors only connected
  non-`PM_SPECTATOR` clients, forces copied snapshots back to
  `PM_SPECTATOR | PMF_FOLLOW`, active-team cycles stale explicit targets, and
  no longer carries source-only POI branches. `StopFollowing` now performs the
  direct retail `SPECTATOR_FREE` reset. `Cmd_Follow_f` now resolves only player
  strings, keeps the retail `"pw"` preserve-current-flag-carrier guard, rejects
  targets through `ps.pm_type == PM_SPECTATOR`, and carries no source-only
  training-map print gate; `Cmd_FollowCycle_f` uses the retail
  `sess.sessionTeam` spectator handoff before tailcalling the inner cycle
  worker. `G_CAADRespawnAsSpectator` now pre-seeds `PM_SPECTATOR` before
  `ClientSpawn` and only enters follow mode through the shared `FollowCycle`
  gate when both active teams still have players, while `ClientSpawn` now
  preserves that pre-existing spectator spawn mode. Shared `PM_FlyMove` is
  back to the retail four-call wish-vector body, and `Pickup_Powerup` no
  longer seeds source-only Flight thrust/fuel stats.
- Evidence note: qagame HLIL at `0x10033E30` shows `trap_UnlinkEntity` before
  the spectator-state branch, `ps.speed = 0x1e0`, `Pmove` before
  `G_TouchTriggers`, an immediate return after attack-edge follow cycling, and
  a later `BUTTON_ANY` stop-follow branch. HLIL at `0x10035470`,
  `0x10040D10`, and `0x10041130` pins the follow mirror, stop-follow reset,
  and client-only follow-cycle filters. HLIL at `0x10040F30` and `0x100412E0`
  pins the follow-command player-string path, `"pw"` suffix guard,
  `PM_SPECTATOR` target rejection, absence of a training gate, and public
  follow-cycle session-team handoff. HLIL at `0x10035960` sets
  `PM_SPECTATOR` before `ClientSpawn`, counts active players by team, and calls
  `FollowCycle` directly instead of using a bespoke target picker or relink
  fallback. The qagame/cgame `PM_FlyMove` symbol-map entries and qagame
  `Pickup_Powerup @ 0x1004DFE0` pin the Flight side of the shared fly-move
  cleanup.
- Reconstruction note:
  `docs/reverse-engineering/qagame-spectator-state-movement-reconstruction-2026-05-26.md`.

## Previous Source Reconstruction Pass

- Scope: qagame client spawning and adjacent selection/finalization helpers:
  `ClientBegin`, `G_SelectClientSpawnPoint`, `G_SelectRankedSpawnPoint`,
  `Team_SelectDominationSpawnPoint`, `G_InitClientSpawnState`,
  `G_FinalizeSpawnLoadout`, `G_GiveItemByName`, and `ClientSpawn`.
- Coverage delta: `+0` curated symbol-map entries; the owning retail functions
  were already mapped, but `ClientSpawn` still missed the null-spawn retry
  edge visible in HLIL and Ghidra.
- Source delta: `ClientSpawn` now exits through a retail-style 600 ms deferred
  retry lane when an active player cannot claim an eligible spawnpoint. The
  reconstructed source keeps bot/human spawnflag retries bounded, sets
  `respawnTime`, parks the player in `PM_SPECTATOR`, increments the recovered
  retry counter, and schedules a guarded retry instead of looping indefinitely
  over an invalid/null spawn. The ClientSpawn-side wrapper also now uses the
  recovered team-spawn gametype band instead of a broad `>= GT_CTF` shortcut:
  Clan Arena routes through the team spawn-class family and Red Rover stays on
  the neutral spawn path before its role/loadout finalizer runs.
- Source delta follow-up: the shared source ranked picker now retains the
  retail `0x1a` ranked-candidate window instead of the older 32-entry cap,
  matching the `G_SelectRankedSpawnPoint @ 0x10039080` clamp.
- Source delta follow-up: ranked spawn candidates now pass through the
  recovered `spawnflags & 2` exclusion before distance scoring and before the
  no-ranked-candidate fallback chooses a raw spawn entity.
- Source delta follow-up: neutral initial spawns now use the ranked picker's
  recovered bit-1 admission mode, and team `TEAM_BEGIN` spawns retry
  `team_CTF_*spawn` after a failed `team_CTF_*player` pass before falling back
  to neutral deathmatch starts.
- Evidence note: qagame HLIL/Ghidra at `0x1003BC30` shows the active-player
  `G_SelectClientSpawnPoint` call before the large client reset, the null
  result branch writing `level.time + 600`, `PM_SPECTATOR`, and the retry
  counter, and the successful branch clearing the retry counter before the
  normal spawn bootstrap.
- Evidence note: qagame HLIL/Ghidra at `0x10039080` shows the ranked helper
  reading spawnflags at `entity + 0x248`; HLIL guards candidate admission with
  `(flags & 2) == 0`, and the Ghidra companion decompile shows the same bit-2
  filter before candidate counting/ranking.
- Evidence note: the same ranked helper admits neutral initial starts only when
  `(flags & 1) != 0`, and when begin-mode team class selection fails it clears
  the begin-mode argument and re-enters selection for the same team's regular
  spawn classname.
- Reconstruction note:
  `docs/reverse-engineering/qagame-client-spawn-reconstruction-2026-05-26.md`.

## Earlier Source Reconstruction Pass

- Scope: qagame teleporting state and related wiring across `TeleportPlayer`,
  `target_teleporter_use`, `trigger_teleporter_touch`, `SP_trigger_teleport`,
  `Touch_DoorTriggerSpectator`, `ClientEvents`, `respawn`,
  `G_DroppedPowerupRunFrame`, `BotSetupForMovement`, and the cgame consumers
  documented in the companion symbol map.
- Coverage delta: `+0` curated symbol-map entries; the owning functions were
  already mapped, but the source helper missed one retail edge.
- Source delta: `TeleportPlayer` now frees an active grappling hook through
  `Weapon_HookFree` after toggling `EF_TELEPORT_BIT` and before applying the
  destination view angles / telefrag path. The ordering matches retail
  `sub_1005A420`.
- Evidence note: the qagame HLIL at `0x1005A420` keeps the full teleport
  contract: temp events, unlink, origin lift, 400 ups exit velocity,
  `pm_time = 160`, `PMF_TIME_KNOCKBACK`, `EF_TELEPORT_BIT`, the active-hook
  `sub_1006E330` call, view-angle setup, destination killbox, entitystate
  mirror, lag-history clear, and non-spectator relink. The related producers
  map through `target_teleporter_use`, `trigger_teleporter_touch`,
  `ClientEvents`, `respawn`, `Touch_DoorTriggerSpectator`, and
  `G_DroppedPowerupRunFrame`; cgame consumes the state through
  `CG_SetNextSnap`, `CG_TransitionSnapshot`, `CG_TouchTriggerPrediction`,
  `CG_CalcViewValues`, and the teleport event cases.
- Reconstruction note:
  `docs/reverse-engineering/qagame-teleport-state-reconstruction-2026-05-26.md`.

## Previous Source Reconstruction Pass

- Scope: qagame knockback application, blocking, and pmove-consumption wiring
  around `G_KnockbackScaleForMOD`, `G_Damage`, `PMF_TIME_KNOCKBACK`,
  `ClientSpawn`, `TeleportPlayer`, `BotSetupForMovement`, `PM_Friction`,
  `PM_WalkMove`, `PM_DropTimers`, `target_laser_think`, and
  `ProximityMine_ExplodeOnPlayer`.
- Coverage delta: `+0` curated symbol-map entries; the owning functions were
  already mapped, but the source path still diverged around signed knockback
  and the meaning of the retail timer-floor cvar.
- Source delta: `G_Damage` now preserves negative knockback by inverting the
  incoming direction and applying the absolute magnitude, keeps
  `FL_NO_KNOCKBACK` / `DAMAGE_NO_KNOCKBACK` as zeroing gates, uses the rounded
  magnitude for the `PMF_TIME_KNOCKBACK` timer, and removes the non-retail
  vertical boost plus crouch/low-health cripple velocity reduction. The
  follow-up feedback pass also removes the inherited `damage_knockback`
  frame-feedback slot/write/reset because retail stores `damage_from`
  immediately after `damage_armor` and `damage_blood`.
- Evidence note: the damage-side path is anchored at `sub_10048C30` in part02
  HLIL. The same slice shows the negative branch, the `g_knockback_cripple`
  timer-floor read, and negative evidence for `g_knockback_z` /
  `g_knockback_z_self` as `G_Damage` consumers. The shared pmove source and
  symbol maps carry the matching `PMF_TIME_KNOCKBACK` consumer contract:
  friction suppression, slick/knockback air acceleration, gravity, and
  `PMF_ALL_TIMES` expiry. `BotSetupForMovement` adds the bot-side bridge by
  translating active `PMF_TIME_KNOCKBACK` plus positive `pm_time` into
  `MFL_TELEPORTED` before the waterjump flag. The producer sweep also pins
  the no-knockback side: null `dir` damage becomes `DAMAGE_NO_KNOCKBACK`,
  target lasers pass that flag with `MOD_TARGET_LASER`, and juiced prox
  discharge passes it with `MOD_JUICED`. The `P_DamageFeedback` HLIL at
  `0x10033800` clears only the armor and blood totals, matching the absence of
  a retail `damage_knockback` feedback slot. `TeleportPlayer` is a separate
  producer: after the 400 ups exit launch it seeds `pm_time = 160` and
  `PMF_TIME_KNOCKBACK`.
- Reconstruction note:
  `docs/reverse-engineering/qagame-knockback-reconstruction-2026-05-26.md`.

## Earlier Source Reconstruction Pass

- Scope: qagame score/stat/ready/vote/cheat `ClientCommand` ladder across ten
  command surfaces: `score`, `acc`, `pstats`, `readyup`, `vote`, `give`,
  `god`, `notarget`, `noclip`, and `kill`.
- Coverage delta: `+0` curated symbol-map entries; the selected helper names
  were already mapped, but the source dispatch order still diverged from the
  retail pre-intermission cluster.
- Source delta: moved `acc`, `pstats`, `readyup`, and `vote` into the
  HLIL-backed pre-intermission cluster, and removed the later post-intermission
  `vote` branch so `G_HandleNextMapVote` is reachable during intermission.
- Evidence note: the command-token chain is anchored at `sub_10045DEC` in
  part01 HLIL. The adjacent retail `ragequit` compare is visible between
  `readyup` and `vote`, but its one-argument native import target remains an
  open boundary for a later import-owner pass.
- Reconstruction note:
  `docs/reverse-engineering/qagame-score-vote-cheat-command-reconstruction-2026-05-25.md`.

## Earlier Source Reconstruction Pass

- Scope: qagame chat and voice client-command ladder across ten command
  surfaces: `say`, `say_team`, `tell`, `botSay`, `vsay`, `vsay_team`,
  `vtell`, `vosay`, `vosay_team`, and `votell`, with `vtaunt` rechecked as the
  adjacent retail boundary.
- Coverage delta: `+0` curated symbol-map entries; the relevant command
  helpers were already mapped, but their source dispatch order was not pinned
  as a retail cluster.
- Source delta: moved the source-local `complaint` branch after `vtaunt` so it
  no longer interrupts the retail `botSay` -> `vsay` chat/voice ladder.
- Evidence note: the command-token chain is anchored at `sub_10045DEC` in
  part01 HLIL. Helper bodies map through `sub_10041B60`, `sub_10041B90`,
  `sub_10041CC0`, `sub_10041E40`, `sub_10041E60`, and `sub_10041F50`.
- Reconstruction note:
  `docs/reverse-engineering/qagame-chat-voice-command-reconstruction-2026-05-25.md`.

## Earlier Source Reconstruction Pass

- Scope: qagame server-command wiring across ten command surfaces:
  `addscore`, `addteamscore`, `setmatchtime`, `entitylist`, `forceteam`,
  `game_memory`, `addbot`, `botlist`, `game_crash`, and `reload_access`.
- Coverage delta: `+0` curated symbol-map entries; the relevant helpers were
  already mapped or deliberately inlined in the retail dispatcher.
- Source delta: corrected the gameplay-time `Svcmd_AddBot_f` media refresh to
  send the retail `loaddeferred\n` server command, matching `sub_10037910` and
  the training-bot path.
- Evidence note: direct rows come from `data_10080750` in part02 HLIL, while
  console wiring is anchored at `sub_10066B90`. The addbot refresh string is
  visible in both `sub_10037910` and `data_1008242C`.
- Reconstruction note:
  `docs/reverse-engineering/qagame-server-command-wiring-reconstruction-2026-05-25.md`.

## Latest Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: unchanged at `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: unchanged at `1027/1027` mapped functions (`100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+0` coverage, but `2` retained Json helpers were tightened from descriptive cleanup labels to source-faithful JsonCpp destructor identities.
- Note: curated overhang stays flat at `101`.
- Note: this was a mapping-only rename pass, so no source-side parity code changed; the embedded `qagame.json` stats block remains `1128/1128`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Source-faithful JsonCpp destructor rename | `JsonValueDestructor` and `JsonValueDestructorCleanup` |

This was another quality pass over the retained Json overhang after coverage had
already reached `1027/1027`. The old labels `JsonValueDestroy` and
`JsonValueDestroyCleanup` were behaviorally accurate, but the committed HLIL and
the surrounding unwind states show that they are specifically the old JsonCpp
`Json::Value::~Value()` body and its paired EH cleanup leaf.

At `0x100793A0` the helper switches on the tagged `Json::Value` kind, releases
allocator-owned strings through the default allocator vtable, recursively tears
down map-backed array/object storage, and frees the optional comment array. The
paired `0x1007B80C` funclet tailcalls that same body for the protected stack
`Json::Value` local used in the resolver seam, which pins it as destructor
cleanup rather than a generic destroy helper.

## Immediate Previous Pass

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: unchanged at `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: unchanged at `1027/1027` mapped functions (`100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+0` coverage, but `4` retained Json helpers were tightened from descriptive labels to source-faithful JsonCpp method names.
- Note: curated overhang stays flat at `101`.
- Note: this was a mapping-only rename pass, so no source-side parity code changed; the embedded `qagame.json` stats block remains `1128/1128`.

## Newly Mapped In The Immediate Previous Pass

| Area | Recovered functions |
| --- | --- |
| Source-faithful JsonCpp method renames | `JsonValueOperatorAssign`, `JsonValueOperatorEquals`, `JsonValueOperatorIndexArrayIndex`, and `JsonValueOperatorIndexCString` |

This was a quality pass over the retained Json overhang after coverage had
already reached `1027/1027`. The old labels for these four entries were
behaviorally accurate but still descriptive. Cross-checking the committed HLIL
against the upstream `json_value.cpp` operator bodies shows that they match the
old JsonCpp source exactly: the assignment helper is the `Value temp(other);
swap(temp);` body of `Json::Value::operator=`, the equality predicate is
`Json::Value::operator==`, and the two resolver leaves are the non-const
`Json::Value::operator[]` overloads for `ArrayIndex` and `const char *`.

The CString member path deserves the extra note that retail optimization has
inlined the private `resolveReference( key, false )` helper into the emitted
`operator[]( const char * )` body. That leaves the compiled helper with the
full promotion/lower-bound/insert sequence rather than the tiny source wrapper,
but the source-level identity is still exact.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1126` -> `1128` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `1025/1027` -> `1027/1027` mapped functions (`99.81%` -> `100.00%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+2` curated names, `+2` corpus-overlap matches, and `+0.19` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `101` because every promoted helper in this round already has a standalone `functions.csv` row.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1128/1128`.

## Newly Mapped In The Previous Coverage Update

| Area | Recovered functions |
| --- | --- |
| Final Json resolver cleanup seam | `JsonValueResolveReferenceInsertPairKeyCleanup` and `JsonValueResolveReferenceInsertPairKeyTeardownCleanup` |

This pass closed the last two anonymous `functions.csv` rows in the embedded
JsonCpp resolver seam. The key evidence was the committed FuncInfo block at
`0x1008BD20`: its six-state unwind map shows `0x1007B81C`, `0x1007B824`, and
`0x1007B82C` all unwinding back to state `2`, with the middle state using the
already-mapped full pair destructor `JsonValueMapNodeDestroyCleanup`. That pins
the two remaining leaves as key-only cleanup states on the same stack
insertion-pair local rather than separate source-level helpers.

The stage split is explicit in HLIL. State `3` is active after the pair
`CZString` key has been copy-constructed but before the sibling `Json::Value`
payload is fully live, so `0x1007B81C` only destroys that pair key. State `5`
is set immediately before the explicit `JsonValueDestructor` teardown of the
stack pair payload after insertion returns, so `0x1007B82C` is the later
key-only cleanup that runs if that teardown path itself unwinds.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1086` -> `1091` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `987/1027` -> `990/1027` mapped functions (`96.11%` -> `96.40%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+5` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang rose from `99` to `101` because the retained `g_inactivityWarning` and `g_instaGib` callback stubs do not have standalone rows in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1091/1091`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Shared gameplay classifiers | `G_PowerupCarrierKillUsesWhitePrefix` and `G_RoundControllerGametypeEnabled` |
| Retained qagame cvar callbacks | `G_InactivityWarningCvarChanged`, `G_InstaGibCvarChanged`, and `G_PlayerScaleCvarsChanged` |

This sweep stayed on small gameplay and callback leaves where the owning seam is
already mapped. `G_RoundControllerGametypeEnabled` is exact: its truth table is
the same `CA` / `Attack & Defend` / `Freeze` / `Red Rover` classifier used by
the reconstructed round-controller source. `G_PowerupCarrierKillUsesWhitePrefix`
is a descriptive split helper under the already mapped carrier-kill announcer,
with the HLIL showing the dedicated objective-gametype branch that selects the
white versus fallback yellow prefix.

The other three promotions come directly from the retained cvar table in the
HLIL. `G_InactivityWarningCvarChanged` hangs off `g_inactivityWarning` and
immediately fans into the already mapped `G_ResetClientInactivityWarnings`.
`G_InstaGibCvarChanged` is the adjacent `g_instaGib` callback that refreshes
the live ammo slab through the nearby instagib/infinite-ammo sync helper.
`G_PlayerScaleCvarsChanged` is shared by `g_playerheadScale` and
`g_playerModelScale` and simply reruns `ClientUserinfoChanged` for connected
clients so forced-appearance state updates in-place.

I rechecked the neighboring player-appearance, Freeze, and startup/runtime
helpers in the same pass, but left them unnamed where the source analogue or
retained implementation boundary was still less explicit than the five entries
promoted here.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1078` -> `1086` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `979/1027` -> `987/1027` mapped functions (`95.33%` -> `96.11%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+8` curated names, `+8` corpus-overlap matches, and `+0.78` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `99` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1086/1086`.

## Newly Mapped In The Immediate Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared gameplay helper | `BG_PlayerCarryingFlag` |
| Json and MSVC EH funclets | `JsonValueMapNodeDestroyThunk`, `CatchAllStdStringGrow`, `CatchAllJsonValueClearMapRange`, `CatchAllJsonValueMapCloneSubtree`, `CatchAllJsonValueMapNodeConstruct`, `EhVectorDestructorIteratorCleanup`, and `EhVectorConstructorIteratorCleanup` |

This sweep stayed on high-confidence leaves only, but widened from the prior
runtime pass into two adjacent seams. The gameplay-side addition is exact:
`BG_PlayerCarryingFlag` is the same three-flag predicate still present as a
static helper in `bg_misc.c`, and the qagame callers pass the leading
`playerState_t` slab through client pointers exactly as the HLIL suggests.

The rest of the round promoted compiler-generated helpers whose owning
functions were already mapped. `CatchAllStdStringGrow`,
`CatchAllJsonValueClearMapRange`, `CatchAllJsonValueMapCloneSubtree`, and
`CatchAllJsonValueMapNodeConstruct` all preserve explicit cleanup-and-rethrow
behavior in HLIL, while `EhVectorDestructorIteratorCleanup` and
`EhVectorConstructorIteratorCleanup` are the paired MSVC `__ArrayUnwind`
cleanup funclets under the two previously landed EH vector iterators. I also
named the tiny `JsonValueMapNodeDestroyThunk` forwarder at `0x100797A0`
because it is a one-step regparm tailcall into the already mapped node
destructor.

I left the remaining `Catch_All@...`, `Unwind@...`, and gameplay-side `FUN_...`
rows untouched where the parent relationship or source analogue was still less
explicit than the entries promoted here.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `1019` -> `1025` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `922/1027` -> `928/1027` mapped functions (`89.78%` -> `90.36%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+6` curated names, `+6` corpus-overlap matches, and `+0.58` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `97` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `1025/1025`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Retained string assignment and growth seam | `StdStringAssignRange`, `StdStringAssignSubstr`, `StdStringGrow`, and `StdStringErase` |
| Json string and map-tail seam | `JsonValueSetCString` and `JsonValueMapSubtreeRightmost` |

This sweep stayed in the retained C++ runtime and the embedded JsonCpp support
layer that sits immediately beneath the already mapped Json value/object
helpers. The retail HLIL preserved the string length/capacity layout, the
small-string and growth rules, the alias-safe substring path, and the sentinel
tree footer handling strongly enough to promote these leaves without forcing
broader STL implementation guesses elsewhere in the runtime seam.

`StdStringAssignRange`, `StdStringAssignSubstr`, `StdStringGrow`, and
`StdStringErase` close the small retained-string corridor adjacent to the
already mapped Json string constructors and copy paths. Retail shows the exact
offset validation, self-alias fallback, 1.5x growth heuristic, suffix-preserve
copy, `memmove`-based erase path, and trailing-NUL maintenance expected from
the old MSVC string runtime used by the binary.

`JsonValueSetCString` and `JsonValueMapSubtreeRightmost` close two remaining
Json internals that were still unnamed beside the previously mapped string and
tree helpers. The first tags a value as an allocated string, clears the
optional comment pointer, duplicates the incoming C string, and returns the new
buffer. The second walks to the rightmost descendant of a map subtree and is
reused by the erase/relink corridor to rebuild the sentinel's cached end
predecessor.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `974` -> `976` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `878/1027` -> `880/1027` mapped functions (`85.49%` -> `85.69%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+2` curated names, `+2` corpus-overlap matches, and `+0.19` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `976/976`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared muzzle-point seam | `CalcMuzzlePoint` |
| Shared network snap seam | `SnapVectorTowards` |

This sweep focused on the remaining small `g_weapon` helpers adjacent to the
already-mapped projectile and muzzle corridors. Two exact source leaves cleared
the promotion bar; the nearby player-name and team-location wrappers were left
unmapped because they no longer match source signatures cleanly enough.

`CalcMuzzlePoint` is exact `g_weapon.c` recovery. HLIL preserves the forward
derivation from `client->ps.viewangles`, the `ent->s.pos.trBase` seed, the
`client->ps.viewheight` lift, and the crouched-versus-standing forward offset.
Retail folds the source-equivalent `CalcMuzzlePointOrigin` no-op variant into
the same leaf.

`SnapVectorTowards` is exact `g_weapon.c` recovery. The HLIL body matches the
three-component truncate-and-bias loop that snaps each coordinate toward the
reference vector so impact endpoints stay on the intended side for networked
missile events.

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `963` -> `964` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `867/1027` -> `868/1027` mapped functions (`84.42%` -> `84.52%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+1` curated name, `+1` corpus-overlap match, and `+0.10` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because this promotion already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `964/964`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Team objective bonus seam | `Team_CheckHurtCarrier` |

This round spent most of its time sweeping adjacent unmapped `g_team`,
`g_items`, and cvar-callback leaves beneath already-mapped callers. Only one
candidate cleared the exact-match bar.

`Team_CheckHurtCarrier` is exact `g_team.c` recovery. HLIL preserves the null
client guards, the target-team switch that chooses the opposing flag powerup,
and the mirrored `lasthurtcarrier = level.time` stamp for both enemy flag
carriers and Harvester skull carriers.

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `960` -> `963` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `864/1027` -> `867/1027` mapped functions (`84.13%` -> `84.42%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `96` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `963/963`.

## Newly Mapped In This Pass

| Area | Recovered functions |
| --- | --- |
| Warmup deadline seam | `G_SetWarmupTime` |
| Inactivity warning seam | `G_ResetClientInactivityWarnings` |
| Memory allocator seam | `G_Alloc` |

This pass focused on two small shared-state helpers in the match-state and
memory-management seam, plus one small cvar-driven client-state reset.
`G_SetWarmupTime` is intentionally descriptive rather than source-exact: HLIL
shows it writing the live warmup deadline, publishing `CS_WARMUP`, refreshing
the adjacent auto-record controller, and then deriving `g_gameState` from the
sign of that deadline.

`G_ResetClientInactivityWarnings` is likewise descriptive. The owning callback
table ties it directly to `g_inactivityWarning`, and the leaf itself only walks
connected clients to clear the per-client inactivity-warning latch so the
warning countdown can be reissued under the updated setting.

`G_Alloc` is exact `g_mem.c` recovery. The retained
`G_Alloc of %i bytes (%i left)\n` and allocation-failure diagnostics, together
with the shared 32-byte alignment math and the 4 MB slab cursor, make the
allocator boundary unambiguous even though retail folds `G_InitMemory` into the
larger init corridor.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `952` -> `960` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `859/1027` -> `864/1027` mapped functions (`83.64%` -> `84.13%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+8` curated names, `+5` corpus-overlap matches, and `+0.49` percentage points on full-corpus parity.
- Note: curated overhang rises from `93` to `96` because the retail rocket, plasma, and BFG acceleration think leaves promoted in this pass are folded into surrounding constructors in the committed `functions.csv` export rather than emitted as standalone rows.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `960/960`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Shared missile / acceleration seam | `G_SpawnConfiguredMissile`, `G_RunGuidedRocketThink`, `G_RunRocketAccelerationThink`, `G_RunPlasmaAccelerationThink`, and `G_RunBfgAccelerationThink` |
| Target use callbacks | `Use_Target_Give`, `Use_Target_RemoveKeys`, and `Use_target_remove_powerups` |

This pass focused on two small retail-only helper families that already had
their owning callers mapped. The missile batch closes the shared projectile
setup seam beneath `fire_grenade`, `fire_rocket`, `fire_plasma`, and `fire_bfg`,
plus the older think-driven guided-rocket and acceleration sidecars that the
current tree now expresses through `G_RunMissile` and inline helper calls.

The target batch is source-faithful recovery from `g_target.c`. HLIL preserves
the `target_give` loop that forwards matching item targets through `Touch_Item`
and then unlinks them, the key-removal callback that drops carried keys through
`G_ResetKeyItem`, and the powerup-removal callback that returns any carried CTF
flags before clearing the activator's powerup array.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `949` -> `952` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `856/1027` -> `859/1027` mapped functions (`83.35%` -> `83.64%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, and `+0.29` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `952/952`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Persistent-powerup flag-base seam | `G_FindPersistantPowerupFlagBaseByTeam` |
| CTF flag sanity seam | `Team_ReturnFlagIfMissing` |
| Round-results client-list seam | `G_CountAndSortConnectedClients` |

This pass focused on small remaining helpers whose ownership was already pinned
down by adjacent mapped callers. The persistent-powerup helper is a team-indexed
mirror of the existing string-keyed flag-base resolver and is only used to seed
the cached red and blue base origins in `G_InitItemPowerupState`.

The CTF helper is the per-frame flag-sanity guard reached from the `GT_CTF`
branch in `G_RunFrame`: it scans for a surviving dropped or visible flag entity,
falls back to a live enemy carrier with an active flag powerup, and auto-calls
`Team_ReturnFlag` only when the flag has vanished entirely. The client-list
helper closes a small round-results split under the Red Rover controller by
counting connected/non-spectator/playing clients, seeding the first two follow
slots, and sorting the emitted client list through the adjacent retail
team/score comparator.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `943` -> `949` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `850/1027` -> `856/1027` mapped functions (`82.77%` -> `83.35%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+6` curated names, `+6` corpus-overlap matches, and `+0.58` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `949/949`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| PMove tuning / wish-move seam | `PM_LoadMoveTuningConstants` and `PM_BuildWishMove3D` |
| Combat knockback seam | `G_KnockbackScaleForMOD` |
| Retail damage / award temp-entity seam | `G_AddDamagePlum`, `G_AddAwardEntity`, and `G_GrantPlayerReward` |

This pass focused on the remaining shared pmove sidecar leaves and the Quake
Live-only reward telemetry seam under `G_Damage` and the kill/round bonus
paths. The PMove pair is backed by the previously mapped cgame movement corridor:
the qagame bodies match the same retail constant-loader and 3D wish-vector
builder already recovered on the client binary. The later dispatcher recheck of
`PmoveSingle` at `0x10031FA0` also confirms the early dead-player trace-mask
gate: retail clears `CONTENTS_BODY` only when health is non-positive and
`PW_INVULNERABILITY` is inactive.

The 2026-05-22 ground-trace source follow-up also rechecked qagame
`0x10030ED0` and the adjacent `PM_CheckDuck` offset evidence. Retail does not
replicate a ground-trace history or latest-normal cache in playerState; the
ground resolver stores only `groundEntityNum`, while frame-local consumers read
the current `pml.groundTrace`.

The same 2026-05-22 playerState wiring pass rechecked the retail engine
netfield table against qagame `PmoveSingle` at `0x10031FA0`. Source now matches
the retail prefix offsets for `clientNum` (`0x88`), `location` (`0x8c`), and
the signed command mirror bytes (`0x1dc..0x1de`), and the progress-backed
holdable timer now uses stats offsets `0xe8`, `0xec`, and `0xf0` instead of
source-only playerState sidecars.
The 2026-05-25 playerState command-gate fixture pass then pinned the
`PMF_NO_MOVE` early return with executable evidence: `PmoveSingle` still
advances `commandTime` from the current command, but it returns before
`PM_UpdateViewAngles`, the `weaponPrimary`/`fov`/signed command-axis mirrors,
trace dispatch, and origin/velocity movement side effects. This keeps the
source aligned with the retail qagame/cgame symbol comments for the no-move
gate instead of relying on structural order checks alone.

The combat batch closes the next reward transport boundary. HLIL preserves the
weapon-specific `g_knockback_%s` selector used by `G_Damage`, the local-client
`EV_DAMAGEPLUM` emitter that stages damage and weapon payloads for cgame, the
paired `EV_AWARD` medal emitter used by the Quake Live award taxonomy, and the
small helper that increments medal counters while latching the corresponding
`EF_AWARD_*` display state.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `936` -> `943` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `843/1027` -> `850/1027` mapped functions (`82.08%` -> `82.77%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+7` curated names, `+7` corpus-overlap matches, and `+0.68` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `943/943`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| PMove jump / step-jump seam | `PM_ApplyJumpTakeoff`, `PM_CanCrouchStepJump`, and `PM_CanStepJump` |
| Domination capture / reward seam | `G_DominationRewardCaptureParticipants`, `G_DominationSelectPrimaryCapturer`, and `G_DominationCheckDefenseBonus` |
| Domination point bootstrap seam | `G_DominationPointActivate` |

This pass focused on the retail-only PMove step-jump split and the adjacent
Domination capture controller. The PMove trio remains descriptive because the
current tree expresses the behavior across `PM_CheckJump` and the
`PM_ApplyStepJump` wrapper, while the retail binary keeps the step-jump gates
and jump takeoff body as separate adjacent leaves. A later 2026-05-22 source
follow-up restored the retail `cmd.serverTime - jumpTime` delay check and the
separate crouch-step fallback after the general `PM_CanStepJump` recheck fails.
The same follow-up series confirmed that both `PM_CanStepJump` and
`PM_CheckJump` use only the compact `autoHop` slot for held-jump release bypass,
leaving `bunnyHop` as separate movement tuning rather than release-gate wiring.
A later jump-takeoff source pass rechecked qagame `0x1002E2C0` against the
HLIL velocity-mode block and moved the reconstructed source away from the
wrapper-side step-velocity add: normal chain jumps now use the retail gradient
scaler, PMF_AIR_CONTROL uses the additive chain/step branch, and ramp jumps
accumulate vertical velocity before the max clamp.
The corrective 2026-05-26 step/chain audit then split the two retail
`PM_StepSlideMove` latches: the normal step-jump latch selects
`pmove_StepJumpVelocity`, while the crouch-step fallback keeps the
`pmove_ChainJumpVelocity` addend and uses its separate latch only to suppress
ramp accumulation. PMF_AIR_CONTROL still overrides disabled `pmove_ChainJump`
mode `0`, and the offset-threshold air-control denominator plus final max clamp
are pinned with executable fixtures.
The 2026-05-27 step-move wrapper pass rechecked qagame `0x1002EFE0` against the
cgame twin and restored the remaining trace-level details in source: the
post-step down trace only clips velocity when the velocity/plane dot is
negative or within the retail `0.001` near-parallel threshold, the direct trace
from the original origin to the stepped endpoint gates `pml.stepUp`, air-step
friction, debug logging, and step-jump probes, and the projected support trace
now rejects both `startsolid` and `allsolid`.
The 2026-05-22 transport follow-up also restored `pmove_ChainJump` as an
integer jump-mode selector rather than a boolean mirror, preserving the disabled
mode `0`, gradient mode `1`, and additive mode `2` across server cvar caching,
configstring publication, and cgame prediction parsing.
The later pmove cvar registration pass walked the qagame cvar-table slab at
`0x1008F7C4..0x1008FB20` and restored the exact retail default strings plus the
four observed flag groups used by the `pmove_*` registrations:
`0x00100000`, `0x00104000`, `0x00140000`, and `0x00144000`. The source keeps
the split `g_pmove.c` owner, but the registration calls now preserve the retail
high-bit flags for air-control, physics, no-player-clip, ramp/step jump, weapon
switching, water scale, and grapple-velocity surfaces before the cached
`pmove_settings_t` payload is published.
The 2026-05-25 selected-cvar mapping sentinel added a cross-VM evidence chain
for representative movement knobs (`pmove_AirAccel`, `pmove_AirControl`,
`pmove_AirStopAccel`, `pmove_AutoHop`, `pmove_ChainJump`,
`pmove_CircleStrafeFriction`, `pmove_StrafeAccel`, `pmove_WalkAccel`,
`pmove_WalkFriction`, and `pmove_WishSpeed`). It checks retail registration
defaults/flags, factory reset defaults, refresh callback ownership, cached
`pmove_settings_t` assignments, compact and JSON cgame parsers, default shared
movement constants, active `bg_pmove.c` consumers, and the committed qagame
symbol-map prose in one test lane.
The 2026-05-25 profile/utility pmove cvar mapping sentinel then covered the
remaining movement-profile and utility fields: `pmove_AirStepFriction`,
`pmove_AirSteps`, `pmove_BunnyHop`, `pmove_CrouchSlide`,
`pmove_CrouchSlideFriction`, `pmove_CrouchSlideTime`,
`pmove_CrouchStepJump`, `pmove_DoubleJump`, `pmove_noPlayerClip`,
`pmove_StepHeight`, `pmove_StepJump`, `pmove_velocity_gh`,
`pmove_WaterSwimScale`, `pmove_WaterWadeScale`, `pmove_WeaponDropTime`, and
`pmove_WeaponRaiseTime`. The test lane ties those names through the same
retail registration/reset/refresh/cache/transport chain, then pins the active
consumers: spawn-time `PMF_CROUCH_SLIDE` / `PMF_DOUBLE_JUMP` /
`PMF_AIR_CONTROL` seeding, crouch-slide friction and timer use, no-player-clip
tracemask clearing, step/crouch-step gates, water scale and step-height globals,
grapple pull speed, weapon raise/drop timers, and the custom-settings masks.
The follow-up callback pass rechecked retail `G_RegisterCvars` at `0x10054920`,
`G_InitPublishedCvarState` at `0x100549E0`, and `G_UpdateCvars` at
`0x10054DD0`. The retail table entry layout is `vmCvar`, name, default, flags,
modification count, callback; all pmove entries except `pmove_AirControl`,
`pmove_CrouchSlide`, and `pmove_DoubleJump` have callback leaves. Source now
mirrors that callback-backed update surface and carries over the three observed
minimum-positive cache clamps for `pmove_velocity_gh`,
`pmove_JumpVelocityTimeThreshold`, and
`pmove_JumpVelocityTimeThresholdOffset`.
The latest grapple-speed cross-check followed `PM_GrappleMove` at `0x1002FF20`
back to cached global `data_1008FEC0`, which `G_InitPublishedCvarState` fills
from the `pmove_velocity_gh` vmCvar with the same `0.001` lower bound. This is
separate from retail `g_velocity_gh`, whose cvar-table default is `1800` and
which feeds the hook projectile speed/custom-settings branch rather than the
pmove pull velocity.
The follow-up full-name sweep also classified the legacy fixed-timestep
surfaces separately from the Quake Live pmove tuning slab: `pmove_fixed` and
`pmove_msec` are not present in the recovered `0x1008F7C4..0x1008FB20`
factory-managed table. Source keeps their GPL-era game/cgame registrations
(`0` and `8`, with server-side `CVAR_SYSTEMINFO`), clamps `pmove_msec` into the
retail-compatible `8..33` range before prediction, and passes the resulting
fields into the shared `Pmove` loop where fixed moves chunk by `pmove_msec`
instead of the normal 66 ms cap.
The same pmove audit round added executable fixtures for the adjacent 3D leaves:
`PM_CheckWaterJump` now has source-backed probes for the two-deep water,
solid-lip, and clearance gates; `PM_WaterMove` pins the idle `-60` sink fallback;
and `PM_CheckLadder` / `PM_LadderMove` pin the `MASK_PLAYERSOLID` ladder trace,
`SURF_LADDER` latch, and `0.66 * speed` vertical clamp.
A later dispatcher-tail fixture rechecked `PM_Weapon`, `PM_Animate`, and
`PmoveSingle` tail ordering. Source stayed unchanged, while executable coverage
now pins `PM_Animate` gesture priority, `EV_TAUNT` emission, voice-command
priority order, 600 ms voice timers, and the active-torso-timer suppression
gate.
The following `PM_TorsoAnimation` pass rechecked qagame `0x1002DB80` and cgame
`0x10002050`, then added executable coverage for the ready gauntlet
`TORSO_STAND2` branch, default ready `TORSO_STAND` branch, torso-timer no-op,
non-ready weaponstate return, and inherited `PM_DEAD` animation-start
suppression.
The next timer pass rechecked qagame `0x10031E30` and cgame `0x10006300`, with
fixtures now pinning `PM_DropTimers` partial/expired misc-time behavior,
`PMF_ALL_TIMES` clearing, independent legs/torso timer clamps, and the
crouch-slide ground-plane decay gate.
The queue-helper pass rechecked qagame `0x1002DAF0` / `0x1002DB20` and cgame
`0x10001FC0` / `0x10001FF0`, with fixtures now pinning `PM_AddEvent` two-slot
event wrapping with zero parms and `PM_AddTouchEnt` world-skip,
duplicate-suppression, and `MAXTOUCH` cap behavior.
The following animation-helper pass rechecked qagame `0x1002DB60`,
`0x1002DBE0`, and `0x1002DC20` against the cgame twins at `0x10002030`,
`0x100020B0`, and `0x100020F0`. Fixtures now pin torso toggle-bit writes,
`PM_DEAD` suppression, legs/torso timer no-ops, current-animation no-ops, and
the forced-legs timer clear before the live/dead start gate.
The command/vector pass rechecked qagame `0x1002DC50`, `0x1002DEF0`,
`0x1002E070`, and `0x1002E1F0` against the cgame twins at `0x10002120`,
`0x100023C0`, `0x10002540`, and `0x100026C0`. Fixtures now pin
`PM_ClipVelocity` overbounce branches, `PM_Accelerate` clamping and overspeed
no-op behavior, `PM_CmdScale` zero/axial/2D/3D scaling, and
`PM_SetMovementDir`'s eight-way ring plus idle side-strafe snaps.

The Domination batch is likewise retail-only boundary recovery. HLIL preserves
the delayed point activation callback queued by `SP_team_dom_point`, the helper
that chooses the primary capturing client from the active participant lists, the
capture/assist reward fan-out, and the nearby defense-bonus checker called from
the team frag-reward path.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `932` -> `936` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `839/1027` -> `843/1027` mapped functions (`81.69%` -> `82.08%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+4` curated names, `+4` corpus-overlap matches, and `+0.39` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `936/936`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Spawn/filter parsing seam | `G_ParseDisableLoadoutString` and `G_ParseSpawnGametypeMask` |
| Shared `bg_` / item helpers | `BG_IsTeamFlagItem` |
| Combat spectator-warning seam | `G_WarnIfSpectatorShot` |

This pass focused on the remaining high-confidence helpers sitting between
`SP_worldspawn`, the item spawn filters, and the splash-damage trace seam. The
strongest exact recovery is `G_ParseDisableLoadoutString`, which the committed
source still exposes verbatim in `g_spawn.c`; the paired gametype parser and
flag-item predicate remain descriptive retail-only names because the current
tree keeps the same behavior inlined or expressed through different helper
boundaries.

`G_WarnIfSpectatorShot` is also intentionally descriptive rather than source
exact. HLIL shows a tiny standalone leaf that resolves an entity slot, checks
for a spectator client, and emits the preserved `A spectator has been shot!`
message from the splash/trace damage seam. The current GPL-derived tree keeps
that text inline under `G_Damage` instead of as a reusable helper.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `923` -> `932` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `830/1027` -> `839/1027` mapped functions (`80.82%` -> `81.69%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+9` curated names, `+9` corpus-overlap matches, and `+0.88` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: this was a mapping-only pass, so no source-side parity code changed; the embedded `qagame.json` stats block is now realigned to `932/932`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| `g_cmds` and client-info seam | `Cmd_Kill_f` and `ClientNameAvailable` |
| Shared `bg_` / gameplay helpers | `BG_WeaponName`, `vtos`, `PM_TorsoAnimation`, and `G_DistanceToEntityBounds` |
| Freeze / Domination round helpers | `G_FreezeCheckExitRules`, `G_FreezeFindThawHelperByClientNum`, and `G_UpdateDominationPointCountConfigstrings` |

This pass closes a thin but high-confidence slab of pure helpers that the
retail binary keeps as standalone bodies even though the current source tree
either inlines the same behavior or has not split it back out yet. The new
names cover the missing `kill` command leaf in the `ClientCommand` ladder, the
client-name deconfliction helper under `ClientUserinfoChanged`, the shared
weapon-name / vector-print / torso-idle utilities, the splash-distance helper
under `G_RadiusDamage`, and two Freeze / one Domination controller sidecars.

The Freeze / Domination promotions are descriptive retail-only names rather
than exact source exports. HLIL and the committed corpus agree on the owning
controller paths and side effects, but the current GPL-derived tree does not
yet expose those helpers as identical standalone functions.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv` and `180` unique decompiled entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `918` -> `923` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `825/1027` -> `830/1027` mapped functions (`80.33%` -> `80.82%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+5` curated names, `+5` corpus-overlap matches, and `+0.49` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `93` because every promoted helper in this pass already has a standalone row in the committed `functions.csv` export.
- Note: the embedded `qagame.json` stats block is now realigned to the live curated total of `923/923`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Hidden lag-hax / rewind seam | `G_InitLagHaxHistory`, `G_StoreHistory`, `G_TimeShiftClient`, `G_TimeShiftAllClients`, and `G_UnTimeShiftAllClients` |
| Source-side parity | `src/code/game/g_main.c` now registers the hidden `g_lagHaxHistory=4` and `g_lagHaxMs=80` cvars, `src/code/game/g_active.c` reconstructs the retail rewind history ring and per-frame store/rewind flow, `src/code/game/g_weapon.c` brackets the retail hitscan weapon set with rewind restore calls, and `src/code/game/g_client.c` plus `src/code/game/g_misc.c` invalidate the current history head on spawn, disconnect, and teleport transitions |

This pass closes the hidden Quake Live lag-hax seam that sits between
`ClientEndFrame`, the hitscan weapon dispatcher, and the client collision
history used by rewind traces. The recovered set covers the per-client ring
allocator, the frame-tail history recorder, the single-client interpolating
rewind helper, the outer per-shot rewind pass, and the matching restore pass.

On the source side, the live code now follows the observed retail behavior more
closely. `ClientEndFrame` records the latest collision history, `FireWeapon`
rewinds and restores the retail hitscan set (`MG`, `HMG`, `SG`, `LG`, `RG`,
and `CG`) using the hidden `g_lagHaxHistory` / `g_lagHaxMs` cvars, and the
spawn/teleport/disconnect transitions now invalidate the current history head so
stale bounds are not reused across those state changes.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `893` -> `906` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `807/1027` -> `820/1027` mapped functions (`78.58%` -> `79.84%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `180/180` mapped functions (`100.00%`).
- Delta from this pass: `+13` curated names, `+13` corpus-overlap matches, and `+1.27` percentage points on full-corpus parity.
- Note: curated overhang stays flat at `86` because every recovered helper in this pass already has a standalone row in the committed `functions.csv` export.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Combat scoring and death-drop seam | `ScorePlum`, `AddScore`, `TossClientItems`, `RaySphereIntersections`, `G_InvulnerabilityEffect`, and `CheckArmor` |
| Shared `q_math` helper seam | `DirToByte`, `vectoangles`, `ProjectPointOnPlane`, `RadiusFromBounds`, `VectorNormalize`, `VectorNormalize2`, and `AngleVectors` |
| Source-side parity | `src/code/game/g_combat.c` now restores retail raw score application in `AddScore` and emits score plums unconditionally through `ScorePlum` instead of routing both behaviors through the non-retail `scoreModifier` / `g_damagePlums` gates |

This pass closes the next exact-name slab in the shared combat utilities and
the reused `q_math` layer. On the gameplay side, the recovered names cover the
score-plum emitter, the core score accumulator, the death-time item/powerup
drop helper, and the invulnerability collision/armor helpers that sit on the
main `G_Damage` path. On the shared-library side, the new names recover the
compact direction encoder plus the vector/angle projection and normalization
helpers that the gameplay, bot, and missile code all reuse.

On the source side, `src/code/game/g_combat.c` now matches the observed retail
scoring path more closely. `ScorePlum` no longer hides behind the built-source
`g_damagePlums` toggle, and `AddScore` now applies the incoming raw score delta
directly instead of running it through the non-retail per-client
`scoreModifier` scaler before the plum, team-score update, and rank refresh.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `756` -> `764` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `680/1027` -> `687/1027` mapped functions (`66.21%` -> `66.89%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `164/180` mapped functions (`91.11%`).
- Delta from this pass: `+8` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and `+0` matches on the top-decompiled slice.
- Note: curated overhang rises `76` -> `77` because retail keeps `BG_CanGrabArmorItem` as a standalone helper at `0x1002ce00`, but that entry is still absent from the committed `functions.csv` corpus.

## Newly Mapped In The Earlier Pass

| Area | Recovered functions |
| --- | --- |
| `bg_misc` item lookup and touch seam | `BG_FindItemByTypeAndTag`, `BG_FindItemForPowerup`, and `BG_PlayerTouchesItem` |
| Retail pickup and trajectory helpers | `BG_CanGrabArmorItem`, `BG_CanGrabWeaponItem`, `BG_EvaluateTrajectory`, `BG_EvaluateTrajectoryDelta`, and `BG_PlayerStateToEntityState` |
| Source-side pickup parity | `src/code/game/bg_misc.c` now mirrors the retail `BG_CanGrabWeaponItem` early rejection when `ps->pm_flags & PMF_IRONSIGHTS` is set |

This pass closes the next high-yield `bg_misc` seam around item lookup, item
touch tests, pickup gating, and the shared movement-state projection helpers.
The recovered names cover the standalone retail powerup lookup path, the
touch-bounds helper used by client prediction, the compiler-split armor and
weapon pickup gates, the trajectory evaluators, and the playerstate-to-
entitystate bridge used throughout both gameplay and bot logic. On the source
side, `src/code/game/bg_misc.c` now follows the observed retail weapon-pickup
path more closely by rejecting pickups while the ironsights bit is active.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `751` -> `756` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `675/1027` -> `680/1027` mapped functions (`65.72%` -> `66.21%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: unchanged at `164/180` mapped functions (`91.11%`).
- Delta from this pass: `+5` curated names, `+5` corpus-overlap matches, `+0.49` percentage points on full-corpus parity, and `+0` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `76` because every promoted helper in this batch is present in the committed `functions.csv` corpus.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Early `g_team` pure/helper seam | `TeamName`, `TeamColorString`, `OtherTeam`, `Team_ForceGesture`, and `Team_CheckDroppedItem` |
| Source-side team visibility/color parity | `src/code/game/g_team.c` now returns retail `^7` for non-red/non-blue `TeamColorString` cases and no longer gates Red Rover infected visibility on `level.roundState` |

This pass closes the next exact `g_team` helper slab that the retail binary
keeps as standalone bodies instead of inlining away. The recovered names cover
the classic team-string helpers, the red/blue swap helper, the dropped-flag
status updater, and the force-gesture broadcaster used by the team objective
announcements. On the source side, `src/code/game/g_team.c` now follows the
observed retail behavior more closely by treating every non-red/non-blue team
as white in `TeamColorString` and by enabling the Red Rover infected visibility
path whenever the gametype is `GT_RED_ROVER` and `g_rrInfected` is non-zero,
without the extra GPL-era `ROUNDSTATE_ACTIVE` gate.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `720` -> `727` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `652/1027` -> `659/1027` mapped functions (`63.49%` -> `64.17%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `160/180` -> `162/180` mapped functions (`88.89%` -> `90.00%`).
- Delta from this pass: `+7` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; the top-slice gains are `BotFindInstaGibTarget` and `BotPublishDebugInfoString`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Instagib target-goal seam | `BotFindInstaGibTarget`, `BotRefreshInstaGibTargetGoal`, and `BotGetInstaGibTargetGoal` |
| `ai_main` retail telemetry | `BotPublishDebugInfoString`, `BotCanSpawnTourPoint`, `BotUpdateItemDelayTime`, and `BotAppendDynamicSkillSample` |
| Source-side frame correction | `BotAIStartFrame` now matches retail more closely by keeping `bot_report` updated without running the stale GPL `BotUpdateInfoConfigStrings()` / `CS_BOTINFO` publish loop |

This pass closes the next retail-only `ai_main` support seam around the
instagib tutorial node, the selected-bot debug publisher, and the training
tail that sits after `BotAIStartFrame`'s main bot-think loop. The instagib
cluster now has coherent target-finding and goal-refresh names, while the
later `ai_main` helpers cover the exact `bot_itemDelayTime` cvar writer, the
dynamic-skill sample recorder, and the tour-point spawn gate used by the
tutorial flow. On the source side, `src/code/game/ai_main.c` now drops the
stale GPL-era `bot_report` info-configstring publish branch that no longer
appears in the retail `BotAIStartFrame` body.

Follow-up on 2026-06-11: the instagib cluster is now source-backed through
`ai_dmnet.c::AIEnter_InstaGib`, `ai_dmnet.c::AINode_InstaGib`, and the
`BotDeathmatchAI` retail instagib-mode callsite. The target-goal helpers remain
the chooser/cache seam, while the node body now owns the transient target goal,
botlib movement path, and `LTG_INSTAGIB` state.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `594` -> `607` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `526/1027` -> `539/1027` mapped functions (`51.22%` -> `52.48%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `149/180` -> `152/180` mapped functions (`82.78%` -> `84.44%`).
- Delta from this pass: `+13` curated names, `+13` corpus-overlap matches, `+1.27` percentage points on full-corpus parity, and `+3` matches on the top-decompiled slice.
- Note: curated overhang stays flat at `68` because every promoted helper in this batch is present in the committed `functions.csv` corpus; only `BotUpdateInventory`, `BotUseKamikaze`, and `BotUseInvulnerability` land inside `decompile_top_functions.c`.

## Newly Mapped In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Inventory and aggression seam | `BotUpdateInventory`, `BotUpdateBattleInventory`, `BotAggression`, `BotCanAndWantsToRocketJump`, and `BotHasPersistantPowerupAndWeapon` |
| Active battle item use | `BotUseKamikaze`, `BotUseInvulnerability`, `BotBattleUseItems`, and `BotIsObserver` |
| Camping and powerup flow | `BotGoCamp`, `BotWantsToCamp`, `BotDontAvoid`, and `BotGoForPowerups` |

This pass closes the next coherent `ai_dmq3.c` utility seam around bot
inventory refresh, consumable use, and long-term camp or powerup decisions. The
recovered set covers the live inventory snapshot, enemy-distance bookkeeping,
aggression scoring, kamikaze and invulnerability activation, and the full camp
spot plus avoid-goal helpers that feed higher-level long-term goal selection.

## Previous Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `374` -> `377` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `342/1027` -> `345/1027` mapped functions (`33.30%` -> `33.59%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `108/180` -> `110/180` mapped functions (`60.00%` -> `61.11%`).
- Delta from this pass: `+3` curated names, `+3` corpus-overlap matches, `+0.29` percentage points on full-corpus parity, and `+2` matches on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Reconstructed In The Previous Pass

| Area | Recovered functions |
| --- | --- |
| Spawn ranking seam | retail-only `G_SelectRankedSpawnPoint`, retail-only `G_SelectClientSpawnPoint`, and retail-only `Team_SelectDominationSpawnPoint` |
| Source-side spawn reconstruction | Domination now selects owned point-linked respawns instead of piggybacking entirely on the CTF path, and `ClientSpawn` now routes through the recovered retail helper split instead of keeping all gametype branching inline |

This pass closes the next high-yield qagame spawn-selection seam around the
ClientSpawn path. The remaining hidden debug-command tail still needs a cleaner
body-to-dispatch match before promotion, but the broader spawn-selection band
is now mapped through the Domination-specific path, the shared ranked picker,
and the ClientSpawn-side wrapper.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Curated symbol-map totals: `362` -> `370` matched functions, with string coverage unchanged at `102/102`.
- Corpus-overlap parity: `331/1027` -> `338/1027` mapped functions (`32.23%` -> `32.91%`) when measured against the committed `functions.csv` retail corpus.
- Top decompiled slice: `105/180` -> `105/180` mapped functions (`58.33%` -> `58.33%`).
- Delta from this pass: `+8` curated names, `+7` corpus-overlap matches, `+0.68` percentage points on full-corpus parity, and no change on the top-decompiled slice.
- Note: `32` curated helper names currently sit outside `functions.csv`, so curated symbol-map totals are tracked separately from corpus-overlap parity.

## Newly Mapped In The Earlier Pass

| Area | Recovered functions |
| --- | --- |
| Direct command surface | retail-only `Cmd_SetMatchTime_f` |
| Auto-record naming | retail-only `G_SanitizeFilenameToken`, retail-only `G_BuildAutoRecordBasename` |
| Match media automation | `g_main.c::G_StopAutoRecord`, `g_main.c::G_StartAutoRecordForClient`, `g_main.c::G_CheckAutoRecord` |
| Timeout state publication | retail-only `G_UpdateTimeoutConfigStrings` |
| Race respawn flow | retail-only `G_RaceResetClientAndSpawn` |

The remaining highest-yield unmapped seams now skew more toward the hidden
`markstate` / `diffstate` / `dumpentities` / `printentitystates` debug band
and the larger gameplay bootstrap and round-support bodies that still sit
outside the current curated map.

## Prior Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `147` curated mapped functions, `33/180` decompiled-top functions (`18.33%`).
- After this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- Delta from this pass: `+22` curated mapped functions and `+12.23` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that round widened function naming coverage rather than the string ledger.

## Previously Mapped In The Prior Sweep

| Area | Recovered functions |
| --- | --- |
| Bot chat and state nodes | `BotChatTest`, `BotGetLongTermGoal`, `AINode_Seek_NBG`, `AINode_Seek_LTG`, `AINode_Battle_Fight`, `AINode_Battle_Chase`, `AINode_Battle_Retreat`, `AINode_Battle_NBG` |
| Bot bootstrap and team control | `BotAI`, `BotAISetupClient`, `BotInitLibrary`, `BotSetupDeathmatchAI`, `BotTeamAI` |
| Bot spawn and writable gameplay helpers | `G_AddRandomBot`, `G_AddBot`, `RegisterItem`, `G_Say`, `Cmd_SetViewpos_f` |
| Gameplay utility and objective flow | `G_DroppedPowerupRunFrame`, `G_TryPushingEntity`, `Team_FragBonuses`, `Team_TouchOurFlag` |

The highest-yield remaining seams after that sweep skewed more toward
tutorial-specific bot flows, ranking/stat publishers, and other retail-only
utility helpers outside that widened control surface.

## Earlier Coverage Update

- Reference totals: `1027` functions in `functions.csv`, `180` entries in `decompile_top_functions.c`.
- Before this pass: `169` curated mapped functions, `55/180` decompiled-top functions (`30.56%`).
- After this pass: `185` curated mapped functions, `71/180` decompiled-top functions (`39.44%`).
- Delta from this pass: `+16` curated mapped functions and `+8.89` percentage points on the top-decompiled slice.
- Curated string coverage was unchanged at `102/102`; that pass widened function naming coverage rather than the string ledger.
## Key Mappings

| Retail address | Recovered name | Closest source analogue | Evidence summary | Confidence |
| --- | --- | --- | --- | --- |
| `0x10023400` | `BotAIStartFrame` | `ai_main.c::BotAIStartFrame` | Native dispatch-table slot plus the `memorydump` / `bot_memorydump` bot-debug cvars and the per-bot frame/routing update loop match the source bot frame driver. | High |
| `0x100327D0` | `G_PrintAccessListPage` | `g_main.c::G_PrintAccessListPage` | Access-list page printer anchored by `Access List: Page %i of %i`, the `=============================` separator, 20-entry pages, `%llu %s %s` rows, and the `TEMP` / `PERM` mode labels. | High |
| `0x10033800` | `P_DamageFeedback` | `g_active.c::P_DamageFeedback` | Aggregates `damage_blood` and `damage_armor`, emits EV_PAIN and damage yaw/pitch, clears only the armor/blood totals, and confirms the retail feedback record has no `damage_knockback` slot. | High |
| `0x10033950` | `P_WorldEffects` | `g_active.c::P_WorldEffects` | Anchored by `sound/player/gurp1.wav` / `sound/player/gurp2.wav` plus the drowning, battlesuit, lava, and slime control flow. | High |
| `0x10033B20` | `G_SetClientSound` | `g_active.c::G_SetClientSound` | Selects the proxmine ticking loop sound or the lava/slime fry loop on the outgoing playerstate, matching the source helper. | High |
| `0x10033B80` | `ClientImpacts` | `g_active.c::ClientImpacts` | Walks unique pmove touchents and dispatches bot self-touch plus touched-entity callbacks exactly like the source post-pmove impact helper. | High |
| `0x10033C00` | `G_TouchTriggers` | `g_active.c::G_TouchTriggers` | Uses the `40,40,52` trigger range box, spectator teleporter gating, ET_ITEM proximity checks, and jump-pad frame reset logic from the source trigger-touch path. | High |
| `0x10033E30` | `SpectatorThink` | `g_active.c::SpectatorThink` | Sets `PM_SPECTATOR` with the retail `480` spectator speed, unlinks linked spectators before `pmove`, touches triggers from the moved spectator origin, handles attack-edge follow cycling through the inner `FollowCycle` worker, and uses the later `BUTTON_ANY` edge to drop follow state. | High |
| `0x10033FD0` | `ClientInactivityTimer` | `g_active.c::ClientInactivityTimer` | Anchored by `Dropped due to inactivity`, the inactivity warning centerprint, and the `client:%i inactivity:%i` debug line. | High |
| `0x100341E0` | `G_CheckClientFlood` | Retail-only descriptive helper adjacent to `g_active.c::ClientThink_real` | Reads the client `floodCount` / `floodLastTime` state, decays it against the retail flood-protection cvars, and drops the offender with `Dropped for flooding the server` once the limit is exceeded. | High |
| `0x10034260` | `G_RunFactoryHealthRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame health regen sidecar tailcalled from `ClientTimerActions`; it waits out the last-damage delay, accumulates the configured regen tick interval, stops once health reaches the target, and applies whole-point health increases to the entity. | High |
| `0x100342F0` | `G_RunFactoryArmorRegen` | Retail-only split of `g_active.c::G_RunFactoryRegen` | Per-frame armor regen sidecar tailcalled after the health helper; it waits out the armor delay, honors the `regenArmorAfterHealth` gate, accumulates the regen tick interval, and applies whole-point armor increases to `ps.stats[STAT_ARMOR]`. | High |
| `0x100343E0` | `ClientTimerActions` | `g_active.c::ClientTimerActions` | Accumulates `timeResidual`, applies once-per-second regeneration and armor decay, and emits the regen event through adjacent Quake Live subhelpers in the same place the source calls `ClientTimerActions`. | High |
| `0x10034860` | `ClientEvents` | `g_active.c::ClientEvents` | Walks the recent playerstate event ring, applies fall damage, fires weapons, and handles teleporter, medkit, kamikaze, portal, invulnerability, and Harvester skull-drop item-use side effects exactly where the source server event switch sits. | High |
| `0x10034B50` | `StuckInOtherClient` | `g_active.c::StuckInOtherClient` | Scans live client entities for AABB overlap against the candidate player's expanded bounds and returns true once invulnerability expansion would still intersect another client. | High |
| `0x10034C00` | `SendPendingPredictableEvents` | `g_active.c::SendPendingPredictableEvents` | Creates temporary ET_EVENTS entities from pending playerstate events, clears/restores `externalEvent`, and targets all clients except the originator. | High |
| `0x10034C90` | `ClientThink_real` | `g_active.c::ClientThink_real` | Driven by the outer `ClientThink` export plus command-time clamping, spectator/inactivity gating, pmove, event dispatch, trigger touch, client impacts, respawn, and timer actions. | High |
| `0x10035410` | `ClientThink` | `g_active.c::ClientThink` | Native dispatch-table slot plus `trap_GetUsercmd`, the `lastCmdTime` write, and the bot-gated tailcall into the deeper think path align with the source export wrapper. | High |
| `0x10035470` | `SpectatorClientEndFrame` | `g_active.c::SpectatorClientEndFrame` | Resolves `follow1` / `follow2`, mirrors connected non-`PM_SPECTATOR` player targets while forcing the copied playerstate back to `PM_SPECTATOR | PMF_FOLLOW`, active-team cycles stale explicit targets, and otherwise falls back through `StopFollowing` before scoreboard flag toggling. | High |
| `0x10035600` | `ClientEndFrame` | `g_active.c::ClientEndFrame` | Spectator short-circuit into `SpectatorClientEndFrame`, expired powerup cleanup, world/damage end-frame helpers, EF_CONNECTION handling, and final entity-state sync match the source end-frame path. | High |
| `0x10035960` | `G_CAADRespawnAsSpectator` | Retail-only shared Clan Arena / Attack and Defend respawn helper | Reached from the dead-client respawn gate once those modes push a player back into spectator follow; it copies the corpse into the body queue, pre-seeds `PM_SPECTATOR` before `ClientSpawn`, counts active players by team, and only calls the shared `FollowCycle` worker when both teams still have live players. | High |
| `0x100359E0` | `G_ADShouldTimeoutActiveRound` | Retail-only Attack and Defend timeout helper | Returns true once both sides still have active players, no objective winner is already latched, and the active-round elapsed time has reached `roundtimelimit`. | High |
| `0x10035780` | `G_ADResolveRoundState` | Retail-only Attack and Defend controller helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the current A/D round-state latch used by damage, objective, and HUD callers. | High |
| `0x100357D0` | `G_ADHandleDamageScore` | Retail-only Attack and Defend damage helper | Reached from the main damage path; it applies the A/D self/team-damage suppression flags, resolves pending round-state work, and converts active-phase enemy damage into score once the accumulated threshold reaches 100. | High |
| `0x10035A20` | `G_ADCheckExitRules` | Retail-only Attack and Defend exit helper | Tie-aware A/D limit checker covering timelimit, side-specific scorelimit, and late mercylimit, including the retail overtime accumulator in the mercy window and the matching print/log side effects. | High |
| `0x10035B70` | `AD_RoundStateTransition` | Retail-only Attack and Defend round-state controller | Anchored by `AD_RoundStateTransition: invalid state`; it updates the A/D match-state configstrings, respawns or releases participants, settles round winners, rotates turns, and schedules the next countdown/restart transition. | High |
| `0x10036300` | `G_ADNotifyLastAlivePlayer` | Retail-only Attack and Defend round alert helper | Services deferred `AD_RoundStateTransition` work, counts live players by team during the active round, and when the queried side is down to one survivor triggers the shared last-alive notification path. | High |
| `0x100363E0` | `G_ADResolveAttackingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently attacking side during the active A/D phase. | High |
| `0x10036440` | `G_ADResolveDefendingTeam` | Retail-only Attack and Defend side helper | Resolves expired deferred `AD_RoundStateTransition` work and returns the currently defending side; the defense-award path calls it directly before incrementing `DEFENSE` credit. | High |
| `0x100364A0` | `G_ADResetScoreHistory` | Retail-only Attack and Defend scoreboard helper | Clears the retained A/D round-delta history and publishes the baseline `scores_ad` payload with current team totals and empty history slots. | High |
| `0x100365F0` | `G_ADUpdateScoreHistory` | Retail-only Attack and Defend scoreboard helper | Records the latest per-turn A/D score delta into the 20-entry circular history, rebuilds the ordered history window, and republishes `scores_ad`. | High |
| `0x100367C0` | `G_ParseInfos` | `g_bot.c::G_ParseInfos` | Exact info-block parser that requires leading `{` tokens, copies each parsed info string into the output table, and emits the preserved malformed-file diagnostics. | High |
| `0x100378E0` | `G_AddTrainerBot` | Retail-only training bootstrap helper | Enqueues the fixed `Trainer` bot through `G_AddBot` with a 5000 ms delay, then issues the usual `loaddeferred` media warmup command. | High |
| `0x10037F80` | `G_CAResolveRoundState` | Retail-only Clan Arena controller helper | Resolves expired deferred `CA_RoundStateTransition` work and returns the current Clan Arena round-state latch used by HUD and end-frame callers. | High |
| `0x10037FD0` | `G_CAHandleDamageScore` | Retail-only Clan Arena damage helper | Reached from the main damage path; it applies the Clan Arena self/team-damage suppression flags, resolves pending CA round-state work, and during the live round converts damage dealt into the retail 100-point score buckets. | High |
| `0x10038160` | `G_CAADResetClientForRound` | Retail-only shared Clan Arena / Attack and Defend round helper | Reused from both `ClientBegin` and the delayed respawn path for GT_CLAN_ARENA and GT_ATTACK_DEFEND; it respawns immediately in the live release state, respawns into the holding state during the pre-release countdown, and otherwise falls back to the spectator-follow reset path used after round loss. | High |
| `0x100389F0` | `G_CANotifyLastAlivePlayer` | Retail-only Clan Arena round alert helper | Services deferred `CA_RoundStateTransition` work, counts live players by team during the active round, and triggers the shared last-alive notification path when the queried side is down to one survivor. | High |
| `0x10038B60` | `Team_SelectDominationSpawnPoint` | Retail-only Domination spawn helper / `g_team.c` analogue | Reached from the ClientSpawn-side spawn wrapper only for active GT_DOMINATION respawns; it walks `team_dom_point` entities, collects linked `info_player_deathmatch` targets for the owning team, ranks them against live players, and writes the chosen origin/angles. | High |
| `0x10039080` | `G_SelectRankedSpawnPoint` | Retail-only shared spawn helper spanning `g_client.c::SelectRandomFurthestSpawnPoint` and `g_team.c::SelectCTFSpawnPoint` | Anchored by the `info_player_deathmatch`, `team_CTF_redspawn`, `team_CTF_bluespawn`, `team_CTF_redplayer`, and `team_CTF_blueplayer` classnames plus the `FindIntermissionPoint` fallback; it rejects spawnflags bit 2, admits bit-1 neutral initial starts, retries team begin classes as same-team regular spawns, filters telefragging candidates, ranks against live players, and picks from the best-ranked subset. | High |
| `0x10039730` | `G_SelectClientSpawnPoint` | Retail-only ClientSpawn-side spawn wrapper | Called directly from `ClientSpawn` before the respawn bootstrap continues; it chooses between domination-linked spawns, team/base spawn classes, and the initial non-team spawn path, then falls back through the shared ranked spawn picker and its begin-mode retry. | High |
| `0x1003A270` | `G_UpdateTournamentQueuePositions` | Retail-only duel queue helper | Sorts eligible waiting spectators by the stored queue timestamp, assigns one-based `pq` queue positions, and marks changed entries dirty for the follow-on userinfo republish pass. | High |
| `0x1003A450` | `ClientUserinfoChanged` | `g_client.c::ClientUserinfoChanged` | Native dispatch-table slot plus `ClientUserinfoChanged: %i %s` log string and matching configstring rebuild flow. | High |
| `0x1003AC10` | `ClientConnect` | `g_client.c::ClientConnect` | `ClientConnect: %i` log string, bot masking, session init/read, and platform auth checks match the source connect routine. | High |
| `0x1003B030` | `ClientBegin` | `g_client.c::ClientBegin` | `ClientBegin: %i` log string and the post-connect spawn/bootstrap path align with the source begin routine. | High |
| `0x1003B5A0` | `G_FinalizeSpawnLoadout` | Retail-only spawn/loadout helper | Post-`ClientSpawn` finalizer that honors `selected_spawn_weapon`, parses the configured spawn-grant tokens, seeds the starting ammo and weapon masks through the deeper helper at `0x1003B2A0`, and applies the remaining intermission and live-weapon cleanup for the spawned client. | High |
| `0x1003BC30` | `ClientSpawn` | `g_client.c::ClientSpawn` | Full retail spawn/bootstrap boundary that selects active or spectator spawn placement from the pre-existing `PM_SPECTATOR` state, preserves the respawn-persistent client/session state, rebuilds the playerstate/entity defaults for the new life, and then tails into the deeper post-spawn finalization helper. | High |
| `0x1003C7E0` | `ClientDisconnect` | `g_client.c::ClientDisconnect` | Present in `functions.csv`, referenced by the native export table, and anchored by `ClientDisconnect: %i`. | High |
| `0x1003CBF0` | `DeathmatchScoreboardMessage` | `g_cmds.c::DeathmatchScoreboardMessage` | Retail scoreboard sender that dispatches through per-gametype builders, falls back to a compact `smscores` serializer when needed, sends the resulting payload to one client, and during intermission fans into the extra mode-specific stat publishers. | High |
| `0x1003CD70` | `G_BuildCompactScoreboardMessage` | Retail-only compact scoreboard helper | Emits the reduced `smscores` payload that `DeathmatchScoreboardMessage` uses when the richer per-mode payload would exceed the server-command limit or the compact-scoreboard gate is active. | High |
| `0x1003CEC0` | `G_BuildObeliskScoreboardMessage` | Retail-only Overload scoreboard helper | GT_OBELISK/default scoreboard serializer that emits the generic `scores` payload with the extra objective columns preserved in the retail build. | High |
| `0x1003D090` | `G_BuildFFAScoreboardMessage` | Retail-only FFA scoreboard helper | Emits `scores_ffa` with the expanded Quake Live FFA per-client stat block. | High |
| `0x1003D2B0` | `G_BuildDuelScoreboardMessage` | Retail-only duel scoreboard helper | Caches the lower and higher duel client numbers into the `level` tail, builds the viewer-facing weapon/timing summaries, and emits the appropriate `scores_duel` payload shape for one or two players. | High |
| `0x1003DBB0` | `G_BuildRaceScoreboardMessage` | Retail-only Race scoreboard helper / `g_race.c` analogue | Emits the `scores_race` payload with the sorted racer list and timing columns. | High |
| `0x1003DD20` | `G_BuildTeamScoreboardMessage` | Retail-only GT_TEAM scoreboard helper | Emits `scores_tdm` with the red/blue team totals plus the retail TDM per-client stat block. | High |
| `0x1003E1B0` | `G_SendTDMStatsMessage` | Retail-only postgame stats helper | Intermission-only `tdmstats` publisher reused by the TDM and Freeze scoreboard families. | High |
| `0x1003E300` | `G_BuildClanArenaScoreboardMessage` | Retail-only Clan Arena scoreboard helper | Emits the `scores_ca` payload with the retail CA per-client stat block. | High |
| `0x1003E510` | `G_SendCAStatsMessage` | Retail-only postgame stats helper | Intermission-only `castats` publisher for the Clan Arena scoreboard family, using the same classic item-tag weapon order consumed by cgame. | High |
| `0x1003E6D0` | `G_BuildCTFStyleScoreboardMessage` | Retail-only shared CTF-style scoreboard helper | Shared serializer for CTF, One Flag, Harvester, Domination, and Attack and Defend. It emits the `scores_ctf` payload and hides the opposing-team detail block from live viewers when the retail policy requires it. | High |
| `0x1003EC40` | `G_SendCTFStatsMessage` | Retail-only postgame stats helper | Intermission-only `ctfstats` publisher reused by the CTF-style scoreboard families. | High |
| `0x1003EDA0` | `G_BuildFreezeScoreboardMessage` | Retail-only Freeze scoreboard helper | Emits the `scores_ft` payload with the Freeze-specific per-client stat block. | High |
| `0x1003F260` | `G_BuildRedRoverScoreboardMessage` | Retail-only Red Rover scoreboard helper | Emits the `scores_rr` payload with the Red Rover per-client stat block. | High |
| `0x100400F0` | `Cmd_TeamTask_f` | `g_cmds.c::Cmd_TeamTask_f` | Exact `Argc == 2` / `teamtask` userinfo rewrite flow from the stock command handler, ending in `ClientUserinfoChanged`. | High |
| `0x10040440` | `G_ApplyTeamChange` | `g_cmds.c::G_ApplyTeamChange` | Recovered inner `SetTeam` executor that handles death/body-queue teardown through `player_die(..., MOD_SWITCHTEAM)`, session mutation, spectator item sync, leadership repair, per-opponent revenge counter cleanup, userinfo publication, `ClientBegin`, and the rank switch-team event. | High |
| `0x100406D0` | `SetTeam` | `g_cmds.c::SetTeam` | Outer team-change parser that handles `follow1`, `follow2`, spectator/team requests, duel-only spectate enforcement, and then forwards into the deeper retail execution helper. | High |
| `0x10040D10` | `StopFollowing` | `g_cmds.c::StopFollowing` | Restores the caller's persisted team, forces `PM_SPECTATOR`, clears `PMF_FOLLOW`, enters `SPECTATOR_FREE`, resets `spectatorClient` and `ps.clientNum` to self, and unlinks if still linked. | High |
| `0x10040F30` | `Cmd_Follow_f` | `g_cmds.c::Cmd_Follow_f` | Resolves argument 1 through `ClientNumberFromString`, preserves the current followed flag carrier on the cgame `"pw"` suffix, rejects self and `PM_SPECTATOR` targets, promotes non-spectator callers through `SetTeam("spectator")`, and keeps no `follow1` / `follow2` parser branch. | High |
| `0x10041130` | `FollowCycle` | `g_cmds.c::FollowCycle` | Inner client-only follow-cycle worker with the retail bad-dir/bad-client diagnostics; it skips disconnected, `PM_SPECTATOR`, and `PMF_FOLLOW` clients, applies same-team filtering for active team callers, updates follow state, and emits the Race info side payload. | High |
| `0x100412E0` | `Cmd_FollowCycle_f` | `g_cmds.c::Cmd_FollowCycle_f` | Public `follownext` / `followprev` entry that has no training-map print gate, counts tournament/free losses, moves non-spectator callers to spectator by testing `sess.sessionTeam`, and then tailcalls the inner `FollowCycle`. | High |
| `0x100423A0` | `Cmd_CallVote_f` | `g_cmds.c::Cmd_CallVote_f` | Retail callvote gate/order, token validation, map/nextmap, kick/clientkick, numeric limit votes, command help, and the handoff into `G_StartPublicVote`. | High |
| `0x10044270` | `Cmd_Vote_f` | `g_cmds.c::Cmd_Vote_f` | Uses the `No vote in progress`, `Vote cast`, and `disable_vote_ui` strings in the source-equivalent vote-cast flow. | High |
| `0x100456B0` | `Cmd_Forfeit_f` | `g_cmds.c::Cmd_Forfeit_f` | Thin forfeit-command wrapper identified by the local pause/timeout and round-countdown rejection strings before the tailcall into the deeper retail forfeit helpers. | High |
| `0x10045BD0` | `Cmd_ReadyUp_f` | `g_cmds.c::Cmd_ReadyUp_f` | Retail ready-up command helper that toggles the per-client ready latch, enforces the minimum-player and team-presence gates, and prints the `Ready` / `Not Ready` warmup centerprint. | High |
| `0x10045DD0` | `ClientCommand` | `g_cmds.c::ClientCommand` | HLIL-visible command dispatch over `say_team`, `vsay_team`, `vosay_team`, `callvote`, `give`, `follow`, `team`, and other retail client commands matches the source dispatcher. | High |
| `0x10046970` | `TossClientCubes` | `g_combat.c::TossClientCubes` | Harvester skull-drop helper backed by the `ps.generic1 & 0x3f` carried-skull count, the `ps.generic1 &= 0xc0` clear, the `Red Skull` / `Blue Skull` item lookups, the `g_dropSkulls` carried-skull loop, and the `GT_HARVESTER && meansOfDeath != MOD_SWITCHTEAM` death-path call before corpse cleanup. | High |
| `0x10046D80` | `GibEntity` | `g_combat.c::GibEntity` | Shared gib helper with the recovered Freeze thaw-respawn branch: marked frozen clients keep the normal gib event prelude, emit `EV_THAW_PLAYER`, restore `PM_NORMAL`, and rerun `ClientSpawn` instead of falling through to ordinary corpse invisibility cleanup. | Medium-High |
| `0x1004BC30` | `G_FreezeResolveRoundState` | Retail-only Freeze controller helper | Resolves any expired deferred round-state transition through `Freeze_RoundStateTransition` and returns the current Freeze controller state for HUD/end-frame callers. | High |
| `0x1004BC80` | `G_FreezeSetClientFrozenState` | Retail-only shared Freeze helper spanning `g_freeze.c::G_FreezeApplyFreezeState` and `g_freeze.c::G_FreezeThawClient` | Shared retail-only mutator that applies frozen or thawed client state, clears the retail synthetic frozen marker on the thaw branch, and owns the adjacent thaw temp-entity/event path; assisted thaw now publishes the recovered obituary/team-sound surface and falls into the reconstructed `GibEntity` thaw respawn tail. | High |
| `0x1004BDE0` | `G_FreezeResetClientForRound` | Retail-only per-client Freeze helper / `g_active.c::G_FreezeResetClientsForRound` analogue | Reused from `ClientBegin` and the delayed active-client reset path; restores clients for warmup or active-round starts and pushes them into the holding state when the controller is not ready to release them. | High |
| `0x1004BF10` | `G_FreezeTeamIsFullyFrozen` | Retail-only Freeze winner predicate | Hidden register-passed team scan used by `G_FreezeEvaluateRoundWinner`; it returns true once no connected members of that team remain unfrozen, letting the outer winner helper distinguish win versus draw. | High |
| `0x1004BF60` | `G_FreezeEvaluateRoundWinner` | Retail-only Freeze result helper / `g_active.c::G_FreezeEvaluateRoundWinner` analogue | Compares the PM_NORMAL living-player tallies and, once the configured draw-delay path is active, the corresponding living-health totals before storing the winning team latch consumed by the adjacent Freeze controller. | High |
| `0x1004C1B0` | `Freeze_RoundStateTransition` | Retail-only Freeze round-state controller | Anchored by `Freeze_RoundStateTransition: invalid state`; it resolves pending transition timers, updates `CS_MATCH_STATE`, resets clients for warmup and active states, applies the Freeze round-complete transition, and directly thaws configured winning-team frozen players through `EV_THAW_PLAYER`, `PM_NORMAL`, and `ClientSpawn`. | High |
| `0x1004CB80` | `G_FreezeRunFrame` | `g_active.c::G_FreezeRunFrame` | Source-faithful Freeze outer frame boundary. Retail keeps the round-state readback and winner-selection pieces in adjacent helpers, but this function still performs the per-frame freeze update and round-end dispatch. | High |
| `0x1004CC20` | `G_FreezeNotifyLastAlivePlayer` | Retail-only Freeze round alert helper | Services deferred `Freeze_RoundStateTransition` work, counts thawed live players by team during the active round, and triggers the shared last-alive notification path when the queried side is down to one survivor. | High |
| `0x1004CD40` | `G_FreezeClientEndFrame` | `g_client.c::G_FreezeClientEndFrame` | Tracks thaw progress, nearby allies, LOS and distance gates, and the auto-thaw timer before fanning into the shared retail Freeze state mutator. | High |
| `0x1004EE20` | `RespawnItem` | `g_items.c::RespawnItem` | Anchored by `RespawnItem: bad teammaster`; it restores grouped item spawns through the teammaster path, reenables item contents and visibility, emits the respawn event, and selects the retail powerup or kamikaze respawn sound. | High |
| `0x1004F020` | `Touch_Item` | `g_items.c::Touch_Item` | Anchored by `Item: %i %s\n`; it validates the touching client, routes by `item->giType` into the deeper pickup helpers, applies the pickup event/sound path, and updates retail per-item pickup telemetry. | High |
| `0x1004FD20` | `Use_Item` | `g_items.c::Use_Item` | Tiny HLIL-visible retail trampoline that preserves the classic use-to-respawn boundary by tailcalling `RespawnItem(ent)`. | High |
| `0x1004FD30` | `G_CheckTeamItems` | `g_items.c::G_CheckTeamItems` | Anchored by the missing red/blue/neutral flag and obelisk warnings; it verifies the active gametype has the required team objective entities in the map. | High |
| `0x100503F0` | `FinishSpawningItem` | `g_items.c::FinishSpawningItem` | Anchored by `FinishSpawningItem: %s startsolid at %s`; it sets ET_ITEM, model indices, touch/use callbacks, the drop-to-floor path, and the delayed powerup spawn gate before linking the entity. | High |
| `0x100507E0` | `G_SpawnItem` | `g_items.c::G_SpawnItem` | Source-faithful outer item spawn helper. It stores the `gitem_t`, parses retail `wait` / `random` overrides, registers assets, seeds persistent-powerup and global-sound flags, and schedules `FinishSpawningItem`. | High |
| `0x10052DC0` | `G_CanClientSeeClient` | Retail-only native export helper | Snapshot-side client-visibility predicate used for client entities: spectators, same-team viewers, the active Red Rover infection phase, and the One Flag bot special case all return true even when the stock PVS path would be the normal gate. | High |
| `0x10052E40` | `G_AreEnemyClients` | Retail-only native export helper | Validates two client slots and returns true only when they are distinct, non-spectators, and not on the same team. | High |
| `0x10052E90` | `G_ShouldSuppressVoiceToClient` | Retail-only native export helper | Steam-voice relay filter that returns true when delivery should be blocked for the candidate recipient, including bots, muted senders, and non-tell self echo; open/all-talk cases return false, otherwise the team/spectator policy falls through `OnSameTeam`. | High |
| `0x10052F40` | `G_IsObjectiveEntity` | Retail-only native export helper | Gametype-aware objective classifier that recognizes CTF/Attack-Defend flag items, One Flag targets, Overload obelisks, and the Quake Live extended item-objective flag path. | High |
| `0x10053020` | `G_FreezeCanSeeThawProgressEvent` | Retail-only Freeze native export helper | Freeze-only visibility predicate for thaw-progress temp entity event `0x58`; it checks the linked entity/player and returns true only for teammates of that linked target. | High |
| `0x100530C0` | `G_IsClientAdmin` | Retail-only native export helper | Native export-tail predicate that validates the client slot and returns true only when `sess.privilege == PRIV_ADMIN`. | High |
| `0x100530F0` | `G_GetClientScore` | Retail-only native export helper | Validates the client slot and returns `gclient->ps.persistant[PERS_SCORE]` from offset `0x100`. | High |
| `0x10053120` | `dllEntry` | Native qagame interface / `g_syscalls.c::dllEntry` analogue | Named export in HLIL and Ghidra. Retail stores the import table pointer, returns the direct-export table, and writes API version `10` through the third out-parameter. | High |
| `0x10053290` | `G_FindTeams` | `g_main.c::G_FindTeams` | Groups entities with matching `team` keys and ends with `%i teams with %i entities`. | High |
| `0x10053400` | `G_UpdateCustomSettingsMaskForCvar` | `g_main.c::G_UpdateCustomSettingsMaskForCvar` | Reused from both `G_RegisterCvars` and `G_UpdateCvars`; the reconstructed source keeps the retail table-entry boundary and dirty-latch ownership while the final mask remains centralized in `G_ComputeCustomSettingsMask`. | High |
| `0x10054920` | `G_RegisterCvars` | `g_main.c::G_RegisterCvars` | Walks the main game cvar table, tracks `g_customSettings`, clamps `g_gametype`, and explicitly registers `g_version`, matching the retail registration pass. | High |
| `0x100549E0` | `G_InitPublishedCvarState` | `g_main.c::G_InitPublishedCvarState` | Called from the `G_InitGame` bootstrap after the effective factory/cvar selection is finalized; it seeds the published player-cylinder, factory-flags, custom-settings, and loadout configstring slab plus the retail Domination/Red Rover numeric configstrings and the source-side mirror state that the later `memset( &level, 0, ... )` would otherwise wipe. | High |
| `0x10054DD0` | `G_UpdateCvars` | `g_main.c::G_UpdateCvars` | Walks the same cvar table with modification-count tracking, refreshes `g_customSettings`, and fans into follow-on update handlers just like the retail cvar update pass. | High |
| `0x10054F00` | `FindIntermissionPoint` | `g_main.c::FindIntermissionPoint` | Anchored by `info_player_intermission` plus the warning fallback and the target-facing intermission-angle adjustment. | High |
| `0x10055000` | `G_CountSpawnPoints` | `g_main.c::G_CountSpawnPoints` | Clears the cached spawn counters, then scans all entities for `info_player_deathmatch`, `team_CTF_redspawn`, and `team_CTF_bluespawn` before the rest of `G_InitGame` continues. | High |
| `0x10055110` | `G_InitGame` | `g_main.c::G_InitGame` | `InitGame: %s` log line, the published-cvar/bootstrap corridor, the inlined session cvar gate, pre-zero admin-access load, intermission-point seed, timeout publication, and the late Quad Hog/persistent-powerup tail now mirror the recovered retail init order while the source keeps spawn parsing factored into helpers. | High |
| `0x10055610` | `G_ShutdownGame` | `g_main.c::G_ShutdownGame` | Reads `com_errorMessage`, falls back to `Shutdown`, routes the reason through `LogExit` before session/admin persistence, then emits the `ShutdownGame:` logfile tail and closes the log handle. | High |
| `0x10055710` | `G_FindNextTournamentPlayer` | `g_main.c::G_FindNextTournamentPlayer` | Returns the oldest waiting spectator while excluding scoreboard spectators and invalid follow states; `AddTournamentPlayer` now calls this recovered selector directly. | High |
| `0x10055780` | `AddTournamentPlayer` | `g_main.c::AddTournamentPlayer` | Duel-only queue promotion path that counts active players, chooses the oldest waiting spectator, calls `SetTeam(..., "f")`, and resets warmup/game-state latches when the second player joins. | High |
| `0x10055900` | `RemoveTournamentLoser` | `g_main.c::RemoveTournamentLoser` | Duel-only queue demotion path that selects `level.sortedClients[1]` when two players are active and calls `SetTeam(..., "s")` to send the loser back to spectator. | High |
| `0x10055950` | `AdjustTournamentScores` | `g_main.c::AdjustTournamentScores` | Tournament intermission helper that increments the winner's wins and loser's losses via `level.sortedClients`, then refreshes both configstrings through `ClientUserinfoChanged`. | High |
| `0x100559E0` | `G_UpdateAwardConfigstrings` | `g_main.c::G_UpdateAwardConfigstrings` | Tailcalled from both `SendScoreboardMessageToAllClients` and `CalculateRanks`; it selects winning clients for the legacy retail award configstrings at `0x2B4`, `0x2B5`, and `0x2B8-0x2BB` and publishes them through the shared `%i` formatter. | High |
| `0x10055E50` | `SendScoreboardMessageToAllClients` | `g_main.c::SendScoreboardMessageToAllClients` | Loops connected clients through the scoreboard sender exactly like the source wrapper, then falls through into the shared retail award-configstring refresh at `0x100559E0`. | High |
| `0x10055EB0` | `SortRanks` | `g_main.c::SortRanks` | The qsort comparator keeps scoreboard/follow spectators last and otherwise sorts active clients by session/score state exactly like the source rank-ordering helper. | High |
| `0x10055FA0` | `G_CountAndSortConnectedClients` | `g_main.c::G_CountAndSortConnectedClients` | Rebuilds connected, non-spectator, playing, voting, and auto-follow counts, writes the caller-provided sorted-client list, and sorts it through `SortRanks` before the rank assignment pass continues. | High |
| `0x10056070` | `CalculateRanks` | `g_main.c::CalculateRanks` | Calls the recovered client count/sort helper, assigns rank/tie state, updates score and leader configstrings, resends scoreboards during intermission, and then tails into the shared retail award-configstring refresh; team modes publish `TEAM_RED` / `TEAM_BLUE` placement-name tokens and non-team placement slots are gated by the playing-client count. | High |
| `0x10056B30` | `MoveClientToIntermission` | `g_main.c::MoveClientToIntermission` | Moves a client to the intermission origin and angles, switches to `PM_INTERMISSION`, and clears powerups plus transient entity/playerstate flags. | High |
| `0x10056CB0` | `BeginIntermission` | `g_main.c::BeginIntermission` | Intermission bootstrap that latches intermission time, runs tournament score adjustment, walks `MoveClientToIntermission`, and then extends the stock GPL flow with vote clearing and `nextmaps` setup. | High |
| `0x10057000` | `ExitLevel` | `g_main.c::ExitLevel` | Match-end exit path that honors `sv_killserver` / `sv_quitOnExitLevel`, clears the intermission latch, removes the duel loser when needed, resolves the `nextmaps` or `map_restart` path unless `VF_NO_ENDVOTE` disables end voting, writes session data, and pushes connected clients back to `CON_CONNECTING`. | High |
| `0x100573F0` | `G_LogPrintf` | `g_main.c::G_LogPrintf` | Timestamped logfile writer used by init/shutdown, connect/disconnect, and other game log traffic. | High |
| `0x10057510` | `LogExit` | `g_main.c::LogExit` | Anchored by `Exit: %s`, `red:%i  blue:%i`, and the per-client `score:` log line while queueing intermission and single-player win/loss follow-ons. | High |
| `0x10057AD0` | `CheckIntermissionExit` | `g_main.c::CheckIntermissionExit` | Tailcalled from `CheckExitRules` during intermission; the body rebuilds the client ready bitmask, honors the `nextmaps`-extended wait, and exits through `ExitLevel` after the grace window. | High |
| `0x10057C60` | `ScoreIsTied` | `g_main.c::ScoreIsTied` | The body compares current leader scores for FFA, duel, Race, and Red Rover, otherwise compares red/blue team scores, and is queried directly from `CheckExitRules` and the Red Rover exit helper before sudden-death or roundlimit handling. | High |
| `0x10057CD0` | `G_CanForfeit` | `g_cmds.c::G_CanForfeit` | Shared gate spanning `Cmd_Forfeit_f` and `g_main.c::CheckExitRules`; it owns the command-side rejection strings, automatic missing-player checks, and the duel surrender score marker before the shared executor runs. | High |
| `0x10057F10` | `G_ApplyForfeit` | `g_main.c::G_ApplyForfeit` | Forces the losing side into the forfeited score state, sets the forfeiture latch, prints `Game has been forfeited.`, and logs `Players have forfeited.` | High |
| `0x10058030` | `CheckExitRules` | `g_main.c::CheckExitRules` | Anchored by `Timelimit hit.`, `Fraglimit hit.`, and `Capturelimit hit.` strings; the current reconstruction preserves the intermission queue delay, overtime-extended generic limits, and the retail Freeze fallback gate keyed by `g_freezeRoundDelay`. | High |
| `0x10058410` | `G_SyncTournamentQueueTeamTasks` | Retail-only duel queue helper | Watches for dirty queue-position updates, mirrors the current `pq` slot back into affected clients' `teamtask` userinfo key, including zero when they leave the queue, and republishes them through `ClientUserinfoChanged`. | High |
| `0x10058580` | `G_CheckReadyUpDelayAction` | Retail-only duel warmup helper | Arms `CS_READYUP_STATUS` from `g_warmupReadyDelay`, then applies `g_warmupReadyDelayAction` by forcing players ready or moving unready players to spectate-only when the deadline expires. | High |
| `0x100586E0` | `CheckTournament` | `g_main.c::CheckTournament` | Warmup/game-state transition logic plus the `Warmup:` log line. | High |
| `0x100588F0` | `G_UpdateVoteCounts` | `g_vote.c::G_UpdateVoteCounts` | Walks per-client vote states, updates the public yes/no vote configstrings, and short-circuits explicit player pass/veto outcomes via `%s passed the vote.` and `%s vetoed the vote.` | High |
| `0x10058AB0` | `G_TryExecuteVoteString` | `g_vote.c::G_TryExecuteVoteString` | Parses and executes Quake Live-specific vote strings such as `cointoss`, `random`, `loadouts`, `timers`, `shuffle`, `teamsize`, and `weaprespawn`, then reports whether the string was consumed. | High |
| `0x10059130` | `G_ClearVoteState` | `g_vote.c::G_ClearVoteState` | Clears vote configstrings and each client's vote-status field; this helper is called from both `CheckVote` and the intermission bootstrap. | High |
| `0x100591B0` | `CheckVote` | `g_main.c::CheckVote` | Handles delayed vote execution plus the `Vote passed.`, `Vote failed.`, and Quake Live-specific `Voting time has expired.` outcomes before clearing vote state. | High |
| `0x100592C0` | `CheckCvars` | `g_main.c::CheckCvars` | Watches `g_password` changes, recomputes `g_needpass`, and republishes the paired server configstrings exactly like the source cvar watcher. | High |
| `0x10059370` | `G_RunThink` | `g_main.c::G_RunThink` | Preserves the classic `nextthink` / `ent->think` gate and `NULL ent->think` error while also servicing a neighboring retail callback slot ahead of the think dispatch. | High |
| `0x100593E0` | `G_UpdateTeamCountConfigstrings` | `g_match_state.c::G_UpdateTeamCountConfigstrings` | Periodically refreshes the auxiliary team-count configstrings at `0x297` and `0x298` on the retail last-publish `> 250 ms` cadence, using raw team rosters in ordinary team states and the active-player counter during round-controller states. | High |
| `0x100594D0` | `G_RunFrame` | `g_main.c::G_RunFrame` | Main frame loop advancing time, stepping entities, and running exit/team/vote helpers. | High |
| `0x10060EE0` | `Cmd_Players_f` | `g_cmds.c::Cmd_Players_f` | Direct command-table `players` entry; walks connected clients and emits `%2d %llu %c %s` rows with the recovered `" MA*"` privilege marker. | High |
| `0x10061090` | `G_ValidateDirectCommandState` | `g_cmds.c::G_ValidateDirectCommandState` | Shared direct-command state gate for warmup, active match, round countdown, and intermission rejection strings. | High |
| `0x100611D0` | `G_AdminResolvePlayerIdArg` | `g_cmds.c::G_AdminResolvePlayerIdArg` | Shared direct admin PlayerID resolver; requires numeric argv 1 and emits the recovered missing/invalid `/players` diagnostics. | High |
| `0x10061350` | `G_AdminParseTeamArg` | `g_cmds.c::G_AdminParseTeamArg` | Shared direct admin team parser; accepts retail single-letter team tokens and owns the recovered TeamName diagnostics. | High |
| `0x10061550` | `Cmd_Abort_f` | `g_cmds.c::Cmd_Abort_f` | Direct command-table `abort` entry; blocks while a timeout is active, broadcasts the recovered abort `pcp` line, resets the match state to `PRE_GAME`, refreshes match-state publication, and queues `map_restart 3`. | High |
| `0x10061670` | `Cmd_AddScore_f` | `g_cmds.c::Cmd_AddScore_f` | Direct command-table `addscore` entry; resolves a PlayerID, parses argv 2 as a score delta, calls `AddScore`, announces `Player score adjusted.`, and reports whether the player's score increased or decreased. | High |
| `0x10061730` | `Cmd_AddTeamScore_f` | `g_cmds.c::Cmd_AddTeamScore_f` | Direct command-table `addteamscore` entry; parses a team token and score delta, calls `AddTeamScore`, announces `Team score adjusted.`, and reports the team score increase/decrease. | High |
| `0x10061800` | `Cmd_AllReady_f` | `g_cmds.c::Cmd_AllReady_f` | HLIL-visible admin helper for the `allready` command table entry; it validates state, enforces the duel two-player restriction, and sets every connected client's retail ready latch. | High |
| `0x100618B0` | `G_TeamJoinAllowed` | `g_cmds.c::G_TeamJoinAllowed` | Team join guard reached from `SetTeam`; permits free/spectator joins and rejects live-team joins when the per-team retail lock latch is set. | High |
| `0x10061940` | `Cmd_Lock_f` | `g_cmds.c::Cmd_Lock_f` | Direct command-table `lock` entry; optionally parses a team token, sets one lock or both live-team locks, and broadcasts `The %s team is now locked`. | High |
| `0x10061A40` | `Cmd_Unlock_f` | `g_cmds.c::Cmd_Unlock_f` | Direct command-table `unlock` entry; mirrors `Cmd_Lock_f` by clearing one lock or both live-team locks and broadcasting the recovered unlocked string. | High |
| `0x10061B40` | `Cmd_PutTeam_f` | `g_cmds.c::Cmd_PutTeam_f` | Direct command-table `putteam` entry; resolves a PlayerID, parses a team token, preserves duel restrictions, notifies the target, and forwards to `SetTeam`. | High |
| `0x10061DB0` | `G_StartTimeout` | `g_cmds.c::G_StartTimeout` | Shared timeout starter; records owner/start/expire state, refreshes timeout configstrings, and emits the recovered `pcp` timeout/pause strings. | High |
| `0x10062130` | `Cmd_Pause_f` | `g_cmds.c::Cmd_Pause_f` | Direct command-table `pause` entry; starts an indefinite pause or lets a player take ownership of a server-owned pause. | High |
| `0x100621C0` | `Cmd_Timeout_f` | `g_cmds.c::Cmd_Timeout_f` | Direct command-table `timeout` entry; checks the timeout pool for player callers and starts a timed timeout through `G_StartTimeout`. | High |
| `0x10062330` | `Cmd_Timein_f` | `g_cmds.c::Cmd_Timein_f` | Direct command-table `timein` / `unpause` entry; verifies ownership or moderator privilege and arms the five-second resume countdown. | High |
| `0x10062470` | `Cmd_AddAdmin_f` | `g_cmds.c::Cmd_AddAdmin_f` | Direct command-table `addadmin` entry; resolves a PlayerID, promotes the target to admin, mirrors the SteamID into the access list, broadcasts `%s has become an administrator`, and sends `priv %i`. | High |
| `0x10062560` | `Cmd_AddMod_f` | `g_cmds.c::Cmd_AddMod_f` | Direct command-table `addmod` entry; mirrors the admin promotion path for moderator tier and broadcasts `%s has become a moderator`. | High |
| `0x10062650` | `Cmd_Demote_f` | `g_cmds.c::Cmd_Demote_f` | Direct command-table `demote` entry; rejects same-or-higher targets, clears live privilege, removes the SteamID access entry, broadcasts `%s has had their privileges removed`, and sends `priv %i`. | High |
| `0x100627C0` | `Cmd_Mute_f` | `g_cmds.c::Cmd_Mute_f` | Direct command-table `mute` entry; resolves a numeric PlayerID, rejects same-or-higher targets, sets the muted session flag, and broadcasts `%s has been muted`. | High |
| `0x10062890` | `Cmd_Unmute_f` | `g_cmds.c::Cmd_Unmute_f` | Direct command-table `unmute` entry; resolves the same PlayerID target, clears the muted session flag, and broadcasts `%s has been unmuted`. | High |
| `0x10062940` | `G_KickOrBanClient` | `g_cmds.c::G_KickOrBanClient` | Shared `tempban` / `ban` drop helper; rejects privileged targets with `Can not kick admins.`, writes a temporary or permanent `-1` access-list entry, and drops the target with `was kicked`. | High |
| `0x10062AD0` | `Cmd_Unban_f` | `g_cmds.c::Cmd_Unban_f` | Direct command-table `unban` entry; parses argv 1 as a SteamID, removes the access-list entry, and prints `%llu has been unbanned`. | High |
| `0x10062BF0` | `Cmd_OpSay_f` | `g_cmds.c::Cmd_OpSay_f` | Direct moderator broadcast chat entry; concatenates argv 1+ and sends the recovered `<@%s^7> %s` print to all clients. | High |
| `0x10062C60` | `Cmd_ListAccess_f` | `g_cmds.c::Cmd_ListAccess_f` | Direct command-table `listaccess` entry; parses an optional one-based page argument and forwards the zero-based index to `G_PrintAccessListPage`. | High |
| `0x10062CE0` | `Cmd_SetMatchTime_f` | `g_cmds.c::Cmd_SetMatchTime_f` | Direct command-table `setmatchtime` entry; parses whole seconds, rewrites `CS_LEVEL_START_TIME` from the current level time, and broadcasts `Match time has been set to %s.` with the retail minute/second formatter. | High |
| `0x10062D60` | `G_PrintDirectCommandHelp` | `g_cmds.c::G_PrintDirectCommandHelp` | Help walker reached from the `?` table entry; filters rows by privilege and visibility flags before printing command descriptions. | High |
| `0x10062E20` | `G_DispatchDirectCommand` | `g_cmds.c::G_DispatchDirectCommand` | Direct command dispatcher for `data_10080750`; scans the table, enforces privilege floors, calls non-null handlers, lets the help-visible null-handler `rcon` row fall through, and emits the recovered insufficient-privileges diagnostic. | High |
| `0x10064280` | `G_RRResolveRoundState` | Retail-only Red Rover controller helper | Freeze-style pending-transition resolver that advances deferred `RR_RoundStateTransition` work and returns the current Red Rover round state. | High |
| `0x10064380` | `G_RRFinalizeSpawnLoadout` | Retail-only Red Rover spawn helper | Reached from `ClientSpawn` before the generic loadout finalizer; survivors fall through to `G_FinalizeSpawnLoadout`, while infected clients are forced onto the zombie role loadout by seeding the reduced weapon mask, selected weapon, and health/maxHealth directly. | High |
| `0x100643E0` | `G_RRHandleDamageScore` | Retail-only Red Rover infection damage helper / `g_client.c::G_RRHandleDamageScore` analogue | Called from the main damage path after armor resolution; it applies the shared self/team damage suppression policy, clamps survivor-vs-infected damage during the active infection state, accumulates threshold credit on the attacker, and pays out score increments through `CalculateRanks`. | High |
| `0x100645A0` | `G_RRResetClientForRound` | Retail-only Red Rover per-client round helper | Reused from both `ClientBegin` and the delayed respawn path; it reruns `ClientSpawn`, reapplies the Red Rover role-aware spawn finalizer, and pushes the client into the holding state while the round controller is still in its pre-release phase. | High |
| `0x100645E0` | `G_RRInitClient` | `g_client.c::G_RRInitClient` analogue | Spawn/bootstrap helper that seeds the infection-role flags from `sess.sessionTeam`, clears them for survivors when the RR toggles are disabled, and forces the holding-state bit while warmup or the pre-active controller state is still in effect. | High |
| `0x10064670` | `G_RRCheckRoundCompletion` | Retail-only Red Rover completion helper / `g_client.c::G_RRCheckRoundCompletion` analogue | Evaluates connected-team counts, applies the draw-delay gate, and latches the carryover infected-slot client when infection mode is down to one surviving blue player. | High |
| `0x10064710` | `G_RRCheckExitRules` | Retail-only Red Rover exit helper | Suppresses exit while `ScoreIsTied()` is true using Red Rover's leader-score tie path, otherwise checks timelimit/roundlimit and optionally prints/logs the corresponding match-end messages. | High |
| `0x100647C0` | `G_RRResolveAutoJoinTeam` | Retail-only Red Rover infection helper | Reached from the autojoin path in `SetTeam` when infection mode is active; it resolves any pending controller transition and returns `TEAM_RED` for the preserved or newly selected infected slots and `TEAM_BLUE` for every other client. | High |
| `0x10064820` | `G_RRSeedInfectionTeams` | Retail-only Red Rover infection helper | Reached from the infection branch of `G_RRTrackRoundActivity`; it moves everyone back to `TEAM_BLUE`, restores the carryover infected-slot client when one exists, otherwise selects a random connected client from `level.sortedClients`, stores that slot, and returns the chosen infected client number. | High |
| `0x100649F0` | `RR_RoundStateTransition` | Retail-only Red Rover round-state controller | Anchored by `RR_RoundStateTransition: invalid state`; it resolves pending transition timers, updates the match-state configstrings, resets active participants, and drives the Red Rover active, complete, and restart phases. | High |
| `0x100652B0` | `G_RRApplySurvivalBonus` | Retail-only Red Rover infection helper | Anchored by `Survival Bonus! +%i`; when the infection ruleset is active it checks the survival-bonus timer, awards the configured score delta to the connected team-2 participants, emits the matching `EV_GLOBAL_TEAM_SOUND` / `GTS_SURVIVOR_WARNING` team-2 broadcast, and refreshes ranks. | High |
| `0x10065410` | `G_RRCheckInfectionSpread` | Retail-only Red Rover infection helper | Anchored by `Infection spreads in %i second%s!`; it announces the next spread window and, when the timer expires, converts the next eligible connected participant through the deeper team/state mutation helper before rearming the timer. | High |
| `0x100655A0` | `G_RRTrackRoundActivity` | `g_client.c::G_RRTrackRoundActivity` | Source-faithful outer Red Rover per-frame activity monitor; it refreshes the controller state, applies the survival-bonus and infection-spread helpers, evaluates round completion, and advances the controller when the round ends. | High |
| `0x10065680` | `G_RRInitRoundController` | Retail-only Red Rover init helper | Reached from `G_InitGame`; it clears the infection-selection trackers, seeds the first pending controller state, and primes the Red Rover state machine for either normal or infection-enabled starts. | High |
| `0x10065700` | `G_RRHandlePlayerDeath` | `g_client.c::G_RRHandlePlayerDeath` analogue | Retail death-path helper that flips the victim between Red Rover teams, refreshes userinfo, emits the infection temp-entity when applicable, updates infection timers/bonus state, and reevaluates round completion. | High |
| `0x10065F30` | `G_SpawnClassExemptFromSpawnFilter` | Retail-only `g_spawn.c` helper (no direct GPL analogue) | Anchored by `item_armor_shard`, `team_redobelisk`, and `team_blueobelisk`, then used inside `G_SpawnGEntityFromSpawnVars` to bypass the normal `notfree` / `notteam` / `gametype` / `not_gametype` rejection path for specific classes. | High |
| `0x10066230` | `G_ParseSpawnVars` | `g_spawn.c::G_ParseSpawnVars` | Parse/error strings match the brace-bounded entity parser. Retail inlines `G_AddSpawnVarToken` here. | High |
| `0x10066440` | `SP_worldspawn` | `g_spawn.c::SP_worldspawn` | `SP_worldspawn: The first entity isn't 'worldspawn'` string, world metadata parsing, and warmup/configstring setup. | High |
| `0x10066B90` | `ConsoleCommand` | `g_svcmds.c::ConsoleCommand` | HLIL-only boundary dispatching `entitylist`, `forceteam`, `game_memory`, `addbot`, `botlist`, `game_crash`, `forceshuffle`, `dumpvars`, the handled legacy no-op debug tokens (`markstate`, `diffstate`, `dumpentities`, `printentitystates`), `reload_access`, and the dedicated-server `say` fallback. | High |
| `0x10067EC0` | `G_ClientsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Compares two `gclient_t` session teams directly and keeps the retail spectator-equality allowance that survives below `GT_TEAM`. | High |
| `0x10067F00` | `G_ClientNumsOnSameTeam` | Retail-only native export helper wrapping `g_team.c::OnSameTeam` | Validates two client numbers against `level.clients` and then tails into `G_ClientsOnSameTeam`. | High |
| `0x10067F30` | `OnSameTeam` | `g_team.c::OnSameTeam` | Entity-level same-team predicate used across combat, chat, and objective logic; retail keeps the classic client/sessionTeam comparison but treats matching spectators as same-team even outside team gametypes. | High |
| `0x10067F70` | `G_IsClientSpectator` | Retail-only native export helper | Validates the client slot and returns whether `sess.sessionTeam == TEAM_SPECTATOR`. | High |
| `0x100680C0` | `TeamCount` | `g_client.c::TeamCount` | HLIL preserves the classic ignore-client, connected-state, and `sess.sessionTeam` loop even though the committed decomp still drops one register-passed argument. | High |
| `0x10068100` | `Team_CountsBalanced` | Retail-only `g_teamForceBalance` helper | Extracted boolean helper that returns true when the current red/blue spread is at most one player; retail reuses it from both `SetTeam` and `Cmd_ReadyUp_f` before their stricter join/ready gates. | High |
| `0x10068140` | `Team_HasMinimumPlayersForWarmup` | `g_team.c::Team_HasMinimumPlayersForWarmup` | Warmup gate that checks the duel/team minimum-player requirements and the stronger both-teams-present rule used by the retail ready-up flow. | High |
| `0x10068490` | `TeamplayInfoMessage` | `g_team.c::TeamplayInfoMessage` | Builds the compact retail `tinfo %i %s` payload from client-number entries; teammate vitals ride entity-state snapshots instead of this command. | High |
| `0x10068670` | `CheckTeamStatus` | `g_team.c::CheckTeamStatus` | Scheduled one-shot team overlay refresher; when `lastTeamLocationTime` is due it resets the timer to `-1`, refreshes connected red/blue clients' `ps.location`, and emits compact `TeamplayInfoMessage` rows. | High |
| `0x1006AAF0` | `SpawnObelisk` | `g_team.c::SpawnObelisk` | `SpawnObelisk: %s startsolid at %s` diagnostic and the matching overload spawn flow. | High |
| `0x1006B110` | `G_TotalLivingHealthByTeam` | Retail-only Freeze tally helper | Sums entity health for the connected `PM_NORMAL` clients grouped by `sess.sessionTeam`, feeding the freeze round-end health summary and tiebreak path. | High |
| `0x1006B170` | `G_CountActivePlayersByTeam` | Retail-only shared team counter | Counts connected clients whose `ps.pm_type == PM_NORMAL`, grouped by `sess.sessionTeam`; retail reuses it for Freeze, Red Rover, teamsize validation, and the auxiliary team-count configstrings. | High |
| `0x1006B1C0` | `G_CountConnectedClientsByTeam` | Retail-only shared roster counter | Counts all connected clients by `sess.sessionTeam` without the `PM_NORMAL` filter used by `G_CountActivePlayersByTeam`. | High |
| `0x1006B210` | `G_NotifyLastAlivePlayer` | Retail-only shared round alert helper | Locates the sole surviving `PM_NORMAL` client on the selected team, emits the paired `EV_GLOBAL_TEAM_SOUND` / `GTS_LAST_STANDING` temp entity, and sends that client the preserved centerprint notification reused by A/D, Clan Arena, Freeze, and Red Rover. The current source now mirrors that shared ownership directly and routes the four mode-local wrappers through it. | High |

## Supporting Helper Aliases Added In The Same Pass

- Active-client helpers: `P_DamageFeedback`, `P_WorldEffects`, `G_SetClientSound`, `ClientImpacts`, `G_TouchTriggers`, `SpectatorThink`, `ClientInactivityTimer`, `G_CheckClientFlood`, `G_RunFactoryHealthRegen`, `G_RunFactoryArmorRegen`, `ClientTimerActions`, `ClientEvents`, `StuckInOtherClient`, `SendPendingPredictableEvents`, `ClientThink_real`, `ClientSpawn`.
- Bot and training helpers: `G_ParseInfos`, `G_AddTrainerBot`.
- Spawn/reset helpers: `G_CAADRespawnAsSpectator`, `G_CAADResetClientForRound`, `G_FinalizeSpawnLoadout`, `G_RRFinalizeSpawnLoadout`, `G_RRResetClientForRound`.
- Item lifecycle helpers: `RespawnItem`, `Touch_Item`, `Use_Item`, `G_CheckTeamItems`, `FinishSpawningItem`, `G_SpawnItem`.
- Attack and Defend controller helpers: `G_ADShouldTimeoutActiveRound`, `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `AD_RoundStateTransition`, `G_ADNotifyLastAlivePlayer`, `G_ADResetScoreHistory`, `G_ADUpdateScoreHistory`.
- Clan Arena round helpers: `G_CAResolveRoundState`, `G_CAHandleDamageScore`, `G_CANotifyLastAlivePlayer`.
- Freeze and round-controller helpers: `G_FreezeResolveRoundState`, `G_FreezeSetClientFrozenState`, `G_FreezeResetClientForRound`, `G_FreezeTeamIsFullyFrozen`, `G_FreezeEvaluateRoundWinner`, `Freeze_RoundStateTransition`, `G_FreezeRunFrame`, `G_FreezeNotifyLastAlivePlayer`, `G_FreezeClientEndFrame`, `G_NotifyLastAlivePlayer`, `RR_RoundStateTransition`, `G_UpdateTeamCountConfigstrings`, `G_TotalLivingHealthByTeam`, `G_CountActivePlayersByTeam`, `G_CountConnectedClientsByTeam`.
- Red Rover controller helpers: `G_RRResolveRoundState`, `G_RRHandleDamageScore`, `G_RRInitClient`, `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`, `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`, `G_RRApplySurvivalBonus`, `G_RRCheckInfectionSpread`, `G_RRTrackRoundActivity`, `G_RRInitRoundController`, `G_RRHandlePlayerDeath`.
- Ready/warmup helpers: `Cmd_ReadyUp_f`, `Cmd_AllReady_f`, `G_CheckReadyUpDelayAction`, `Team_HasMinimumPlayersForWarmup`.
- Command/tournament queue helpers: `Cmd_TeamTask_f`, `SetTeam`, `G_UpdateTournamentQueuePositions`, `G_SyncTournamentQueueTeamTasks`.
- Scoreboard helpers: `DeathmatchScoreboardMessage`, `G_BuildCompactScoreboardMessage`, `G_BuildObeliskScoreboardMessage`, `G_BuildFFAScoreboardMessage`, `G_BuildDuelScoreboardMessage`, `G_BuildRaceScoreboardMessage`, `G_BuildTeamScoreboardMessage`, `G_SendTDMStatsMessage`, `G_BuildClanArenaScoreboardMessage`, `G_SendCAStatsMessage`, `G_BuildCTFStyleScoreboardMessage`, `G_SendCTFStatsMessage`, `G_BuildFreezeScoreboardMessage`, `G_BuildRedRoverScoreboardMessage`.
- Session helpers: `G_WriteClientSessionData`, `G_ReadSessionData`, `G_InitSessionData`, `G_WriteSessionData`.
- Intermission/rank helpers: `FindIntermissionPoint`, `G_CountSpawnPoints`, `G_FindNextTournamentPlayer`, `AddTournamentPlayer`, `RemoveTournamentLoser`, `AdjustTournamentScores`, `G_UpdateAwardConfigstrings`, `SendScoreboardMessageToAllClients`, `SortRanks`, `CalculateRanks`, `MoveClientToIntermission`, `BeginIntermission`, `ExitLevel`.
- Spawn helpers: `G_SpawnString`, `G_NewString`, `G_ParseField`, `G_CallSpawn`, `G_SpawnGEntityFromSpawnVars`.
- Server console helpers: `ClientForString`, `Svcmd_ForceTeam_f`.
- Team helpers: `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, `G_IsClientSpectator`, `TeamCount`, `Team_CountsBalanced`, `Team_HasMinimumPlayersForWarmup`, `CheckTeamStatus`, `Team_ReturnFlagSound`, `Team_TakeFlagSound`, `Team_CaptureFlagSound`.
- Retail-only vote/forfeit helpers: `G_CanForfeit`, `G_ApplyForfeit`, `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, `G_ClearVoteState`.
- Native export-tail helpers: `G_AreEnemyClients`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_IsClientAdmin`, `G_GetClientScore`.
- Core wrappers: `G_Printf`, `G_Error`.

## Important Disagreements And Split Paths

- `dllEntry` writes `0xA` through its third out-parameter. In the native Quake Live loader contract this is an API-version handoff, not a reliable export-count field; the returned qagame export table starts at the recovered shutdown/run-frame/register-cvars/init ordering and carries the 19-slot native export slab. The host dispatch now covers the live engine-call slots while `GAME_NATIVE_EXPORT_REGISTER_CVARS` remains a required table entry that retail also reaches from the qagame init path.
- `ClientThink` at `0x10035410` is visible in HLIL and in the native export table, but the committed `functions.csv` still does not emit that function start.
- `G_CheckClientFlood` at `0x100341E0` is a descriptive retail-only split from the broader `ClientThink_real` path. It shares the same `floodCount` / `floodLastTime` state used by the current source tree, but unlike `g_cmds.c::G_FloodLimited` it drops over-limit clients directly from the active-client path instead of only rate-limiting commands.
- `ClientThink_real` is a clean retail boundary at `0x10034C90`, and the surrounding `ClientEvents` (`0x10034860`) plus `StuckInOtherClient` (`0x10034B50`) splits are now settled.
- `G_RunFactoryHealthRegen` at `0x10034260` and `G_RunFactoryArmorRegen` at `0x100342F0` are descriptive retail-only helpers keyed off a shared last-damage timestamp plus separate client-side accumulators/latches. The reconstructed tree now preserves the split helper flow, the retail spawn/damage latch-arming behavior, and the adjacent `ClientTimerActions` client-state names (`factoryRegenLastDamageTime`, `factoryRegenHealthAccumulatorMs`, `factoryRegenArmorAccumulatorMs`, `factoryRegenHealthPending`, `factoryRegenArmorPending`).
- `ClientSpawn` at `0x1003BC30` is source-faithful on its outer boundary, and the current source now mirrors the recovered spawn-finalizer lane more directly by running the Red Rover override helper ahead of `G_FinalizeSpawnLoadout`, seeding the retail `PMF_CROUCH_SLIDE` / `PMF_DOUBLE_JUMP` / `PMF_AIR_CONTROL` movement-profile bits during spawn, preserving pre-existing `PM_SPECTATOR` as the spectator-spawn selector used by CA/A-D elimination, and preserving the retail null-spawn retry edge that sets `respawnTime = level.time + 600`, parks the player in `PM_SPECTATOR`, increments the retry counter, and returns before the full client reset. The broader bootstrap remains GPL-shaped around that helper chain.
- The 2026-05-25 active-client pmove wiring sweep tightened the `G_RunFrame` edge around that same boundary: source now runs client-slot scheduled thinks inline in the frame entity loop and dispatches bot/synchronous clients directly to `ClientThink_real`, matching the recovered retail shape instead of routing the frame loop through the classic source `G_RunClient` wrapper. The new structural sentinel follows that call-site into `ClientThink_real` and pins command-time clamping, pmove setup, playerState-to-entityState projection, predictable-event flushing, trigger touch, client impacts, respawn checks, and timer actions.
- `DeathmatchScoreboardMessage` at `0x1003CBF0` remains source-faithful on its public role, and the current source now mirrors the retail helper-family split directly: compact fallback, duel, Race, TDM, Clan Arena, shared CTF-style, Freeze, Red Rover, and Overload serializers all feed the scoreboard sender through payload-builder helpers, the intermission-only `tdmstats` / `castats` / `ctfstats` publishers remain sequenced under that sender, and the duel serializer now caches the lower/higher live duel client numbers in `level + 0x1C08/+0x1C0C` instead of keeping that ordering purely local. The `castats` publisher uses the cgame-matched classic weapon order G, MG, SG, GL, RL, LG, RG, PG, BFG, grappling hook, NG, PL, CG, HMG.
- `G_CAADRespawnAsSpectator` at `0x10035960` and `G_CAADResetClientForRound` at `0x10038160` are descriptive retail-only shared Clan Arena / Attack and Defend helpers. Retail keeps the per-client round reset and dead-player spectator-follow fallback in standalone helpers that the GPL-derived tree does not preserve with these exact boundaries.
- `G_FinalizeSpawnLoadout` at `0x1003B5A0` is a descriptive retail-only recovery name. The current source now preserves the selected-weapon fallback latch directly through `client->sess.selectedSpawnWeapon`, keeps the shared ammo/weapon-mask seeding under that helper, and leaves the grant-script tail in the adjacent shared spawn helper instead of collapsing the whole path back into one large `ClientSpawn` block.
- Retail keeps the item lifecycle split cleanly across `G_SpawnItem -> FinishSpawningItem -> Touch_Item` with the optional `Use_Item -> RespawnItem` trampoline, while `G_CheckTeamItems` remains a separate objective-validator pass. The current GPL-derived tree preserves the same core behavior, but some map bootstrap and spawn-side item setup is easier to read inline than in this retail helper chain.
- `G_ADResolveRoundState`, `G_ADResolveAttackingTeam`, `G_ADResolveDefendingTeam`, `G_ADHandleDamageScore`, `G_ADCheckExitRules`, `G_ADResetScoreHistory`, and `G_ADUpdateScoreHistory` are descriptive retail-only helper names. The current source now preserves those A/D round-state reads, side selection, damage-credit thresholds, exit-rule gates, and `scores_ad` publishing as standalone boundaries, with the recovered exit helper retaining the retail overtime-adjusted mercy window.
- `G_ADShouldTimeoutActiveRound`, `G_ADNotifyLastAlivePlayer`, `G_CAResolveRoundState`, `G_CAHandleDamageScore`, `G_CANotifyLastAlivePlayer`, `G_FreezeNotifyLastAlivePlayer`, and `G_NotifyLastAlivePlayer` are likewise descriptive retail-only helper names. The current tree now preserves the shared last-alive alert ownership for A/D, Clan Arena, Freeze, and Red Rover by routing those wrappers through `G_NotifyLastAlivePlayer`, which emits the retail `EV_GLOBAL_TEAM_SOUND` / `GTS_LAST_STANDING` broadcast plus the lone-survivor centerprint; the separate `GTS_SURVIVOR_WARNING` path remains scoped to Red Rover survival-bonus alerts.
- `AD_RoundStateTransition` at `0x10035B70` is a retail-only controller name recovered directly from the preserved invalid-state diagnostic. The current source now preserves a standalone Attack and Defend controller boundary plus the adjacent side-resolver and score-history publisher split.
- `G_AddTrainerBot` at `0x100378E0` is a descriptive retail-only training helper name. The current source now preserves that dedicated wrapper in `g_bot.c`, routing the `special=training` single-player bootstrap through the fixed `Trainer` / `5000 ms` / `loaddeferred` lane instead of approximating it through the generic arena bot spawner.
- `G_InitWorldSession` is inlined into retail `G_InitGame`. The current source now mirrors that directly: the `session` cvar read and the `Gametype changed, clearing session data.` print occur inside `G_InitGame`, not a separate helper boundary.
- The outer `G_SpawnEntitiesFromString` loop is likewise inlined into `G_InitGame`: retail parses the first entity, runs `SP_worldspawn`, then loops `G_SpawnGEntityFromSpawnVars` until `G_ParseSpawnVars` returns false.
- `G_CountSpawnPoints` at `0x10055000` is a descriptive recovery name. The current source now mirrors that recovered standalone helper directly from `G_InitGame` instead of keeping the scan inline.
- The current source now mirrors the recovered `G_InitGame` bootstrap corridor more closely: `G_LoadAdminAccessFile` uses static storage and runs before the `level` wipe, `G_InitPublishedCvarState` seeds the init-time configstring slab before entity parsing, `g_levelStartTime` is republished from the post-`memset` time-seed lane, the retail `CS_MATCH_GUID` snapshot is generated or restored and published before `trap_LocateGameData`, `FindIntermissionPoint` is restored to the init path, and the late `G_SpawnQuadHogQuad` / `G_SpawnItemPowerups` tail now runs after bot setup. The earlier source-only `G_ProcessIPBans` init call and init-time `AUTOACTION_MATCH_START` tail have been removed from this corridor.
- `G_FindNextTournamentPlayer` at `0x10055710` is now preserved as a stable callable helper in `g_main.c`, and `AddTournamentPlayer` delegates the duel queue selection to it before resetting the duel pregame state.
- `G_UpdateAwardConfigstrings` at `0x100559E0` is now preserved as a standalone `g_main.c` helper. It publishes winning client numbers into the legacy award configstring block (`0x2B4`, `0x2B5`, `0x2B8-0x2BB`) and remains wired as the shared tail after both `SendScoreboardMessageToAllClients` and `CalculateRanks`.
- `SendScoreboardMessageToAllClients` at `0x10055E50` is source-faithful on its outer boundary, but retail makes it slightly fatter by tailcalling `G_UpdateAwardConfigstrings` instead of returning immediately after the scoreboard loop.
- `G_CountAndSortConnectedClients` at `0x10055FA0` is now preserved as a standalone `g_main.c` helper instead of keeping the count/sort prelude inline in `CalculateRanks`; the helper owns the connected/non-spectator/playing/voting/follow counts and the `SortRanks` qsort call.
- `CalculateRanks` at `0x10056070` is a clean outer boundary, and now calls the recovered count/sort helper before the rank assignment and score-configstring work while still appending the shared `G_UpdateAwardConfigstrings` tail path. The score/configstring lane now follows retail's exact placement split: team modes always publish red/blue scores plus `TEAM_RED` / `TEAM_BLUE` name tokens, while non-team modes publish first and second rows only when `level.numPlayingClients` reaches one and two respectively.
- `G_UpdateCustomSettingsMaskForCvar` at `0x10053400` is now preserved as a small `g_main.c` helper called from both cvar registration and update passes. The source still computes the final published mask through the stronger centralized `G_ComputeCustomSettingsMask` path, so this helper currently owns the table-entry dirty latch rather than per-cvar bit assignment.
- `G_AddSpawnVarToken` is inlined into `G_ParseSpawnVars`; the error string survives, but the helper body does not exist as a stable standalone function in the current retail build.
- Retail `G_SpawnGEntityFromSpawnVars` also adds a classname-based exemption helper plus a `not_gametype` path around the source-equivalent gametype filters. That logic does not survive as a direct GPL helper name, so `G_SpawnClassExemptFromSpawnFilter` is a descriptive recovery name for the observed retail behavior.
- `ConsoleCommand` at `0x10066B90` is visible in HLIL and in the native export table, but the committed `functions.csv` does not currently list that function start.
- `ClientCommand` at `0x10045DD0` is in the same situation: it is visible in HLIL and the native export table, but not currently emitted as a function start in the committed `functions.csv`.
- `Use_Item` at `0x1004FD20` is also HLIL-visible as a stable standalone thunk, but the committed `functions.csv` does not currently emit that function start.
- `Cmd_AllReady_f` at `0x10061800` is likewise HLIL-visible via the `allready` command table entry, but the committed `functions.csv` does not currently emit that function start.
- `G_FreezeEvaluateRoundWinner` at `0x1004BF60` is a descriptive retail-only helper name. The current source now preserves the explicit count/health-driven timeout tiebreak path and the adjacent frozen-team checks, while retail still stores the resolved winner in the controller-local latch at `data_105df598` instead of returning it directly.
- `G_FreezeResolveRoundState` at `0x1004BC30` and `G_RRResolveRoundState` at `0x10064280` are descriptive retail-only controller read helpers. The current source now routes Freeze and Red Rover helper callers through standalone pending-transition resolvers that mirror the committed HLIL readback timing.
- `G_FreezeSetClientFrozenState` at `0x1004BC80` is a descriptive retail-only shared helper name. The current source now preserves that shared mutator boundary directly in `g_freeze.c`, with `G_FreezeApplyFreezeState`, `G_FreezeThawClient`, and `G_FreezeClientEndFrame` all fanning into it instead of carrying split mutation logic at the call sites. The qagame producer for the cgame frozen-player marker is now mirrored through `ps.powerups[PW_NUM_POWERUPS] = INT_MAX` / `ent->s.powerups = ( 1 << PW_NUM_POWERUPS )` on freeze entry and cleared on init/thaw to match retail `client + 0x17c` and `gentity + 0xc4` writes. Assisted thaw now also emits the recovered `EV_OBITUARY`/`MOD_THAW` payload plus the paired `EV_GLOBAL_TEAM_SOUND` return-sound payload before preserving the marker for the reconstructed `GibEntity` tail, which emits `EV_THAW_PLAYER`, restores `PM_NORMAL`, and calls `ClientSpawn`.
- `G_FreezeResetClientForRound` at `0x1004BDE0` is likewise descriptive. The current source now preserves a standalone per-client round reset helper under the Freeze controller path; retail still appears to reuse that boundary more broadly from bootstrap as well, but the warmup and active-round reset behavior is no longer merged into one large loop body.
- `G_FreezeTeamIsFullyFrozen` at `0x1004BF10` is a descriptive retail-only helper name. The committed decomp still hides the register-passed team argument, but HLIL shows the connected-client scan that `G_FreezeEvaluateRoundWinner` uses to detect when one side has no unfrozen members left.
- `G_FreezeRunFrame` at `0x1004CB80` is source-faithful on its outer boundary, and the current source now mirrors the retail helper split by routing pending-transition readback through `G_FreezeResolveRoundState`, delegating round-completion gating to `G_FreezeShouldCompleteRound`, and delegating winner selection to `G_FreezeEvaluateRoundWinner`.
- `G_FreezeClientEndFrame` at `0x1004CD40` is source-faithful on its outer boundary, and the current source now gates thaw progression through the live Freeze round-state resolver before fanning the actual state mutation into `G_FreezeSetClientFrozenState`. The thaw lane now mirrors the recovered Ghidra/HLIL shape more closely as a remaining-time counter at the client field equivalent of retail `+500`, with top-of-frame low `EF_DEAD`/`EF_TICKING` thaw-progress buckets, helper retention through the adjacent active/client-number pair, `trap_EntitiesInBox` helper enumeration, and `g_freezeThawTick` acting only as the non-zero event gate for `EV_THAW_TICK`.
- `G_CanClientSeeClient` at `0x10052DC0` is a descriptive retail-only native export helper. The current GPL tree does not expose a standalone client-visibility predicate for the snapshot builder, while retail uses this slot from `SV_AddEntitiesVisibleFromPoint` to force-include spectator, teammate, and Red Rover infection client entities outside the ordinary PVS-only path.
- `G_AreEnemyClients` at `0x10052E40` is a descriptive retail-only native export helper. The current source tree does not expose a standalone client-number predicate for "distinct non-spectator opponents", so the recovered name reflects the exact HLIL gate rather than a GPL symbol.
- `G_ShouldSuppressVoiceToClient` at `0x10052E90` is a descriptive retail-only native export helper. The host calls it from the Steam voice relay loop and forwards the packet only when this predicate returns false, so the recovered name follows the real suppression semantics instead of pretending the GPL chat/voice helpers expose an equivalent standalone filter.
- `G_IsObjectiveEntity` at `0x10052F40` is likewise descriptive. Retail centralizes gametype-specific objective detection for flag items, obelisks, and extended Quake Live objective items in this export-tail helper instead of leaving that policy scattered through UI- or engine-facing call sites.
- `G_FreezeCanSeeThawProgressEvent` at `0x10053020` is a descriptive retail-only helper name. The stock GPL tree does not expose a standalone Freeze event-visibility predicate; retail split out the thaw-progress temp-entity filter keyed by event `0x58` and the linked teammate entity, and the current source now mirrors that directly through `EV_THAW_TICK` / `ET_EVENTS + EV_THAW_TICK` instead of the older synthetic alias.
- `G_RunFrame` at `0x100594D0` does not appear to call a standalone `G_RunClient` helper in the current retail build. The entity loop walks client slots inline and dispatches `ClientThink_real` directly, so the classic thin wrapper appears to be inlined or absent.
- `OnSameTeam` at `0x10067F30` is source-faithful on its outer boundary, but retail broadens the non-team-gametype case: matching spectators are treated as same-team instead of immediately returning false whenever `g_gametype < GT_TEAM`.
- `G_GetClientScore` at `0x100530F0` is a synthetic recovery name for a stable retail helper boundary. The body is just a validated getter for `gclient->ps.persistant[PERS_SCORE]`, and the GPL-derived tree does not preserve it as a standalone named function.
- The native export table tail beyond the public `GAME_*` slots now appears fully settled. `G_CanClientSeeClient`, `G_AreEnemyClients`, `G_ShouldSuppressVoiceToClient`, `G_IsObjectiveEntity`, `G_FreezeCanSeeThawProgressEvent`, `G_GetClientScore`, `G_IsClientAdmin`, `G_ClientsOnSameTeam`, `G_ClientNumsOnSameTeam`, `OnSameTeam`, and `G_IsClientSpectator` all have stable HLIL bodies plus host-side consumers.
- `Freeze_RoundStateTransition` at `0x1004C1B0` and `RR_RoundStateTransition` at `0x100649F0` are retail-only controller names recovered directly from preserved invalid-state diagnostics. The current source now preserves standalone Freeze and Red Rover controller shells plus the paired public read helpers. Freeze winning-team thaw now mirrors the recovered direct `EV_THAW_PLAYER` / `PM_NORMAL` / `ClientSpawn` handoff, while Red Rover mirrors the recovered six-state internal controller lane (`0..5`) with the same pending-transition timing split between warmup, seeding, active, complete, and exit.
- `SetTeam` at `0x100406D0` is source-faithful on its outer boundary, and the current source now preserves the retail split by forwarding the actual session/team mutation and respawn execution into `G_ApplyTeamChange` at `0x10040440`. The parser also mirrors the recovered null/auto fallthrough, `follow1`/`follow2` active-player downgrades, Red Rover's pre-balance autojoin branch, and the retail `level.sortedClients` revenge-counter cleanup before userinfo publication.
- `TeamCount` at `0x100680C0` is source-faithful on its outer boundary, but the committed decomp still drops the register-passed `ignoreClientNum` argument even though HLIL preserves the comparison against the skipped client slot.
- `Team_CountsBalanced` at `0x10068100` is a descriptive retail-only helper name. The current source preserves the extracted `g_teamForceBalance` spread check as a shared callable boundary used by both `SetTeam` and ready-up gating.
- `G_UpdateTeamCountConfigstrings` at `0x100593E0` is now preserved through `g_match_state.c` and called from the recovered `g_main.c` init/frame wiring. The helper publishes configstrings `0x297` and `0x298`, uses the HLIL-observed last-publish gate (`level.time <= last` or `level.time - last > 250`), and switches between raw `TeamCount`-style rosters and `PM_NORMAL` active counts for round-controller states.
- `G_CountActivePlayersByTeam`, `G_TotalLivingHealthByTeam`, and `G_CountConnectedClientsByTeam` are descriptive retail-only helper names. The current GPL-derived tree keeps the same counting logic inside larger Freeze, Red Rover, and match-state routines instead of preserving these standalone helpers.
- `G_RRCheckRoundCompletion` at `0x10064670` is a descriptive retail-only helper name. The current source now preserves the caller-supplied counts interface, the roundtimelimit gate before tied-state completion, the carryover infected-slot latch, and the delayed post-round exit-vs-restart split consumed by the Red Rover controller.
- `G_RRCheckExitRules` at `0x10064710` is a descriptive retail-only helper name. The current source now preserves the standalone tie-aware RR timelimit/roundlimit gate, the Red Rover-specific `ScoreIsTied` leader-score path, the retail `Timelimit hit.` / `Roundlimit hit.` logging path, and the dedicated RR exit-state handoff that invokes that gate after the delayed complete-state timer expires.
- `G_RRHandleDamageScore` at `0x100643E0` is a descriptive retail-only helper name. The current source now preserves the retail post-armor boolean damage helper shape in `g_client.c::G_RRHandleDamageScore`, including same-team suppression, active-round damage gating, health/armor caps, and threshold score payout before the main `G_Damage` path continues.
- `G_RRFinalizeSpawnLoadout` at `0x10064380` and `G_RRResetClientForRound` at `0x100645A0` are descriptive retail-only Red Rover spawn helpers. The current source now preserves the recovered ordering more directly: `ClientSpawn` runs the RR infection override before the generic finalizer, infected clients consume the gauntlet/zombie-health path without falling through to generic loadout selection, and the per-round RR reset wrapper routes back through `ClientSpawn` while reapplying the warmup attack lockout.
- `G_RRInitClient` at `0x100645E0` is source-faithful on role but not on exact state shape. The current GPL-derived tree stores richer `rrInfectionState` and timer fields, while the retail helper mostly seeds the infection-role flag bits and the temporary holding-state latch during spawn/bootstrap.
- `G_RRResolveAutoJoinTeam` at `0x100647C0` and `G_RRSeedInfectionTeams` at `0x10064820` are descriptive retail-only infection helpers. The current source now services the pending RR controller transition before resolving infected autojoin slots and still mirrors the preserved infected-slot handoff through `SetTeam` plus the round-start reseed back to `TEAM_BLUE` with one promoted `TEAM_RED` infected client.
- `G_RRApplySurvivalBonus` at `0x100652B0` and `G_RRCheckInfectionSpread` at `0x10065410` are descriptive retail-only Red Rover infection helper names. The current source now mirrors the survival-bonus timer/forced-award split, the survivor-only bonus print, the retail `EV_GLOBAL_TEAM_SOUND` / `GTS_SURVIVOR_WARNING` team-2 broadcast, and the global infection-spread countdown/forced conversion order.
- `G_RRTrackRoundActivity` at `0x100655A0` is source-faithful on its outer boundary, and the current source now follows the retail survival-bonus then infection-spread then completion ordering while feeding the recovered counts array into `G_RRCheckRoundCompletion` and honoring the delayed complete-state transition split.
- `G_RRInitRoundController` at `0x10065680` is a descriptive retail-only init helper. The current source now preserves a dedicated Red Rover controller bootstrap boundary that primes the internal `RR_ROUNDSTATE_*` lane, the infection-selection trackers, and the pending transition timer ahead of the seeding/warmup/active phases.
- `G_RRHandlePlayerDeath` at `0x10065700` is now aligned on both role and public interface. The current source receives the victim's pre-mutation team directly from `player_die`, performs the retail-style team flip/infection bookkeeping under the active-controller gate, refreshes userinfo/events, and routes completion through the recovered counts-driven helper chain.
- `Cmd_ReadyUp_f` and `Cmd_AllReady_f` are source-faithful outer command boundaries, and the current source now preserves the dedicated Quake Live-style ready latch directly in `gclient_t` before mirroring it into the visible playerstate bits and the published `rp` configstring field.
- `AddTournamentPlayer` and `RemoveTournamentLoser` are source-faithful queue boundaries, but the surrounding retail tournament flow is still split more aggressively than GPL, including the descriptive selector/helper layer around them and the retail-only award publisher at `0x100559E0`.
- `G_UpdateTournamentQueuePositions` and `G_SyncTournamentQueueTeamTasks` are descriptive retail-only queue helpers. The current source now preserves that queue sidecar directly: the waiting-spectator eligibility predicate is shared across queue selection and queue-position sorting, `ClientUserinfoChanged` publishes the recovered `rp` / `p` / `so` / `pq` slab, and the queue helper mirrors dirty `pq` positions, including zero clears, back through `teamtask` for HUD/UI compatibility.
- `G_CheckReadyUpDelayAction` at `0x10058580` is a descriptive retail-only helper name. The current source now preserves that standalone `g_warmupReadyDelay` / `g_warmupReadyDelayAction` controller, including the cached ready-up tally consumed by `CheckTournament`, the spectate-only branch for the unready duelist, and the forced ready-latch clears when retail drops warmup back to `PRE_GAME`.
- The 2026-06-12 warmup-state wiring pass keeps `G_SetWarmupTime` as the shared source boundary for public warmup deadline mutations. Duel lifecycle reset/countdown, round-controller waiting/countdown/live transitions, timeout pause adjustment, auto-shuffle countdown clamping, Freeze warmup expiry, and admin abort now route through that helper so `CS_WARMUP`, ready-up deadline publication, auto-record state, and `g_gameState` stay coupled. The only remaining direct mutation is the documented internal `G_RequestWarmupMapRestart` grace bump immediately before `map_restart 0`.
- `BeginIntermission` at `0x10056CB0` is broader than the stock GPL helper: in the retail build it also clears vote state through `G_ClearVoteState` and bundles extra `nextmaps` setup/configstring work after the core intermission transition.
- `ExitLevel` at `0x10057000` is likewise broader than the stock GPL helper: the retail build honors `sv_killserver` / `sv_quitOnExitLevel`, clears `CS_INTERMISSION`, resolves `nextmaps`, falls back to `map_restart 0` when needed, clears extra intermission/vote state, and still preserves the stock tournament-loser restart path.
- `Cmd_Forfeit_f` at `0x100456B0` is only a thin client-facing gate. The current source now mirrors the retail helper split: pause/countdown rejection stays in the command wrapper, duel surrender score marking lives in `G_CanForfeit`, and the final broadcast/log path is handled by `G_ApplyForfeit`.
- `G_UpdateVoteCounts`, `G_TryExecuteVoteString`, and `G_ClearVoteState` are now preserved as real `g_vote.c` helpers and are wired back into `g_main.c::CheckVote`, the intermission bootstrap, and the vote-cancel command path. `G_CanForfeit` is likewise preserved as a real command-side helper reached by both `Cmd_Forfeit_f` and `g_main.c::CheckExitRules`.
- `CheckVote` at `0x100591B0` is a clean outer boundary, but retail keeps the tally, special-vote execution, and vote-state clearing work split into the adjacent helper trio rather than inlining it all into one GPL-shaped body.
- `G_RunThink` at `0x10059370` is slightly fatter than the stock GPL helper because it services an additional callback slot at `ent + 0x2FC` before the usual `nextthink` / `ent->think` dispatch. The source overlay now names that slot as `ql_gentity_t::runFrame` with an explicit `0x2FC` offset assertion.
- `Team_HasMinimumPlayersForWarmup` at `0x10068140` is source-faithful on its outer boundary. Retail feeds it through the same `TeamCount` primitive used by `SetTeam`, but the committed decomp still obscures the low-level register-passed ignore-client argument on that helper.

## Open Questions

- No high-confidence unresolved function seams remain in the current curated qagame control surface. Remaining work in qagame is now low-confidence annotation cleanup or broader runtime verification rather than an active helper/boundary recovery gap.
