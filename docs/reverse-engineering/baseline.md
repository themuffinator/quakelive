# Reverse Engineering Baseline

The initial symbol export covers the retail Quake Live client, dedicated server,
UI, and cgame modules. Data comes from the automated Ghidra workflow in
`ghidra_scripts/ExportSymbolMap.py`, normalized with
`references/analysis/quakelive_symbol_aliases.json` and captured in
`references/symbol-maps/`.

This baseline now sits alongside the committed OpenAlice-style Ghidra corpus under
`references/reverse-engineering/ghidra/`. Use the symbol manifests as a normalized
name and relocation view, but use the committed corpus plus HLIL dumps as the main
behavior and interface evidence set.

## Coverage snapshot

| Binary | Functions resolved / retired | Strings resolved / retired | Relocations captured |
| ------ | ------------------ | ---------------- | -------------------- |
| Client | 4 resolved, 1 retired / 5 | 4 resolved, 1 retired / 5 | 4 |
| Server | 4 resolved, 1 retired / 5 | 4 resolved, 2 retired / 6 | 5 |
| UI     | 4 / 5 | 4 / 5 | 4 |
| Cgame  | 154 / 154 | 168 / 168 | 0 |

Key metrics come directly from the `stats` nodes in the exported JSON manifests
(`client.json`, `server.json`, `ui.json`, `cgame.json`).

## Retired legacy seed rows

### Client
- The old `0x00445AB0` client seed row has been retired rather than carried as
  an unresolved Quake Live gap. The newer `quakelive_steam.exe` mapping rounds
  resolve the renderer/bootstrap surface through current host aliases including
  `CL_InitRenderer`, `CL_InitRef`, and `RE_RenderScene`; the old
  `render backend missing implementation` string is not a current retail host
  string in the committed Ghidra/HLIL corpus.

### Server
- The old `0x00412190` server seed row has been retired. The current
  function-to-function qagame map resolves the corresponding team-score and
  lead-change behavior through `AddTeamScore` at `0x100681B0`, with the
  surrounding retail scoreboard serialization covered by
  `G_BuildTeamScoreboardMessage` and `G_SendTDMStatsMessage`.

## Remaining baseline unknowns

### UI
- `UNRESOLVED_UI_func_0030F8A0` at `0x0030F8A0` references
  `UNRESOLVED_UI_str_0058F200` (“challenge hub update pending”). Investigate this
  dispatcher to uncover the new challenge/changelog systems.

### Cgame
- `docs/reverse-engineering/cgame-mapping.md` records the current `cgamex86.dll`
  naming pass and the three main mapping caveats: Ghidra claiming
  `0x10063D56 entry` as an export, HLIL exposing `CG_Init` at `0x10029820`
  while the committed Ghidra function inventory does not, and retail `dllEntry`
  reporting native API version `8` plus an export array whose slot order should
  not be assumed to match the legacy `cgameExport_t` enum without revalidation.
- The ledger now also covers the retail native entry table plus the HUD callback
  bridge through `Com_Printf`, `Com_Error`, `CG_RegisterCvars`,
  `CG_UpdateCvars`, `CG_Shutdown`, `CG_ConsoleCommand`, `CG_KeyEvent`,
  `CG_MouseEvent`,
  `CG_CrosshairPlayer`, `CG_LastAttacker`, `CG_EventHandling`,
  `CG_InitConsoleCommands`, the recovered command-table sweep from
  `CG_TargetCommand_f` through the order / task / taunt family, the retail
  `startOrbit` / chat-history / print / `clientmute` tail, the cross-file
  `loaddeferred` / zoom / weapon handlers, the retail-only drop / ready /
  team / forfeit / ragequit / team-color wrappers, the feeder helpers,
  ownerdraw-width, the retail `CG_DrawNewChatArea` / chat-reset path, the
  synthetic `CG_Cvar_GetString` bridge, the synthetic buffered-chat helper
  `CG_PushPrintString`, the synthetic tracked-slot helpers
  `CG_Show1stTrackedPlayer` / `CG_Show2ndTrackedPlayer`, the synthetic native-export helpers
  `CG_CopyClientIdentity`, `CG_GetChatFieldY`,
  `CG_GetChatFieldPixelWidth`, `CG_GetChatFieldWidthInChars`,
  `CG_SetClientSpeakingState`, `CG_GetPhysicsTime`, the synthetic HUD
  bootstrap helper `CG_InitDisplayContext`, and the full
  cinematic wrapper set
  including `CG_DrawCinematic`, in addition to the voice-chat / server-command
  cluster around `0x1004A4xx-0x1004ADxx`.
- The current pass also anchors the retail social/spectator sidecar more
  explicitly through `cg_trackPlayer`, the `1st_plyr_*` / `2nd_plyr_*`
  spectator-follow assets, `ui/assets/score/muted`,
  `ui/assets/score/speaking`, `ui/assets/voiceWindow`, and `ui_priv`, and now
  closes the native export tail through host `quakelive_steam.exe`
  `data_146cc38` callsites: the identity/speaking helpers, the native
  chat-input layout getters, and `CG_GetPhysicsTime`.
- The newest HUD/status tranche now also covers `CG_DrawKiller`,
  `CG_GetScoreboardTimerSeconds`, `CG_DrawCapFragLimit`,
  `CG_DrawClanArenaPlayers`, `CG_DrawPlayerCount`, `CG_DrawRoundLabel`,
  `CG_DrawDominationOwnedFlags`, the narrower retail `CG_DrawGameLimit`,
  `CG_DrawGameTypeIcon`, `CG_DrawFirstPlaceModel`, the synthetic
  `CG_DrawPlayerModel`,
  `CG_GetGameStatusText`, `CG_DrawGameStatus`, `CG_DrawGameType`,
  `CG_DrawMatchStatus`, `CG_DrawSpectatorMessages`, and the synthetic retail
  compositor `CG_GetMatchStatusText`, along with the match-state and spectator
  anchors such as `MATCH WARMUP`, `MATCH IN PROGRESS`, `MATCH SUMMARY`,
  `Warmup`, `Round %d`, `Round In Progress`, and `SPECTATOR MODE`.
- The current pass also recovers the intro/endgame ownerdraw tranche through
  `CG_DrawLevelTimer`, `CG_DrawStartingWeapons`, `CG_DrawLocalTime`,
  `CG_DrawMatchEndCondition`, `CG_DrawMapName`, `CG_DrawMatchDetails`,
  `CG_DrawGameTypeMap`, `CG_DrawSelectedPlayerAccuracy`,
  `CG_DrawSelectedPlayerBestWeapon`, and `CG_DrawEndGameScore`, together with
  retail anchors such as `%i:%i%i`, `%02d:%02d (%s %02d, %d)`,
  `First to reach the mercy limit`, `Highest score at the end of the game`,
  `%s - %s - %s`, `You forfeited the match.`, and `You captured %d skull%s.`.
- The event-side sweep now also covers `CG_PlaceString`, `CG_Obituary`,
  `CG_UseItem`, `CG_PainEvent`, and the synthetic retail helper
  `CG_TryAutoFollowPowerup`, together with the obituary/use-item/follow anchors
  such as `CG_Obituary: target out of range`, `You fragged %s.`,
  `was killed by`, `CG_UseItem: invalid item %d`, `No item to use`, `Use %s`,
  `follow %d%s`, and `cg_followPowerup`.
- The retail HUD bootstrap is still split across `0x10029120` and an earlier
  setup helper at `0x10029210`, but that split is now better characterized:
  `0x10029210` resolves as the synthetic `CG_InitDisplayContext` helper that
  wires `cgDC` and performs the `Init_Display(&cgDC)` handoff, while
  `0x10006E40` resolves as the retail `CG_LoadHud_f` console wrapper rather
  than an unnamed bootstrap clone.
- The remaining `cgame` instability is now mostly documentary rather than
  behavioral: the HLIL-only `CG_Init` boundary at `0x10029820`, the Ghidra
  `entry` export disagreement, and the native export-array slot-order mismatch
  against the legacy `cgameExport_t` enum.

## Next steps

1. Feed the JSON manifests into the documentation build so that unresolved
   prefixes surface on dashboards.
2. Expand the alias map with additional leak/debug symbol data to raise the
   resolution beyond ~80% for strings.
3. Refresh the dedicated `cgame` ledger in `docs/reverse-engineering/cgame-mapping.md`
   when the committed Ghidra corpus is refreshed, especially around the
   HLIL-only `CG_Init` boundary.
4. Re-run the exporter once the alias map grows to verify normalization remains
   stable across binaries.
5. Refresh the committed Ghidra corpus with `scripts\ghidra\run_quakelive_reference.ps1`
   whenever the retail binary snapshot changes.
