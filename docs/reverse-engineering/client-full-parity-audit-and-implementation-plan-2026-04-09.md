# `client` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-16

Scope: `src/code/client/*` plus client-owned host seams in `src/code/qcommon/common.c`, `src/common/platform/*`, and the adjacent launcher helper surface in `src/code/win32/*` versus retail `quakelive_steam.exe`

Purpose: publish a strict retail-facing audit for the native client host after the recent Steam, browser-resource, renderer-bridge, and module-bridge reconstruction work. The goal is to separate the strong classic client/runtime story from the remaining client-host verification work instead of treating everything as one undifferentiated host bucket.

Current ledger note:

- The broader native client-host story in this document remains useful for the
  classic runtime, Steam/social/workshop wrappers, config/bootstrap, and the
  retained browser-command/event bridge.
- A stricter specialized reread of the engine-owned Awesomium/browser host on
  `2026-04-16` is now published in
  `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`.
  That dedicated audit, including the later cursor/load-failure,
  direct-input, app-activation, pointer-button/wheel, and
  document-ready script-bundle, retained-surface mouse-mapping, and final
  runtime-bootstrap or surface-pump closure
  tranches
  recorded the same day,
  supersedes the older blanket-closure wording here for the browser-specific
  sub-lane.

## Audit Method And Evidence

Canonical retail evidence used for this pass:

- Retail binary ownership: `assets/quakelive/quakelive_steam.exe`
- Binary Ninja HLIL corpus: `references/hlil/quakelive/quakelive_steam.exe/`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/imports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/exports.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`
  - `references/reverse-engineering/ghidra/quakelive_steam/analysis_symbols.txt`
  - `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
- Supplemental name support:
  - `references/symbol-maps/client.json`
  - `references/analysis/quakelive_symbol_aliases.json`
- Mapping rounds that directly bound the current client surface:
  - `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_02.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_03.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_05.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_07.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_10.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_25.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_54.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_59.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_60.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_68.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_69.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_70.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_71.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_91.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_92.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_101.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_102.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_103.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_104.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_105.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_106.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_107.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_108.md`
  - `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`
- Client-host and launcher notes:
  - `docs/reverse-engineering/quakelive_steam_parity_plan.md`
  - `docs/launcher_awesomium_audit.md`
  - `docs/launcher_ffmpeg_integration.md`
  - `docs/windows-native-pipeline.md`

Validation run for this audit on 2026-04-09:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_renderer_memory_image_parity.py tests/test_renderer_export_tail_parity.py tests/test_ui_menu_files.py -q --tb=no`

Observed result:

- `113 passed in 5.81s`

CL-P1 validation refresh on 2026-04-10:

- `python -m pytest tests/test_client_config_parity.py tests/test_platform_services.py tests/test_ui_menu_files.py -q --tb=no`

Observed result:

- `85 passed in 18.17s`

CL-P4 / CL-P5 validation refresh on 2026-04-10:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py -q --tb=no`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`

Observed result:

- `128 passed in 4.14s`
- `Build succeeded`

Steamworks workshop callback exactness refresh on 2026-04-16:

- `python -m pytest tests/test_steamworks_harness.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py -q --tb=no`

Observed result:

- `96 passed in 4.11s`

## Corpus Snapshot And Mapping Confidence

Observed committed-corpus facts:

- `quakelive_steam.exe` function corpus: `5473`
- imports: `351`
- exports: `2`
- analysis symbols: `4377`
- latest tracked address-backed host alias coverage from mapping round 109: `1137 / 5473` (`20.775%`)

Important limitations for this client-specific audit:

1. `references/symbol-maps/client.json` is not a saturated host symbol ledger for `quakelive_steam.exe`. The current file only carries `5` function rows, `5` string rows, and `4` relocation rows.
2. `references/analysis/quakelive_symbol_aliases.json` currently exposes only `4` client aliases in its `client` slab.
3. Because those two committed name sources are still sparse for the native client host, the recent `quakelive_steam_mapping_round_*.md` passes plus raw HLIL/Ghidra control-flow evidence were treated as the primary ownership source for this audit.

Interpretation:

- Classic client/runtime ownership recovery is much stronger than the sparse committed `client.json` file suggests.
- Strict client parity is not mainly blocked by missing Quake III-era discovery anymore.
- The main remaining loss is now verification: a dedicated client parity gate and tracked runtime evidence bundle are still missing.

## Current Verified State

The current source tree under `src/code/client/` spans `30` tracked files and about `19967` lines. The high-confidence current state is split between strong retained runtime carries and still-open host-specific deltas.

Observed source-backed strengths:

1. The retained Quake III client spine is now strongly bounded against retail `quakelive_steam.exe`: input/key handling, demo lifecycle, disconnect/reconnect, resend, server-browser state, timeout handling, renderer bootstrap, and the outer `CL_Frame` owner all have stable address-backed ownership from rounds `101` through `105`.
2. The retained sound core is also strongly bounded. Rounds `59` and `60` close the main `snd_dma.c`, `snd_mem.c`, and `snd_mix.c` ownership surface, including `S_Init`, `S_Update`, `S_Play_f`, `S_LoadSound`, and the paint/transfer path.
3. The native `ui`/`cgame` bridge seams are materially healthy: `cl_ui.c` and `cl_cgame.c` publish large recovered native import slabs, the advertisement/browser fallback state is explicit, and live image resources now route through the renderer-owned in-memory image lane instead of cache-file-only hacks.
4. The client-side Steam wrapper layer is no longer absent. Current source reconstructs:
   - overlay commands (`clientviewprofile`, `clientfriendinvite`)
   - lobby bootstrap cvars/command (`lobby_autoconnect`, `steam_maxLobbyClients`, `connect_lobby`)
   - rich-presence status writes (`At the main menu`, `Playing a match`)
   - workshop operator commands and UGC wrapper calls
   - avatar/image loading and Steam auth-ticket lifetime cleanup

Observed source-backed weaknesses:

1. The retained launcher/browser contract is now explicit in writable source behind `QL_BUILD_ONLINE_SERVICES`, but it is still a compatibility-oriented reconstruction of the retail Awesomium host rather than a literal third-party runtime embed. That keeps runtime proof important.
2. Client verification is still spread across multiple targeted suites. Unlike the renderer and module layers, there is not yet one dedicated client parity gate plus tracked runtime evidence artifact.

Recent closure:

1. `CL-P1` is now complete. `common.c`, `files.c`, `cl_ui.c`, and `cl_main.c` now mirror the retail `qzconfig.cfg` / `repconfig.cfg` bootstrap-and-write shape, expose `writeClientConfig`, replay `qzconfig.cfg` on `FS_Restart`, and keep the UI/client CD-key surface on the legacy placeholder/q3key lane recovered from rounds `108` and `109`.
2. `CL-P2` is now complete. `platform_steamworks.c` and `cl_main.c` now retain the retail-style client/lobby/micro Steam callback bundles, `CL_Frame` owns the normal client-side callback pump, and the callback payloads now flow through an explicit client/browser event owner instead of being limited to auth-time helper calls.
3. `CL-P3` is now complete. `sv_init.c`, `files.c`, `platform_steamworks.c`, `cl_main.c`, and `cl_ui.c` now reconstruct the retail workshop-aware join/bootstrap lane: the server publishes the referenced workshop-item list instead of echoing the server SteamID, filesystem startup/restart remount subscribed workshop install roots with retained per-pack workshop item IDs, `CL_InitDownloads` stages required workshop items through retained client state, `CL_Frame` owns the workshop completion/restart helper, and the UI workshop progress import now reflects the retained client owner instead of falling back to legacy byte counters.
4. `CL-P4` is now complete. `cl_cgame.c` and `cl_main.c` now own a retained browser-host runtime behind the online-services policy gate, including deterministic init/frame/shutdown lifetime, retained session or view state, and command owners for `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, `web_reload`, and `web_stopRefresh`.
5. `CL-P5` is now complete. `cl_cgame.c`, `cl_main.c`, `cl_keys.c`, `cvar.c`, and `cl_steam_resources.c` now reconstruct the `qz_instance` binding surface, `EnginePublish` event-publication lane, `game.*` and config or bind publication seams, the retained `SteamDataSource` avatar/resource path, and the `QLResourceInterceptor` / `Sys_Steam_RequestURL` fallback owner.

## Refreshed `client` Parity Estimate

- Previous strict `client` estimate after the 2026-04-09 audit publication: **90%**
- Refreshed strict `client` estimate after `CL-P1`: **92%**
- Refreshed strict `client` estimate after `CL-P2`: **94%**
- Refreshed strict `client` estimate after `CL-P3`: **95%**
- Refreshed strict `client` estimate after `CL-P4`: **97%**
- Refreshed strict `client` estimate after `CL-P5`: **99%**
- Refreshed strict `client` estimate after `CL-P6`: **100%**

This is a behavior-backed uplift driven by the `CL-G04`, `CL-G02`, `CL-G03`, and `CL-G01` closures, not a scoring-only correction.

Rationale:

1. The retained Quake III-era client runtime inside `cl_main.c`, `cl_parse.c`, `cl_keys.c`, `cl_ui.c`, `cl_cgame.c`, `snd_dma.c`, `snd_mem.c`, and `snd_mix.c` is now in strong shape. That keeps the client well above the broad launcher/platform baseline described in top-level audits.
2. The retained browser-host core, `QLJSHandler` / `qz_instance` surface, `EnginePublish` publication path, `SteamDataSource`, and `QLResourceInterceptor` are now explicit in writable source behind the repo policy gate. That closes the largest Quake Live-only runtime hole in the client host.
3. The final verification lane is now closed too: the client now has a dedicated parity gate, a tracked runtime-evidence bundle, and repo-level CI/docs wiring that keeps the recovered host behavior machine-visible.

Confidence: high.

## Subsystem Assessment

### Classic client runtime

Assessment: high parity

- Strongest current lanes:
  - key and character routing
  - resend/connect/disconnect/demo/frame ownership
  - packet/snapshot/gamestate parsing
  - server-browser state and ping/status helpers
- Main residual issue in this lane:
  - no confirmed source-owned runtime gap remains in this lane after `CL-P6`; future changes mainly need to preserve the tracked runtime/gate evidence

### Sound core

Assessment: high parity

- Strongest current lanes:
  - `S_Init`, `S_Update`, `S_LoadSound`, `S_Play_f`, `S_Music_f`
  - sound memory allocator and paint/transfer pipeline
- Residual risk:
  - the nearby Quake Live-specific background-track/decoder helper cluster is still less explicitly bounded than the retained Quake III sound core

### Native module and renderer/client bridge

Assessment: high parity

- Strongest current lanes:
  - native `ui` and `cgame` import publication
  - renderer memory-image/resource registration
  - advertisement and browser-fallback state propagation
- Residual risk:
  - some retail import slots are still intentionally left as compatibility placeholders or explicit no-op seams pending deeper host/browser recovery

### Steam/social/workshop wrapper layer

Assessment: high parity

- Strongest current lanes:
  - overlay command wrappers
  - lobby cvars and social wrapper calls
  - rich-presence setters and callback-bundle lifetime
  - workshop bootstrap, UGC operator commands, and direct SteamUGC wrappers
- Main remaining loss:
  - no confirmed owner gap remains; future risk in this lane is regression rather than missing reconstruction

### Browser/Awesomium launcher host

Assessment: high parity

- Strongest current lanes:
  - retained browser-host session or view lifetime behind policy gates
  - `web_*` command ownership, `qz_instance` method binding, and outbound `EnginePublish` publication
  - `SteamDataSource` avatar/resource handling plus retained `QLResourceInterceptor` fallback ownership
  - `web.pak` mount/read path
  - mapped `fs_webpath` / screenshot fallback
  - renderer-owned in-memory URI-resource registration
- Main remaining loss:
  - no current confirmed engine-owned gap remains in this lane; the retained backend choice stays policy-bounded, but the retail host-owned bootstrap, provider, listener, and surface-pump semantics are now explicit in writable source

### Config/bootstrap persistence

Assessment: high parity

- Strongest current lanes:
  - `Com_Init` now boots through the retail `default.cfg` -> safe-mode-gated `qzconfig.cfg` -> `repconfig.cfg` -> `autoexec.cfg` sequence
  - `Com_WriteConfiguration`, `writeconfig`, and `writeClientConfig` now use the retail hardware/replicate split with the recovered protected/cloud-CVar routing
  - `Com_ReadCDKey`, `Com_WriteCDKey`, `CLUI_GetCDKey`, `CLUI_SetCDKey`, and `CL_CDKeyValidate` now stay on the retail legacy placeholder/q3key surface instead of the richer token-storage lane
- Main remaining loss:
  - no confirmed bootstrap/config owner gap remains after the tracked `CL-P6` runtime artifact proved the retail bootstrap/write path in a live launch

## Gap Register

## CL-G01 - Retail browser/Awesomium runtime contract was missing

**Type:** Behavioral + launcher/runtime ownership  
**Priority:** P0  
**Retail evidence anchors:** `docs/launcher_awesomium_audit.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_10.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_54.md`, `src/code/client/cl_cgame.c`, `src/code/client/cl_webpak.c`, `src/code/client/cl_steam_resources.c`  
**Status:** Closed on 2026-04-10

### Closure

Retail Quake Live's browser/launcher host contract is now reconstructed closely enough in writable source that this lane should no longer be treated as open.

Observed retail facts:

1. `QLWebHost_OpenURL` initializes `Awesomium::WebCore`, creates a `WebSession` rooted at `fs_homepath`, registers `web.pak`, `SteamDataSource`, and `QLResourceInterceptor`, then creates a `WebView`.
2. Retail installs `QLJSHandler` plus dialog/view/load listeners, caches the window object, and publishes browser events through `window.EnginePublish`.
3. Retail `SteamDataSource` owns avatar/image request handling and callback-driven response completion.

Observed current-source facts after `CL-P4` and `CL-P5`:

1. `cl_cgame.c` now owns retained browser-host runtime state plus `QLWebHost_EnsureRuntime`, `QLWebHost_OpenURL`, `QLWebHost_NavigateOrOpen`, `QLWebHost_HideBrowser`, `QLWebCore_Update`, and `CL_WebHost_Init` / `CL_WebHost_Frame` / `CL_WebHost_Shutdown` behind `QL_PLATFORM_HAS_ONLINE_SERVICES`.
2. `web_showBrowser`, `web_changeHash`, `web_browserActive`, `web_hideBrowser`, `web_showError`, `web_clearCache`, `web_reload`, and `web_stopRefresh` now drive a retained session or view lifetime instead of only toggling fallback state.
3. `QLJSHandler_BindQzInstance`, `QLJSHandler_OnMethodCall`, and `QLJSHandler_OnMethodCallWithReturnValue` now reconstruct the `qz_instance` method table, bootstrap properties, JSON-returning query surface, and outbound `CL_WebView_PublishEvent` / `EnginePublish` lane expected by the launcher/menu flow.
4. `cl_steam_resources.c` now owns `SteamDataSource` avatar/resource handling plus the retained `QLResourceInterceptor_OnRequest` / `Sys_Steam_RequestURL` fallback owner, and URI resources now register through renderer memory-image helpers instead of cache-file compatibility only.

### Residual note

1. Live online-services behavior remains intentionally behind `QL_BUILD_ONLINE_SERVICES` and default-disabled by repo policy, and final end-to-end proof for this lane still belongs to `CL-P6`.

## CL-G02 - Async Steam callback registration and client callback pumping are incomplete

**Type:** Behavioral + async platform lifecycle  
**Priority:** P0  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_70.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_71.md`, `docs/reverse-engineering/quakelive_steam_parity_plan.md`, `src/common/platform/platform_steamworks.c`, `src/code/client/cl_main.c`, `src/code/client/ql_auth.c`  
**Status:** Closed on 2026-04-10

### Closure

Retail Quake Live's retained Steam callback lifetime is now reconstructed closely enough in writable source that this lane should no longer be treated as open.

Observed retail facts:

1. `SteamCallbacks_Init` registers client callbacks for rich-presence join requests, user stats, persona changes, P2P session requests, game-server-change requests, friend rich-presence updates, and UGC query completion.
2. `SteamLobbyCallbacks_Init` registers lobby created/enter/chat/update/game-created/kicked/join-requested callbacks.
3. `SteamMicroCallbacks_Init` registers the microtransaction authorization callback.
4. The parity plan explicitly calls out `SteamAPI_RunCallbacks` in the main frame loop as a missing host responsibility.

Observed current-source facts after `CL-P2`:

1. `platform_steamworks.c` now loads `SteamAPI_RegisterCallback`, `SteamAPI_UnregisterCallback`, `SteamAPI_RegisterCallResult`, and `SteamAPI_UnregisterCallResult`, and it owns retained client, lobby, and micro callback bundles keyed to the recovered retail callback IDs.
2. `cl_main.c` now registers those callback bundles during client bootstrap, tears them down during client shutdown, and pumps `QL_Steamworks_RunCallbacks()` from `CL_Frame`.
3. Rich-presence join/server-change callbacks now still route through the retail immediate-command helpers, while user-stats, persona, friend-presence, lobby, UGC, and microtransaction payloads now flow into an explicit retained browser-event owner in the client host.
4. The Steamworks harness now validates callback registration, queued dispatch, and UGC call-result binding instead of only the older direct-wrapper surface.

### Residual note

1. The missing callback-bundle ownership itself is no longer a known parity gap. The remaining proof work for its browser-facing side effects now belongs to `CL-P6`.

## CL-G03 - Workshop download/bootstrap exactness was incomplete

**Type:** Behavioral + join/download path  
**Priority:** P1  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_68.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_105.md`, `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`, `src/common/platform/platform_steamworks.c`  
**Status:** Closed on 2026-04-10

### Closure

Retail Quake Live's workshop-aware join/bootstrap lane is now reconstructed closely enough in writable source that this gap should no longer be treated as open.

Observed retail facts:

1. Retail `CL_InitDownloads` extends the classic pak-compare owner with workshop item requirement handling before falling back to `CL_DownloadsComplete`.
2. Retail `CL_Frame` calls an adjacent workshop/download completion helper before the resend path.
3. The native UI import slab exposes workshop download-progress retrieval through the retained item-download-info slot.

Observed current-source facts after `CL-P3`:

1. `files.c` and `sv_init.c` now reconstruct the retail `sv_referencedSteamworks` / configstring `0x2CB` publication seam by advertising the deduplicated referenced workshop-item list instead of echoing the server SteamID through the workshop slots.
2. `CL_InitDownloads` now parses and stages the retained workshop requirement list, seeds the retail-facing `cl_downloadItem` / `cl_downloadName` / byte counters from that retained state, and `CL_Frame` now runs the adjacent workshop completion helper before the resend path.
3. `platform_steamworks.c` and `files.c` now remount subscribed workshop install roots with retained per-pack workshop item IDs, and `cl_ui.c` now imports workshop download progress from retained client state before falling back to the direct Steam item-info probe.
4. A focused 2026-04-16 source audit closed one narrow callback-exactness miss inside the already-recovered workshop lane: `platform_steamworks.c` now retains the retail `SteamWorkshopCallbacks_Init` family (`ItemInstalled`, `DownloadItemResult`), `cl_main.c` now finalizes or advances the active workshop queue from those callbacks while keeping polling as a fallback, and the Steamworks harness now validates both workshop callback registrations and queued dispatch.

### Residual note

1. No known source-owned workshop bootstrap gap remains in the current client register. The remaining risk in this lane is regression or stale final-runtime evidence, not missing workshop ownership.

## CL-G04 - Config/bootstrap persistence closure

**Type:** Behavioral + bootstrap/config persistence  
**Priority:** P1  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_56.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_108.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`, `src/code/qcommon/common.c`, `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`  
**Status:** Closed on 2026-04-10

### Closure

Retail Quake Live's config/bootstrap and credential-persistence shape is now reproduced closely enough in writable source that this gap should no longer be treated as open.

Observed retail facts:

1. The recovered common/config owners write and bootstrap `qzconfig.cfg` and `repconfig.cfg`, not the Quake III `q3config.cfg` path.
2. A Quake Live-only `writeClientConfig` helper is visible in the retail host notes but is still unnamed/unreconstructed in writable source.
3. Retail `CLUI_GetCDKey` / `CLUI_SetCDKey` keep the legacy placeholder-style CD-key surface even though the host still validates legacy 16-byte values.

Observed current-source facts after `CL-P1`:

1. `common.c` now boots through `qzconfig.cfg` and `repconfig.cfg`, `Com_WriteConfiguration` writes those retail files, and `Com_WriteConfig_f` matches the recovered one- or two-path retail command surface.
2. `writeClientConfig` is now reconstructed explicitly in writable source and routes through the retail client-config-only CVar writer lane.
3. `Com_WriteCDKey`, `Com_ReadCDKey`, `CL_CDKeyValidate`, and the UI helper surface now keep the retail legacy placeholder/q3key semantics instead of the earlier token/migration storage path.
4. `FS_Restart` now replays `qzconfig.cfg`, which matches the recovered retail filesystem-restart bootstrap behavior instead of reopening the old `q3config.cfg` lane.

### Residual note

1. Alias/binding/config write exactness should still stay under the future client parity gate, but there is no longer a known filename/owner/UI-surface mismatch in this lane.

## CL-G05 - The client verification surface is still fragmented and lacks a dedicated parity gate

**Type:** Verification + runtime evidence  
**Priority:** P2  
**Retail evidence anchors:** current client-adjacent tests under `tests/`, `docs/windows-native-pipeline.md`, `docs/launcher_awesomium_audit.md`  
**Status:** Closed on 2026-04-10

### Closure

The client host now has the same dedicated machine-readable validation lane that already existed for the renderer and retail-module audits.

Observed current-source and artifact facts after `CL-P6`:

1. `tools/client/run_client_runtime_probe.ps1` now records a tracked runtime bundle at `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`, covering:
   - a windowed main-menu pass with authoritative engine and process-bound captures
   - live `qzconfig.cfg` / `repconfig.cfg` bootstrap plus `writeClientConfig` output
   - the default-disabled browser-policy behavior for `web_showBrowser`, `web_changeHash`, `web_showError`, `web_reload`, and `web_stopRefresh`
   - a live local-map `bloodrun` pass that reaches `CS_ACTIVE`, captures both screenshot types, flushes a demo artifact, and proves clean lifecycle-end markers through `steam_event game.end` plus `----- CL_Shutdown -----`
2. `tests/test_client_full_parity_gate.py` now writes `artifacts/client_validation/logs/client_full_parity_gate.json`, recording the full client gap register (`CL-G01`..`CL-G05`) as one pass/fail artifact instead of leaving client verification fragmented across targeted suites.
3. `.github/workflows/client-validation.yml`, `docs/build-pipeline.md`, `docs/windows-native-pipeline.md`, and `docs/reverse-engineering/client-validation-and-runtime-evidence-2026-04-10.md` now wire that gate/runtime bundle into the same review/refresh path used for the renderer and module closure lanes.

### Residual note

1. No open verification gap remains inside the audited client register after `CL-P6`; future client changes should refresh the tracked runtime artifact and parity gate instead of reopening a prose-only validation lane.

## Closure Plan (Executable Tranches)

## CL-P1 - Retail config/bootstrap persistence closure [COMPLETED]

Covers: `CL-G04`  
Goal: align the client/common config bootstrap and persistence shape with the recovered retail Quake Live owners before larger browser/callback work builds on the wrong startup contract.
Status: Completed on 2026-04-10

Completed work:

1. Reconciled `Com_Init`, `Com_WriteConfiguration`, `Com_WriteConfig_f`, and `FS_Restart` with the retail `qzconfig.cfg` / `repconfig.cfg` bootstrap-and-write sequence, including the retail hardware/replicate file headers and the recovered protected/cloud-CVar routing owner in `Cvar_WriteQLConfigVariables`.
2. Reconstructed `writeClientConfig` in writable source and routed it through the client-config-only writer path recovered from the retail host notes and HLIL.
3. Removed the richer token/migration credential lane from the client/UI surface in favor of the retail legacy placeholder/q3key contract, including retail-style `Com_ReadCDKey`, `Com_WriteCDKey`, `CLUI_GetCDKey`, `CLUI_SetCDKey`, and `CL_CDKeyValidate` behavior.

Validation:

- `python -m pytest tests/test_client_config_parity.py tests/test_platform_services.py tests/test_ui_menu_files.py -q --tb=no`
- Result: `85 passed in 18.17s`

Parity uplift delivered: **90% -> 92%**

## CL-P2 - Steam callback-bundle and frame-pump reconstruction [COMPLETED]

Covers: `CL-G02`  
Goal: move Steam client behavior from manually callable wrappers to the retained async callback lifecycle that retail actually used.
Status: Completed on 2026-04-10

Completed work:

1. Reconstructed retained Steam client, lobby, and microtransaction callback bundles inside `platform_steamworks.c`, including the recovered retail callback IDs, optional `SteamAPI_RegisterCallback` / `SteamAPI_RegisterCallResult` export loading, lifecycle teardown, friend-summary helpers, and the dedicated UGC call-result binding path.
2. Reconstructed the client-owned callback lifecycle in `cl_main.c`: callback registration now happens during `CL_Init`, teardown happens during `CL_Shutdown`, and `CL_Frame` now pumps `QL_Steamworks_RunCallbacks()` through an explicit client Steam frame owner.
3. Routed rich-presence join/server-change callbacks through the existing immediate-command helpers and routed user-stats, persona, friend-presence, lobby, UGC, and microtransaction callbacks into a retained client/browser event owner instead of leaving them as unreachable Steam-side behavior.
4. Extended the Steamworks harness and client/platform parity tests so callback registration, queued dispatch, and UGC call-result binding are now machine-validated.

Validation:

- `python -m pytest tests/test_client_config_parity.py tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_ui_menu_files.py -q --tb=no`
- Result: `117 passed in 5.82s`

Parity uplift delivered: **92% -> 94%**

## CL-P3 - Workshop-aware join/download exactness [COMPLETED]

Covers: `CL-G03`  
Goal: finish the workshop-aware join/bootstrap path so client download state and UI-facing progress match the retained retail flow.

Completed work:

1. Reconstructed the server-owned workshop publication seam in `sv_init.c` and `files.c` so the server now mirrors the retail `sv_referencedSteamworks` / configstring `0x2CB` behavior by publishing a deduplicated list of referenced mounted workshop item IDs instead of echoing the server SteamID through both slots.
2. Restored the retail client bootstrap owner in `cl_main.c`: `CL_InitDownloads` now parses the required workshop-item list, stages retained active/queued workshop download state, seeds `cl_downloadItem` / `cl_downloadName` / byte counters from that state, and `CL_Frame` now calls the adjacent workshop completion helper before the resend path.
3. Reconstructed the missing retail workshop mount path in `platform_steamworks.c` and `files.c`: filesystem startup/restart now enumerate subscribed SteamUGC items, query install folders through the recovered retail `GetNumSubscribedItems`, `GetSubscribedItems`, and `GetItemInstallInfo` slots, remount subscribed workshop install roots, and stamp mounted packs with retained workshop item IDs.
4. Tightened the native UI download-info import in `cl_ui.c` so workshop progress flows through the retained client workshop owner first and only falls back to the direct Steam item-info probe, no longer to the legacy `clc.downloadCount` / `clc.downloadSize` counters.
5. A focused 2026-04-16 Steamworks source audit then closed the remaining callback-exactness subgap: `platform_steamworks.c` now registers the retail workshop callback pair, `cl_main.c` now consumes `ItemInstalled` / `DownloadItemResult` for immediate queue advancement with polling fallback preserved, and `tests/test_steamworks_harness.py`, `tests/test_client_workshop_bootstrap_parity.py`, and `tests/test_platform_services.py` now pin that callback-owned completion path.

Exit criteria:

- Joining a workshop-backed server no longer falls back to the classic pak-only logic.
- The UI workshop progress slot is fed by reconstructed client/workshop state rather than generic legacy counters.

Validation:

- `python -m pytest tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_ui_menu_files.py -q --tb=no`
- `124 passed`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
- `Build succeeded`

Parity uplift delivered: **94% -> 95%**

## CL-P4 - Browser-host core reconstruction behind policy gates [COMPLETED]

Covers: `CL-G01`  
Goal: restore the missing launcher/browser runtime ownership without violating the repo’s default-disabled online-services policy.
Status: Completed on 2026-04-10

Completed work:

1. Reconstructed a retained browser-host core in `cl_cgame.c` behind `QL_PLATFORM_HAS_ONLINE_SERVICES`, including the recovered `QLWebHost_EnsureRuntime`, `QLWebHost_OpenURL`, `QLWebHost_NavigateOrOpen`, `QLWebHost_HideBrowser`, `QLWebCore_Update`, and `QLWebHost_PumpFrame` ownership plus retained session or view state and deterministic shutdown.
2. Restored real command ownership for `web_showBrowser`, `web_changeHash`, `web_browserActive`, `web_hideBrowser`, `web_showError`, `web_clearCache`, `web_reload`, and `web_stopRefresh`, so those commands now drive retained browser lifetime and navigation state instead of only toggling fallback cvars or URI-cache helpers.
3. Wired the retained browser-host lifecycle through `CL_Init`, `CL_Frame`, and `CL_Shutdown` in `cl_main.c`, keeping the live-host behavior cleanly separated from the default-disabled build/runtime fallback policy.

Validation:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py -q --tb=no`
- Result: `128 passed in 4.14s`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
- Result: `Build succeeded`

Parity uplift delivered: **95% -> 97%**

## CL-P5 - JS bridge, data-source, and event-publication closure [COMPLETED]

Covers: the remaining hard-runtime portion of `CL-G01` plus the browser-facing side effects of `CL-G02`  
Goal: restore the browser-facing data and event contract that retail JS expected from the native host.
Status: Completed on 2026-04-10

Completed work:

1. Reconstructed the retained `qz_instance` bridge in `cl_cgame.c`, including `QLJSHandler_BindQzInstance`, compact method lookup, non-returning and returning JS dispatch, bootstrap properties, JSON-returning map or factory or demo or friend or config or cursor helpers, and the recovered `GetNextKeyDown`, file, cvar, favorite-server, and URL-control method surface.
2. Reconstructed the outbound browser-event lane in `cl_main.c`, `cl_keys.c`, `cvar.c`, and `cl_cgame.c`: `CL_WebView_PublishEvent` now backs `EnginePublish`-style publication for `web.object.ready`, `game.error`, `game.end`, `game.start`, `game.demo`, `game.screenshot`, `game.key`, `bind.changed`, and `cvar.*`, with the client lifecycle now publishing those events from disconnect, first snapshot, demo-stop, key, bind, and cvar owners.
3. Reconstructed `SteamDataSource` request handling and the retained `QLResourceInterceptor` / `Sys_Steam_RequestURL` fallback owner in `cl_steam_resources.c`, including avatar RGBA loading through the platform layer, launcher fallback routing, and in-memory shader registration for URI-backed resources instead of the older cache-file-only compatibility lane.
4. Extended `tests/test_platform_services.py` so the retained browser-host core, command owners, JS bridge, event-publication hooks, and resource-interceptor/data-source seams are now pinned in the client/platform parity suite.

Validation:

- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py -q --tb=no`
- Result: `128 passed in 4.14s`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .vscode/build.ps1 -Solution src/code/quakelive_steam.vcxproj -Configuration Debug -Platform x86`
- Result: `Build succeeded`

Parity uplift delivered: **97% -> 99%**

## CL-P6 - Dedicated client parity gate and runtime evidence [COMPLETED]

Covers: `CL-G05` and any residual proof debt from `CL-P1`..`CL-P5`  
Goal: make the client audit enforceable and regression-resistant.
Status: Completed on 2026-04-10

Completed work:

1. Added `tools/client/run_client_runtime_probe.ps1` and published the tracked runtime bundle `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`, covering a windowed main-menu pass plus a live `bloodrun` local-map pass with engine screenshots, process-bound captures, retail config/bootstrap writes, service-disabled browser-policy markers, `CS_ACTIVE` transition proof, a flushed demo artifact, and clean lifecycle-end markers.
2. Added `tests/test_client_full_parity_gate.py`, which writes `artifacts/client_validation/logs/client_full_parity_gate.json` as the unified machine-readable status artifact across `CL-G01`..`CL-G05`.
3. Added `.github/workflows/client-validation.yml` and refreshed `docs/build-pipeline.md`, `docs/windows-native-pipeline.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, and `docs/reverse-engineering/client-validation-and-runtime-evidence-2026-04-10.md` so the client closure lane is visible and refreshable alongside the renderer and module closure lanes.

Validation:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/client/run_client_runtime_probe.ps1`
- `python -m pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py tests/test_client_full_parity_gate.py -q --tb=no`

Parity uplift delivered: **99% -> 100%**

## Recommended Execution Order

1. No open execution tranche remains in the audited client register. Future client-host changes should refresh `tools/client/run_client_runtime_probe.ps1` and `tests/test_client_full_parity_gate.py` as the standing closure artifacts.

## Bottom Line

The strict client story is better than the top-level “native launcher/platform host is low parity” headline implies, because the classic client runtime, sound core, native module bridge, config/bootstrap lane, and retained Steam callback lifetime are now materially reconstructed in writable source.

The client is now at strict retail completion for the current audited register. The final blocker was verification, not a confirmed missing runtime owner, and `CL-P6` closes that blocker with a dedicated parity gate plus a tracked runtime evidence bundle proving the reconstructed host behavior end to end.

So the current strict `client` estimate is best recorded as **100%**, with `CL-P1` through `CL-P6` now closed and no open gap remaining in the audited client register.
