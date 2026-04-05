# Quake Live Parity Audit

Last updated: 2026-04-05

This audit reflects the current repository state against the retail Quake Live HLIL references and a fresh Windows `Debug|x86` build/runtime pass. The goal is not to score every file equally; it is to rank the gaps that still materially separate the repo from retail behavior.

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
