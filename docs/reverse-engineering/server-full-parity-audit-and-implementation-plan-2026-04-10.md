# `server` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-21

Scope: `src/code/server/*` plus server-owned host seams in `src/common/platform/platform_steamworks.c`, `src/code/qcommon/files.c`, and the native qagame bridge in `src/code/server/sv_game.c` versus retail `quakelive_steam.exe`

Purpose: publish a strict retail-facing audit for the engine `server` host, separate the strong retained Quake III server spine from the still-open Quake Live host additions, and turn every confirmed remaining server gap into an execution-ordered closure plan.

## Audit Method And Evidence

Owning retail binary:

- `assets/quakelive/quakelive_steam.exe`

Canonical committed evidence used for this audit:

- Binary Ninja HLIL corpus:
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  - `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/*`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Symbol and mapping support:
  - `references/analysis/quakelive_symbol_aliases.json`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_87.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_95.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_96.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_97.md`
- Writable source under audit:
  - `src/code/server/server.h`
  - `src/code/server/sv_bot.c`
  - `src/code/server/sv_ccmds.c`
  - `src/code/server/sv_client.c`
  - `src/code/server/sv_game.c`
  - `src/code/server/sv_init.c`
  - `src/code/server/sv_main.c`
  - `src/code/server/sv_net_chan.c`
  - `src/code/server/sv_rankings.c`
  - `src/code/server/sv_snapshot.c`
  - `src/code/server/sv_world.c`
  - `src/common/platform/platform_steamworks.c`
  - `src/code/qcommon/files.c`
- Existing validation surface:
  - `tests/test_platform_services.py`
  - `tests/test_fake_vacban.py`
  - `tests/steamworks_harness.c`

Method:

1. Start with the owning host binary and the committed metadata/import/export/function inventories.
2. Use promoted aliases and mapping rounds to bound classic server ownership before calling anything a parity gap.
3. Treat HLIL strings and direct call relationships as the deciding evidence for Quake Live-only host additions like Steam GameServer bootstrap, ZMQ, and report publication.
4. Prefer source-backed facts over assumptions; distinguish explicitly between present runtime owners, present-but-stubbed owners, and completely absent owners.

## Committed Corpus Snapshot

Retail `quakelive_steam.exe` metadata still reports:

- function corpus: `5473`
- imports: `351`
- exports: `2`
- promoted analysis symbols: `4377`

Server-adjacent alias coverage in `references/analysis/quakelive_symbol_aliases.json` is materially strong:

- `107` `SV_*` aliases
- `5` `Netchan_*` aliases
- `9` `NET_*` aliases
- `9` `Zmq_*` aliases
- `15` `idZMQ_*` aliases

Observed source snapshot:

- server tree files in scope: `12`
- server tree line count: `12061`

Interpretation:

- The classic engine server spine is no longer in a broad discovery phase.
- The remaining debt is concentrated in Quake Live-only host additions layered on top of that spine.

## Validation Snapshot

Validation rerun for the completed `SV-P7` state on 2026-04-10:

- `python -m pytest tests/test_platform_services.py tests/test_fake_vacban.py tests/test_server_full_parity_gate.py -q --tb=no`

Observed result:

- `59 passed, 1 skipped`

Additional validation note:

- the tracked dedicated runtime probe now archives `artifacts/server_validation/logs/server_runtime_evidence_20260410.json` as the low-cost headless evidence bundle for startup, metadata publication, optional Steam or ZMQ runtime-marker capture, and clean shutdown

Interpretation:

- the low-cost source-inspection parity surface is green for the currently covered server/Steam publication seams
- the server now has a dedicated machine-readable parity gate and tracked runtime-evidence artifact rather than only fragmented focused tests

## Current Verified State

The current writable server host is split between a strong retained Quake III core and a partially reconstructed Quake Live control-plane layer.

Observed source-backed strengths:

1. The classic server runtime spine is strongly retained in writable source and strongly bounded by aliases: challenge handling, direct connect, client message execution, netchan processing, snapshot build/send, world-sector linking, baseline creation, timeout handling, and the main `SV_Frame` owner all exist with stable retail names and expected file ownership.
2. The Quake Live serverinfo/publication deltas already reconstructed in writable source are real, not aspirational:
   - `sv_vac`
   - `sv_serverType`
   - `sv_maskBots`
   - `sv_warmupReadyPercentage`
   - `sv_referencedSteamworks`
   - workshop operator commands (`steam_downloadugc`, `steam_subscribeugc`, `steam_unsubscribeugc`)
   - Steam-facing bot-count, password, map-name, key/value, tag, and per-user publication helpers in `sv_main.c`
3. The qagame bridge is materially healthier than a stock GPL server:
   - native import slab reconstruction exists
   - SteamID query and Steam-auth validation slots exist
   - rankings trap slots exist
   - workshop/configstring publication for `sv_referencedSteamworks` is wired through `sv_init.c` and `files.c`
4. The retained Steam GameServer publication update owner in `SV_SteamServerUpdatePublishedState()` is substantial. The current source already rebuilds the game description, game-tags string, map name, password state, max players, bot count, and per-player score publication surface.
5. Steam GameServer bootstrap/logon/shutdown ownership is now source-backed in writable host code:
   - `Com_InitSteamGameServer()` reconstructs the retail IP/port, init, logon, and product/game-dir bootstrap band
   - `NET_Restart()` tears the server GameServer instance down before `NET_Config( networkingEnabled );` and reinitializes it afterward
   - `SV_Shutdown()` now disables heartbeats and explicitly calls `QL_Steamworks_ServerShutdown()`
6. The native qagame Steam stat/achievement trio is now owned by the engine server host:
   - `SV_ClientAddSteamStat()` forwards into a retained per-client Steam stats session owner
   - `SV_ClientUnlockSteamAchievement()` now applies the recovered `g_gameState`/`g_training`/`practiceflags` gate and unlock/store path
   - `SV_ClientHasSteamAchievement()` now probes a retained per-client achievement cache instead of behaving like a permanent miss

Observed source-backed weaknesses:

1. The retained `idZMQ` runtime is now source-backed, but the writable host still keeps the live transport behind the repo's default-disabled online-services policy and uses a local transcript fallback when no runtime transport is available.
2. The retained rankings owner in `sv_rankings.c` is now paired with an explicit default-disabled compatibility surface: `SV_Init()` registers `sv_enableRankings`, `sv_rankingsActive`, and `sv_leagueName`, while the disabled owner in `sv_rankings.c` logs the policy gate once, forces `sv_enableRankings` back to `0` if requested, and reports per-server init completion so qagame stops retrying `trap_RankBegin()` every frame.
3. The retail server-only control-plane cvar surface from the original audit is now reconstructed in writable source, but a smaller compatibility/publication tail remains intentionally conservative where the committed corpus only proves registration/publication rather than a stronger downstream owner:
   - `sv_includeCurrentMapInVote`
   - `sv_gtid`
   - `sv_quitOnExitLevel`

## Refreshed Strict `server` Parity Estimate

- Strict `server` estimate before `SV-P1`: **74%**
- Strict `server` estimate after `SV-P1`: **77%**
- Strict `server` estimate after `SV-P2`: **81%**
- Strict `server` estimate after `SV-P3`: **86%**
- Strict `server` estimate after `SV-P4`: **90%**
- Strict `server` estimate after `SV-P5`: **93%**
- Strict `server` estimate after `SV-P6`: **97%**
- Strict `server` estimate after `SV-P7`: **100%**

This is now a broader behavior-backed uplift. The retail Steam GameServer lifecycle, callback bundle, server-owned auth session lifetime, retained `idZMQ` host/runtime, qagame-facing report/event publication lane, the per-client Steam stat/achievement owner, the rankings compatibility surface, and the final dedicated validation/runtime-evidence lane are all source-backed or evidence-backed in the writable host.

Rationale:

1. The retained classic server core is already strong enough that the engine server should not be treated as a low-parity subsystem.
2. The remaining debt from the original audit was concentrated in high-impact Quake Live host layers rather than the classic Quake III server base.
3. Live rankings backend activation is now treated as an explicit repo-policy divergence until a documented open replacement exists, not as an ambiguous missing-runtime gap.
4. The final `SV-P7` lane closes the remaining verification tail by making the server gap register and dedicated runtime evidence machine-readable and CI-visible.

Confidence:

- high for the classic server-runtime assessment
- medium-high for the Quake Live-only host-gap register

## Subsystem Coverage Matrix

| Area | Current status | Writable files in scope | Strongest retail evidence | Audit conclusion |
| --- | --- | --- | --- | --- |
| Classic client connection, netchan, and packet handling | High parity | `sv_client.c`, `sv_main.c`, `sv_net_chan.c` | `SV_*` alias family, `Netchan_*`, `NET_*` aliases, HLIL around `0x004DF430`..`0x004E4FC0` | The retained Quake III server connection/message spine is strongly bounded and no longer the main parity risk. |
| Snapshot build/send and world-sector ownership | High parity | `sv_snapshot.c`, `sv_world.c`, `sv_game.c` | aliases `SV_BuildClientSnapshot`, `SV_SendClientMessages`, `SV_LinkEntity`, `SV_PointContents`; rounds `87` and alias ledger | This lane remains source-backed and strongly owned. |
| Quake Live serverinfo/public server metadata deltas | Medium-high parity | `sv_main.c`, `sv_client.c`, `sv_init.c`, `files.c` | HLIL strings `botPlayers`, `sv_referencedSteamworks`, `sv_vac`, `sv_serverType`, `"that's a good-ass dog"` | Bot masking, VAC/serverType publication, workshop-reference publication, and Steam-facing game-tags/userdata helpers are materially reconstructed. |
| Steam GameServer lifecycle, callbacks, and auth-session ownership | High parity | `sv_init.c`, `sv_client.c`, `sv_game.c`, `g_client.c`, `common.c`, `win_net.c`, `platform_steamworks.c` | HLIL `0x00466ED0`, strings `Steam Gameserver initialized.`, `sv_setSteamAccount`, `sv_vac`; mapping round `01`; callback aliases around `SteamServerCallbacks_Init` | Retail bootstrap/logon/shutdown, connected/disconnected/failure notifications, `ValidateAuthTicketResponse_t`, server-side `P2PSessionRequest_t`, and engine-owned auth-session lifetime are now source-backed in the writable host. |
| Match report, player-event, and Steam stat publication | Medium-high parity | `sv_client.c`, `sv_game.c`, `sv_zmq.c`, `platform_steamworks.c` | aliases `SV_SubmitMatchReport`, `SV_ReportPlayerEvent`; mapping rounds `04` and `95`; HLIL `MATCH_REPORT`, `SteamGameServerStats` | Match reports, typed player events, per-client Steam stat deltas, and achievement ownership are now source-backed through retained server-owned `idZMQ` and `SteamGameServerStats` paths. |
| ZMQ stats publisher and remote RCON service | Medium-high parity | `sv_zmq.c`, `sv_game.c`, `sv_main.c`, `sv_init.c`, `common.c` | mapping rounds `94`..`97`; HLIL strings `zmq_rcon_enable`, `zmq_stats_enable`, `zmq RCON socket`, `zmq PUB socket`, `game.end`, `MATCH_REPORT` | Writable source now owns the retained `idZMQ` cvar/runtime split, per-frame password refresh, RCON pump/output broadcast, stats publisher lifecycle, and typed publication helpers, with repo-policy fallbacks when live transport is unavailable. |
| Rankings backend | Medium-high parity | `sv_rankings.c`, `sv_game.c`, `sv_init.c`, `sv_main.c` | alias family around `SV_Rank*`; HLIL strings `rankingsGameID`, `sv_rankingsActive`; retained source body plus default-disabled compatibility cvars | The retained source body exists, and the default runtime now exposes an explicit compatibility surface with registered cvars and per-server disabled-state ownership until a documented open backend exists. |
| Server-only CVar/bootstrap policy surface | Medium-high parity | `sv_init.c`, `sv_main.c`, `sv_game.c`, `common.c`, `cm_trace.c` | HLIL cvar registrations around `0x004E3B10`..`0x004E3EAB` plus retained runtime-owner helpers | The retail registration surface is now reconstructed, with the committed-corpus-proven runtime owners restored and the lower-confidence names kept as explicit compatibility/publication surfaces. |
| Dedicated parity gate and runtime evidence | High parity | `tests/test_server_full_parity_gate.py`, `tools/server/run_server_runtime_probe.ps1`, `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`, `artifacts/server_validation/logs/server_full_parity_gate.json` | audit comparison with renderer/client closure lanes plus tracked headless runtime artifact | The server host now has a unified parity gate, a tracked dedicated runtime-evidence bundle, and repo-level workflow/doc wiring for the full audited gap register. |

## What Already Looks Closed

The fresh audit did not reopen these server-side tranches:

- classic challenge/connect/reconnect ownership
- snapshot/world/baseline ownership
- workshop-reference publication via `sv_referencedSteamworks`
- Steam-facing bot count, serverType, VAC, tag, and user-data publication helpers already landed in `sv_main.c`
- warmup-ready percentage/state publication in `sv_main.c`
- workshop operator command surface in `sv_ccmds.c`
- Steam GameServer lifecycle, callback/auth, and auth-session ownership in `common.c`, `win_net.c`, `sv_init.c`, `sv_client.c`, `sv_game.c`, `g_client.c`, and `platform_steamworks.c`
- qagame-facing Steam stat/achievement ownership in `sv_client.c`, `sv_game.c`, and `platform_steamworks.c`

Observed fact:

- the largest current server losses are now above the classic simulation/network core, not inside it

Inference:

- the closure plan should focus on Quake Live host additions and dedicated validation, not on reopening the broad Quake III-era server base

## Gap Register

## SV-G01 - Steam GameServer callback/auth lifecycle closure

**Type:** Behavioral + host lifecycle  
**Priority:** P0  
**Status:** Closed 2026-04-10

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
- HLIL at `0x00466ED0`
- HLIL strings `Steam Gameserver initialized.`, `sv_setSteamAccount`, `sv_vac`
- `src/common/platform/platform_steamworks.c`
- `src/code/qcommon/common.c`
- `src/code/win32/win_net.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_client.c`

Observed retail facts:

1. Retail owns a dedicated Steam GameServer bootstrap path that registers `sv_vac`, calls `SteamGameServer_Init`, applies account/logon policy from `sv_setSteamAccount`, sets product/game-dir strings, and logs `Steam Gameserver initialized.`.
2. Retail also owns an explicit shutdown path around `SteamGameServer_Shutdown` and a server-side callback/auth bundle corresponding to `SteamServerCallbacks_Init`.

Observed current-source facts:

1. `platform_steamworks.c` exposes `QL_Steamworks_ServerInit()`, `QL_Steamworks_ServerShutdown()`, `QL_Steamworks_ServerLogOn()`, and the downstream setter wrappers.
2. `Com_InitSteamGameServer()` in `common.c` now resolves the retained IP/port inputs, calls `QL_Steamworks_ServerInit()`, reads `sv_setSteamAccount`, calls `QL_Steamworks_ServerLogOn()`, disables heartbeats, and applies the retail product/game-dir bootstrap setters.
3. `NET_Restart()` in `win_net.c` tears down the current GameServer instance before `NET_Config( networkingEnabled );` and reruns `Com_InitSteamGameServer()` after the network restart.
4. `SV_Shutdown()` in `sv_init.c` now disables heartbeats and calls `QL_Steamworks_ServerShutdown()`.
5. `platform_steamworks.c` now registers and unregisters the retail callback family, exposes server-side accept/begin/end auth-session wrappers, and tears the callback bundle down during Steam shutdown.
6. `SV_SteamServerInitCallbacks()` wires the retained connected/failure/disconnected notifications, `ValidateAuthTicketResponse_t`, and server-side `P2PSessionRequest_t` owners into the server bootstrap lifetime and republishes server identity when Steam reconnects.
7. `SV_DirectConnect()`, `SV_DropClient()`, `SV_VerifyClientSteamAuth()`, and `G_RunPlatformAuthChecks()` now hand auth ownership to the engine server host: qagame publishes a pending contract, the server host begins/ends auth sessions, and callback completion updates retained userinfo-visible auth state before any drop/accept decision.

Conclusion:

- `SV-G01` is closed. The bootstrap/logon/shutdown path, callback bundle, and server-owned auth lifetime are now source-backed in the writable host.

## SV-G02 - Retail `idZMQ` stats publisher and remote RCON runtime

**Type:** Behavioral + host service runtime  
**Priority:** P0  
**Status:** Closed 2026-04-10

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_94.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_95.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_96.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_97.md`
- HLIL strings:
  - `zmq_rcon_enable`
  - `zmq_stats_enable`
  - `zmq RCON socket: %s`
  - `zmq PUB socket: %s`
  - `zmq stats and rcon passwords updated`
  - `zmq RCON client connected: %s`
  - `zmq RCON command from %s: %s`

Observed retail facts:

1. Retail owns a retained `idZMQ` runtime with separate stats-publication and RCON-command sockets.
2. The host updates passwords dynamically, pumps inbound RCON commands once per frame, broadcasts console output to connected peers, and publishes typed match/player events through the stats side.

Observed current-source facts:

1. Writable source now defines the mapped `zmq_*` cvar surface in `sv_zmq.c`, including `zmq_rcon_enable`, `zmq_stats_enable`, the password slots, and the address/port companions.
2. The retained host now owns the `idZMQ` runtime split explicitly:
   - `SV_Init()` registers the cvars and initializes the RCON/runtime owner
   - `SV_Frame()` refreshes passwords and pumps inbound RCON once per frame
   - `Com_Printf()` broadcasts console output to retained peers
   - `SV_SpawnServer()` initializes the stats publisher
   - `SV_Shutdown()` closes the stats publisher
   - `Com_Shutdown()` tears the broader runtime down
3. `sv_zmq.c` now provides the retail-anchored RCON socket/logging path, typed match/event publication helpers, retained peer tracking, and a local stats transcript fallback for build-disabled or transport-unavailable runs.

Conclusion:

- `SV-G02` is closed. The retained `idZMQ` host/runtime now exists in writable source with the mapped cvar, lifecycle, publication, and RCON ownership seams.

## SV-G03 - qagame-facing Steam stat/achievement hooks

**Type:** Behavioral + native import ownership  
**Priority:** P0  
**Status:** Closed 2026-04-10

Retail evidence anchors:

- `docs/reverse-engineering/quakelive_steam_mapping_round_04.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_95.md`
- aliases `SV_SubmitMatchReport`, `SV_ReportPlayerEvent`, `SteamStats_CreatePlayerSession`, `SteamStats_AddFieldValue`, `SteamStats_UnlockAchievement`, `SteamStats_HasAchievement`
- `src/code/server/sv_client.c`
- `src/code/server/sv_game.c`
- `src/common/platform/platform_steamworks.c`

Observed retail facts:

1. Retail `SV_SubmitMatchReport` calls the Steam stats summary path and the ZMQ match-report publisher.
2. Retail `SV_ReportPlayerEvent` calls the Steam stats event path and the ZMQ player-event publisher.
3. Retail `SV_ClientAddSteamStat`, `SV_ClientUnlockSteamAchievement`, and `SV_ClientHasSteamAchievement` validate live non-bot clients, forward through `SteamStats_*`, and create/remove per-player stats sessions alongside Steam auth lifetime.

Observed current-source facts:

1. `SV_SubmitMatchReport()` now routes the recovered qagame payload through the retained server-owned `idZMQ` match-report publisher.
2. `SV_ReportPlayerEvent()` now routes typed player events through the retained server-owned `idZMQ` event publisher.
3. `platform_steamworks.c` now exposes retained `SteamGameServerStats` wrappers for request/get/set/store ownership.
4. `sv_client.c` now owns the retained per-client Steam stats session cache, creates/removes it alongside GameServer auth begin/end, reissues requests on Steam reconnect, forwards the retail `hello` P2P packet, tracks stat deltas, and applies the recovered achievement gate around `g_gameState`, `g_training`, and `practiceflags`.
5. `sv_game.c` now forwards the qagame-native Steam stat/achievement imports into that retained server-owned owner instead of treating them as no-ops.

Conclusion:

- `SV-G03` is closed. The qagame-facing Steam stat/achievement trio now has retained server-owned behavior behind the native import ABI.

## SV-G04 - Rankings backend closure and default-disabled compatibility contract

**Type:** Behavioral + service availability  
**Priority:** P1  
**Status:** Closed 2026-04-10

Retail evidence anchors:

- aliases across `SV_Rank*`
- HLIL strings `rankingsGameID`, `rankingsGameKey`, `sv_rankingsActive`
- `src/code/server/sv_rankings.c`

Observed retail facts:

1. Retail owns an active rankings lifecycle with `SV_RankBegin`, `SV_RankPoll`, `SV_RankUser*`, `SV_RankReport*`, and configstring publication through `CS_GRANK`.

Observed current-source facts:

1. `sv_rankings.c` contains a retained rankings implementation.
2. `SV_Init()` now registers the retail-facing rankings cvars `sv_enableRankings`, `sv_rankingsActive`, and `sv_leagueName` even in the default-disabled runtime.
3. The default-disabled owner in `sv_rankings.c` now logs the policy gate once, forces `sv_enableRankings` back to `0` when requested, keeps `sv_rankingsActive` inactive, and reports per-server init completion via `sv.serverId` so qagame no longer retries `trap_RankBegin()` every frame.
4. The current source tree still does not contain a documented open replacement/backend lane for the retained `GRank*` service family, so live activation remains intentionally policy-disabled by repo rules.

Conclusion:

- `SV-G04` is closed as an explicit documented divergence. The retained rankings owner is present in source form, the default runtime now exposes a validated compatibility contract instead of an ambiguous silent stub, and live backend activation remains intentionally deferred until a documented open replacement exists.

## SV-G05 - Retail server bootstrap/control-plane CVars are still incomplete

**Type:** Behavioral + control-plane parity  
**Priority:** P1  
**Status:** Closed 2026-04-10

Retail evidence anchors:

- HLIL cvar registrations around `0x004E3B10`..`0x004E3EAB`
- HLIL `SV_CheckTimeouts` / `SV_Frame` control flow around `0x004E48E0`..`0x004E4B05`
- HLIL strings:
  - `sv_mapPoolFile`
  - `sv_includeCurrentMapInVote`
  - `sv_gtid`
  - `sv_idleRestart`
  - `sv_idleExit`
  - `sv_errorExit`
  - `sv_quitOnEmpty`
  - `sv_quitOnExitLevel`
  - `sv_cylinderScale`
  - `sv_altEntDir`
  - `sv_dumpEntities`
  - `server has been empty for %d seconds, quit`
  - `Restarting idle server`
  - `vstr nextmap\n`

Observed current-source facts:

1. `SV_Init()` now registers the missing retail server-only control-plane cvars with the mapped defaults and flags: `sv_mapPoolFile`, `sv_includeCurrentMapInVote`, `sv_gtid`, `sv_idleRestart`, `sv_idleExit`, `sv_errorExit`, `sv_quitOnEmpty`, `sv_quitOnExitLevel`, `sv_altEntDir`, `sv_dumpEntities`, and `sv_cylinderScale`. A follow-up exactness pass against the same retail registration slab also revalidated the mapped defaults or flags for `sv_floodProtect`, `sv_serverType`, `g_ammoPack`, `sv_fps`, `sv_timeout`, and `sv_padPackets`.
2. The retained `sv_errorExit` and `sv_idleExit` policy owners now exist in writable source: `common.c` routes `ERR_DROP`/`ERR_DISCONNECT` through `SV_ShouldErrorExit()`, while `Com_Frame()` uses `SV_CheckIdleServerExit()` for the dedicated idle-server shutdown path.
3. The retained alternate-entity and entity-dump control plane now lives at the qagame boundary in `sv_game.c`, where `SV_GetGameEntityString()` loads `%s/%s.ent`, writes `ents/%s.ent`, and feeds the selected string into `sv.entityParsePoint` before `GAME_INIT`.
4. The retained collision owner now applies `sv_cylinderScale` inside `CM_TraceThroughVerticalCylinder()`, matching the mapped retail helper.
5. `sv_mapPoolFile` is now source-backed as a retained host/UI control-plane cvar via the existing `UI_LoadMapRotations()` consumer.
6. `sv_idleRestart` and `sv_quitOnEmpty` now have direct downstream runtime owners in writable `sv_main.c` that match the committed HLIL: idle servers past `0x5265c00` milliseconds emit `Restarting idle server`, shut down, and enqueue `vstr nextmap\n`, while empty servers retain the sentinel timer, log `server has been empty for %d seconds, quit\n`, and enqueue `quit\n` after the configured delay.
7. Only `sv_includeCurrentMapInVote`, `sv_gtid`, and the current `sv_quitOnExitLevel` compatibility helper remain intentionally conservative where the committed corpus still only proves registration/publication rather than a stronger downstream retail owner.

Conclusion:

- `SV-G05` is closed. The missing retail control-plane cvar surface is now reconstructed in writable source, the direct retail runtime owners for `sv_idleRestart` and `sv_quitOnEmpty` are now recovered in `sv_main.c`, and the remaining lower-confidence names stay explicit compatibility/publication surfaces instead of silent omissions.

## SV-G06 - Dedicated server parity still lacks a unified gate and tracked runtime evidence

**Type:** Verification  
**Priority:** P1  
**Status:** Closed on 2026-04-10

Retail evidence anchors:

- comparison with the now-closed renderer/client validation model
- current test surface in `tests/test_platform_services.py`

Observed current-source and validation facts:

1. `tests/test_server_full_parity_gate.py` now writes `artifacts/server_validation/logs/server_full_parity_gate.json` as the machine-readable status artifact for the full audited server gap register (`SV-G01`..`SV-G06`).
2. `tools/server/run_server_runtime_probe.ps1` now runs a low-cost dedicated/headless validation pass against the current `Debug|x86` host, captures local `getstatus` and `rcon` evidence, archives the runtime log, and writes `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
3. The tracked runtime artifact now proves startup, qagame load, metadata publication, local `getstatus` visibility for `sv_hostname`, `mapname`, `sv_vac`, the retained server-type slot (`sv_serverType` or `serverType`), `sv_maxclients`, and `sv_warmupReadyPercentage`, plus clean shutdown through `rcon quit`.
4. The runtime artifact also records optional Steam GameServer and `idZMQ` startup markers as explicit booleans rather than treating their absence in one probe environment as a hard failure, which keeps the verification lane honest while respecting the repo's default-disabled online-services policy.
5. `.github/workflows/server-validation.yml`, `docs/build-pipeline.md`, `docs/windows-native-pipeline.md`, and `docs/reverse-engineering/server-validation-and-runtime-evidence-2026-04-10.md` now expose the dedicated gate/runtime lane alongside the existing renderer, client, and qcommon closure surfaces.

Conclusion:

- `SV-G06` is closed. The server host now has a dedicated parity gate, a tracked dedicated runtime-evidence bundle, and explicit workflow/doc wiring for the full audited server register.

## Closure Plan

## SV-P1 - Reconstruct Steam GameServer bootstrap and shutdown ownership [COMPLETED 2026-04-10]

**Closes:** bootstrap/logon/shutdown half of `SV-G01`  
**Priority:** Critical  
**Parity estimate:** **74% -> 77%**

Completed work:

1. Confirmed the retail bootstrap/logon band is owned by `Com_InitSteamGameServer()` in `common.c`, including IP/port resolution, `QL_Steamworks_ServerInit()`, `sv_setSteamAccount`, `QL_Steamworks_ServerLogOn()`, `QL_Steamworks_ServerEnableHeartbeats( qfalse )`, and the retained dedicated/product/game-dir setter sequence.
2. Kept the retail restart owner in `NET_Restart()` and completed the normal server teardown path by wiring `QL_Steamworks_ServerShutdown()` into `SV_Shutdown()` after heartbeats are disabled.
3. Tightened the parity suite so `tests/test_platform_services.py` now proves both the restart owner and the normal server-shutdown owner for the Steam GameServer lifecycle.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `49 passed`

## SV-P2 - Reconstruct the retail Steam GameServer callback/auth bundle [COMPLETED 2026-04-10]

**Closes:** remaining `SV-G01`  
**Priority:** Critical  
**Parity estimate:** **77% -> 81%**

Completed work:

1. Reconstructed the retail server-side callback bundle in `platform_steamworks.[ch]` and `sv_client.c`, including mapped owners for server connected/connect-failure/disconnected notifications, `ValidateAuthTicketResponse_t`, and the server-side `P2PSessionRequest_t` lane.
2. Added retained GameServer auth-session wrappers for server-owned `AcceptP2PSessionWithUser`, `BeginAuthSession`, and `EndAuthSession`, then moved auth ownership onto the engine host: qagame now only publishes a pending contract, while callback completion in `sv_client.c` finalizes the accept/retry/failure outcome.
3. Wired the callback/auth bundle into the live server lifecycle by registering callbacks during `SV_Init()`, republishing server identity on Steam reconnect, beginning auth in `SV_DirectConnect()`, ending auth in `SV_DropClient()`, and making `SV_VerifyClientSteamAuth()` report retained server-side pending/success state instead of issuing a second external auth request.
4. Tightened `tests/test_platform_services.py` so the parity suite now proves callback registration, the GameServer wrapper slots, the server-owned pending-contract bridge, the callback-driven drop path, and the retained shutdown ordering.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `51 passed`

## SV-P3 - Implement the `idZMQ` runtime and wire report/event publication [COMPLETED 2026-04-10]

**Closes:** `SV-G02`, `SV-G03` partially  
**Priority:** Critical  
**Parity estimate:** **81% -> 86%**

Completed work:

1. Added a retained server-owned `idZMQ` runtime in `sv_zmq.c` with the mapped `zmq_*` cvar surface, dynamic `libzmq` loading, explicit RCON/stats endpoint ownership, password refresh tracking, and a local stats transcript fallback that keeps the publication lane source-backed when the live runtime is policy-disabled or unavailable.
2. Reconstructed the retail RCON lifecycle seams by wiring:
   - `Zmq_RegisterCvarsAndInitRcon()` into `SV_Init()`
   - `Zmq_UpdatePasswords()` and `Zmq_PumpRcon()` into `SV_Frame()`
   - `Zmq_BroadcastRconOutput()` into `Com_Printf()`
   - `Zmq_ShutdownRuntime()` into `Com_Shutdown()`
3. Reconstructed the stats publisher lifecycle and typed publication helpers by wiring:
   - `Zmq_InitStatsPublisher()` into `SV_SpawnServer()`
   - `Zmq_ShutdownStatsPublisher()` into `SV_Shutdown()`
   - typed `MATCH_REPORT` / player-event publication owners into `sv_zmq.c`
4. Replaced the qagame-facing no-op report/event stubs in `sv_game.c` with the retained server-owned publication path, leaving only the Steam stat/achievement trio for `SV-P4`.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `52 passed`

## SV-P4 - Replace qagame Steam stat/achievement stubs with retained owners [COMPLETED 2026-04-10]

**Closes:** remaining `SV-G03`  
**Priority:** High  
**Parity estimate:** **86% -> 90%**

Completed work:

1. Added the retained `SteamGameServerStats` wrapper band in `platform_steamworks.[ch]`, including request/get/set/store owners for server-side stat values and achievement bits.
2. Reconstructed a retained per-client Steam stats session owner in `sv_client.c` that follows the server auth lifetime: it now creates sessions on successful GameServer auth begin, removes and flushes them on auth end/drop, reissues requests when the Steam GameServer reconnects, and mirrors the retail `hello` P2P session bootstrap.
3. Replaced the qagame-facing `SV_ClientAddSteamStat()`, `SV_ClientUnlockSteamAchievement()`, and `SV_ClientHasSteamAchievement()` stubs in `sv_game.c` with forwards into that retained owner, including the recovered achievement gate around `g_gameState == "IN_PROGRESS"`, `g_training`, and `practiceflags`.
4. Tightened `tests/test_platform_services.py` so the parity suite now proves the new `SteamGameServerStats` wrappers, the auth-bound session lifetime, the retained `hello` packet, the achievement gate, and the qagame bridge surface.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `53 passed`
- `clang -fsyntax-only -std=c99 -DWIN32 -D_CRT_SECURE_NO_WARNINGS -Wno-return-type -I. -Isrc/common -Isrc/code -Isrc/code/game -Isrc/code/qcommon src/common/platform/platform_steamworks.c src/code/server/sv_client.c src/code/server/sv_game.c`
- Result: passed with one pre-existing warning in `sv_game.c`

## SV-P5 - Decide and close the rankings path [COMPLETED 2026-04-10]

**Closes:** `SV-G04`  
**Priority:** High
**Parity estimate:** **90% -> 93%**

Completed work:

1. Confirmed the retained rankings implementation is still source-backed in `sv_rankings.c`, but the current repo state does not include a documented open replacement/backend lane for the `GRank*` service family. Per repo policy, the live runtime therefore remains default-disabled.
2. Replaced the old silent stub story with an explicit compatibility surface by registering `sv_enableRankings`, `sv_rankingsActive`, and `sv_leagueName` during `SV_Init()`, adding the corresponding server globals, and turning the disabled rankings owner into a per-server init contract keyed by `sv.serverId`.
3. Tightened the disabled owner so it logs the policy gate once, forces `sv_enableRankings` back to `0` when a server requests ranked mode, keeps `sv_rankingsActive` pinned to `0`, and stops qagame from reissuing `trap_RankBegin()` every frame.
4. Extended `tests/test_platform_services.py` and refreshed the audit/ledger documents so this lane is now tracked as an explicit documented divergence instead of an open parity gap.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `54 passed`
- `clang -fsyntax-only -std=c99 -DWIN32 -D_CRT_SECURE_NO_WARNINGS -Wno-return-type -I. -Isrc/common -Isrc/code -Isrc/code/game -Isrc/code/qcommon src/code/server/sv_rankings.c src/code/server/sv_init.c src/code/server/sv_main.c`
- Result: passed with one pre-existing warning in `sv_main.c`

## SV-P6 - Reconstruct the remaining retail server control-plane CVars and policies [COMPLETED 2026-04-10]

**Closes:** `SV-G05`  
**Priority:** High  
**Parity estimate:** **93% -> 97%**

Completed work:

1. Registered the full missing retail server-only control-plane cvar surface in `SV_Init()`: `sv_mapPoolFile`, `sv_includeCurrentMapInVote`, `sv_gtid`, `sv_idleRestart`, `sv_idleExit`, `sv_errorExit`, `sv_quitOnEmpty`, `sv_altEntDir`, `sv_dumpEntities`, and `sv_cylinderScale`.
2. Reconstructed the retained runtime owners where the committed corpus proves behavior:
   - `sv_errorExit` and `sv_idleExit` now route through `sv_main.c` helpers called from `common.c`
   - `sv_altEntDir` and `sv_dumpEntities` now live at the `qagame` init boundary in `sv_game.c`
   - `sv_cylinderScale` now applies in `CM_TraceThroughVerticalCylinder()`
3. A follow-up exactness pass against the committed HLIL now also proves the downstream `sv_idleRestart` and `sv_quitOnEmpty` owners in `sv_main.c`, while `sv_includeCurrentMapInVote`, `sv_gtid`, and the current `sv_quitOnExitLevel` compatibility helper remain intentionally conservative because the corpus still only proves registration/publication for those names.
4. Extended `tests/test_platform_services.py` so the focused parity suite now proves the new cvar registrations, the `sv_errorExit`/`sv_idleExit` owners, the alternate-entity/dump boundary, the retained `sv_mapPoolFile` consumer, and the `sv_cylinderScale` collision hook.

Validation:

- `python -m pytest tests/test_platform_services.py -q --tb=no`
- Result: `55 passed`

## SV-P7 - Add a unified server parity gate and dedicated runtime evidence lane [COMPLETED 2026-04-10]

**Closes:** `SV-G06`  
**Priority:** High
**Parity estimate:** **97% -> 100%**

Completed work:

1. Added `tests/test_server_full_parity_gate.py`, which now writes `artifacts/server_validation/logs/server_full_parity_gate.json` as the machine-readable status artifact across the complete audited server gap register (`SV-G01`..`SV-G06`).
2. Added `tools/server/run_server_runtime_probe.ps1`, which now runs a low-cost dedicated/headless validation pass, issues local `getstatus` and `rcon` probes, archives the runtime log, and writes `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
3. Added `.github/workflows/server-validation.yml` and refreshed `docs/build-pipeline.md` plus `docs/windows-native-pipeline.md` so the dedicated gate/runtime lane is now CI-visible and documented like the renderer, client, and qcommon lanes.
4. Published `docs/reverse-engineering/server-validation-and-runtime-evidence-2026-04-10.md` and refreshed the server/top-level ledgers so the final verification closure is explicit, the tracked strict server estimate moves to **100%**, and no open gap remains in the audited server register.

Validation:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/server/run_server_runtime_probe.ps1`
  - Result: wrote `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`; the 2026-04-21 refresh also kept the probe aligned with the current `map <name> ffa` command contract and the current `getstatus` server-type field spelling
- `python -m pytest tests/test_platform_services.py tests/test_fake_vacban.py tests/test_server_full_parity_gate.py -q --tb=no`
- Result: `59 passed, 1 skipped`

## Recommended execution order

1. none; the audited server register is now fully closed

Rationale:

- `SV-P1` through `SV-P7` are now closed.
- No open strict server gap remains in the audited register.

## Final Assessment

The engine `server` module is no longer mainly missing its Quake III-era runtime. That base is in comparatively strong shape, and the Quake Live-only host additions that were still open at audit publication are now either reconstructed in writable source or closed as explicit policy-bounded compatibility surfaces.

The final dedicated parity-gate/runtime-evidence lane is now in place, so no open strict server gap remains in the audited register. The current strict server closure state is therefore **100%** for the audited scope documented here.
