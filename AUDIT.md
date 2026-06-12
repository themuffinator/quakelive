# Quake Live Parity Audit

Last updated: 2026-06-05

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
- The 2026-06-12 all-gametype integration pass keeps the focused gametype
  routing surface at **99%** by pinning the complete QL enum/factory matrix,
  qagame lifecycle/runframe/exit/scoreboard buckets, cgame scoreboard parser
  and HUD feeder families, and shared objective configstring consumers in one
  executable parity gate.
- The 2026-06-05 Race gametype closure keeps the focused Race qagame/cgame
  wiring surface at **100%** by matching the retail evidence for `race_info`,
  `race_init`, admin `racepoint`/`admin_race_point_N` transport, checkpoint
  touch events, finish ranking, and `scores_race` rows sourced from
  `level.sortedClients` / `level.numPlayingClients`.
- The 2026-06-05 Domination gametype closure keeps the focused Domination
  qagame/cgame wiring surface at **100%** by matching the qagame HLIL evidence
  for the five-point registration cap, delayed point activation, participant
  capture/assist rewards, primary-capturer retention, shared point-count
  configstrings, owned-point spawn selection, and point-defense bonus routing.
- The 2026-05-25 movement/playerState re-audit keeps the shared pmove,
  playerState replication, pmove settings transport, and prediction wiring
  surface at **100%** for the scoped retail source reconstruction; no source
  patch was required.
- The 2026-05-25 pmove factory wiring re-audit keeps the retail `pmove_*`
  factory cvar table, reset/apply ordering, reload-to-pmove refresh handoff,
  custom-settings mask grouping, and cgame/UI publication wiring at **100%**;
  the pass added a focused regression guard for the factory apply sequence.
- The 2026-05-25 deep pmove/playerState mapping sweep keeps the shared
  qagame/cgame movement island at **100%** while adding executable coverage
  for the `PMF_NO_MOVE` command gate and validating selected `pmove_*` cvars
  from retail registration through cgame parse and active movement consumers.
- The follow-up 2026-05-25 profile/utility pmove/playerState wiring sweep keeps
  that same scoped surface at **100%** while pinning the remaining profile and
  utility cvars through registration, cache/transport, playerState profile
  flags, movement consumers, and custom-settings mask wiring.
- The 2026-05-25 active-client pmove/playerState wiring reconstruction closes
  the qagame frame-step-to-`ClientThink_real` source mismatch by dispatching
  bot/synchronous client movement frames inline from the entity loop, matching
  the recovered retail `G_RunFrame` shape while keeping the scoped movement
  wiring estimate at **100%**.
- The 2026-05-25 cgame prediction pmove replay re-audit keeps the local
  prediction/playerState handoff at **100%** while pinning `CG_PredictPlayerState`
  through local `pmove_t` setup, command replay, item/trigger prediction,
  mover adjustment, step smoothing, predictable-event handoff, and committed
  cgame symbol evidence.
- The 2026-06-05 client-side prediction recheck keeps that focused cgame
  prediction slice at **100%** while tightening executable coverage for the
  mapped solid-list, box/capsule trace, point-contents, interpolation,
  red/blue-flag predicate, high-value item skip, trigger-touch, step smoothing,
  rail replay, active-frame caller, packet-entity predicted proxy, mover
  compensation, snapshot handoff/pump, native export, snapshot import, usercmd
  import, pmove settings, and symbol-map evidence corridor.
- The 2026-05-25 qcommon playerState delta-codec re-audit keeps the snapshot
  replication bridge at **100%** while pinning the Quake Live scalar netfield
  table, signed movement command mirrors, and the `stats[]`, `persistant[]`,
  `ammo[]`, and `powerups[]` array-mask round trips that feed cgame prediction.
- The 2026-05-25 server/client snapshot playerState transport re-audit keeps
  the live server-to-cgame bridge at **100%** while pinning
  `SV_BuildClientSnapshot`, `SV_WriteSnapshotToClient`, `CL_ParseSnapshot`,
  `CL_GetSnapshot`, and `trap_GetSnapshot` ordering around playerState,
  areamask, packet entities, and `ps.commandTime` ping derivation.
- The 2026-06-05 server snapshot send-wrapper closure keeps the focused
  snapshot system at **100%** by removing the non-retail classic
  `SV_WriteDownloadToClient` injection from `SV_SendClientSnapshot`; retail
  `0x004E5AC0` now maps cleanly from snapshot body write to overflow handling
  and `SV_SendMessageToClient`.
- The 2026-06-05 related snapshot wiring re-audit keeps the adjacent
  snapshot corridor at **100%** by rechecking server authoring, client parse,
  cgame readback, qagame visibility exports, and bot snapshot entity access.
  The pass added an executable guard for `SV_BotGetSnapshotEntity` and
  `QL_G_trap_BotGetSnapshotEntity` against retail `sub_4DDAC0` and
  `sub_4E17E0`.
- The 2026-05-25 client/server usercmd movement-transport re-audit keeps the
  command side of the movement bridge at **100%** while pinning client
  `CL_CreateCmd` / `CL_WritePacket`, qcommon keyed usercmd deltas, server
  `SV_UserMove` / `SV_ClientThink`, qagame `G_GET_USERCMD`, and cgame
  `trap_GetUserCmd` prediction access.
- The 2026-05-31 referenced-pak publication re-audit keeps the
  `sv_referencedPaks` / `sv_referencedPakNames` filesystem publication and
  client autodownload decision lane at **100%** by matching the retail
  `FS_ReferencedPakChecksums` / `FS_ReferencedPakNames` flag-only condition
  instead of the older Quake III fs_game-wide publication rule.
- The 2026-05-26 renderer framebuffer/post-process reconstruction keeps the
  scoped post-process framebuffer owner lane at **99.93%** by retiring the
  disconnected legacy `GL_TEXTURE_2D` scene-target and scratch-bloom helper
  family in favor of the retail `RBPP_CreateRenderTarget` rectangle-texture
  owner.
- The follow-up 2026-05-26 renderer bloom teardown reconstruction keeps the
  scoped post-process bloom teardown lane at **99.95%** by matching retail's
  grouped program, texture, framebuffer, and renderbuffer shutdown order.
- The next 2026-05-26 renderer renderbuffer-cache reconstruction keeps the
  scoped post-process depth-stencil renderbuffer cache lane at **99.97%** by
  matching retail's eight-entry width/height renderbuffer reuse helper and its
  render-target creation wiring.
- The follow-up 2026-05-26 renderer GL-error/link reconstruction keeps the
  scoped post-process GL error and link lane at **99.985%** by restoring the
  return-valued `GL_CheckErrors` contract, render-target error branches, and
  the recovered post-effect program link helper.
- The next 2026-05-26 renderer proc-gate reconstruction keeps the scoped
  post-process proc gate lane at **99.99%** by splitting framebuffer-only
  render-target procedure loading from the shader/uniform procedure gate used
  by post-effect program setup.
- The 2026-05-31 renderer post-process command-payload reconstruction closes
  the scoped post-process command wiring lane at **100%** by matching retail's
  command-buffer texture/program handle consumption for color-correct and
  bloom execution.
- The strict-retail Windows replacement target remains defensible at
  **100%** on the current worktree.
- Repo-wide parity is not **100%** once the deliberate compatibility-only
  lanes and the remaining evidence-freshness gap are counted. The current
  repo-wide estimate for the whole checked-in tree is **99%** after the
  non-Windows portability lanes were closed as explicit compatibility-only
  containment on 2026-06-05.
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
- `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/modules/run_retail_module_runtime_probe.ps1` -> refreshed `artifacts/module_validation/logs/retail_module_runtime_evidence_latest.json`; the latest alias now points at the clean `20260602` retail-module probe bundle
- `C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\ci\wow64-smoketest.ps1` -> refreshed `artifacts/wow64-smoketest/wow64-smoketest.log`
- 2026-06-05 A6 native Windows preflight captured in
  `docs/reverse-engineering/windows-native-validation-preflight-2026-06-05.md`:
  `audit-retail-toolchain.ps1 -Strict` and
  `validate-windows-native.ps1 -RuntimeProfile retail` now reach project
  metadata checks, but both stop before build because the strict retail audit
  expects `PlatformToolset=v100` while the current project files report `v141`
- 2026-06-05 A6 modern-host build evidence captured in
  `docs/reverse-engineering/runtime-build-evidence-refresh-2026-06-05.md`:
  Visual Studio 2022 `v143` is available, the modern `Release|x86` build
  completed with `0` warnings and `0` errors, and the direct gameplay DLL
  export audit passed against the fresh `Release\modules` outputs
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
- `python -m pytest tests/test_racepoint_commands.py tests/test_game_nonteam_scoreboard_helper_parity.py tests/test_game_helper_seam_parity.py::test_timeout_race_and_direct_command_helpers_match_recovered_boundaries tests/test_cgame_event_transport_parity.py tests/test_gametype_lifecycle.py -q --tb=short` -> `28 passed`
- `pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py -q` -> `14 passed`
- `python -m pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py -q --tb=short` -> `145 passed, 107 subtests passed`
- `python -m pytest tools/tests/test_pmove_settings_configstring.py tests/test_game_factory_regen_parity.py tests/test_game_weapon_parity.py::test_grappling_hook_full_server_and_cgame_wiring_matches_retail tests/test_ui_menu_files.py::test_ui_retail_server_settings_ownerdraw_restored tests/test_ui_menu_files.py::test_game_retail_weapon_reload_configstring_restored tests/test_cgame_displaycontext_parity.py::test_cgame_weapon_reload_configstring_bridge_restored tests/test_cgame_displaycontext_parity.py::test_cgame_server_settings_panel_reconstruction_uses_retail_custom_setting_configstrings -q --tb=short` -> `32 passed, 107 subtests passed`
- `python -m pytest tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `12 passed`
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py -q --tb=short` -> `4 passed`
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_game_helper_seam_parity.py tests/test_game_spectator_connection_parity.py -q --tb=short` -> `30 passed`
- `python -m pytest tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `158 passed, 107 subtests passed`
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `162 passed, 107 subtests passed`
- `python -m pytest tests/test_cgame_snapshot_parity.py -q --tb=short` -> `11 passed`
- `python -m pytest tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py -q --tb=short` -> `23 passed`
- `python -m pytest tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tests/test_playerstate_replication.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `180 passed, 107 subtests passed`
- `python -m pytest tests/test_playerstate_replication.py -q --tb=short` -> `10 passed`
- `python -m pytest tests/test_playerstate_replication.py -q --tb=short` -> `14 passed`
- `python -m pytest tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `184 passed, 107 subtests passed`
- `python -m pytest tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_game_native_export_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `194 passed, 107 subtests passed`
- `python -m pytest tests/test_usercmd_movement_transport_parity.py -q --tb=short` -> `5 passed`
- `python -m pytest tests/test_usercmd_movement_transport_parity.py tests/test_engine_client_command_parity.py::test_usercmd_cgame_bridge_matches_retail_weapon_primary_and_fov_bytes tests/test_engine_client_command_parity.py::test_client_input_mapping_round_277_promotes_console_input_and_usercmd_symbols -q --tb=short` -> `7 passed`
- `python -m pytest tests/test_usercmd_movement_transport_parity.py tests/test_playerstate_replication.py tests/test_game_active_pmove_wiring_parity.py tests/test_cgame_snapshot_parity.py tests/test_cgame_playerstate_transition_parity.py tests/test_cgame_item_respawn_timer_parity.py tests/test_game_native_export_helper_parity.py tests/test_pmove_validation_fixtures.py tests/test_pmove_air_control_runtime_parity.py tests/test_pmove_jump_timing_parity.py tests/test_pmove_movement_fixtures.py tests/test_pmove_helper_parity.py tests/test_pmove_acceleration_scope_parity.py tests/test_pmove_crouch_time_parity.py tests/test_pmove_crouch_slide_friction_parity.py tests/test_pmove_reload_fallback_parity.py tests/test_pmove_water_scale_parity.py tests/test_bg_playerstate_bridge_parity.py tools/tests/test_pmove_settings_configstring.py tests/test_pmove_selected_cvar_parity.py -q --tb=short` -> `199 passed, 107 subtests passed`
- `python -m pytest tests/test_bg_misc_validation_fixtures.py tests/test_bg_misc_runtime_parity.py tests/test_bg_misc_helper_parity.py -q --tb=short` -> `39 passed`
- `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py -q --tb=short` -> `4 passed, 2 skipped`
- `python -m pytest tests/test_game_module_retail_parity_gate.py tests/test_qcommon_full_parity_gate.py tests/test_client_full_parity_gate.py -q --tb=short` -> `6 passed, 3 skipped`
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

The formerly active portability gap and the remaining active gap now stand as
follows:

- The former `RW-G02` non-Windows portability gap is now closed as an active
  repo-wide gap by the 2026-06-05 boundary decision. The Linux path remains
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
  key-pump surface. The optional profiling lane, Linux sound backend, broader
  Unix runtime, Linux client renderer/input stack, and null runtime remain
  documented compatibility-only carries rather than retail-equivalent hosts.
  Reopening this family now requires a successor task that intentionally
  adopts a modern renderer/audio/input dependency stack and reproducible
  validation lane.
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
  hash-optional. The module alias now points at the `2026-06-02`
  retail-module artifact, whose live-map pass loads retail `ui`, `qagame`, and
  `cgame`, reaches `CS_ACTIVE` on `bloodrun`, and records no missing markers
  or warnings. The 2026-06-05 A6 build refresh also produced current
  modern-host `v143` `Release|x86` outputs and a passing direct export audit
  after `tools/ci/assert-dll-exports.ps1` was tightened to prefer the newest
  Release candidate. Strict VC10 staged-runtime evidence remains documented as
  a local toolchain/project-shape boundary: the strict retail audit still
  expects `PlatformToolset=v100`, while the current checked-in projects report
  `v141`.

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
