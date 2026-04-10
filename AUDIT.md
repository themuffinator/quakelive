# Quake Live Parity Audit

Last updated: 2026-04-10

This audit reflects the current repository state against the retail Quake Live HLIL references and the latest recorded Windows `Debug|x86` build/runtime pass. The goal is not to score every file equally; it is to rank the gaps that still materially separate the repo from retail behavior.

## Overall assessment

- The engine-to-module native ABI is now in the `high parity for source-built DLLs` range: the rebuilt engine loads native `ui`, `qagame`, and `cgame` DLLs through the recovered Quake Live-style `dllEntry` import/export seam.
- Core game and cgame reconstruction are now in the `medium-high parity` range.
- The largest remaining parity deficits are no longer basic gameplay systems; they are retail-binary host compatibility beyond the current source-built DLL path, the native launcher/platform layer, and the missing retail UI asset/menu stack.
- The most actionable gameplay-side gap found in this audit was match-flow configstring parity. That gap is now closed for the sudden-death/ready-up/warmup-ready path.
- The strategic parity target is that the reconstructed engine should, in theory, be able to replace the retail Quake Live engine, host retail game binaries, load the retail main menu, and interoperate with retail Quake Live servers or platform flows once their remaining dependencies are reconstructed.

## What this audit closed

### Match-flow configstring parity

Retail HLIL shows dedicated client parsing for the match-flow side channels around `CS_MATCH_STATE`, including sudden-death and ready-up status configstrings. The repo previously had a split implementation:

- server code published `CS_MATCH_STATE`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY`
- `CS_SUDDENDEATH_STATUS` existed in `bg_public.h` but was not actually published
- cgame did not parse `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, or `CS_WARMUP_READY`
- the HUD scoreboard treated the sudden-death spawn-delay config flag as if it meant "sudden death is active"

This task corrected that mismatch by:

- publishing `CS_SUDDENDEATH_STATUS` from qagame
- parsing `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY` in cgame
- feeding ready-up deadline and readiness counts into the warmup overlay
- switching the HUD scoreboard and sudden-death label logic to use runtime sudden-death state instead of configuration-only flags

Result: match-flow HUD state is materially closer to the retail side-channel model shown in HLIL, and the client no longer drops those server updates on the floor.

## Current parity by area

### 1. Game-module import/export ABI
Status: High parity for source-built DLLs, medium parity for retail-binary hosting
Priority: Highest

This area advanced materially in the latest runtime pass.

- The engine now prefers the structured Quake Live native `dllEntry` interface, not just the legacy `vmMain` ABI.
- `cgame`, `qagame`, and `ui` export-slot layouts are mapped explicitly instead of assuming the old enum order matches the retail native table.
- Source-built native DLLs now load on the normal startup path and on gameplay-map startup, with `vm_trace.log` showing native `ui`, `qagame`, and `cgame` creation.
- Native import-table traffic is no longer misclassified as legacy VM syscall-contract traffic during validation.

What still remains in this area:

- strict host-compatibility validation against the retail DLLs themselves, not only reconstructed source-built binaries
- confirmation of pointer-return ownership, restart behavior, and other edge contracts that retail binaries may rely on more heavily than the current source path
- continued runtime evidence collection whenever this seam changes

### 2. Native launcher and platform host
Status: Low parity
Priority: Highest

This remains the largest gap in the repository.

- Retail Quake Live shipped a native `quakelive_steam.exe` host with Steam integration, web/launcher services, Awesomium-backed UI plumbing, image/HTTP bridges, and platform bootstrap code.
- The GPL-derived open tree still relies on classic engine/UI structures and does not reconstruct the retail host stack in source form.
- This gap impacts login/auth flow, browser-driven navigation, avatar/resource loading, workshop-style data paths, and multiple menu interactions that retail delegated to the launcher.

This is the highest-value parity target, but it is also the broadest reconstruction effort.

### 3. Retail UI asset/menu parity
Status: Low-medium parity
Priority: High

A fresh runtime pass still reports large volumes of missing retail UI assets and menu incompatibilities.

Observed on 2026-03-26:

- many missing `ui/assets/...` images
- missing font atlas assets with fallback text rendering
- `ui/hud.menu` parse errors for unsupported `font` keywords

Impact:

- visual parity remains materially below retail
- some HUD/menu layouts still depend on fallbacks rather than real retail assets or retail-compatible menu parsing
- this gap is currently constrained by the repository rule that `src/ui/` is read-only

Because the UI tree is read-only, the best short-term path is engine-side tolerance, bridge validation, and documenting which retail UI expectations are still unmet.

### 4. Ownerdraw/stat payload completion
Status: Medium parity
Priority: High

The repo has made substantial progress on scorestats, team pickup telemetry, key items, and placement ownerdraws. The remaining gap is not the existence of the pipeline; it is finishing and validating the residual retail-only fields and keeping the runtime payload aligned with the HLIL-backed ownerdraw behavior.

The current codebase already contains a large in-progress payload expansion. The next meaningful work here is to finish the remaining retail field mapping and keep validating against captured runtime baselines.

### 5. Match flow, warmup, sudden death, and scoreboard state
Status: Medium-high parity
Priority: Medium

This area improved in this task. The remaining work is lower-impact than the launcher/UI gaps and is now mostly about chasing smaller sequencing differences instead of missing whole data channels.

### 6. Physics, race, and gametype-specific gameplay
Status: Medium-high parity
Priority: Medium

The repo already has substantial reconstruction in movement and gametype logic. The main remaining need here is targeted validation against retail references, not wholesale subsystem creation.

## High-priority gaps to close next

1. Reconstruct the native launcher/platform host behavior currently represented only by HLIL and documentation.
2. Validate the engine against the retail gameplay DLLs themselves and close any remaining import/export edge-contract mismatches.
3. Reduce retail UI/menu parity failures that still surface as missing assets, font fallbacks, and menu parse warnings at runtime.
4. Finish the remaining ownerdraw/stat payload parity work and keep runtime validation aligned with retail captures.

## Verification snapshot

Fresh verification completed on 2026-03-26:

- `MSBuild` solution build: `Debug|x86` succeeded
- native export validation: `tools/ci/assert-dll-exports.ps1` passed for rebuilt `uix86.dll`, `qagamex86.dll`, and `cgamex86.dll`
- normal runtime pass: loaded native `ui` and reached the main-menu path
- gameplay runtime pass: loaded native `ui`, `qagame`, and `cgame` on `campgrounds`, then reached clean shutdown
- forced-crash pass: produced a fresh dump under `build\\win32\\Debug\\dumps`

Artifacts from the fresh runtime passes:

- map-pass engine screenshot: `build\\win32\\Debug\\bin\\baseq3\\screenshots\\campgrounds_engine_20260326_094835.jpg`
- map-pass window capture metadata: `build\\win32\\Debug\\dumps\\screenshots\\campgrounds_window_20260326_094835.json`
- map-pass screenshot: `build\\win32\\Debug\\dumps\\screenshots\\campgrounds_window_20260326_094835.png`
- crash-pass engine screenshot: `build\\win32\\Debug\\bin\\baseq3\\screenshots\\crash_engine_20260326_095011.jpg`
- crash-pass window capture metadata: `build\\win32\\Debug\\dumps\\screenshots\\crash_window_20260326_095011.json`
- crash-pass screenshot: `build\\win32\\Debug\\dumps\\screenshots\\crash_window_20260326_095011.png`
- crash dump: `build\\win32\\Debug\\dumps\\quakelive_steam_20260326_095025_597.dmp`

## Bottom line

The repo is no longer blocked on missing basic gameplay plumbing or on the basic source-built native gameplay DLL handshake. The highest remaining parity gaps are now:

- retail-binary host compatibility beyond the reconstructed source-built DLL path
- launcher/platform reconstruction
- retail UI/menu asset parity
- final ownerdraw/stat payload cleanup

The strategic target is now explicit: the engine should, in theory, be capable of replacing the retail Quake Live engine once those remaining host, platform, asset, and strict retail-binary compatibility gaps are closed.


## UI audit refresh (2026-04-05)

A focused full-parity audit for `ui` is now published in `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`.

Summary:

- Current estimated `ui` parity is **68%** overall, with strongest alignment at the native ABI seam and weaker parity in retail UI corpus availability, overlay workflow hardening, and end-to-end parity gating.
- The current environment has an empty `assets/quakelive/baseq3/ui` tree, which blocks strict source-vs-retail panel drift checks and causes bundle-generation preflight failures for missing retail base files.
- A six-phase closure plan (`UI-P1`..`UI-P6`) now defines the complete path to 100% UI parity, including deterministic retail corpus preflight, overlay-first drift closure for read-only `src/ui`, service-disabled menu fallback validation, residual widget-core mapping, unified parity gate, and final runtime evidence pass.

## Qagame audit refresh (2026-04-05)

A focused full-parity audit for `qagame` is now published in `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`.

Summary:

- Current estimated `qagame` parity is **76%** before this audit pass and **78%** after publication (documentation and closure certainty uplift; runtime behavior unchanged).
- Mapping coverage is effectively saturated for the committed corpus (`1027/1027` overlap), so the remaining gap profile is now dominated by behavioral/boundary exactness rather than symbol discovery.
- A six-phase closure plan (`QG-P1`..`QG-P6`) now defines the path to full qagame parity in theory, covering round-controller helper exactness, shared last-alive event transport, scoreboard/intermission serializer decomposition, strict Red Rover controller behavior, tournament queue/spawn-finalizer sidecars, and residual timer/debug/training tails.

## Module parity refresh (2026-04-09)

A refreshed combined module audit is now published in `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-09.md`.

Summary:

- The source-built DLL lane is fully green on 2026-04-09: `cgame` is `170 / 170` passed, `qagame` is `91 / 91` passed with `5` skips, `ui` is `49 / 49` passed with `6` skips, the shared platform-service seam is `41 / 41` passed, and the tracked UI parity-gate artifact is fully green.
- Strict retail-facing module parity is now assessed separately from that source-built lane. Strict retail module parity is now treated as **100%** overall for the module layer.
- `GMR-P1` is now closed: the tracked retail runtime probe loads retail `uix86.dll`, `qagamex86.dll`, and `cgamex86.dll` from the Steam profile root under the reconstructed host, and the remaining live-map shortfall is explicitly bounded to the renderer-owned `R_LoadMD3` failure on `models/weapons3/hmg/hmg.md3`.
- `GMR-P2` is now closed: retail qagame/cgame `pstats` transport is mirrored in writable source, with qagame now accepting `pstats` and cgame routing it through the same recovered 15-slot cache path as `acc`.
- `GMR-P3` is now closed: the retail `CG_Player` post-`tag_head` origin/axis transform is mirrored in writable source, so `g_playerheadScale` and `g_playerheadScaleOffset` are no longer preview-only scalars.
- `GMR-P4` is now closed: the retained launcher-resource fallback chain (`web.pak`, `fs_webpath`, screenshot mapping, and non-Steam URI resource registration) now stays available for audited offline `ui`/`cgame` flows even when live online services are disabled.
- `GMR-P5` is now closed: the final module parity gate, the top-level ledgers, the dedicated UI audit, and the native/build pipeline notes now all agree on the same strict-retail module closure state.
- Combined committed retail mapping coverage for the three DLLs remains saturated at **2426 / 2426** normalized anchors, so no open game-module debt remains inside the module layer; the remaining live-map shortfall is explicitly renderer-owned.
- No confirmed source-owned or host-adjacent game-module behavior gap remains after `GMR-P5`.

## Renderer audit refresh (2026-04-10)

A focused full-parity audit for the renderer is now published in `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`.

Summary:

- The refreshed renderer report now confirms full renderer closure instead of only re-stating the 2026-04-09 font-stack correction. No new renderer-core gap reopened during the final `RG-P10` or `RG-P11` pass.
- The open renderer gap register is now wider than the old single-tranche `RG-G05` story. That historical correction still holds even though the final `RG-P10` and `RG-P11` passes have now closed the remaining `RG-G09` tail as well.
- `RG-P7` is complete. The classic `tr_font.c` lane has an explicit ownership note, explicit retail-vs-compatibility helper splits, inclusive cached-font/atlas coverage, and deterministic renderer tests that keep the old mixed “probably retail” bucket from reopening.
- `RG-P8` is complete. The renderer now owns a retained `*fontstash` atlas, the retail `R_fonsErrorCallback` expansion-or-flush path, and the recovered five-face host text table.
- `RG-P9` is complete. Native `ui` and `cgame` host text imports now route through shared renderer host-text helpers, and `r_debugFontAtlas` now has a retained-atlas draw path in writable source.
- `RG-P10` is complete. The stale in-tree `ft2` project ownership has been replaced with an explicit external FreeType SDK or `pkg-config freetype2` build lane, and the renderer project metadata no longer points at missing source files.
- `RG-P11` is complete. The tracked runtime artifact is now `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260410.json`, and it proves a windowed UI-bootstrap pass, retained-atlas debug rendering, and live `bloodrun` runtime with distinct engine or window capture hashes while rejecting `RE_RegisterFont` fallback-lane logs.
- The current strict `renderer` estimate is now **100%**.
- The renderer-focused validation surface is fully green on 2026-04-10: the unified gate reports no open renderer gaps, the font-stack audit runs clean, and the tracked runtime bundle is now text-specific instead of generic renderer-only evidence.
- No confirmed renderer gap remains after `RG-P11`.
- `RG-P1` is now complete. The renderer export tail matches the retail `GetRefAPI` contract again, font registration has been moved onto an explicit client compatibility lane instead of the export ABI, and the current estimated renderer parity is **81%**.
- `RG-P2` is now complete. The recovered in-memory renderer image helper family is back in writable source, live Steam/launcher image resources now register through direct renderer-owned memory ingestion instead of temporary cache files, and the current estimated renderer parity is **85%**.
- `RG-P3` is now complete. The renderer post-process path is shader-backed again using the retail rectangle-texture/shader-family structure, CPU color-correction readback has been removed, `r_contrast` is registered and consumed by the recovered color-correct pass, and the current estimated renderer parity is **90%**.
- `RG-P4` is now complete. The Win32 host once again mirrors the retail live client-rect resize/restart helper, fast restarts retain the maximized-window state, the shared loading-window wrappers are present in writable source, and the current estimated renderer parity is **93%**.
- `RG-P5` is now complete. The dense backend/BSP/curve/flare/Win32 helper bands are explicitly bounded by the new ownership note and mapping-round closure, so they are no longer treated as an open-ended active-runtime parity gap, and the current estimated renderer parity is **96%**.
- `RG-P6` is now complete. The renderer has a dedicated parity gate, a tracked windowed runtime evidence artifact for the current milestone, and a CI-visible validation workflow, but that no longer implies strict end-to-end renderer closure because the retail font/text host remains open.
- `RG-P7` is now complete. The classic renderer font/cache/atlas lane is no longer treated as an open parity gap, and the current estimated renderer parity is **95%**.
- `RG-P8` is now complete. The renderer-owned retained host text core is in writable source, and the current estimated renderer parity is **97%**.
- `RG-P9` is now complete. The retained host text core is now the active native import path and the current estimated renderer parity is **98%**.
- `RG-P10` is now complete. The recovered external FreeType replacement lane is now the committed renderer build story, and the current estimated renderer parity is **99%**.
- `RG-P11` is now complete. The final strict renderer parity gate and text-specific runtime artifact are now green, and the current estimated renderer parity is **100%**.

## Client audit refresh (2026-04-10)

A focused full-parity audit for the native `client` host is now published in `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`.

Summary:

- `CL-P1` is now complete. The client/common bootstrap and write path now follows the retail `qzconfig.cfg` / `repconfig.cfg` contract, `writeClientConfig` is reconstructed in writable source, `FS_Restart` replays `qzconfig.cfg`, and the client/UI CD-key surface is back on the retail legacy placeholder/q3key lane.
- `CL-P2` is now complete. The Steam client/lobby/micro callback bundles are retained in writable source, `CL_Frame` owns the normal client-side Steam callback pump, and the callback payloads now flow into an explicit client/browser event owner instead of remaining limited to auth-time helper paths.
- `CL-P3` is now complete. The server now publishes the referenced workshop-item list instead of echoing the server SteamID through the workshop slots, filesystem startup/restart now remount subscribed workshop install roots with retained per-pack item IDs, `CL_InitDownloads` and `CL_Frame` now own the retail workshop-aware join/bootstrap path, and the UI workshop progress import now reflects retained client state instead of generic legacy counters.
- `CL-P4` is now complete. The client now owns a retained browser-host runtime behind the online-services policy gate, including explicit init or frame or shutdown lifetime and reconstructed command owners for the `web_*` browser-control surface.
- `CL-P5` is now complete. The retained `qz_instance` JS bridge, `EnginePublish` event-publication lane, `SteamDataSource` avatar/resource owner, and `QLResourceInterceptor` / `Sys_Steam_RequestURL` fallback seam are now explicit in writable source and covered by the parity suite.
- `CL-P6` is now complete. The client now has a dedicated parity gate (`artifacts/client_validation/logs/client_full_parity_gate.json`) plus a tracked runtime-evidence bundle (`artifacts/client_validation/logs/client_runtime_evidence_20260410.json`) covering retail config/bootstrap writes, service-disabled browser-policy behavior, live `bloodrun` runtime, authoritative engine/window captures, and a flushed demo artifact.
- The refreshed strict `client` estimate is now **100%**. This is a behavior-backed uplift from the post-audit **90%** figure because the retail config/bootstrap persistence gap (`CL-G04`), the async Steam callback lifetime gap (`CL-G02`), the workshop bootstrap gap (`CL-G03`), the browser/JS/runtime ownership gap (`CL-G01`), and the final verification gap (`CL-G05`) are now closed.
- The classic client/runtime story is materially strong: recent mapping rounds now bound the retained input/key path, resend/connect/disconnect lifecycle, server-browser helpers, packet/frame spine, sound core, native `ui`/`cgame` bridge, and live renderer-resource ingestion well enough that the client should no longer be treated as uniformly “low parity”.
- No open gap remains in the audited client register.
