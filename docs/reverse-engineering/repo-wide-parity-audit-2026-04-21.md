# Repo-Wide Parity Audit

Last updated: 2026-04-22

## Scope

This note is the current repo-wide parity register. It exists because the
repository now has two different but valid parity views:

- the strict-retail Windows replacement target scored by the dedicated parity
  gates; and
- repo-wide parity across the whole checked-in tree, including
  compatibility-only ports, build-disabled ecosystem surfaces, and
  packaging-dependent corrections that the strict-retail score intentionally
  excludes.

The strict-retail Windows target remains closed on the current worktree. This
document tracks the remaining repo-wide gaps that still matter once the whole
tree is counted.

## Audit method

Validated directly on 2026-04-21:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/client/run_client_runtime_probe.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/qcommon/run_qcommon_runtime_probe.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/renderer/run_renderer_runtime_probe.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/server/run_server_runtime_probe.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/modules/run_retail_module_runtime_probe.ps1`
- `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\ci\wow64-smoketest.ps1`
- `pytest tests/test_client_full_parity_gate.py -q --tb=no`
- `pytest tests/test_ui_full_parity_gate.py -q --tb=no`
- `pytest tests/test_game_module_retail_parity_gate.py -q --tb=no`
- `pytest tests/test_qcommon_full_parity_gate.py -q --tb=no`
- `pytest tests/test_renderer_full_parity_gate.py -q --tb=no`
- `pytest tests/test_server_full_parity_gate.py -q --tb=no`
- `pytest tests/test_engine_host_support_full_parity_gate.py -q --tb=no`
- `pytest tests/test_ui_src_panel_parity.py tests/test_non_windows_portability.py -q --tb=no`
- `pytest tests/test_non_windows_portability.py tests/test_retail_dependency_runtime_audit.py tests/test_ui_src_panel_parity.py tests/test_ui_full_parity_gate.py tests/test_client_full_parity_gate.py tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py tests/test_renderer_full_parity_gate.py tests/test_server_full_parity_gate.py tests/test_engine_host_support_full_parity_gate.py tests/test_gametype_lifecycle.py tests/test_game_readyup_parity.py tests/test_game_team_count_parity.py tests/test_racepoint_commands.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q --tb=no` -> `60 passed, 7 skipped`

Reviewed by source and current documentation:

- `src/common/platform/platform_config.h`
- `src/common/platform/platform_services.c`
- `src/common/platform/backends/platform_backend_open_steam.c`
- `src/common/platform/backends/platform_backend_steamworks.c`
- `src/code/unix/unix_main.c`
- `tools/ci/audit-retail-dependencies.ps1`
- `tools/ci/validate-windows-native.ps1`
- `docs/build/linux-glibc-32bit.md`
- `docs/platform/authentication.md`
- `docs/platform/retail-dependencies.md`
- `docs/platform/toolchain-matrix.md`
- `docs/toolchain-ci.md`
- `docs/windows-native-pipeline.md`
- `docs/quakelive_asset_audit.md`
- `docs/ui/hud-audit.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Current assessment

- Strict-retail Windows replacement target: **100%**
- Repo-wide parity across the checked-in tree: **96%**

Rationale:

1. The dedicated Windows parity gates are green and continue to support the
   strict-retail closure story for `ui`, module, `qcommon`, `qshared`,
   renderer, server, client, and the remaining engine host/support scope.
2. That score no longer maps cleanly to the whole repository because the repo
   intentionally carries compatibility-only lanes and archived runtime/build
   evidence that are outside the strict-retail gate model.
3. The checked-in `src/ui` runtime-panel compare is now clean, and the
   accepted runtime correction/proof path remains explicit, machine-described,
   and test-backed if future drift ever reappears.
4. The remaining repo-wide deficit is concentrated in three bounded gap
   families rather than broad unknown engine debt.

## Gap register

### RW-G01 - Online services and external ecosystems remain compatibility-only

Observed facts:

- `src/common/platform/platform_config.h` defaults `QL_BUILD_ONLINE_SERVICES`
  to `0` and forces both provider flags off in default builds.
- `src/common/platform/platform_services.c` reports
  `Build-disabled (QL_BUILD_ONLINE_SERVICES=0)` for auth, matchmaking,
  workshop, overlay, and stats when the default build is used.
- `src/common/platform/backends/platform_backend_steamworks.c` and
  `src/common/platform/backends/platform_backend_open_steam.c` currently make
  accept/retry/deny decisions from token shape and substring heuristics rather
  than from real transport-backed service exchanges.
- `docs/platform/authentication.md` already classifies this lane as
  compatibility-only and explicitly says the open/hybrid backends are a
  documented divergence until a real open replacement path exists.

Impact:

- Default builds do not reproduce retail Quake Live live-service behavior.
- Opted-in builds expose bounded compatibility behavior rather than a complete
  retail-equivalent ecosystem implementation.
- The strict-retail score remains valid because this lane is deliberately
  excluded there, but the repo-wide score cannot call this surface closed.

Current status: **Open repo-wide gap**

### RW-G02 - Non-Windows portability remains incomplete

Observed facts:

- `docs/platform/toolchain-matrix.md` and `docs/build/linux-glibc-32bit.md`
  explicitly say the Linux path is still server-only, treat the glibc preset
  as server-module-only evidence rather than Linux client/runtime parity
  proof, and keep the Unix/null trees classified as compatibility-only rather
  than part of the retail replacement target.
- `src/code/unix/unix_main.c` now restores `Sys_LowPhysicalMemory()` through a
  `sysconf()`-backed physical page-count query, provides symbol-backed
  `Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` coverage on Linux/glibc,
  reconstructs `Sys_MonkeyShouldBeSpanked()` as a retained `q3monkeyid`
  marker probe, exposes a bounded `gprof`-compatible profiling control path
  through `moncontrol` / `_mcleanup` when the Unix engine is built with
  `QL_ENABLE_GPROF=1`, and now carries a bounded clipboard retrieval path
  through `wl-paste`, `xclip`, or `xsel` when the surrounding Wayland/X11
  environment is present. `Sys_CheckCD()` now also acts as a bounded
  data-root probe across the configured `baseq3` roots instead of an
  unconditional success path, accepting `default.cfg`, `pak00.pk3`, or
  `pak0.pk3` as sufficient evidence of usable game data.
- `src/code/null/null_main.c`, `src/code/null/null_net.c`,
  `src/code/null/null_glimp.c`, `src/code/null/null_client.c`,
  `src/code/null/null_snddma.c`, and `src/code/null/null_input.c` now carry
  current executable-name, timer/path, loopback-network, browser/advert/input, and silent sound/device activation/voice shims
  plus the newer input bootstrap-cvar surface instead of the older stale
  `Com_Init( argc, argv )`, `NET_StringToAdr`, `FILE *`, and missing
  web-host/audio/input compatibility contracts, but the null runtime still
  does not implement a real live graphics/audio/input host.
- The same platform note now records a successful 2026-04-21 WOW64 smoke run,
  but it still carries open follow-ups for broader glibc validation breadth
  and Unix-side modernization.

Impact:

- The repository cannot claim broad retail-equivalent parity outside the
  Windows host/runtime target.
- Linux/macOS/null support remains a bounded compatibility story, not a closed
  replacement story.

Current status: **Open repo-wide gap**

### RW-G03 - UI overlay dependence is now explicit and machine-verified

Observed facts:

- `tests/test_ui_src_panel_parity.py` and
  `artifacts/ui_bundle/ui_src_retail_overlay.json` now both record a clean
  `src/ui` runtime-panel compare (`65 / 65`, `0` content diffs,
  `drift_files: []`).
- Default `tools/build_ui_bundle.py` runs still keep retail runtime PK3s
  unmaterialized and write the overlay/staging evidence instead of silently
  duplicating retail distributables.
- Explicit `--runtime-root` runs now emit `pak_uiql.pk3`, preserve a bounded
  `pak_ui_src_retail_overlay.pk3` slot, and write
  `artifacts/ui_bundle/runtime_ui_package_manifest.json`, which records the
  runtime root, hashes, required-entry coverage, and whether an overlay
  package was needed.
- `tests/test_ui_src_panel_parity.py` now verifies that explicit runtime-root
  emission produces the required main-package entries and that any emitted
  overlay package matches the manifest contract exactly.
- `tools/client/run_client_runtime_probe.ps1` now refuses to launch unless the
  runtime-package manifest exists, the required UI entries are present, and
  any declared overlay package was actually emitted into the writable runtime
  root.

Impact:

- Packaged/runtime UI parity no longer depends on an undocumented manual
  staging step.
- The checked-in `src/ui` runtime-panel baseline is currently clean, and the
  overlay contract now acts as a regression sentinel rather than an active
  correction path.

Current status: **Closed as an active repo-wide proof gap; bounded fallback remains documented**

### RW-G04 - Evidence freshness remains weaker than the structural gate story

Observed facts:

- The 2026-04-21 audit re-ran the parity-gate suites and confirmed they stay
  green on the current worktree.
- The tracked client, qcommon, and server runtime evidence bundles were all
  refreshed on 2026-04-21 and now reflect the current probe contracts,
  including the repaired `map <name> ffa` command shape in the qcommon and
  dedicated-server lanes plus the current offline-browser or status-publication
  markers.
- The renderer runtime probe was also repaired and rerun on 2026-04-21. The
  tracked alias
  `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json`
  now points at the clean
  `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260421.json`
  bundle, and the probe only promotes that alias when a rerun remains
  sufficient.
- The retail module probe was rerun on 2026-04-21 and now again reaches the
  current `map <name> ffa` contract, retail `qagamex86.dll` / `cgamex86.dll`
  load, and `Server: catalyst`. The stable alias
  `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`
  now points at the current bounded `2026-04-21` artifact, whose remaining
  live-map shortfall is the renderer-owned `R_fonsErrorCallback` font-atlas
  saturation blocker preventing `CS_ACTIVE` after retail module load.
- The retained WOW64 smoke harness was also rerun successfully on 2026-04-21
  from 32-bit PowerShell, with the current log captured at
  `artifacts/wow64-smoketest/wow64-smoketest.log`.
- The retail native validation lane now also stages
  `build\win32\<Config>\retail-runtime\` from rebuilt executables/modules plus
  the exact retail launcher DLL payload and audits that strict root for
  missing or extra DLLs. The older "fail fast on extra non-retail runtime DLLs"
  follow-up in the Windows/toolchain docs is therefore no longer open.
- The strict staged-runtime DLL boundary is now also pinned by
  `tests/test_retail_dependency_runtime_audit.py`, which proves that the mixed
  `build\win32\Debug\bin` root still fails under strict audit while a clean
  staged root passes with rebuilt `cgamex86.dll`, `qagamex86.dll`, and
  `uix86.dll` treated as required-but-hash-optional validation outputs rather
  than retail byte-identity targets.
- Fresh native build outputs were still not regenerated on this pass, and the
  remaining freshness debt is now concentrated in the still-open
  build/publication follow-ups plus the broader need to regenerate additional
  runtime/build artifacts on current toolchains.
- `docs/platform/toolchain-matrix.md` still lists outstanding follow-ups for
  broader glibc validation and continuous/self-hosted publication of the WOW64
  lane.

Impact:

- The current closure story is structurally strong, but some proof remains
  artifact-backed rather than freshly regenerated on this audit pass.
- This is a validation/freshness gap, not a broad source-reconstruction gap.

Current status: **Open repo-wide gap**

## Historical docs corrected in this pass

The following broad planning/status documents were still describing older open
UI/HUD/menu gaps even though the current reverse-engineering ledgers had
already closed or rebounded those surfaces:

- `docs/parity-plan.md`
- `docs/ui_deltas.md`
- `docs/ui_followup_issues.md`

They are now explicitly marked historical so they stop conflicting with the
current ledgers.

## Source-file audit campaign

A new file-by-file campaign now sits alongside this repo-wide summary:

- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`
- `docs/reverse-engineering/source-file-gap-notes/`

It tracks `567` source entries, keeps the existing subsystem audits as
inherited baselines, and only opens dedicated per-file notes when the current
evidence isolates a concrete parity gap. That campaign does not add a new
repo-wide gap family; it turns `RW-G01` and `RW-G02` into a cleaner
file-ownership queue.

## Recommended next steps

1. Drive the new source-file campaign through the primary runtime and module
   surface so the remaining repo-wide gaps are isolated file-by-file instead
   of only by tree or subsystem.
2. Decide whether online services stay permanently bounded or receive real open
   replacements.
3. Re-baseline the Unix/null portability boundary and finish any platform work
   that should count toward repo-wide parity.
4. Refresh archived runtime/build evidence on current toolchains when the
   remaining Windows and non-Windows environments are available, especially the
   native build outputs, a fresh
   `tools/ci/validate-windows-native.ps1 -RuntimeProfile retail` pass, and the
   next promotable retail-module rerun.
5. Keep the clean `src/ui` runtime-panel baseline and overlay manifests in
   sync so future regressions are caught immediately without reviving a manual
   packaging dependency.
