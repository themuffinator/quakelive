# Implementation Plan

Last updated: 2026-04-21

This file now tracks only active repo-level work. Detailed closure narratives
live in the dedicated subsystem audits under `docs/reverse-engineering/`.
Historical task headings that existing parity gates still check are preserved in
the appendix as compact archival anchors instead of repeated full narratives.

## Strategic goal

The long-term parity target remains the same: the reconstructed engine should,
in theory, be able to replace the retail Quake Live engine, load retail
`cgamex86.dll`, `qagamex86.dll`, and `uix86.dll`, present the retail main menu,
and interoperate with the retail Windows host/runtime contracts. Quake
Live-only online services remain behind `QL_BUILD_ONLINE_SERVICES`, default
disabled, until a documented open replacement path exists.

## Current planning baseline

- Treat `AUDIT.md` and
  `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md` as the
  current cross-subsystem truth.
- Treat the 2026-04-10 engine-wide **100%** report as the strict-retail
  Windows closure milestone, not as a whole-repo all-green claim.
- The strict-retail Windows replacement target remains **100%** on the current
  worktree, but the current repo-wide parity estimate is **96%** once the
  compatibility-only and packaging-dependent surfaces are counted.
- Top-level planning is reopened in this file because the 2026-04-21 repo-wide
  audit identified active gaps outside the strict-retail score.
- The older broad planning notes under `docs/parity-plan.md`,
  `docs/ui_deltas.md`, and `docs/ui_followup_issues.md` are historical
  snapshots, not current gap ledgers.

## Recent closure

### Task A2c: Refresh the repo-wide parity audit evidence on the current worktree [COMPLETED]
Priority: Medium
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Re-ran a broad current-worktree parity sweep across the top-level
   strict-retail gates, gameplay validation fixtures, portability suite, and
   staged runtime-audit lane, producing `60 passed, 7 skipped`.
2. Rebased the top-level ledgers on that sweep so the current repo-wide gap
   register is explicitly backed by one aggregated evidence pass instead of
   only by the individual runtime-probe refresh notes.
3. Clarified that the remaining repo-wide gap families still collapse to
   `RW-G01`, `RW-G02`, and `RW-G04`, with the staged retail-runtime DLL guard
   now treated as closed and the remaining `RW-G04` debt narrowed to fresh
   artifact regeneration/publication.
4. Cleaned up stale date language in the historical top-level audit anchors so
   the repo-wide ledgers no longer point readers at the older `2026-04-17`
   top-level state while describing the current 2026-04-21 worktree.

### Task A6f: Add a strict staged retail-runtime DLL audit for native Windows validation [COMPLETED]
Priority: Medium
Primary areas: `tools/ci/audit-retail-dependencies.ps1`,
`tools/ci/validate-windows-native.ps1`, Windows/toolchain docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Extended the retail dependency auditor so it can now audit either the local
   Steam install or an explicit runtime root, checking for missing expected
   retail DLLs, extra non-retail DLLs, and byte-hash mismatches instead of
   only diffing the Steam tree opportunistically.
2. Added a strict retail-runtime staging step to
   `tools/ci/validate-windows-native.ps1`: the retail validation lane now
   assembles `build\win32\<Config>\retail-runtime\` from the rebuilt host
   executables and gameplay/UI DLLs plus the exact retail launcher DLL payload
   from `assets\quakelive\`, then fails fast if the staged root contains extra
   DLLs or is missing any retail payload DLLs.
3. Rebased the Windows/toolchain documentation on that explicit staging
   boundary so the mixed developer build root `build\win32\<Config>\bin\` is
   no longer described as the strict retail payload surface.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer the
   previously documented local/runtime DLL-guard follow-up, and is instead
   concentrated in refreshed native build outputs plus the broader glibc and
   self-hosted publication follow-ups.

### Task A6e: Re-promote the retail module runtime alias through an explicit renderer-text bounded blocker [COMPLETED]
Priority: Medium
Primary areas: `tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Expanded the retail-module probe's bounded-owner classification so the
   current 2026-04-21 rerun can distinguish two renderer-owned live-map
   blocker shapes outside module scope: the older fatal `R_LoadMD3` drop path
   and the current `R_fonsErrorCallback` font-atlas saturation lane that keeps
   retail `uix86.dll`, `cgamex86.dll`, and `qagamex86.dll` loaded but prevents
   `CS_ACTIVE`.
2. Rebased the module runtime probe on the current map-launch contract again by
   threading the same `com_maxfps 30` / no-warmup assumptions used by the
   other runtime probes into the retail-module lane, while keeping the stable
   alias guarded so only sufficient reruns are promoted.
3. Reran `tools/modules/run_retail_module_runtime_probe.ps1` on 2026-04-21 and
   refreshed
   `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
   to the current bounded `20260421` bundle instead of leaving it pinned to
   the older `2026-04-09` artifact.
4. Narrowed `RW-G04` again: the remaining freshness debt is now no longer a
   non-promotable retail-module alias question, and is instead concentrated in
   fresh native build outputs plus the broader glibc/self-hosted publication
   follow-ups.

### Task A4g: Restore a bounded Unix profiling control path [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`src/code/unix/Makefile`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Replaced the empty Unix profiling hooks with a bounded `gprof`-compatible
   runtime path: `Sys_Init()` now pauses profiling early when `moncontrol` is
   available, `Sys_BeginProfiling()` re-enables it on first active play, and
   `Sys_Exit()` now flushes `_mcleanup()` through `Sys_EndProfiling()`.
2. Added an explicit Unix build toggle `QL_ENABLE_GPROF=1` so profiling is a
   reproducible opt-in lane rather than an undocumented linker accident. The
   Unix makefile now threads `-pg` through the relevant engine compile/link
   paths when that toggle is enabled.
3. Rebased the focused non-Windows portability checks and ledgers so they now
   record a bounded profiling lane instead of an empty Unix no-op while still
   keeping the broader Unix renderer/audio/input host gap open.
4. Narrowed `RW-G02` again: the remaining portability debt is now even more
   clearly in the modern Unix runtime boundary itself, not in stale host-side
   syscall placeholders.

### Task A6d: Refresh renderer runtime evidence and stabilize alias promotion for the renderer/module probes [COMPLETED]
Priority: Medium
Primary areas: `tools/renderer/run_renderer_runtime_probe.ps1`,
`tools/modules/run_retail_module_runtime_probe.ps1`,
`tests/test_renderer_full_parity_gate.py`,
`tests/test_renderer_text_runtime_validation_parity.py`,
`tests/test_game_module_retail_parity_gate.py`, runtime-evidence docs
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Repaired the renderer runtime probe contract so the current `map <name>
   ffa` path, quoted launch arguments, and normalized path handling work
   reliably again, then reran the probe on 2026-04-21 to refresh the clean
   dated bundle
   `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260421.json`.
2. Added guarded `*_latest.json` promotion to both the renderer and retail
   module probes so only sufficient reruns replace the stable tracked alias.
   The renderer alias now points at the clean 2026-04-21 bundle, and the
   retail-module lane gained the guarded promotion rules that later enabled
   `A6e` to refresh the stable alias to the current bounded `2026-04-21`
   module artifact instead of silently accepting degraded reruns.
3. Rebased the renderer/module parity gates, the font audit script, and the
   active runtime-evidence docs on those stable aliases plus the current
   `map <name> ffa` launch contract.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs and the broader glibc/self-hosted publication
   follow-ups.

### Task A4f: Classify the Linux glibc preset as server-only portability evidence [COMPLETED]
Priority: Medium
Primary areas: `docs/build/linux-glibc-32bit.md`,
`docs/platform/toolchain-matrix.md`,
`tests/test_non_windows_portability.py`, portability ledgers
Parity estimate: **before 96% -> after 96%**

Completed work:

1. Updated `docs/build/linux-glibc-32bit.md` so the helper is explicitly
   framed as a `qagamei386.so` server-module reconstruction preset rather than
   as evidence of a retail-equivalent Linux client/runtime.
2. Mirrored that portability boundary in the native toolchain matrix so the
   top-level Linux lane description now points contributors at the correct
   server-only interpretation immediately.
3. Expanded the focused non-Windows portability regression coverage so the
   server-module-only classification and the still-open Unix profiling or
   renderer/audio/input host gaps are pinned in the docs.
4. Narrowed `RW-G02` procedurally: the remaining work is now more cleanly
   about whether to modernise the real Unix host boundary, not about what the
   existing Linux build helper is supposed to prove.

### Task A4e: Modernise the null input compatibility contract [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_input.c`,
`tests/test_non_windows_portability.py`,
`tests/test_engine_host_support_full_parity_gate.py`, portability ledgers
Parity estimate: **before 95% -> after 96%**

Completed work:

1. Modernised `src/code/null/null_input.c` so the dedicated/null host now
   carries the current input bootstrap cvars (`in_mouse`, `in_nograb`,
   `in_joystick`, `in_debugjoystick`, and `joy_threshold`) plus an explicit
   compatibility-state refresh that keeps `ui_joyavail` pinned to `0`
   instead of leaving the file as a bare inert no-op.
2. Reconstructed the null input frame pump as an explicit no-device contract:
   `IN_Frame()` now maintains the compatibility cvar surface and consumes
   joystick modification latches, while `Sys_SendKeyEvents()` remains the
   documented null-host no-op event source rather than an unstructured empty
   placeholder.
3. Expanded both the focused non-Windows portability suite and the
   engine-host/support compatibility gate so the current null input lane is
   pinned alongside the earlier null host/client/audio modernization work.
4. Narrowed `RW-G02` again: the remaining portability debt is now
   concentrated even more tightly in the Unix profiling placeholders and the
   absence of a real modern Unix client/renderer/audio/input host, rather
   than in stale null input bootstrap/event-pump seams.

### Task A4d: Modernise the null client/audio compatibility contracts [COMPLETED]
Priority: Medium
Primary areas: `src/code/null/null_client.c`,
`src/code/null/null_snddma.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 94% -> after 95%**

Completed work:

1. Modernised `src/code/null/null_client.c` so the null compatibility lane now
   exposes the current browser/advert/input-facing `client.h` contract instead
   of only the older partial web-host shim set: the null client now carries
   `CL_RefreshOnlineServicesBridgeState()`, the current browser cursor and app
   activation hooks, mouse/button/wheel webview input stubs, and the retained
   advertisement-bridge entry points while explicitly forcing the browser
   cvars back to the non-live state.
2. Promoted `src/code/null/null_snddma.c` from a narrow legacy dummy into an
   explicit current silent-audio compatibility seam by adding the current
   `SNDDMA_Activate()` and `S_AddVoiceSamples()` entry points alongside the
   existing null DMA and local-sound hooks.
3. Expanded the focused non-Windows portability regression coverage so it now
   asserts the current null client/audio contract surfaces directly instead of
   only pinning the older null host/network/glimp tranche.
4. Narrowed `RW-G02` again: the remaining non-Windows debt is now
   concentrated in the profiling hooks plus the absence of a real modern Unix
   client/renderer/audio/input host, rather than in stale or missing null
   browser/advert/audio contract entry points.

### Task A4c: Modernise the null host contracts and reconstruct the Unix monkey-marker hook [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `src/code/null/null_main.c`,
`src/code/null/null_net.c`, `src/code/null/mac_net.c`,
`src/code/null/null_glimp.c`, `tests/test_non_windows_portability.py`,
portability ledgers
Parity estimate: **before 93% -> after 94%**

Completed work:

1. Reconstructed the Unix `Sys_MonkeyShouldBeSpanked()` compatibility hook as
   a retained `q3monkeyid` release-marker probe rooted in the historical
   `Construct` script plus the committed retail string corpus, instead of
   leaving it as an unconditional placeholder.
2. Modernised the stale null host shims so they now match the current
   `qcommon` contracts: `null_main.c` now carries current command-line,
   executable-name, timer, path, and homepath scaffolding; `null_net.c` and
   `mac_net.c` now expose `Sys_StringToAdr()` plus the current loopback packet
   stub signatures; and `null_glimp.c` no longer carries the stale `int
   GLimp_Init()` signature.
3. Added focused non-Windows portability coverage for the new Unix marker
   probe and the null-host contract cleanup.
4. Narrowed `RW-G02` again: the remaining open portability debt is now
   concentrated in the profiling hooks plus the broader Unix/client/audio/input
   and still-stubbed null runtime surfaces, rather than in stale host-contract
   mismatches or the old `q3monkeyid` placeholder.

### Task A6c: Refresh the qcommon, server, and WOW64 evidence contracts on the current machine [COMPLETED]
Priority: Medium
Primary areas: `tools/qcommon/run_qcommon_runtime_probe.ps1`,
`tools/server/run_server_runtime_probe.ps1`,
`tools/ci/wow64-smoketest.ps1`,
their tracked artifacts, and repo-wide validation ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Repaired the stale qcommon and dedicated-server probe contracts so both
   runtime lanes now use the current `map <name> ffa` command shape, then
   re-ran them on 2026-04-21 to refresh
   `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
   and
   `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`.
2. Rebased the qcommon and server gate/documentation expectations on the
   current runtime markers, including the qcommon `game.error` plus native
   `stopRefresh` fallback evidence and the current dedicated `getstatus`
   server-type field spelling.
3. Updated the retained WOW64 smoke harness so it now prefers retail DLLs from
   `assets/quakelive/baseq3/` when present but falls back to the current
   Win32 build outputs under `build/win32/Debug/bin/baseq3/`, then captured a
   successful 32-bit PowerShell run at
   `artifacts/wow64-smoketest/wow64-smoketest.log`.
4. Narrowed `RW-G04` again: the remaining freshness debt is now concentrated
   in fresh native build outputs, the still-archived runtime bundles outside
   the refreshed client/qcommon/server lanes, and the broader glibc or
   self-hosted validation publication follow-ups.

### Task A4b: Restore bounded Unix function compare/checksum coverage on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`,
`tests/test_non_windows_portability.py`, `docs/platform/toolchain-matrix.md`,
top-level portability ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Restored Unix `Sys_FunctionCmp()` and `Sys_FunctionCheckSum()` with a
   Linux/glibc symbol-backed path that resolves function byte ranges through
   `dladdr1(..., RTLD_DL_SYMENT)` and hashes them with
   `Com_BlockChecksum()` when symbol sizes are available.
2. Added focused portability coverage that now checks the new source-side
   helper path directly instead of only tracking the old placeholder story in
   documentation.
3. Narrowed `RW-G02` again: the remaining open Unix helper debt is now
   concentrated in the historical profiling lane plus the broader
   non-Windows client/audio/input/toolchain boundary.

### Task A6b: Re-baseline the `src/ui` runtime-panel contract to the clean current state [COMPLETED]
Priority: Medium
Primary areas: `tests/test_ui_src_panel_parity.py`,
`tests/test_ui_full_parity_gate.py`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`, top-level ledgers
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the repo/UI parity gates so the current worktree now expects the
   `src/ui` runtime-panel compare to be clean (`65 / 65`, `0` content diffs)
   instead of tolerating the older historical non-zero drift contract.
2. Re-based the UI documentation and the repo-wide ledgers so they now
   distinguish clean checked-in runtime-panel parity from the separate
   bundle-staged retail art path.
3. Documented that explicit runtime-root refreshes always write the runtime
   package manifest, but only emit `pak_ui_src_retail_overlay.pk3` when
   `drift_files` is non-empty.

### Task A6a: Refresh the tracked client runtime evidence bundle after UI package-proof hardening [COMPLETED]
Priority: Medium
Primary areas: `tools/client/run_client_runtime_probe.ps1`,
`tests/test_client_full_parity_gate.py`,
`artifacts/client_validation/logs/client_runtime_evidence_20260410.json`,
client/runtime audit docs
Parity estimate: **before 93% -> after 93%**

Completed work:

1. Tightened the client parity gate so the tracked runtime bundle must now
   prove the emitted UI runtime-package manifest plus the refreshed main
   package hashes instead of relying only on the older screenshot/log bundle.
2. Rebased the main-menu offline-browser proof on the current retained runtime
   behavior, using the observed `game.error` publication and UI-side
   `stopRefresh` fallback markers instead of the older stale probe
   expectations.
3. Re-ran `tools/client/run_client_runtime_probe.ps1` on 2026-04-21 and
   refreshed `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   with fresh screenshots, logs, demo output, and UI package evidence.
4. Narrowed `RW-G04` by refreshing the client runtime bundle while leaving the
   remaining archived runtime/build artifacts as the still-open repo-wide
   freshness debt.

### Task A5: Harden the read-only `src/ui` parity path with runtime package proof [COMPLETED]
Priority: High
Primary areas: `tools/build_ui_bundle.py`, `tests/test_ui_src_panel_parity.py`,
`tools/client/run_client_runtime_probe.ps1`, `docs/quakelive_asset_audit.md`,
`docs/ui/hud-audit.md`, `docs/ui/scripting-guide.md`
Parity estimate: **before 92% -> after 93%**

Completed work:

1. Added an explicit runtime-package manifest to `tools/build_ui_bundle.py`
   for `--runtime-root` runs so emitted `pak_uiql.pk3` and
   `pak_ui_src_retail_overlay.pk3` outputs are now machine-described instead
   of assumed from console output alone.
2. Added focused UI bundle coverage that proves the explicit runtime-root path
   emits the expected PK3s, includes the required runtime entries and
   compatibility aliases, and keeps any emitted overlay package in lockstep
   with the source-vs-retail drift contract.
3. Tightened the client runtime probe so it now verifies the refreshed runtime
   package manifest and fails fast if the required UI runtime package was not
   emitted into the writable homepath.
4. Refreshed the UI packaging docs so they consistently describe the current
   contract: staging/overlay manifests by default, explicit package emission
   only for runtime-root refreshes or probe flows, with the overlay PK3
   remaining optional when the drift contract is empty.

### Task A4a: Restore Unix low-memory detection on the compatibility host lane [COMPLETED]
Priority: Medium
Primary areas: `src/code/unix/unix_main.c`, `docs/platform/toolchain-matrix.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Replaced the unconditional Unix `Sys_LowPhysicalMemory()` placeholder with
   a native `sysconf()`-backed physical page-count query so the renderer/cgame
   low-memory heuristic no longer hardcodes the non-low-memory path on Unix.
2. Refreshed the platform note so it now records the restored low-memory
   probe separately from the still-bounded checksum/comparison/profiling
   helpers.
3. Narrowed the active `RW-G02` description to the remaining portability debt
   instead of continuing to list `Sys_LowPhysicalMemory()` as an unresolved
   placeholder.

### Task A2: Repo-wide parity re-baseline and documentation convergence [COMPLETED]
Priority: Critical
Primary areas: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`,
`docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`,
`docs/parity-plan.md`, `docs/ui_deltas.md`, `docs/ui_followup_issues.md`,
`docs/quakelive_asset_audit.md`
Parity estimate: **before 92% -> after 92%**

Completed work:

1. Re-ran the repo's top-level parity-gate suites on 2026-04-21 and confirmed
   that the strict-retail Windows gate set remains green on the current
   worktree.
2. Re-based the top-level ledger so it now distinguishes the strict-retail
   Windows closure state from repo-wide parity across compatibility-only,
   portability, and packaging-dependent lanes.
3. Published a dedicated repo-wide gap register in
   `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`.
4. Demoted the most misleading broad-planning documents to explicit historical
   references so they no longer conflict with the current reverse-engineering
   ledgers.

### Task A1: Client parity-gate revalidation and workflow restoration [COMPLETED]
Priority: Critical
Primary areas: `.github/workflows/client-validation.yml`,
`tools/client/run_client_runtime_probe.ps1`,
`artifacts/client_validation/logs/*`, client ledger docs
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Restored `.github/workflows/client-validation.yml` so the client validation
   lane again runs the focused platform, Steamworks, config, workshop, UI-menu,
   and unified parity-gate suites expected by the audited `CL-P6` closure.
2. Repaired `tools/client/run_client_runtime_probe.ps1` so it now:
   - runs against the default build-disabled client configuration
   - uses the valid `map bloodrun ffa` command shape for the local-map probe
   - avoids helper-stdout pollution in the structured probe return path
   - retries transient `pak_uiql.pk3` rewrite locks on Windows
   - caps the probe at `com_maxfps 30`, which lets the map pass reach
     `CS_ACTIVE` before the queued demo/screenshot/disconnect commands fire
3. Refreshed
   `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
   and
   `artifacts/client_validation/logs/client_full_parity_gate.json` with a
   clean runtime bundle.
4. Revalidated the lane with:
   - `pytest tests/test_client_full_parity_gate.py -q --tb=no`
   - `pytest tests/test_platform_services.py tests/test_steamworks_harness.py tests/test_client_config_parity.py tests/test_client_workshop_bootstrap_parity.py tests/test_ui_menu_files.py tests/test_client_full_parity_gate.py -q --tb=no`

## Active tasks

### Task A3: Replace or further bound the compatibility-only online-service lanes [OPEN]
Priority: Critical
Primary areas: `src/common/platform/`, `src/code/client/`, `src/code/server/`,
`docs/platform/authentication.md`, `docs/steam_platform_abstraction.md`
Estimated repo-wide lift if closed: **96% -> 98%**

Scope:

1. Decide whether the repo will keep online services permanently bounded as a
   documented divergence or pursue real open replacements.
2. If the lane remains bounded, keep the default-disabled policy and
   compatibility labeling explicit everywhere the service table, auth flow,
   workshop flow, advert flow, or browser overlay surfaces are exposed.
3. If an open replacement path is pursued, replace the current heuristic
   backends with transport-backed implementations and refresh the runtime
   evidence for opted-in builds.

### Task A4: Modernise or explicitly contain the non-Windows portability lanes [OPEN]
Priority: High
Primary areas: `src/code/unix/`, `src/code/null/`,
`docs/platform/toolchain-matrix.md`, `docs/build/linux-glibc-32bit.md`
Estimated repo-wide lift if closed: **96% -> 97%**

Scope:

1. Replace the remaining Unix `Sys_*` helper placeholders that still matter
   after the restored low-memory, Linux/glibc function compare/checksum,
   `q3monkeyid` marker-probe, and bounded `gprof`-control paths, or keep them
   clearly classified as
   compatibility-only. The null host/client/audio shims now match the current
   contract surface closely enough that the remaining work is primarily about
   the real Unix host boundary rather than stale null host/client/audio/input
   entry points.
2. Decide whether Linux client/renderer/audio/input support is a real target or
   whether the current server-only path should remain the bounded endpoint.
3. Refresh the toolchain/runtime guidance and validation coverage once the
   intended portability boundary is settled.

### Task A6: Refresh build/runtime evidence for the repo-wide ledger [OPEN]
Priority: Medium
Primary areas: tracked runtime probe bundles, native build helpers, platform
docs
Estimated repo-wide lift if closed: **96% -> 97%**

Scope:

1. Refresh the archived runtime evidence bundles on a current toolchain instead
   of relying solely on the April 2026 tracked artifacts, and promote the
   stable `latest` aliases only when reruns remain sufficient.
2. Re-run native build validation where the required Windows toolchain is
   available and fold the results back into the repo-wide audit.
3. Capture the remaining glibc and continuous/self-hosted publication
   follow-ups called out in `docs/platform/toolchain-matrix.md`, including the
   remaining retail-module runtime freshness tail.

### Task 23: Ownerdraw/stat payload completion and validation [COMPLETED]
Priority: High
Primary areas: `src/code/game/`, `src/code/cgame/`, runtime validation harnesses
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Revalidated the ownerdraw debug payload against the current runtime capture
   path and confirmed that the live `pickupAvg` slab is emitted as fixed-point
   seconds rather than the older integer-only fixture assumption.
2. Updated the ownerdraw runtime harness in
   `tests/test_ownerdraw_stats_logging.py` so the debug-ownerdraw assertion
   path now accepts and normalizes float `pickupAvg` CSV payloads while keeping
   the integer stat families strict.
3. Re-ran the focused ownerdraw/stat validation surface on the current
   worktree; no concrete unsupported ownerdraw or `PLAYER_STATS` payload field
   remains in the active repo-level gap register.

### Task 24: Gameplay validation sweep [COMPLETED]
Priority: High
Primary areas: physics, Race, gametype-specific rules
Parity estimate: **before 99% -> after 100%**

Completed work:

1. Expanded the gametype lifecycle harness so it now builds through the shared
   compiler helper on Windows as well as POSIX, and it directly validates duel
   warmup/configstring sequencing, Race lifecycle routing, and CA/RR
   round-warmup init dispatch.
2. Tightened the ready-up and match-state regression guards around the retail
   gametype truth tables, including the both-teams-present gate and the
   Attack & Defend inclusion in the round-controller team-count publisher set.
3. Reconfirmed the focused Race and shared `pmove` regression lanes on the
   current worktree; the gameplay validation sweep is now covered by dedicated
   fixtures rather than left as an open catch-all validation reminder.

## Working priority order

1. Resolve the online-service compatibility boundary and evidence story.
2. Re-baseline the non-Windows portability lanes.
3. Refresh archived build/runtime evidence on current toolchains.

## Reference audits for closed surfaces

- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Historical closure anchors kept for parity-gate compatibility

The entries below are intentionally terse. They preserve the exact historical
task headings and parity-estimate lines that checked-in parity gates still read
from this file, without keeping pages of duplicated completed-task prose in the
active plan.

### Task 34: Cgame Attack and Defend round-scoreboard owner parity closure [COMPLETED]

### Task 31: Strict retail game-module parity closure [COMPLETED]

### Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]
Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)

### Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]

### Task 87: Client CL-P6 parity gate and runtime-evidence closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 92: Qcommon QC-P2 parity gate and Windows-friendly harness closure [COMPLETED]

### Task 94: Qcommon QC-P3 retail homepath closure [COMPLETED]

### Task 97: Qcommon QC-P4 collision leaf ownership closure [COMPLETED]

### Task 100: Server SV-P7 parity gate and dedicated runtime-evidence closure [COMPLETED]
Parity estimate: **before 97% -> after 100%**

### Task 102: Qcommon QC-P5 fallback VM closure [COMPLETED]

### Task 103: Remaining engine host/support EH-P2 Win32 Unicode clipboard closure [COMPLETED]

### Task 104: Strict retail game-module final ledger and runtime-evidence reconciliation [COMPLETED]

### Task 104: Qcommon QC-P6 runtime-evidence and ledger closure [COMPLETED]
Parity estimate: **before 98% -> after 100%**

### Task 110: Qshared shared-helper exactness and validation-lane closure [COMPLETED]
Parity estimate: **before 99% -> after 100%**

### Task 105: Remaining engine host/support EH-P3 raw-input host closure [COMPLETED]

### Task 106: Remaining engine host/support EH-P6 parity gate and evidence closure [COMPLETED]
Parity estimate: **before 89% -> after 92%**

### Task 107: Remaining engine host/support EH-P4 botlib internal proof closure [COMPLETED]
Parity estimate: **before 92% -> after 95%**

### Task 109: Remaining engine host/support EH-P1 boundary formalisation closure [COMPLETED]
Parity estimate: **before 100% -> after 100%** (`EH-P1` complete; strict-retail scope classification formalised)
