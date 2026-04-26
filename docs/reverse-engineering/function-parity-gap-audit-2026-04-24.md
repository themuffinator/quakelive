# Function-Level Parity Gap Audit

Last updated: 2026-04-26

## Purpose

This document is a current function-to-function parity gap register built from
the committed Ghidra references, symbol maps, HLIL mapping notes, and the
current source-file gap notes.

It does not duplicate every closed function row from the symbol maps. Instead,
it records:

- which retail binaries are function-mapped cleanly;
- which Ghidra or HLIL-owned functions still map to bounded compatibility,
  divergence, or open portability behavior in source; and
- which mapping-only gaps remain where source parity may be closed or bounded,
  but the reference corpus is not yet fully named.

The current top-level estimates remain unchanged:

- strict-retail Windows replacement target: **100%**
- repo-wide checked-in tree parity: **98%**

## Evidence Inputs

Primary reference corpus:

- `references/reverse-engineering/ghidra/quakelive_steam/`
- `references/reverse-engineering/ghidra/qagamex86/`
- `references/reverse-engineering/ghidra/cgamex86/`
- `references/reverse-engineering/ghidra/uix86/`
- `references/reverse-engineering/ghidra/awesomium_process/`
- `references/hlil/quakelive/quakelive_steam.exe/`
- `references/hlil/quakelive/uix86.all/`
- `references/hlil/quakelive/qagamex86.dll_split/`

Mapping and status corpus:

- `references/symbol-maps/qagame.json`
- `references/symbol-maps/cgame.json`
- `references/symbol-maps/ui.json`
- `references/symbol-maps/client.json`
- `references/symbol-maps/server.json`
- `references/analysis/quakelive_symbol_aliases.json`
- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- `docs/reverse-engineering/source-file-gap-notes/`
- `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_110.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_111.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_112.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_113.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_114.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_115.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_116.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_117.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_118.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_119.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_120.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_121.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_122.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_123.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_124.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_125.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_126.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_127.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_128.md`
- `docs/mapping-ref/quakelive_steam_mapping_appendix.md`

## Reference Function Inventory

| Retail reference | Ghidra functions | Imports | Exports | Function-map state | Current source parity gap |
| --- | ---: | ---: | ---: | --- | --- |
| `quakelive_steam.exe` | `5473` | `351` | `2` | `1415` alias entries, `1409` address-backed aliases, about `25.745%` address-backed coverage after round 128 | Yes: online services are bounded divergence; host mapping is still partial |
| `qagamex86.dll` | `1027` | `65` | `2` | `1128 / 1128` committed `qagame` map rows are `matched` | No active module function gap |
| `cgamex86.dll` | `751` | `55` | `2` | `854 / 854` committed `cgame` rows are `matched`, including `103` HLIL-only anchors | No active module function gap |
| `uix86.dll` | `348` | `50` | `2` | `444 / 444` committed `ui` rows are `matched`, including `96` HLIL-only anchors | No active UI function gap |
| `awesomium_process.exe` | `139` | `54` | `1` | Alias corpus covers the narrow executable-owned wrapper/CRT surface | No active source gap; browser runtime remains outside executable-owned code |
| legacy `client.json` map | `5` map rows | n/a | n/a | `4` matched, `1` retired | No active gap; stale renderer placeholder retired |
| legacy `server.json` map | `5` map rows | n/a | n/a | `4` matched, `1` retired | No active gap; stale team-score placeholder retired |

Interpretation:

- The native game module maps are closed at the committed function-map level.
- The source-file campaign has walked `567` tracked source entries and
  currently isolates `7` documented online-service divergences plus `9`
  active non-Windows/null portability gap notes.
- The largest open function-map surface is the Steam host executable. That is
  expected because it includes proprietary platform services, Awesomium,
  Steamworks, CRT/STL code, and launcher glue that do not have a direct Quake
  III GPL source analogue.

## Closed Function-Map Areas

### `qagamex86.dll`

Current status: no active function-level source parity gap.

The committed `qagame` map carries `1128` matched rows. Current source-file
status under `src/code/game/` is walked closed on this audit baseline. The
remaining repo-wide gaps do not currently originate in qagame gameplay logic.

Evidence signals:

- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/symbol-maps/qagame.json`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`

### `cgamex86.dll`

Current status: no active function-level source parity gap.

The committed `cgame` map carries `854` matched rows: all `751` Ghidra
function starts plus `103` HLIL-only anchors. Current source-file status under
`src/code/cgame/`, plus shared `bg_*` and UI helper dependencies, remains
walked closed on this audit baseline.

Evidence signals:

- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/symbol-maps/cgame.json`
- `docs/reverse-engineering/cgame-mapping.md`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`

### `uix86.dll`

Current status: no active function-level source parity gap.

The committed `ui` map carries `444` matched rows: all `348` Ghidra function
starts plus `96` HLIL-only anchors. The `src/code/ui/` tree is read-only for
this task and remains closed by the existing UI parity ledger. The checked-in
`src/ui` runtime-panel compare is currently clean (`65 / 65`, `0` diffs).

Evidence signals:

- `references/reverse-engineering/ghidra/uix86/functions.csv`
- `references/symbol-maps/ui.json`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`

### `awesomium_process.exe`

Current status: no active executable-owned source parity gap.

The Ghidra corpus shows this executable is mainly a narrow process wrapper and
CRT surface around the imported Awesomium child-process entry. The reconstructed
source ownership stays bounded to the executable-owned launcher helper path;
the browser engine itself belongs to proprietary `awesomium.dll`, not to this
wrapper.

Evidence signals:

- `references/reverse-engineering/ghidra/awesomium_process/functions.csv`
- `docs/reverse-engineering/awesomium_process-mapping.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Current Gap Families

### FG-01: Online Services And External Ecosystems

Classification: documented bounded divergence, not active strict-retail
Windows debt.

Owning retail reference: `assets/quakelive/quakelive_steam.exe`

Representative retail function clusters:

- Steam client and auth: `SteamClient_Init`,
  `SteamCallbacks_Init`, `SteamClient_GetAuthSessionTicket`,
  `SteamClient_CancelAuthTicket`
- Steam server and VAC/auth: `SteamServer_Init`,
  `SteamServer_BeginAuthSession`, `SteamServer_EndAuthSession`,
  `SteamServer_Frame`
- Lobby and matchmaking: `SteamLobby_Init`,
  `SteamLobbyCallbacks_Init`, `SteamLobbyCallbacks_OnLobbyEnter`
- Workshop/UGC: `SteamWorkshop_Init`,
  `SteamWorkshop_RequestDownload`, `SteamWorkshop_FinalizeItem`,
  `SteamCmd_DownloadUGC_f`
- Steam stats and overlay: `SteamStats_Init`,
  `SteamStats_ProcessEvent`, `SteamStats_BroadcastSummary`,
  `SteamOverlay_Command_f`
- Browser/Steam data source: `QLWebHost_OpenURL`,
  `QLWebView_PublishEvent`, `QLResourceInterceptor_OnRequest`

Function-level source gaps:

| Source owner | Function or surface | Current parity state | Gap reason |
| --- | --- | --- | --- |
| `src/common/platform/platform_config.h` | `QL_BUILD_ONLINE_SERVICES` | divergence owner | Defaults to disabled, so the repo intentionally does not claim live-service parity in default builds |
| `src/common/platform/platform_config.h` | `QL_BUILD_STEAMWORKS`, `QL_BUILD_OPEN_STEAM` | bounded compatibility | Provider builds are forced off unless online services are explicitly enabled |
| `src/common/platform/platform_config.h` | `QL_PLATFORM_HAS_ONLINE_SERVICES`, `QL_PLATFORM_HAS_STEAMWORKS`, `QL_PLATFORM_HAS_OPEN_STEAM`, `QL_PLATFORM_BUILD_HYBRID`, `QL_PLATFORM_HAS_STEAM_SERVICES` | derived divergence flags | Advertise bounded capability rather than retail-equivalent service closure |
| `src/common/platform/platform_services.c` | `QL_PlatformExternalEcosystemsDisabled`, `QL_FinaliseDescriptor`, `QL_PlatformSteamworks_InitOnce` | bounded compatibility | Preserve explicit disabled or compatibility provider descriptors |
| `src/common/platform/platform_services.c` | `QL_BuildServiceTable` | divergence owner | Builds the table that reports build-disabled or compatibility-only providers |
| `src/common/platform/backends/platform_backend_steamworks.c` | `QL_PlatformBackendSteamworks_Authenticate` | divergence owner | Decides accepted, pending, or denied auth from local ticket shape instead of a live Steamworks validation exchange |
| `src/common/platform/backends/platform_backend_open_steam.c` | `QL_PlatformBackendOpenSteam_Authenticate` | divergence owner | Uses token-length and substring heuristics instead of a documented open transport |
| `src/code/client/ql_auth.c` | `QL_ClientAuth_InvokeBackend`, `QL_ClientAuth_RequestSteamTicket` | bounded compatibility | Auth flow still depends on build/runtime service gates |
| `src/code/client/ql_auth.c` | `QL_ClientAuth_HandleSteamworksTicket`, `QL_ClientAuth_HandleOpenSteamTicket`, `QL_ClientAuth_HandleStandaloneToken`, `QL_ClientAuth_HandleHybridSteam`, `QL_ClientAuth_DispatchSteam`, `QL_Auth_ExecuteRequest` | divergence owners | Dispatches to heuristic or bounded providers rather than a retail-equivalent service path |
| `src/code/client/cl_steam_resources.c` | `CL_SteamResources_RequestAvatarRGBA`, `CL_InitSteamResources` | bounded compatibility | Steam resource path reports unavailable or falls back when services are disabled |
| `src/code/client/cl_steam_resources.c` | `CL_SteamDataSource_Request`, `QLResourceInterceptor_OnRequest`, `CL_Steam_RegisterShader`, `Sys_Steam_RequestURL` | divergence owners | Resource requests route through fallback/stub behavior instead of a closed Steam data-source implementation |
| `src/code/server/sv_rankings.c` | `SV_RankPublishDisabledState`, `SV_RankLogDisabledState`, `SV_RankBegin` | divergence owners | Disabled default build forces rankings into compatibility-only behavior |
| `src/code/server/sv_rankings.c` | `SV_GetRankingsProviderLabel`, `SV_GetRankingsPolicyLabel`, `SV_RefreshRankingsPolicyCvars`, `SV_RankCheckInit`, `SV_RankActive`, `SV_RankPoll`, `SV_RankUserStatus`, `SV_RankUserReset`, `SV_RankReportInt`, `SV_RankReportStr`, `SV_RankEnd`, `SV_RankUserGrank`, `SV_RankUserSpectate`, `SV_RankUserCreate`, `SV_RankUserLogin`, `SV_RankUserValidate`, `SV_RankUserLogout`, `SV_RankQuit`, `SV_RankNewGameCBF`, `SV_RankUserCBF`, `SV_RankJoinGameCBF`, `SV_RankSendReportsCBF`, `SV_RankCleanupCBF`, `SV_RankCloseContext`, `least`, `SV_RankEncodeGameID`, `SV_RankDecodePlayerID`, `SV_RankDecodePlayerKey`, `SV_RankStatusString`, `SV_RankError` | bounded compatibility | The retained rankings API surface returns safe defaults or no-ops under the disabled branch |

Closure requirement:

- Adopt a documented open replacement path, or explicitly keep this family as
  a permanent divergence.
- If pursued, replace heuristic auth/resource/rankings behavior with validated
  transport-backed flows and refresh the corresponding runtime evidence.

### FG-02: Unix And Linux Client/Runtime Portability

Classification: open repo-wide gap.

Owning retail reference: primarily `quakelive_steam.exe` host/runtime
behavior. There is no retail Linux client target in the current strict-retail
Windows score.

Function-level source gaps:

| Source owner | Function(s) | Current parity state | Gap reason |
| --- | --- | --- | --- |
| `src/code/unix/unix_main.c` | `Sys_ResolveProfilingHooks`, `Sys_SetProfilingEnabled`, `Sys_BeginProfiling`, `Sys_EndProfiling` | bounded compatibility | Profiling only exists behind optional host/build support |
| `src/code/unix/unix_main.c` | `Sys_CheckCD` | bounded compatibility | Now probes data roots, but remains a coarse compatibility check rather than broad host parity proof |
| `src/code/unix/unix_main.c` | `Sys_IsExecutableOnPath` | bounded compatibility | Supports the bounded clipboard helper chain |
| `src/code/unix/unix_main.c` | `main` | compatibility host owner | Unix host entry remains outside the closed Windows replacement target |
| `src/code/unix/linux_glimp.c` | `GLimp_SetGamma`, `GLimp_Shutdown`, `GLimp_Init`, `GLimp_EndFrame` | open portability owners | Linux GLX renderer host path is not validated as a retail-equivalent client/runtime |
| `src/code/unix/linux_glimp.c` | `IN_Shutdown`, `IN_Frame`, `IN_Activate`, `IN_StartupJoystick` | open portability owners | Linux input/client activation remains part of the unresolved portability lane |
| `src/code/unix/linux_glimp.c` | `Q_stristr`, `XLateKey`, `CreateNullCursor`, `install_grabs`, `uninstall_grabs`, `X11_PendingInput`, `repeated_press`, `HandleEvents`, `KBD_Init`, `KBD_Close`, `IN_ActivateMouse`, `IN_DeactivateMouse`, `GLimp_LogComment`, `GLW_StartDriverAndSetMode`, `GLW_SetMode`, `GLW_InitExtensions`, `GLW_InitGamma`, `GLW_LoadOpenGL`, `qXErrorHandler`, `GLimp_RenderThreadWrapper`, `GLimp_SpawnRenderThread`, `GLimp_RendererSleep`, `GLimp_FrontEndSleep`, `GLimp_WakeRenderer`, `IN_Init`, `Sys_SendKeyEvents`, `IN_JoyMove` | bounded compatibility | Retained legacy Linux renderer/input helper surface |
| `src/code/unix/linux_snd.c` | `Snd_Memset`, `SNDDMA_Init`, `SNDDMA_GetDMAPos`, `SNDDMA_Shutdown`, `SNDDMA_Submit`, `SNDDMA_BeginPainting` | open portability owners | OSS `/dev/dsp` sound path is not modernized or validated as a client/runtime parity target |
| `src/code/unix/linux_joystick.c` | `IN_StartupJoystick`, `IN_JoyMove` | open portability owners | `/dev/js*` joystick lane remains unresolved Linux input portability |

Closure requirement:

- Decide whether Unix/Linux client parity is an actual target or a permanently
  bounded support lane.
- If it is a target, validate real graphics, input, audio, module loading, and
  runtime packaging on current Linux hosts.

### FG-03: Null Host Compatibility Surface

Classification: open repo-wide gap.

Owning retail reference: no direct retail target. This is a checked-in
compatibility host and therefore counts against whole-tree parity even though
the strict-retail Windows target excludes it.

Function-level source gaps:

| Source owner | Function(s) | Current parity state | Gap reason |
| --- | --- | --- | --- |
| `src/code/null/null_main.c` | `Sys_GetGameAPI`, `Sys_GetClipboardData`, `main` | open portability owners | Null host has no real module API, clipboard, or runtime entry parity target |
| `src/code/null/null_main.c` | `Sys_CurrentWallClockMilliseconds`, `Sys_CopyDirectoryName`, `Sys_BeginStreamedFile`, `Sys_EndStreamedFile`, `Sys_StreamedRead`, `Sys_StreamSeek`, `Sys_Error`, `Sys_Quit`, `Sys_UnloadGame`, `Sys_Print`, `Sys_DisplaySystemConsole`, `Sys_SetErrorText`, `Sys_ExecutableBaseName`, `Sys_Milliseconds`, `Sys_Mkdir`, `Sys_Cwd`, `Sys_SetDefaultCDPath`, `Sys_DefaultCDPath`, `Sys_SetDefaultInstallPath`, `Sys_DefaultInstallPath`, `Sys_SetDefaultHomePath`, `Sys_DefaultHomePath`, `Sys_GetCurrentUser`, `Sys_Init`, `Sys_EarlyOutput` | bounded compatibility | Utility shims keep the null host buildable, but do not close runtime parity |
| `src/code/null/null_glimp.c` | `GLimp_EndFrame`, `GLimp_Init`, `GLimp_Shutdown`, `QGL_Init` | open portability owners | No graphics context, swap path, or real GL loader exists |
| `src/code/null/null_glimp.c` | `GLimp_EnableLogging`, `GLimp_LogComment`, `QGL_Shutdown` | bounded compatibility | Null renderer host shims |
| `src/code/null/null_client.c` | `CL_RefreshOnlineServicesBridgeState`, `CL_WebHost_Init`, `CL_WebHost_Shutdown`, `CL_WebHost_Frame`, `CL_WebHost_HasLiveView`, `CL_WebHost_HasBoundWindowObject`, `CL_WebHost_GetCursorHandle`, `CL_WebView_PublishEvent`, `CL_WebView_InvokeCommNotice`, `CL_WebView_PublishGameError`, `CL_WebView_PublishGameEnd`, `CL_WebView_PublishBindChanged`, `CL_WebView_PublishGameStart`, `CL_WebView_PublishGameScreenshot`, `CL_WebView_OnMouseMove`, `CL_WebView_OnMouseButtonEvent`, `CL_WebView_OnMouseWheelEvent`, `CL_WebView_OnKeyEvent`, `CL_AdvertisementBridge_RefreshLoadingViewParameters`, `CL_AdvertisementBridge_UpdateLoadingViewParameters`, `CL_AdvertisementBridge_InitUI`, `CL_AdvertisementBridge_ActivateAdvert`, `CL_AdvertisementBridge_SetActiveAdvert` | open portability owners | Browser, advert, and web-view behavior is stubbed |
| `src/code/null/null_client.c` | `CL_NullResetAdvertisementBridgeState`, `CL_NullRefreshBrowserCvars`, `CL_Shutdown`, `CL_Init`, `CL_MouseEvent`, `Key_WriteBindings`, `Key_EnumerateBindings`, `CL_Frame`, `CL_PacketEvent`, `CL_CharEvent`, `CL_Disconnect`, `CL_MapLoading`, `CL_GameCommand`, `CL_KeyEvent`, `UI_GameCommand`, `CL_WebHost_NotifyAppActivation`, `CL_WebView_PublishCvarChange`, `CL_WebView_PublishGameDemo`, `CL_ForwardCommandToServer`, `CL_ConsolePrint`, `CL_JoystickEvent`, `CL_InitKeyCommands`, `CL_CDDialog`, `CL_FlushMemory`, `CL_StartHunkUsers`, `CL_ShutdownAll`, `CL_CDKeyValidate` | bounded compatibility | Null-client no-op or safe-default shims |
| `src/code/null/null_input.c` | `IN_NullRefreshCompatibilityState`, `IN_Init`, `IN_Frame`, `Sys_SendKeyEvents` | open portability owners | No real input device or key-event pump exists |
| `src/code/null/null_input.c` | `IN_NullTouchCompatibilityCvars`, `IN_Shutdown` | bounded compatibility | Null input cvar/shutdown shims |
| `src/code/null/null_snddma.c` | `SNDDMA_Init`, `SNDDMA_GetDMAPos`, `SNDDMA_Shutdown`, `SNDDMA_BeginPainting`, `SNDDMA_Submit`, `SNDDMA_Activate`, `S_RegisterSound`, `S_StartLocalSound`, `S_ClearSoundBuffer`, `S_AddVoiceSamples` | open portability owners | Sound and voice paths are intentionally silent/no-op |

Closure requirement:

- Keep null host as an explicit compatibility lane, or define a stronger
  parity target with non-null graphics, audio, input, module, and browser
  contracts.

### FG-04: Runtime Evidence Freshness

Classification: open repo-wide validation gap, not a broad source-code
reconstruction gap.

Function-level blocker:

| Owner | Function or probe surface | Current state | Gap reason |
| --- | --- | --- | --- |
| `src/code/renderer/tr_font.c` | `R_fonsErrorCallback` | bounded runtime blocker | Retail-module live-map probe can load retail `qagamex86.dll` and `cgamex86.dll`, but repeated font-atlas saturation still prevents `CS_ACTIVE` in that probe lane |
| `tools/modules/run_retail_module_runtime_probe.ps1` | map-probe blocker classification | evidence bounded | Probe recognizes the renderer-owned blocker rather than treating it as module parity failure |
| `tools/ci/validate-windows-native.ps1` | staged `retail-runtime` validation | evidence needs fresh rerun | Current audit did not regenerate all native build outputs on current toolchains |
| `docs/platform/toolchain-matrix.md` | glibc and self-hosted publication follow-ups | evidence needs breadth | Broader glibc validation and continuous/self-hosted WOW64 publication remain follow-up work |

Closure requirement:

- Regenerate current native build outputs and rerun the strict staged retail
  runtime validation lane.
- Rerun/promote retail-module evidence only when the renderer-owned font-atlas
  blocker is either fixed or deliberately reclassified with fresh artifacts.

## Mapping-Only Gaps

These entries are not automatically source parity failures. They are reference
coverage gaps: the committed host Ghidra map still has unresolved or opaque
function ownership, while the legacy sparse client/server rows below are kept
only as retired historical seed entries.

### `quakelive_steam.exe` Partial Mapping

Current coverage:

- Ghidra baseline: `5473` functions
- Current alias corpus: `1415` raw aliases
- Address-backed aliases: `1409`
- Address-backed coverage: about `25.745%`

High-priority opaque/unfinished areas from the current mapping notes:

| Address | Current raw symbol | Current status |
| --- | --- | --- |
| `0x004F1EE0` | bridge/JS-handler candidate | Opaque bridge region around `data_12d2670`; wrapper semantics still need final names |
| `0x004F1F10` through `0x004F2280` | bridge wrapper cluster | Vtable forwarding wrappers; list/projection/browser bridge roles are still not fully stabilized |
| `0x004B9430` | `sub_4B9430` | High-value unresolved client/host leftover called out after round 109 |
| `0x004B9940` | `sub_4B9940` | High-value unresolved client/host leftover called out after round 109 |
| `0x004B81F0` | `sub_4B81F0` | High-value unresolved client/host leftover called out after round 109 |
| `0x004ECDF0` | `sub_4ECDF0` | High-value unresolved host leftover called out after round 109 |
| `0x004F1290` | `sub_4F1290` | High-value unresolved host leftover called out after round 109 |
| `0x004F2900` | `sub_4F2900` | High-value unresolved browser/host leftover called out after round 109 |
| `0x004F4640` | `sub_4F4640` | High-value unresolved host leftover called out after round 109 |

Largest currently unaliased Ghidra functions by byte size after
[mapping round 128](./quakelive_steam_mapping_round_128.md):

| Rank | Address | Raw symbol | Size |
| ---: | --- | --- | ---: |
| 1 | `0x0049FC30` | `FUN_0049fc30` | `659` |
| 2 | `0x00408EC0` | `FUN_00408ec0` | `659` |
| 3 | `0x00525370` | `FUN_00525370` | `658` |
| 4 | `0x00501AD0` | `FUN_00501ad0` | `657` |
| 5 | `0x0047ED10` | `FUN_0047ed10` | `655` |
| 6 | `0x004B0CD0` | `FUN_004b0cd0` | `654` |
| 7 | `0x0047B710` | `FUN_0047b710` | `654` |
| 8 | `0x004FBB00` | `FUN_004fbb00` | `647` |
| 9 | `0x00435FF0` | `FUN_00435ff0` | `647` |
| 10 | `0x0049CD80` | `FUN_0049cd80` | `646` |
| 11 | `0x0040A8F0` | `FUN_0040a8f0` | `645` |
| 12 | `0x0040A660` | `FUN_0040a660` | `645` |
| 13 | `0x0040A3D0` | `FUN_0040a3d0` | `645` |
| 14 | `0x00409F20` | `FUN_00409f20` | `645` |
| 15 | `0x00515250` | `FUN_00515250` | `643` |
| 16 | `0x00474D90` | `FUN_00474d90` | `642` |
| 17 | `0x004B07C0` | `FUN_004b07c0` | `641` |
| 18 | `0x004193B0` | `FUN_004193b0` | `641` |
| 19 | `0x0051D0A0` | `FUN_0051d0a0` | `639` |
| 20 | `0x0047AE50` | `FUN_0047ae50` | `639` |

Interpretation:

- This is the only major reference corpus where function-to-function naming
  coverage is still far below complete.
- Many unmapped functions may be CRT/STL/Awesomium/Steam SDK support rather
  than engine-owned behavior. Rounds 118 through 128 resolved the former
  largest candidates as retained engine/source-owned functions,
  ZeroMQ/CZMQ platform-service helpers, and bundled support-library functions
  without opening source debt. Round 121 specifically classified `12`
  engine-owned, `5` platform-service-owned, and `8` CRT/STL/support-library
  functions. Round 122 classified `12` engine-owned, `3`
  platform-service-owned, and `10` CRT/STL/support-library functions. Round
  123 classified `16` engine-owned, `4` platform-service-owned, and `5`
  CRT/STL/support-library functions. Round 124 classified `9` engine-owned,
  `5` platform-service-owned, and `11` CRT/STL/support-library functions.
  Round 125 classified `12` engine-owned, `5` platform-service-owned, and
  `8` CRT/STL/support-library functions. Round 126 classified `12`
  engine-owned, `5` platform-service-owned, and `8`
  CRT/STL/support-library functions. Round 127 classified `10`
  engine-owned, `2` platform-service-owned, and `13`
  CRT/STL/support-library functions. Round 128 classified `11` engine-owned,
  `3` platform-service-owned, and `11` CRT/STL/support-library functions, and
  corrected `sub_41A7C0` from listener event handling to the ZeroMQ TCP accept
  helper. Each later pass still needs to classify candidates before treating
  them as source parity debt.
- The source gap consequences currently flow through FG-01, not through every
  raw unmapped host function.

### Legacy `client.json` Map

| Address | Raw symbol | Normalized name | Current status |
| --- | --- | --- | --- |
| `0x00445AB0` | `sub_445AB0` | `RETIRED_LEGACY_CLIENT_RENDER_BACKEND_PLACEHOLDER` | Retired legacy seed row; superseded by `quakelive_steam.exe` renderer/bootstrap aliases including `CL_InitRenderer`, `CL_InitRef`, and `RE_RenderScene` |

The current strict client parity gate is closed through the newer subsystem
audits. This old row no longer carries an unresolved prefix because the current
host mapping has the relevant renderer/bootstrap ownership, and the legacy
`render backend missing implementation` string is not present in the current
retail Ghidra/HLIL corpus.

### Legacy `server.json` Map

| Address | Raw symbol | Normalized name | Current status |
| --- | --- | --- | --- |
| `0x00412190` | `sub_412190` | `RETIRED_LEGACY_SERVER_TEAM_SCORE_PLACEHOLDER` | Retired legacy seed row; superseded by the current qagame map row `AddTeamScore @ 0x100681B0` plus scoreboard serializers |

The current strict server parity gate is closed through the newer subsystem
audits. This old row no longer carries an unresolved prefix because the current
function-to-function map places the team-score and lead-change behavior in the
native qagame corpus rather than in the legacy sparse `server.json` seed file.

## Current Gap Summary

| Gap family | Source parity impact | Mapping impact | Status |
| --- | --- | --- | --- |
| FG-01 online services and external ecosystems | Default builds intentionally use disabled, heuristic, or fallback behavior | `quakelive_steam.exe` service clusters remain only partially mapped | Documented bounded divergence |
| FG-02 Unix/Linux client/runtime portability | Linux client graphics, input, audio, and host runtime remain compatibility-only | Mostly source-file gap notes, not closed retail reference debt | Open repo-wide gap |
| FG-03 null host compatibility | Null graphics/audio/input/browser/module hosts are no-op or safe-default shims | No direct retail target; whole-tree parity gap only | Open repo-wide gap |
| FG-04 evidence freshness | Structural gates are green, but some runtime/build artifacts need fresh regeneration | Retail-module live-map probe still records `R_fonsErrorCallback` blocker | Open validation gap |
| Mapping-only host coverage | Not automatically source debt | `quakelive_steam.exe` retains unresolved function rows; legacy `client.json` and `server.json` stale rows are retired | Open host mapping work |

## Recommended Next Audit Tasks

1. Continue `quakelive_steam.exe` mapping from the refreshed largest-unaliased
   queue beginning with `sub_49FC30`, `sub_408EC0`, and `sub_525370`; classify
   each as engine-owned, platform-service-owned, CRT/STL, Awesomium, or Steam
   SDK support before opening source debt.
2. If repo-wide parity is the target, choose whether FG-01 is permanently
   excluded or whether an open service replacement should be designed.
3. Re-baseline the Unix/null portability target so FG-02 and FG-03 can either
   become explicit permanent compatibility lanes or receive real runtime work.
4. Refresh native Windows runtime/build evidence and rerun the retail-module
   probe after the renderer font-atlas blocker has a current disposition.
