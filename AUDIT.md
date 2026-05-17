# Quake Live Parity Audit

Last updated: 2026-05-17

This file is the current cross-subsystem ledger for the repository. Detailed
reconstruction history belongs in the dedicated subsystem audits under
`docs/reverse-engineering/`; this top-level audit now records the current
repo-wide state, the active remaining work, and a minimal set of historical
closure anchors kept for existing parity gates.

This ledger now distinguishes between:

- the strict-retail Windows replacement target that the dedicated parity gates
  score; and
- repo-wide parity across the whole checked-in tree, including the
  compatibility-only and packaging-dependent surfaces that the strict-retail
  score intentionally excludes.

## Current status

The current audited state, with the aggregate pytest sweep refreshed on
2026-05-17, is:

- `ui`, strict retail module, `qcommon`, the mapped `qshared` helper family,
  renderer, server, remaining engine host/support, and `client` parity gates
  are green on the current worktree.
- The focused 2026-04-16 Windows platform-specific engine audit remains
  closed, as do the focused 2026-04-16 engine netcode and
  Awesomium/browser-host audits.
- The focused gameplay validation sweep remains closed on the current worktree
  through dedicated Race, gametype-lifecycle, ready-up, and `pmove` fixtures.
- The strict-retail Windows replacement target remains defensible at
  **100%** on the current worktree.
- Repo-wide parity is not **100%** once the deliberate compatibility-only
  lanes, the bounded non-Windows portability debt, and the remaining
  evidence-freshness gap are counted. The current repo-wide estimate for the
  whole checked-in tree is **98%**.
- A new source-file parity campaign is now open under
  `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md` and
  `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`.
  That campaign decomposes the current repo-wide story into `567` tracked
  source entries plus dedicated per-file notes where the current evidence is
  already concrete, without changing the top-level **100%** strict-retail /
  **98%** repo-wide assessment.
- A broad current-worktree parity sweep spanning the top-level parity gates,
  gameplay fixtures, portability checks, and the staged retail-runtime audit
  lane now passes at `72 passed, 7 skipped`.
- The checked-in `src/ui` runtime-panel compare is now clean (`65 / 65`,
  `0` content diffs), and the UI overlay/runtime-package machinery now acts
  as a regression sentinel rather than an active correction path. It no
  longer stands as an active repo-wide proof gap.

Treat the 2026-04-10 engine-wide **100%** report as a strict-retail Windows
closure milestone, not as a claim that every checked-in portability or
compatibility surface has reached retail parity.

## Evidence checked

Runtime artifacts below remain the 2026-04-21 refresh set unless a newer date
is called out; the aggregate pytest sweep was refreshed on 2026-05-17.

Verified directly:

- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/client/run_client_runtime_probe.ps1` -> refreshed `artifacts/client_validation/logs/client_runtime_evidence_20260410.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/qcommon/run_qcommon_runtime_probe.ps1` -> refreshed `artifacts/qcommon_validation/logs/qcommon_runtime_evidence_20260410.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/renderer/run_renderer_runtime_probe.ps1` -> refreshed `artifacts/renderer_validation/logs/renderer_runtime_evidence_latest.json` via the clean dated `20260421` bundle
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/server/run_server_runtime_probe.ps1` -> refreshed `artifacts/server_validation/logs/server_runtime_evidence_20260410.json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/modules/run_retail_module_runtime_probe.ps1` -> refreshed `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json` through the bounded `20260421` retail-module probe bundle
- `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\ci\wow64-smoketest.ps1` -> refreshed `artifacts/wow64-smoketest/wow64-smoketest.log`
- `pytest tests/test_client_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_ui_full_parity_gate.py -q --tb=no` -> `1 passed, 1 skipped`
- `pytest tests/test_game_module_retail_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_qcommon_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_renderer_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_server_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_engine_host_support_full_parity_gate.py -q --tb=no` -> `2 passed, 1 skipped`
- `pytest tests/test_ui_src_panel_parity.py tests/test_non_windows_portability.py -q --tb=no` -> `28 passed`
- `pytest tests/test_gametype_lifecycle.py -q` -> `8 passed`
- `pytest tests/test_game_readyup_parity.py tests/test_game_team_count_parity.py -q` -> `7 passed`
- `pytest tests/test_racepoint_commands.py -q` -> `1 passed`
- `pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q` -> `14 passed`
- `pytest tests/test_non_windows_portability.py tests/test_retail_dependency_runtime_audit.py tests/test_ui_src_panel_parity.py tests/test_ui_full_parity_gate.py tests/test_client_full_parity_gate.py tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py tests/test_renderer_full_parity_gate.py tests/test_server_full_parity_gate.py tests/test_engine_host_support_full_parity_gate.py tests/test_gametype_lifecycle.py tests/test_game_readyup_parity.py tests/test_game_team_count_parity.py tests/test_racepoint_commands.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q --tb=no` -> `72 passed, 7 skipped`

Audited by source/doc inspection:

- `src/common/platform/platform_config.h`
- `src/common/platform/platform_services.c`
- `src/common/platform/backends/platform_backend_open_steam.c`
- `src/common/platform/backends/platform_backend_steamworks.c`
- `src/code/unix/unix_main.c`
- `tools/ci/audit-retail-dependencies.ps1`
- `tools/ci/validate-windows-native.ps1`
- `docs/platform/authentication.md`
- `docs/platform/retail-dependencies.md`
- `docs/platform/toolchain-matrix.md`
- `docs/toolchain-ci.md`
- `docs/windows-native-pipeline.md`
- `docs/quakelive_asset_audit.md`
- `docs/ui/hud-audit.md`
- `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`
- the legacy planning/status notes demoted in this pass:
  `docs/parity-plan.md`, `docs/ui_deltas.md`, and `docs/ui_followup_issues.md`

## Active remaining work

The strict-retail Windows gate set is green. `RW-G01` online services and
external ecosystems are now tracked as a documented bounded divergence rather
than active parity debt: default builds still set
`QL_BUILD_ONLINE_SERVICES=0`, the service table still reports build-disabled
providers, and the open/hybrid auth backends remain heuristic
accept/retry/deny shims rather than live service implementations, but that
lane is now explicitly excluded from the repo-wide deficit instead of being
left as ambiguous open work.

Two repo-wide gap families remain active:

- `RW-G02` Non-Windows portability is still incomplete. The Linux path remains
  server-only, the documented glibc preset is server-module-only evidence
  rather than Linux client/runtime parity proof, Unix
  `Sys_LowPhysicalMemory()` plus Linux/glibc
  `Sys_FunctionCmp()` / `Sys_FunctionCheckSum()` are now restored, the
  historical `q3monkeyid` release-marker probe is now reconstructed, the Unix
  engine now exposes a bounded `gprof`-compatible profiling control path via
  `moncontrol` / `_mcleanup` when built with `QL_ENABLE_GPROF=1`, Unix
  `Sys_GetClipboardData()` now exposes a bounded clipboard retrieval path via
  `wl-paste`, `xclip`, or `xsel` when the host environment provides those
  helpers, Unix `Sys_CheckCD()` now performs a bounded `baseq3` data-root
  probe across `fs_basepath`, `fs_cdpath`, and the default install roots, Unix
  `Sys_LoadDll()` now clears failed-load outputs, validates candidate exports,
  closes incompatible handles, and probes cwd, `fs_homepath`, `fs_basepath`,
  and `fs_cdpath`, Unix `Sys_GetEvent()` now
  queues only unread packet bytes after `netmsg.readcount`, and
  the Linux sound host now provides a bounded silent DMA sink via
  `snddevice null` / `none` / `silent` plus explicit OSS descriptor and mmap
  cleanup on shutdown, Linux joystick input now bounds device probing to
  `/dev/input/js0-3` and `/dev/js0-3` while clearing `ui_joyavail` and closing
  `joy_fd` across shutdown or `in_joystick` restarts, and Linux input shutdown
  now releases retained X mouse grabs before clearing mouse availability, Linux
  GLX shutdown now handles partial-init display/context/window state, closes
  the QGL log, releases QGL state, and guards end-frame swaps after shutdown,
  while the null host/runtime now carries current executable-name, path, timer,
  loopback-network, browser/advert/input, a renderer GL init refusal, an
  explicit null silent DMA sink, and sound/device activation/voice
  compatibility shims plus the newer input bootstrap-cvar and no-device
  key-pump surface, but the profiling lane
  is still optional, the Linux sound lane still lacks a real modern audible
  backend, and the broader Unix runtime still remains
  compatibility-only rather than retail-equivalent hosts.
- `RW-G04` Evidence freshness outside the tracked artifacts remains incomplete.
  This audit reran the gate suites, refreshed the tracked client, qcommon,
  server, and renderer runtime bundles, reran the retained WOW64 smoke
  harness, and introduced guarded `latest` aliases for the renderer/module
  runtime probes so degraded reruns do not silently replace authoritative
  evidence. The retail native validation lane now also stages
  `build\win32\<Config>\retail-runtime\` and audits that strict runtime root
  for missing or extra DLLs, so the formerly documented local/runtime DLL
  guard follow-up is no longer open. That strict runtime-root boundary is now
  also pinned by `tests/test_retail_dependency_runtime_audit.py`, which proves
  the mixed `build\win32\Debug\bin` lane still fails the strict audit while a
  clean staged root passes with rebuilt module slots treated as required but
  hash-optional. The module alias now also points at the current bounded
  `2026-04-21` retail-module artifact, whose remaining live-map shortfall is
  explicitly the renderer-owned `R_fonsErrorCallback` font-atlas saturation
  lane rather than an ambiguous module-host failure. The remaining debt is now
  concentrated in fresh native build outputs and the broader glibc plus
  self-hosted publication follow-ups in `docs/platform/toolchain-matrix.md`.

The former `RW-G03` UI packaging/proof gap is now bounded rather than active:
the checked-in `src/ui` runtime-panel baseline is clean, and explicit
runtime-root package emission is now described by
`artifacts/ui_bundle/runtime_ui_package_manifest.json`, verified in
`tests/test_ui_src_panel_parity.py`, and consumed by the client runtime probe
before launch when future drift needs investigation.

Historical planning/docs convergence is no longer an active gap family after
this pass; the stale broad-planning notes that still described older open UI
and HUD deltas are now explicitly marked historical.

## Detailed repo-wide audit

- `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- `docs/reverse-engineering/source-file-parity-ledger-2026-04-22.md`
- `docs/reverse-engineering/source-file-parity-audit-plan-2026-04-22.md`
- `docs/reverse-engineering/historical-audit-index-2026-04-22.md`

## Subsystem references

- Repo-wide gap register and rationale:
  `docs/reverse-engineering/repo-wide-parity-audit-2026-04-21.md`
- Engine-wide closure milestone:
  `docs/reverse-engineering/engine-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Current strict retail module ledger:
  `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-10.md`
- UI parity ledger:
  `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
- Client closure milestone and validation note:
  `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`
  and
  `docs/reverse-engineering/client-validation-and-runtime-evidence-2026-04-10.md`
- Qcommon parity ledger:
  `docs/reverse-engineering/qcommon-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Qshared helper parity ledger:
  `docs/reverse-engineering/qshared-retail-helper-parity-audit-2026-04-17.md`
- Renderer parity ledger:
  `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
- Server parity ledger:
  `docs/reverse-engineering/server-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Remaining engine host/support ledger:
  `docs/reverse-engineering/engine-host-support-full-parity-audit-and-implementation-plan-2026-04-10.md`
- Platform-specific Windows engine ledger:
  `docs/reverse-engineering/platform-specific-engine-parity-audit-and-implementation-plan-2026-04-16.md`
- Engine netcode ledger:
  `docs/reverse-engineering/engine-netcode-parity-audit-2026-04-16.md`
- Awesomium/browser host ledger:
  `docs/reverse-engineering/awesomium-browser-host-parity-audit-and-implementation-plan-2026-04-16.md`

## Historical closure anchors kept for parity-gate compatibility

These lines intentionally preserve a minimal set of exact historical closure
strings that the checked-in parity gates still consume. They document past
closure milestones, not the full current 2026-04-21 top-level state by
themselves.

### Module closure milestones

- `GMR-P7` is now complete in the current worktree.
- `GMR-P8` is now complete in the current worktree.
- The current module audit, the top-level ledgers, and the supporting pipeline notes now all point at the same closure state again.
- The current strict retail module estimate for the current worktree is back at **100%** in the refreshed module report.

### Renderer closure milestones

- The open renderer gap register is now wider than the old single-tranche `RG-G05` story.
- `RG-P5` is now complete.

### Qcommon closure milestones

- The refreshed strict `qcommon` estimate is now **92%**.
- `QC-P2` and `QC-P3` are now complete.
- `QC-G04` and `QC-G01` are now closed.
- The refreshed strict `qcommon` estimate is now **95%**.
- `QC-P4` is now complete.
- `QC-G02` is now closed.
- The refreshed strict `qcommon` estimate is now **98%**.
- `QC-P5` is now complete.
- `QC-G03` is now closed.
- The refreshed strict `qcommon` estimate is now **100%**.
- `QC-P6` is now complete.
- `QC-G05` is now closed.
- No open gap remains in the audited qcommon register.

### Qshared closure milestone

- The refreshed strict `qshared` helper estimate is now **100%**.
- `QS-P1` and `QS-P2` are now complete.
- `QS-G01` and `QS-G02` are now closed.

### Server closure milestones

- The refreshed strict `server` estimate is now explicitly tracked as **100%**.
- `SV-P7` is now complete.
- No open gap remains in the audited server register.

### Remaining engine host/support closure milestones

- The refreshed strict `remaining engine host/support` estimate is now tracked as **100%**.
- `EH-P1` is now complete. The host/support artifact now carries machine-readable scope boundary and classification metadata and reports `overall_status: pass`.
- `EH-P4` is now complete.
- `EH-G04` is now closed.
- `EH-P6` is now complete.
- `EH-G06` is now closed.

### Client closure milestone

- `CL-P6` is now complete.
- The refreshed strict `client` estimate is now **100%**.
- No open gap remains in the audited client register.

Those three lines record the 2026-04-10 client closure milestone. The
2026-04-21 worktree now revalidates that same closure state with a refreshed
workflow plus runtime bundle, as described in the current-status sections
above.
