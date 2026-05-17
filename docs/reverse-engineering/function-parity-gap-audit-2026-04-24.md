# Function-Level Parity Gap Audit

Last updated: 2026-05-17

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
- `docs/reverse-engineering/quakelive_steam_mapping_round_129.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_130.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_131.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_132.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_133.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_134.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_135.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_136.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_137.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_138.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_139.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_140.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_141.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_142.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_143.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_144.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_145.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_146.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_147.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_148.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_149.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_150.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_151.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_152.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_153.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_154.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_155.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_156.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_157.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_158.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_159.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_160.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_161.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_162.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_163.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_164.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_165.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_166.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_167.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_168.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_176.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_177.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_178.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_179.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_180.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_181.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_182.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_183.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_184.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_185.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_186.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_187.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_188.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_189.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_190.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_191.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_192.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_193.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_194.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_195.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_196.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_197.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_198.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_199.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_200.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_201.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_202.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_203.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_204.md`
- `docs/reverse-engineering/quakelive_steam_mapping_round_205.md`
- `docs/mapping-ref/quakelive_steam_mapping_appendix.md`

## Reference Function Inventory

| Retail reference | Ghidra functions | Imports | Exports | Function-map state | Current source parity gap |
| --- | ---: | ---: | ---: | --- | --- |
| `quakelive_steam.exe` | `5473` | `351` | `2` | `2167` alias entries, `2094` strict Ghidra address-backed aliases, about `38.261%` strict Ghidra address-backed coverage after round 205 | Yes: online services are bounded divergence; host mapping is still partial |
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
| `src/code/unix/unix_main.c` | `Sys_LoadDll` | bounded compatibility | Unix native-module loading now resets failed-load outputs, validates candidate exports, closes incompatible handles, and probes cwd, `fs_homepath`, `fs_basepath`, and `fs_cdpath`, but remains part of the compatibility-only Unix host lane |
| `src/code/unix/unix_main.c` | `Sys_GetEvent` | bounded compatibility | Unix packet event queuing now preserves only unread bytes after `netmsg.readcount`, matching the recovered Win32 event-loop shape while remaining in the compatibility-only Unix host lane |
| `src/code/unix/unix_main.c` | `main` | compatibility host owner | Unix host entry remains outside the closed Windows replacement target |
| `src/code/unix/linux_glimp.c` | `GLimp_SetGamma`, `GLimp_Init` | open portability owners | Linux GLX renderer host path is not validated as a retail-equivalent client/runtime |
| `src/code/unix/linux_glimp.c` | `GLimp_Shutdown`, `GLimp_EndFrame` | bounded compatibility | Linux GLX teardown now handles partial display/context/window state, closes the QGL log, releases QGL state, and guards end-frame swaps after shutdown or partial init failure while remaining compatibility-only |
| `src/code/unix/linux_glimp.c` | `IN_Frame`, `IN_Activate`, `IN_StartupJoystick` | open portability owners | Linux input/client activation remains part of the unresolved portability lane |
| `src/code/unix/linux_glimp.c` | `IN_Shutdown` | bounded compatibility | Linux input teardown now releases retained X mouse grabs before clearing mouse availability/activity state, then closes the retained joystick descriptor and clears `ui_joyavail` through `IN_ShutdownJoystick()` |
| `src/code/unix/linux_glimp.c` | `Q_stristr`, `XLateKey`, `CreateNullCursor`, `install_grabs`, `uninstall_grabs`, `X11_PendingInput`, `repeated_press`, `HandleEvents`, `KBD_Init`, `KBD_Close`, `IN_ActivateMouse`, `IN_DeactivateMouse`, `GLimp_LogComment`, `GLW_StartDriverAndSetMode`, `GLW_SetMode`, `GLW_InitExtensions`, `GLW_InitGamma`, `GLW_LoadOpenGL`, `qXErrorHandler`, `GLimp_RenderThreadWrapper`, `GLimp_SpawnRenderThread`, `GLimp_RendererSleep`, `GLimp_FrontEndSleep`, `GLimp_WakeRenderer`, `IN_Init`, `Sys_SendKeyEvents`, `IN_JoyMove` | bounded compatibility | Retained legacy Linux renderer/input helper surface |
| `src/code/unix/linux_snd.c` | `SNDDMA_Init`, `SNDDMA_Submit` | open portability owners | OSS `/dev/dsp` remains the only real audible Linux backend, so the sound path is not validated as a client/runtime parity target |
| `src/code/unix/linux_snd.c` | `Snd_Memset`, `SNDDMA_InitCvars`, `SNDDMA_IsNullDevice`, `SNDDMA_InitNull`, `SNDDMA_GetDMAPos`, `SNDDMA_Shutdown`, `SNDDMA_BeginPainting` | bounded compatibility | Silent `snddevice null` DMA sink and OSS mmap/descriptor shutdown reduce headless/runtime friction without closing modern Linux audio parity |
| `src/code/unix/linux_joystick.c` | `IN_StartupJoystick`, `IN_JoyMove` | open portability owners | Linux joystick startup/event translation remains unresolved input portability, though the scan and event ranges are now bounded |
| `src/code/unix/linux_joystick.c` | `IN_ClearJoystickState`, `IN_ReleaseJoystickKeys`, `IN_TryOpenJoystick`, `IN_ShutdownJoystick` | bounded compatibility | Modern `/dev/input/js*` plus historical `/dev/js*` probing, `ui_joyavail`, descriptor cleanup, and key-release state are now explicit compatibility work |

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
| `src/code/null/null_glimp.c` | `GLimp_EndFrame`, `GLimp_Init` | open portability owners | No graphics context or swap path exists; `GLimp_Init()` now fails explicitly instead of letting the null host look like a renderer |
| `src/code/null/null_glimp.c` | `GLimp_Shutdown`, `GLimp_EnableLogging`, `GLimp_LogComment`, `QGL_Init`, `QGL_Shutdown` | bounded compatibility | Null renderer host now refuses fake GL init success and clears retained extension/logging state |
| `src/code/null/null_client.c` | `CL_RefreshOnlineServicesBridgeState`, `CL_WebHost_Init`, `CL_WebHost_Shutdown`, `CL_WebHost_Frame`, `CL_WebHost_HasLiveView`, `CL_WebHost_HasBoundWindowObject`, `CL_WebHost_GetCursorHandle`, `CL_WebView_PublishEvent`, `CL_WebView_InvokeCommNotice`, `CL_WebView_PublishGameError`, `CL_WebView_PublishGameEnd`, `CL_WebView_PublishBindChanged`, `CL_WebView_PublishGameStart`, `CL_WebView_PublishGameScreenshot`, `CL_WebView_OnMouseMove`, `CL_WebView_OnMouseButtonEvent`, `CL_WebView_OnMouseWheelEvent`, `CL_WebView_OnKeyEvent`, `CL_AdvertisementBridge_RefreshLoadingViewParameters`, `CL_AdvertisementBridge_UpdateLoadingViewParameters`, `CL_AdvertisementBridge_InitUI`, `CL_AdvertisementBridge_ActivateAdvert`, `CL_AdvertisementBridge_SetActiveAdvert` | open portability owners | Browser, advert, and web-view behavior is stubbed |
| `src/code/null/null_client.c` | `CL_NullResetAdvertisementBridgeState`, `CL_NullRefreshBrowserCvars`, `CL_Shutdown`, `CL_Init`, `CL_MouseEvent`, `Key_WriteBindings`, `Key_EnumerateBindings`, `CL_Frame`, `CL_PacketEvent`, `CL_CharEvent`, `CL_Disconnect`, `CL_MapLoading`, `CL_GameCommand`, `CL_KeyEvent`, `UI_GameCommand`, `CL_WebHost_NotifyAppActivation`, `CL_WebView_PublishCvarChange`, `CL_WebView_PublishGameDemo`, `CL_ForwardCommandToServer`, `CL_ConsolePrint`, `CL_JoystickEvent`, `CL_InitKeyCommands`, `CL_CDDialog`, `CL_FlushMemory`, `CL_StartHunkUsers`, `CL_ShutdownAll`, `CL_CDKeyValidate` | bounded compatibility | Null-client no-op or safe-default shims |
| `src/code/null/null_input.c` | `IN_Init`, `IN_Frame`, `Sys_SendKeyEvents` | open portability owners | No real input device or key-event pump exists; the pump now refreshes no-device state but still emits no events |
| `src/code/null/null_input.c` | `IN_NullTouchCompatibilityCvars`, `IN_NullRefreshCompatibilityState`, `IN_Shutdown` | bounded compatibility | Null input cvar/no-device-state/shutdown shims |
| `src/code/null/null_snddma.c` | `SNDDMA_ClearNullState`, `SNDDMA_Init`, `SNDDMA_GetDMAPos`, `SNDDMA_Shutdown`, `SNDDMA_BeginPainting`, `S_ClearSoundBuffer` | bounded compatibility | Null sound now carries an explicit silent DMA sink and cursor/buffer cleanup without becoming an audible backend |
| `src/code/null/null_snddma.c` | `SNDDMA_Submit`, `SNDDMA_Activate`, `S_RegisterSound`, `S_StartLocalSound`, `S_AddVoiceSamples` | open portability owners | Sound/device activation and voice paths remain intentionally silent/no-op |

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
- Current alias corpus: `2149` raw aliases
- Strict Ghidra address-backed aliases: `2076`
- Strict Ghidra address-backed coverage: about `37.932%`

The strict address-backed figure above now counts only alias keys whose
address exists in the committed Ghidra `functions.csv`. Useful HLIL-backed
aliases that do not appear as separate Ghidra function rows still contribute
to the raw alias corpus, but not to the strict address-backed subtotal.

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
[mapping round 205](./quakelive_steam_mapping_round_205.md):

| Rank | Address | Raw symbol | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004B3672` | `FUN_004b3672` | `495` |
| 2 | `0x004241C0` | `FUN_004241c0` | `482` |
| 3 | `0x00498890` | `FUN_00498890` | `480` |
| 4 | `0x00480DD0` | `FUN_00480dd0` | `479` |
| 5 | `0x004C84E0` | `FUN_004c84e0` | `479` |
| 6 | `0x0050EF80` | `FUN_0050ef80` | `476` |
| 7 | `0x00412970` | `FUN_00412970` | `472` |
| 8 | `0x004A21A0` | `FUN_004a21a0` | `470` |
| 9 | `0x0050BB00` | `FUN_0050bb00` | `469` |
| 10 | `0x004A0770` | `FUN_004a0770` | `467` |
| 11 | `0x0042C830` | `FUN_0042c830` | `465` |
| 12 | `0x0049FED0` | `FUN_0049fed0` | `465` |
| 13 | `0x0050BB00` | `FUN_0050bb00` | `469` |
| 14 | `0x004A0770` | `FUN_004a0770` | `467` |
| 15 | `0x0042C830` | `FUN_0042c830` | `465` |
| 16 | `0x0049FED0` | `FUN_0049fed0` | `465` |
| 17 | `0x004092D0` | `FUN_004092d0` | `463` |
| 18 | `0x004AD9C0` | `FUN_004ad9c0` | `463` |
| 19 | `0x004EC2A0` | `FUN_004ec2a0` | `462` |
| 20 | `0x004936D0` | `FUN_004936d0` | `460` |

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
  helper. Round 129 classified `6` engine-owned, `6`
  platform-service-owned, and `5` CRT/STL/support-library functions. Round
  130 classified `2` engine-owned, `2` platform-service-owned, and `9`
  CRT/STL/support-library functions, and corrected `sub_4770A0` from
  `jpeg_gen_optimal_table` to `finish_pass_gather`. Round 131 classified `8`
  engine-owned, `1` platform-service-owned, and `6`
  CRT/STL/support-library functions, and corrected the refreshed queue
  computation to normalize alias-key addresses against Ghidra entries before
  ranking unresolved functions. Round 132 classified `5` engine-owned, `1`
  platform-service-owned, and `17` CRT/STL/support-library functions, and
  corrected `sub_501AD0` from `crc32_z` to `crc32_little` while resolving
  adjacent zlib, libpng, and libvorbis support clusters. Round 133 classified
  `0` engine-owned, `2` platform-service-owned, and `23`
  CRT/STL/support-library functions while resolving a contiguous libogg queue
  block, the libvorbis `vorbis_staticbook_unpack` helper, and exact ZeroMQ TCP
  address/connecter helpers; it also intentionally left `sub_411F30`
  unresolved because the printed HLIL demangle conflicts with the observed
  `tcp_address.cpp` parsing body. Round 134 classified `0` engine-owned, `2`
  platform-service-owned, and `15` CRT/STL/support-library functions while
  resolving exact JPEG main/coef-controller helpers, `stbtt_FlattenCurves`,
  zlib `send_all_trees`, and a coherent libpng read-transform cluster headed
  by `png_do_expand_palette`; it also left `sub_4F67A0` unresolved pending a
  stable local CZMQ source-level function-name anchor. Round 135 classified
  `12` engine-owned, `2` platform-service-owned, and `2`
  CRT/STL/support-library functions while resolving exact botlib, client,
  renderer, qcommon, JsonCpp, libpng, and libzmq rows including
  `AAS_ClipToBBox`, `AAS_CalculateAreaTravelTimes`, `AAS_WriteRouteCache`,
  `LAN_GetServerInfo`, `Com_Printf`, `FS_SV_FOpenFileRead`,
  `JsonStyledWriter_isMultineArray`, and `zmq_req_t_xrecv`; it also kept
  `sub_4615E0`, `sub_463670`, and `sub_463980` intentionally unresolved until
  their exact STL container-type naming is anchored. Round 136 classified `4`
  engine-owned, `2` platform-service-owned, and `1`
  CRT/STL/support-library function while resolving the previously deferred
  `tcp_address.cpp` lane as `zmq_tcp_address_t_resolve` plus
  `zmq_tcp_address_mask_t_resolve`, exact botlib/parser rows
  `BotMovementViewTarget`, `PC_ExpandBuiltinDefine`, and
  `PS_ReadEscapeCharacter`, the JsonCpp numeric helper
  `JsonReader_decodeDouble`, and the chat validator
  `BotCheckValidReplyChatKeySet`; it also reclassified `sub_40B050` and
  `sub_419AD0` as STL tree-insert support rather than engine debt. Round 137
  classified `0` engine-owned, `0` platform-service-owned, and `15`
  CRT/STL/support-library functions while resolving the queue-head shared
  SteamID STL helpers plus an exact IJG/libjpeg marker-reader cluster headed
  by `get_dqt`, `get_dri`, `next_marker`, `read_markers`,
  `read_restart_marker`, `reset_marker_reader`, and `jinit_marker_reader`; it
  intentionally left `sub_463980` unresolved because the second
  `SteamDataSource` STL tree still lacks a stable specific owner name. Round
  138 classified `0` engine-owned, `7` platform-service-owned, and `4`
  CRT/STL/support-library functions while resolving the ZeroMQ
  `plain_mechanism` HELLO/WELCOME/INITIATE/READY handshake lane, the libvorbis
  `res2_class`/`res2_forward`/`res2_inverse` trio, and an STL ostream
  c-string insertion helper. Round 139 classified `0` engine-owned, `6`
  platform-service-owned, and `2` CRT/STL/support-library functions while
  closing a coherent `zmq::socket_base_t` destructor/URI/protocol/pipe/option
  lane plus the lower-level SteamID insert rebalance helpers
  `std_tree_insert_steamid_node_rebalance` and
  `std_tree_insert_steamid_map_node_rebalance`. Round 140 classified `0`
  engine-owned, `0` platform-service-owned, and `13`
  CRT/STL/support-library functions while closing the queue-head-adjacent
  libvorbisfile/libvorbis lifecycle lane around `_fetch_headers`,
  `vorbis_dsp_clear`, `_make_decode_ready`, `_decode_clear`, `ov_clear`,
  `_open_seekable2`, `_ov_open1`, `_ov_open2`, `ov_open_callbacks`,
  `vorbis_block_init`, `vorbis_block_clear`, `vorbis_synthesis_restart`, and
  `vorbis_synthesis_init`. Round 141 classified `5` engine-owned, `7`
  platform-service-owned, and `9` CRT/STL/support-library functions while
  closing the Win32 `NET_Config`/`NET_Init`/`NET_Shutdown`/`NET_Sleep` lane,
  the CZMQ `zauth.c` request/authentication cluster around
  `s_zap_request_new` and `s_self_authenticate`, the zlib
  `deflateInit2_`/`deflateInit_` pair, and a libpng storage-function lane
  headed by `png_set_IHDR`; it also normalized the audit's address-backed
  coverage wording to a strict Ghidra `functions.csv` check so HLIL-only alias
  rows no longer inflate the reported subtotal. Round 142 classified `0`
  engine-owned, `18` platform-service-owned, and `0`
  CRT/STL/support-library functions while closing the exact libzmq
  `pipe.cpp` lifecycle lane headed by `zmq_pipe_t_process_pipe_term_ack`.
  Round 143 classified `0` engine-owned, `0` platform-service-owned, and
  `14` CRT/STL/support-library functions while closing the missing SteamID STL
  helper families around `std_tree_find_or_insert_steamid_value_node`,
  `std_tree_insert_steamid_map_node`, and the newly anchored second
  SteamID-to-value tree. Round 144 classified `13` engine-owned functions
  while closing the qcommon collision helper split around
  `CM_TraceCapsuleThroughCapsule`, `CM_TraceBoundingBoxThroughCapsule`,
  `CM_TraceThroughLeaf`, `CM_TestInLeaf`, `CM_TestBoxInBrush`,
  `CM_ClipHandleToModel`, and `CM_ModelBounds`, plus the adjacent renderer
  `GL_Bind`, `GL_SelectTexture`, `GL_Cull`, and `GL_TexEnv` wrappers; it also
  corrected the earlier `sub_4C55D0` alias from
  `CM_TraceCapsuleThroughCapsule` to the exact position-test owner
  `CM_TestCapsuleInCapsule`. Round 158 classified `0` engine-owned, `0`
  platform-service-owned, and `6` CRT/STL/support-library functions while
  closing the remaining obvious libpng chunk-handler gaps around
  `png_handle_iCCP`, `png_handle_sPLT`, `png_handle_sCAL`,
  `png_handle_tIME`, `png_handle_tEXt`, and `png_handle_zTXt`; it
  intentionally left the adjacent unknown-chunk control helper at
  `sub_511670` deferred because the retail wording still diverged from the
  checked-in `png_handle_unknown` body. Round 159 classified `0`
  engine-owned, `0` platform-service-owned, and `15`
  CRT/STL/support-library functions while closing the retained
  `zlib/trees.c` Huffman-management lane around `gen_bitlen`, `scan_tree`,
  `detect_data_type`, `_tr_init`, `build_tree`, `build_bl_tree`,
  `_tr_stored_block`, `_tr_align`, and `_tr_flush_block`; it intentionally
  left the compiler-split stored-block copy helper unnamed because the
  checked-in `trees.c` keeps that payload copy logic inlined rather than as a
  standalone helper. Round 162 later closed that earlier libpng deferral with
  `png_handle_unknown` and the adjacent `pngwutil.c` chunk-write helper lane
  (`png_save_uint_32`, `png_save_uint_16`, `png_write_sig`,
  `png_write_chunk_header`, `png_write_chunk_data`, and
  `png_write_chunk_end`). Round 163 then closed the retained libvorbis
  `floor1.c` setup-and-fit scaffold around `floor1_pack`, `floor1_unpack`,
  `floor1_look`, `render_point`, `render_line`, `render_line0`,
  `accumulate_fit`, `fit_line`, `inspect_error`, and `post_Y`, plus the small
  `floor1_free_*`, `icomp`, `vorbis_dBquant`, and shared `ov_ilog` helpers.
  Round 164 then closed the adjacent libpng writer lane around
  `png_check_keyword`, `png_write_complete_chunk`, `png_write_tEXt`,
  `png_write_zTXt`, `png_write_pCAL`, `png_write_iCCP`, `png_write_sPLT`,
  `png_write_IEND`, `png_write_gAMA_fixed`, and `png_write_sRGB`.
  Each later pass still needs to classify candidates before treating them as
  source parity debt.
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
   queue beginning with `sub_41AD70`, `sub_4E6730`, and `sub_4B4100`; classify
   each as engine-owned, platform-service-owned, CRT/STL, Awesomium, or Steam
   SDK support before opening source debt.
2. If repo-wide parity is the target, choose whether FG-01 is permanently
   excluded or whether an open service replacement should be designed.
3. Re-baseline the Unix/null portability target so FG-02 and FG-03 can either
   become explicit permanent compatibility lanes or receive real runtime work.
4. Refresh native Windows runtime/build evidence and rerun the retail-module
   probe after the renderer font-atlas blocker has a current disposition.
