# `client` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-09

Scope: `src/code/client/*` plus client-owned host seams in `src/code/qcommon/common.c`, `src/common/platform/*`, and the adjacent launcher helper surface in `src/code/win32/*` versus retail `quakelive_steam.exe`

Purpose: publish a strict retail-facing audit for the native client host after the recent Steam, browser-resource, renderer-bridge, and module-bridge reconstruction work. The goal is to separate the strong classic client/runtime story from the still-open Quake Live launcher/platform story instead of treating both as one undifferentiated host bucket.

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
- The main remaining loss is Quake Live launcher/bootstrap behavior, async Steam callback ownership, workshop/bootstrap exactness, and retail config/persistence shape.

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

1. The browser/Awesomium surface is still compatibility-grade, not retail-complete. `web_showBrowser`, `web_changeHash`, `web_browserActive`, and `web_stopRefresh` mostly toggle local state or early-out on missing providers, while the real retail host owns `WebCore`, `WebSession`, `WebView`, listeners, JS method tables, and event publication.
2. The async Steam callback system is still missing as a first-class client owner. The repo now reconstructs several callback *targets*, but it does not yet reconstruct the callback bundle registration/lifetime itself.
3. `CL_InitDownloads` still follows the classic pak-comparison path only. Retail Quake Live extends that owner with workshop item requirement handling and a companion completion helper inside `CL_Frame`.
4. Config/bootstrap persistence still follows Quake III-oriented filenames and write paths in `common.c` rather than the retail `qzconfig.cfg` / `repconfig.cfg` / `writeClientConfig` shape recovered in rounds `108` and `109`.
5. Client verification is still spread across multiple targeted suites. Unlike the renderer and module layers, there is not yet one dedicated client parity gate plus tracked runtime evidence artifact.

## Refreshed `client` Parity Estimate

- Previous implicit client-host estimate from the recent source-reconstruction passes: **92%**
- Refreshed strict `client` estimate after this audit: **90%**

This is a confidence correction, not a runtime regression.

Rationale:

1. The retained Quake III-era client runtime inside `cl_main.c`, `cl_parse.c`, `cl_keys.c`, `cl_ui.c`, `cl_cgame.c`, `snd_dma.c`, `snd_mem.c`, and `snd_mix.c` is now in strong shape. That keeps the client well above the broad launcher/platform baseline described in top-level audits.
2. The still-missing retail browser runtime is too large to ignore in a strict client estimate. Retail owns `WebCore`, `WebSession`, `WebView`, `QLJSHandler`, `QLResourceInterceptor`, `SteamDataSource`, and a large event-publication surface. Current source reconstructs only command/cvar/resource-cache compatibility around that runtime.
3. Async Steam callback registration, workshop bootstrap exactness, and retail config/bootstrap persistence remain materially open, and they all belong to the client/host layer rather than to renderer-only or module-only closure work.

Confidence: medium.

## Subsystem Assessment

### Classic client runtime

Assessment: high parity

- Strongest current lanes:
  - key and character routing
  - resend/connect/disconnect/demo/frame ownership
  - packet/snapshot/gamestate parsing
  - server-browser state and ping/status helpers
- Main residual issue in this lane:
  - retail Quake Live-only workshop/bootstrap extensions layered onto those owners are not fully reconstructed yet

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

Assessment: medium parity

- Strongest current lanes:
  - overlay command wrappers
  - lobby cvars and social wrapper calls
  - rich-presence setters
  - UGC operator commands and direct SteamUGC wrappers
- Main remaining loss:
  - no reconstructed callback bundle/lifetime, no client-side callback pump, and no strict workshop bootstrap integration into the join/download path

### Browser/Awesomium launcher host

Assessment: low-medium parity

- Strongest current lanes:
  - `web.pak` mount/read path
  - mapped `fs_webpath` / screenshot fallback
  - URI-resource cache bridge
- Main remaining loss:
  - no actual retail browser runtime, no JS bridge, no `EnginePublish`, no `SteamDataSource`, no live `WebView` event loop

### Config/bootstrap persistence

Assessment: medium-low parity

- Strongest current lanes:
  - retained ownership is now bounded from the corpus
  - credential migration/storage paths are explicit in source
- Main remaining loss:
  - strict retail filenames, config replication flow, and `writeClientConfig` ownership are still missing

## Open Gap Register

## CL-G01 - Retail browser/Awesomium runtime is still missing

**Type:** Behavioral + launcher/runtime ownership  
**Priority:** P0  
**Retail evidence anchors:** `docs/launcher_awesomium_audit.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_09.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_10.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_54.md`, `src/code/client/cl_cgame.c`, `src/code/client/cl_webpak.c`, `src/code/client/cl_steam_resources.c`  
**Status:** Open

### Gap

Retail Quake Live owns a full embedded browser runtime. The current tree reconstructs command, cvar, and resource-cache compatibility around that runtime, but not the runtime itself.

Observed retail facts:

1. `QLWebHost_OpenURL` initializes `Awesomium::WebCore`, creates a `WebSession` rooted at `fs_homepath`, registers `web.pak`, `SteamDataSource`, and `QLResourceInterceptor`, then creates a `WebView`.
2. Retail installs `QLJSHandler` plus dialog/view/load listeners, caches the window object, and publishes browser events through `window.EnginePublish`.
3. Retail `SteamDataSource` owns avatar/image request handling and callback-driven response completion.

Observed current-source facts:

1. `cl_webpak.c` restores `web.pak` mounting and the mapped filesystem fallback, but it does not own a `WebCore`, `WebSession`, or `WebView`.
2. `cl_cgame.c` keeps `web_*` commands alive, but the command bodies mostly toggle local overlay state, clear URI cache state, or early-out when the overlay provider is unavailable.
3. No committed writable source currently implements `QLJSHandler`, `QLWebView_PublishEvent`, `SteamDataSource`, or the retail listener bundle described in the audit note.

### Closure target

1. Reconstruct a retail-compatible browser host lifetime behind `QL_BUILD_ONLINE_SERVICES`, including session/view ownership and shutdown.
2. Restore the JS bridge and event publication surface expected by the launcher/menu flow.
3. Reconstruct the live `SteamDataSource` and the retained `QLResourceInterceptor` behavior as runtime owners, not only as file/cache helpers.

## CL-G02 - Async Steam callback registration and client callback pumping are incomplete

**Type:** Behavioral + async platform lifecycle  
**Priority:** P0  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_01.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_70.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_71.md`, `docs/reverse-engineering/quakelive_steam_parity_plan.md`, `src/common/platform/platform_steamworks.c`, `src/code/client/cl_main.c`, `src/code/client/ql_auth.c`  
**Status:** Open

### Gap

The repo now has several callback *payload handlers*, but it still lacks the retail callback bundle ownership and the normal client-side callback pump.

Observed retail facts:

1. `SteamCallbacks_Init` registers client callbacks for rich-presence join requests, user stats, persona changes, P2P session requests, game-server-change requests, friend rich-presence updates, and UGC query completion.
2. `SteamLobbyCallbacks_Init` registers lobby created/enter/chat/update/game-created/kicked/join-requested callbacks.
3. `SteamMicroCallbacks_Init` registers the microtransaction authorization callback.
4. The parity plan explicitly calls out `SteamAPI_RunCallbacks` in the main frame loop as a missing host responsibility.

Observed current-source facts:

1. `cl_main.c` reconstructs `CL_Steam_OnRichPresenceJoinRequested` and `CL_Steam_OnGameServerChangeRequested`, but there is no reconstructed callback bundle that registers those handlers with Steamworks.
2. `platform_steamworks.c` exposes `QL_Steamworks_RunCallbacks`, but the current source only uses it in `ql_auth.c` during ticket request/validation flows.
3. No current client frame owner (`CL_Frame` or `Com_Frame`) pumps client-side Steam callbacks each frame.
4. No writable source currently owns the callback registration classes or the retail lobby/microtransaction/event publication layer.

### Closure target

1. Reconstruct the client callback bundles and their lifetime/registration order.
2. Pump `QL_Steamworks_RunCallbacks()` from the correct client-frame owner instead of only from auth helpers.
3. Route persona, lobby, UGC, friend-presence, and microtransaction callbacks into explicit client/browser event owners.

## CL-G03 - Workshop download/bootstrap exactness is still incomplete

**Type:** Behavioral + join/download path  
**Priority:** P1  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_68.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_105.md`, `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`, `src/common/platform/platform_steamworks.c`  
**Status:** Open

### Gap

The repo has reconstructed manual SteamUGC command and wrapper surfaces, but the client join/bootstrap path still does not match the retail workshop-aware download flow.

Observed retail facts:

1. Retail `CL_InitDownloads` extends the classic pak-compare owner with workshop item requirement handling before falling back to `CL_DownloadsComplete`.
2. Retail `CL_Frame` calls an adjacent workshop/download completion helper before the resend path.
3. The native UI import slab exposes workshop download-progress retrieval through the retained item-download-info slot.

Observed current-source facts:

1. `CL_InitDownloads` in `cl_main.c` is still the classic `FS_ComparePaks` path; it does not parse or stage server-required workshop items.
2. `cl_downloadItem`, `cl_downloadCount`, and `cl_downloadSize` cvars exist, but the join/download path does not currently drive a workshop-specific owner around them.
3. `cl_ui.c` exposes the workshop download-info import, but it falls back to legacy byte counters whenever Steam item info is unavailable.
4. Manual operator commands and platform UGC wrappers exist, so the missing work is the client bootstrap integration, not the raw SteamUGC slot discovery.

### Closure target

1. Reconstruct the workshop requirement parser and bootstrap state in `CL_InitDownloads`.
2. Restore the adjacent completion helper inside the client frame path.
3. Make the UI-facing workshop progress path reflect the retained retail item/download state rather than a legacy byte-count fallback.

## CL-G04 - Config/bootstrap persistence still diverges from retail Quake Live

**Type:** Behavioral + bootstrap/config persistence  
**Priority:** P1  
**Retail evidence anchors:** `docs/reverse-engineering/quakelive_steam_mapping_round_56.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_108.md`, `docs/reverse-engineering/quakelive_steam_mapping_round_109.md`, `src/code/qcommon/common.c`, `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`  
**Status:** Open

### Gap

Retail Quake Live’s config/bootstrap and credential-persistence shape is still not reproduced exactly in the current tree.

Observed retail facts:

1. The recovered common/config owners write and bootstrap `qzconfig.cfg` and `repconfig.cfg`, not the Quake III `q3config.cfg` path.
2. A Quake Live-only `writeClientConfig` helper is visible in the retail host notes but is still unnamed/unreconstructed in writable source.
3. Retail `CLUI_GetCDKey` / `CLUI_SetCDKey` keep the legacy placeholder-style CD-key surface even though the host still validates legacy 16-byte values.

Observed current-source facts:

1. `common.c` still executes and writes `q3config.cfg`.
2. There is no `writeClientConfig` command or owner in current writable source.
3. `Com_WriteCDKey`, `Com_ReadCDKey`, `CL_CDKeyValidate`, and the UI helper surface now support richer credential parsing, migration, and token storage that do not match the stricter retail placeholder/file semantics.

### Closure target

1. Reconcile `Com_Init`, `Com_WriteConfiguration`, and the explicit write-config helpers with the retail `qzconfig.cfg` / `repconfig.cfg` bootstrap and persistence shape.
2. Recover or intentionally bound the `writeClientConfig` owner instead of leaving it as a retail-only note.
3. Decide whether the richer credential-storage path remains an intentional divergence or whether a stricter retail-compatibility lane is required for the client/UI host surface.

## CL-G05 - The client verification surface is still fragmented and lacks a dedicated parity gate

**Type:** Verification + runtime evidence  
**Priority:** P2  
**Retail evidence anchors:** current client-adjacent tests under `tests/`, `docs/windows-native-pipeline.md`, `docs/launcher_awesomium_audit.md`  
**Status:** Open

### Gap

The current repo has useful client-adjacent coverage, but it does not yet have one dedicated machine-readable client parity gate or a tracked runtime-evidence artifact for the client host itself.

Observed facts:

1. This audit validated the current source through `113` targeted passes across platform services, the Steamworks harness, renderer memory-image/export tail checks, and UI menu/runtime contract assertions.
2. The renderer and retail-module layers already have dedicated parity-gate tests plus tracked artifact outputs under `artifacts/renderer_validation/` and `artifacts/module_validation/`.
3. The client host currently has no equivalent single gate or client-runtime evidence bundle proving browser/bootstrap/social/download behavior as one audited tranche.

### Closure target

1. Add a dedicated client parity gate that records the current gap register (`CL-G01`..`CL-G05`) into one tracked artifact.
2. Add a focused runtime probe and evidence bundle for client-host behaviors that static tests cannot close cleanly.
3. Keep that gate distinct from renderer-only and module-only validation so future client-host regressions stay visible.

## Closure Plan (Executable Tranches)

## CL-P1 - Retail config/bootstrap persistence closure

Covers: `CL-G04`  
Goal: align the client/common config bootstrap and persistence shape with the recovered retail Quake Live owners before larger browser/callback work builds on the wrong startup contract.

Deliverables:

1. Reconcile `Com_Init` and `Com_WriteConfiguration` with the retail `qzconfig.cfg` / `repconfig.cfg` load-write sequence.
2. Recover or intentionally document the `writeClientConfig` owner and command surface.
3. Make the client/UI credential persistence contract explicitly retail-compatible or explicitly documented as a deliberate divergence.

Exit criteria:

- The client no longer boots and flushes config through the old Quake III-only filename path when strict retail parity is claimed.
- The remaining credential-storage behavior is either retail-matched or crisply documented as intentional compatibility policy.

Projected parity uplift: **90% -> 92%**

## CL-P2 - Steam callback-bundle and frame-pump reconstruction

Covers: `CL-G02`  
Goal: move Steam client behavior from manually callable wrappers to the retained async callback lifecycle that retail actually used.

Deliverables:

1. Reconstruct client, lobby, and microtransaction callback registration/lifetime owners.
2. Pump `QL_Steamworks_RunCallbacks()` from the correct client frame owner.
3. Route rich-presence, persona, lobby, UGC, and microtransaction callback payloads into explicit client/browser event owners.

Exit criteria:

- Client-side Steam callbacks are no longer limited to auth-time calls and direct helper invocation.
- The client frame owns the expected async callback pump and callback objects.

Projected parity uplift: **92% -> 94%**

## CL-P3 - Workshop-aware join/download exactness

Covers: `CL-G03`  
Goal: finish the workshop-aware join/bootstrap path so client download state and UI-facing progress match the retained retail flow.

Deliverables:

1. Restore workshop requirement parsing in `CL_InitDownloads`.
2. Reconstruct the adjacent completion helper called from `CL_Frame`.
3. Tighten the native UI workshop progress surface so it reflects the retained client download state exactly.

Exit criteria:

- Joining a workshop-backed server no longer falls back to the classic pak-only logic.
- The UI workshop progress slot is fed by reconstructed client/workshop state rather than generic legacy counters.

Projected parity uplift: **94% -> 95%**

## CL-P4 - Browser-host core reconstruction behind policy gates

Covers: `CL-G01`  
Goal: restore the missing launcher/browser runtime ownership without violating the repo’s default-disabled online-services policy.

Deliverables:

1. A reviewable browser-host core behind `QL_BUILD_ONLINE_SERVICES`, including session/view lifetime and deterministic shutdown.
2. Reconstructed ownership for `web_showBrowser`, `web_changeHash`, `web_hideBrowser`, `web_showError`, `web_clearCache`, `web_reload`, and `web_stopRefresh` beyond state-only stubs.
3. Explicit separation between live-host behavior and build-disabled/offline fallbacks.

Exit criteria:

- The client owns a real browser runtime contract instead of only fallback state toggles and URI cache helpers.
- Browser commands can drive a retained session/view lifetime when the feature is enabled.

Projected parity uplift: **95% -> 97%**

## CL-P5 - JS bridge, data-source, and event-publication closure

Covers: the remaining hard-runtime portion of `CL-G01` plus the browser-facing side effects of `CL-G02`  
Goal: restore the browser-facing data and event contract that retail JS expected from the native host.

Deliverables:

1. Reconstruct `SteamDataSource` request handling and the resource-interceptor/event-publication seam.
2. Reconstruct the `qz_instance`/JS-method binding surface and the outbound `EnginePublish` event path needed by lobby/store/social/menu flows.
3. Revisit the current compatibility `+voice` / browser / advert fallbacks once the real host event path exists.

Exit criteria:

- Avatar/resource requests, browser events, and JS/native method calls are no longer simulated only through cvars and compatibility menus.
- The browser-facing social/lobby/store/event contract is explicit in source.

Projected parity uplift: **97% -> 99%**

## CL-P6 - Dedicated client parity gate and runtime evidence

Covers: `CL-G05` and any residual proof debt from `CL-P1`..`CL-P5`  
Goal: make the client audit enforceable and regression-resistant.

Deliverables:

1. A dedicated client parity gate test and machine-readable artifact.
2. A focused client runtime probe plus tracked evidence bundle.
3. Updated top-level audit/summary wiring so client parity state is visible alongside module and renderer parity.

Exit criteria:

- The client host has a single machine-readable parity artifact instead of only scattered targeted tests.
- Runtime-only client behaviors are backed by tracked evidence, not just prose notes.

Projected parity uplift: **99% -> 100%**

## Recommended Execution Order

1. Start with `CL-P1`. The current config/bootstrap contract is still source-biased, and the later browser/callback/runtime work should not build on the wrong startup/persistence story.
2. Move to `CL-P2` next. Async Steam callback ownership is the highest-value missing non-browser runtime seam and unlocks several later client behaviors.
3. Follow with `CL-P3`. Once callback lifetime is explicit, the workshop-aware join/download path becomes a tractable bounded tranche instead of a scattered symptom.
4. Then take `CL-P4` and `CL-P5` together in that order: browser-host core first, JS/data/event surface second.
5. Finish with `CL-P6` once the major runtime gaps are genuinely closed.

## Bottom Line

The strict client story is better than the top-level “native launcher/platform host is low parity” headline implies, because the classic client runtime, sound core, native module bridge, and several Steam/social wrapper seams are now materially reconstructed in writable source.

But the client is not near strict retail completion yet. The missing browser runtime, missing async callback bundle, incomplete workshop bootstrap path, and still-source-biased config/persistence surface are all real parity gaps that belong to the client host itself.

So the current strict `client` estimate is best recorded as **90%**, with the remaining closure path grouped into six concrete phases (`CL-P1`..`CL-P6`) centered on retail bootstrap/config persistence, Steam callback lifetime, workshop-aware join/download handling, browser runtime ownership, JS/data/event publication, and final parity gating.
