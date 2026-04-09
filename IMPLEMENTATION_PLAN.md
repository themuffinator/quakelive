# Implementation Plan

This plan tracks the highest-value parity work remaining after the 2026-03-06 audit refresh.

## Strategic goal

The long-term parity target is that this engine should, in theory, be able to replace the retail Quake Live engine: load retail `cgamex86.dll`, `qagamex86.dll`, and `uix86.dll`, present the retail main menu, and interoperate with retail Quake Live server/platform flows. Quake Live-only online services remain behind `QL_BUILD_ONLINE_SERVICES`, default disabled, until an open replacement path exists.

## Recently closed

### Task 76: Client full parity audit and closure-plan publication [COMPLETED]
Priority: High
Files: `docs/reverse-engineering/client-full-parity-audit-and-implementation-plan-2026-04-09.md`, `IMPLEMENTATION_PLAN.md`, `AUDIT.md`
Parity estimate: **before 92% -> after 90%** (confidence correction; runtime behavior unchanged)

Completed work:

1. Re-audited the native `client` host against the committed retail `quakelive_steam.exe` HLIL/Ghidra corpus, the recent host mapping rounds, the launcher/browser notes, and the current writable source under `src/code/client`, `src/common/platform`, and the adjacent client-owned `common.c` seams.
2. Published a dedicated client parity document that separates the strong retained client/runtime story from the still-open Quake Live launcher/platform work, records the refreshed strict client estimate as **90%**, and turns the remaining debt into an explicit gap register (`CL-G01`..`CL-G05`) instead of leaving it spread across mapping rounds and top-level host notes.
3. Broke the remaining client closure work into six executable phases (`CL-P1`..`CL-P6`) covering retail config/bootstrap persistence, Steam callback lifecycle, workshop-aware download bootstrap, browser-host core reconstruction, JS/data/event publication, and a dedicated client parity gate plus runtime evidence lane.

### Task 75: Renderer strict retail-font-stack re-audit and closure-plan refresh [COMPLETED]
Priority: High
Files: `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `tests/test_renderer_full_parity_gate.py`, `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 98% -> after 94%** (confidence correction; runtime behavior unchanged)

Completed work:

1. Re-audited the renderer against the committed retail HLIL/Ghidra corpus, the tracked runtime evidence, and the dedicated retail font-stack note/audit, then corrected the strict renderer estimate from the earlier post-`RG-P6` public **98%** figure down to **94%** because the old estimate undercounted the unresolved retail text-host debt.
2. Expanded the renderer gap register beyond the old single open tranche `RG-G05`. The refreshed report now keeps `RG-G05` for classic `tr_font.c` proof work, adds `RG-G08` for the still-missing retail host FontStash text engine (`*fontstash`, `R_fonsErrorCallback`, direct host `DrawScaledText` / `MeasureText`), and adds `RG-G09` for the missing in-tree `src/code/ft2/` source lane plus unfinished strict text/debug-atlas validation.
3. Updated the machine-readable renderer parity gate and the top-level audit summaries so repo-wide status now reflects the refreshed strict renderer story instead of continuing to report that only the old font helper-family proof tranche remained.

### Task 74: Renderer parity-gate and runtime-evidence closure tranche [COMPLETED]
Priority: High
Files: `tests/test_renderer_full_parity_gate.py`, `tools/renderer/run_renderer_runtime_probe.ps1`, `.github/workflows/renderer-validation.yml`, `artifacts/renderer_validation/logs/renderer_full_parity_gate.json`, `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260409.json`, `docs/build-pipeline.md`, `docs/hud_render_baseline.md`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 98%** (`RG-P6` complete; `RG-G07` closed)

Completed work:

1. Added the unified renderer parity gate in `tests/test_renderer_full_parity_gate.py`, which writes `artifacts/renderer_validation/logs/renderer_full_parity_gate.json` and makes the current renderer gap register (`RG-G01`..`RG-G07`) machine-readable instead of leaving it only in prose.
2. Added the tracked Windows runtime probe at `tools/renderer/run_renderer_runtime_probe.ps1` and refreshed `artifacts/renderer_validation/logs/renderer_runtime_evidence_20260409.json`, which now records forced-windowed main-menu and live `bloodrun` captures, archived `qconsole.log` evidence, and process-bound window metadata for the current renderer milestone.
3. Wired the renderer validation surface into `.github/workflows/renderer-validation.yml`, updated the renderer audit/docs to point at the new gate and runtime artifact, and narrowed the remaining renderer gap register to the still-open font helper-family proof work.

### Task 73: Renderer internal helper-family ownership closure tranche [COMPLETED]
Priority: High
Files: `docs/reverse-engineering/quakelive_steam_mapping_round_100.md`, `docs/reverse-engineering/renderer-internal-helper-ownership-2026-04-09.md`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `tests/test_renderer_internal_helper_mapping_parity.py`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 93% -> after 96%** (`RG-P5` complete; `RG-G06` closed)

Completed work:

1. Rechecked the dense helper bands in `tr_backend.c`, `tr_bsp.c`, `tr_curve.c`, `tr_flares.c`, and `win_glimp.c` against the committed alias ledger, HLIL, Ghidra function starts, and prior renderer mapping rounds, then recorded that pass in `quakelive_steam_mapping_round_100.md`.
2. Published `renderer-internal-helper-ownership-2026-04-09.md` to bound the remaining file-local helpers explicitly as source-backed compatibility decompositions or compiler-shaped micro-splits beneath already-mapped runtime owners, instead of leaving those files in an open-ended missing-owner bucket.
3. Updated the renderer audit/summary documents and added `tests/test_renderer_internal_helper_mapping_parity.py` so the `RG-G06` file band stays closed unless a future change reopens a high-impact active-runtime ownership gap.

### Task 72: Renderer Win32 host-glue closure tranche [COMPLETED]
Priority: High
Files: `src/code/win32/win_glimp.c`, `src/code/win32/win_main.c`, `src/code/win32/win_syscon.c`, `src/code/win32/win_wndproc.c`, `src/code/win32/win_local.h`, `tests/test_renderer_win32_host_glue_parity.py`, `docs/renderer_cvar_matrix.md`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 90% -> after 93%** (`RG-P4` complete; `RG-G04` closed)

Completed work:

1. Restored the retail Win32 live client-rect sync seam in `win_wndproc.c`, so `WM_SIZE` / `WM_EXITSIZEMOVE` now re-read the retained windowed client rect, switch `r_windowedMode` to `-1`, refresh `r_windowedWidth` / `r_windowedHeight`, and queue `vid_restart fast` when the live window size changes.
2. Recovered the adjacent host-side resize behavior by adding the retail `WM_SIZING` constraint helper and by teaching `win_glimp.c` to preserve the retained maximized-window state across fast fullscreen->windowed restarts, instead of always dropping back to the plain GPL window style.
3. Added the shared loading-window wrapper family (`Sys_CreateLoadingWindow` / `Sys_DestroyLoadingWindow`) around the `Q3 WinConsole` class, wired the retail startup order into `win_main.c`, documented the missing-asset fallback for `splash.bmp`, and pinned the whole host-glue tranche with `tests/test_renderer_win32_host_glue_parity.py`.

### Task 71: Renderer post-process and color-correction closure tranche [COMPLETED]
Priority: High
Files: `src/code/renderer/tr_backend.c`, `src/code/renderer/tr_init.c`, `src/code/renderer/tr_local.h`, `tests/test_renderer_post_process_parity.py`, `docs/renderer_cvar_matrix.md`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 85% -> after 90%** (`RG-P3` complete; `RG-G03` closed)

Completed work:

1. Replaced the approximation-backed post-process layer with a shader-backed rectangle-texture/FBO pipeline keyed to the retail Quake Live shader family (`posteffect`, `brightpass`, `downsample1`, `blurvertical`, `blurhoriz`, `combine`, and `colorcorrect`) recovered from the committed HLIL corpus.
2. Removed the CPU `qglGetTexImage` color-correction path, restored backend-owned active-state mirroring for `r_postProcessActive` / `r_bloomActive` / `r_colorCorrectActive`, tightened `r_enableBloom` back to the retail `0/1` toggle contract, and registered the missing `r_contrast` surface consumed by the recovered color-correct shader.
3. Added `tests/test_renderer_post_process_parity.py` and refreshed the renderer audit/CVar notes so the post-process shader family, rectangle-texture copy path, active-mirror ownership, and recovered CVar surface are now pinned by focused parity checks.

### Task 70: Renderer memory-image and live resource-ingestion closure tranche [COMPLETED]
Priority: High
Files: `src/code/client/cl_main.c`, `src/code/client/cl_steam_resources.c`, `src/code/client/client.h`, `src/code/renderer/tr_image.c`, `src/code/renderer/tr_local.h`, `tests/test_renderer_memory_image_parity.py`, `tests/test_platform_services.py`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 81% -> after 85%** (`RG-P2` complete; `RG-G02` closed)

Completed work:

1. Restored the retail renderer memory-image helper family by introducing `R_CreateImageWithTarget`, `R_DetectImageTypeFromMemory`, `R_LoadImageFromMemory`, and the adjoining buffer-backed BMP/TGA/JPG/PNG decode cores in `tr_image.c`, with the public `R_CreateImage` entry point now wrapping the target-aware internal constructor.
2. Added explicit client compatibility wrappers (`CL_RegisterShaderFromRGBA` and `CL_RegisterShaderFromMemory`) so live image payloads can enter the renderer directly without claiming a new retail export slot, while still reusing the normal shader-registration path.
3. Rewrote the Steam/launcher resource bridge to stop writing temporary cache files purely to reach `re.RegisterShaderNoMip`; avatars now register directly from live RGBA data, launcher/browser image payloads now register through the new renderer memory-loader lane, and the static parity gates were updated to lock that path in place.

### Task 69: Renderer export-tail and font-contract closure tranche [COMPLETED]
Priority: High
Files: `src/code/client/cl_cgame.c`, `src/code/client/cl_main.c`, `src/code/client/cl_ui.c`, `src/code/client/client.h`, `src/code/renderer/tr_font.c`, `src/code/renderer/tr_init.c`, `src/code/renderer/tr_local.h`, `src/code/renderer/tr_public.h`, `src/code/renderer/tr_scene.c`, `tests/test_renderer_export_tail_parity.py`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`, `AUDIT.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 76% -> after 81%** (`RG-P1` complete; `RG-G01` closed, `RG-G05` narrowed)

Completed work:

1. Restored the retail renderer export-tail ABI by removing `RegisterFont` from `refexport_t`, inserting the no-argument `AdvertisementBridge_UpdateLoadingViewParameters` slot immediately after `RenderScene`, and reordering the `GetRefAPI` tail assignments to match the retail contract.
2. Moved UI/cgame font registration onto a dedicated client compatibility wrapper (`CL_RegisterFont`) so `R_RegisterFont` remains reachable through the proven syscall/native-import lanes without continuing to claim ownership of a retail renderer export slot.
3. Routed the loading-view bridge through the new renderer export seam, documented the remaining `tr_font.c` compatibility scaffolding explicitly, and added `tests/test_renderer_export_tail_parity.py` to pin the export order, the font registration lane, and the loading-view bridge dispatch.

### Task 68: Renderer full parity audit and closure-plan publication [COMPLETED]
Priority: High
Files: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/renderer-full-parity-audit-and-implementation-plan-2026-04-09.md`
Parity estimate: **before 74% -> after 76%** (confidence/documentation uplift; runtime behavior unchanged)

Completed work:

1. Performed a full renderer parity audit against the committed Quake Live host HLIL/Ghidra corpus, the existing renderer mapping rounds, and the current renderer-facing source tree across `src/code/renderer`, `src/code/win32`, and the adjacent client-side image/resource bridge.
2. Published a dedicated renderer closure-plan document that records the remaining gap register (`RG-G01`..`RG-G07`), including the retail export-tail ABI mismatch, missing in-memory image/target-aware texture path, approximation-backed post-process band, Win32 host-glue drift, font/internal-helper ownership gaps, and the missing renderer parity gate.
3. Broke the closure path into six executable renderer phases (`RG-P1`..`RG-P6`) with explicit deliverables, exit criteria, and projected parity uplift targets, so renderer parity can now be tracked and closed deliberately instead of through isolated mapping passes.

### Task 67: Qagame residual timer/debug/training tail closure [COMPLETED]
Priority: High
Files: `src/code/game/g_bot.c`, `src/code/game/g_local.h`, `tests/test_game_factory_regen_parity.py`, `tests/test_game_helper_seam_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 96% -> after 98%** (`QG-P6` complete)

`QG-G08`, `QG-G09`, and `QG-G10` from the dedicated qagame closure plan are now closed, which completes `QG-P6` and the qagame closure plan as a whole.

Completed work:

1. Finalized the adjacent factory-regen client-state naming so the split health/armor regen helpers now sit on explicitly named retail timer-side accumulators and pending latches instead of partially described layout placeholders.
2. Locked the recovered `ConsoleCommand` legacy debug/admin tail with focused seam coverage, keeping the dangerous `game_crash` path developer-gated while preserving the handled no-op tokens and the remaining safe helper routes.
3. Restored the dedicated `G_AddTrainerBot` bootstrap wrapper in the bot init flow so training maps now use the retail fixed `Trainer` / `5000 ms` / `loaddeferred` sequence rather than the older generic delayed spawn approximation.

### Task 66: Qagame queue sidecar and spawn-finalizer closure [COMPLETED]
Priority: High
Files: `src/code/game/g_client.c`, `src/code/game/g_main.c`, `src/code/game/g_session.c`, `src/code/game/g_local.h`, `src/game/ql_game_types.h`, `tests/test_game_tournament_queue_parity.py`, `tests/test_game_helper_seam_parity.py`, `tests/test_game_duel_ready_delay_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 93% -> after 96%** (tournament queue sidecar + spawn/loadout finalizer exactness; `QG-P5` complete)

`QG-G06` and `QG-G07` from the dedicated qagame closure plan are now closed, which completes `QG-P5`. The remaining open qagame parity work is the residual timer/debug/training tail grouped under `QG-P6`.

Completed work:

1. Restored the retail duel queue sidecar around a shared waiting-spectator eligibility helper so queue selection, queue sorting, and `teamtask` mirroring now exclude scoreboard/follow spectators and stay aligned with the published `rp` / `p` / `so` / `pq` configstring slab.
2. Recovered the session-side selected-spawn-weapon lane and wired it into `G_FinalizeSpawnLoadout`, so the spawn finalizer now latches retail fallback weapon choices back into the session block instead of hardwiring the generic factory default every spawn.
3. Moved the Red Rover infected override ahead of the generic finalizer, routed `G_RRResetClientForRound` back through `ClientSpawn`, and refreshed the focused queue/loadout parity fixtures plus the qagame mapping/closure docs to remove the remaining `QG-P5` caveats.

### Task 65: Qagame Red Rover strict controller recovery [COMPLETED]
Priority: High
Files: `src/code/game/g_active.c`, `src/code/game/g_client.c`, `src/code/game/g_local.h`, `src/code/game/g_main.c`, `tests/test_game_round_controller_helper_parity.py`, `tests/test_game_helper_seam_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 90% -> after 93%** (Red Rover strict controller/death-path closure; `QG-P4` complete)

`QG-G04` from the dedicated qagame closure plan is now closed, which completes `QG-P4`. The remaining open qagame parity work is focused on tournament queue/spawn-finalizer recovery (`QG-P5`) and the residual low-risk tails (`QG-P6`).

Completed work:

1. Rebuilt Red Rover around a dedicated internal `RR_ROUNDSTATE_*` lane so the controller now preserves the recovered `0..5` state split, pending-transition timers, infection seeding handoff, and delayed complete-state restart versus exit scheduling while still publishing the shared coarse `ROUNDSTATE_*` view.
2. Switched `G_RRCheckRoundCompletion` onto the caller-supplied counts contract and roundtimelimit gate recovered from HLIL, then routed both the death path and per-frame activity monitor through the same completion helper plus the delayed `1500 ms` / `3500 ms` post-round schedule.
3. Aligned `G_RRHandlePlayerDeath` with the recovered pre-mutation team interface, refreshed the RR parity fixtures around the new enum/helper surface and delayed-complete behavior, and updated the qagame mapping/closure docs to remove the remaining RR controller caveats.

### Task 64: Qagame scoreboard serializer-family closure [COMPLETED]
Priority: High
Files: `src/code/game/g_cmds.c`, `tests/test_game_nonteam_scoreboard_helper_parity.py`, `tests/test_game_compact_scoreboard_parity.py`, `tests/test_game_intermission_stats_parity.py`, `tests/test_game_team_scoreboard_header_parity.py`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 86% -> after 90%** (scoreboard/intermission serializer exactness; `QG-P3` complete)

`QG-G03` from the dedicated qagame closure plan is now closed, which completes `QG-P3`. The remaining open qagame parity work is focused on the deeper Red Rover controller/death-path tranche (`QG-G04`) and the later queue/spawn/residual tails.

Completed work:

1. Moved the duel scoreboard branch onto the same retail payload-builder contract used by the other scoreboard serializers, while preserving the viewer-specific pickup-timing visibility split and the cached low/high duel client ordering in the `level` tail.
2. Revalidated the existing rich, compact, team-family, and intermission-only scoreboard/stat publishers and locked the ordering under `DeathmatchScoreboardMessage` so `scorestats`, `scoreteam`, and the intermission-only stat publishers stay sequenced on the recovered retail path.
3. Refreshed the focused qagame/cgame scoreboard tests so compact `smscores`, duel serializer dispatch, helper-family decomposition, and intermission publisher ordering are all pinned together.

### Task 63: Qagame last-alive public alert transport closure [COMPLETED]
Priority: High
Files: `src/code/game/g_team.c`, `src/code/game/g_local.h`, `tests/test_game_helper_seam_parity.py`, `tests/test_cgame_event_transport_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 83% -> after 86%** (shared last-alive alert transport closure; `QG-P2` complete)

`QG-G02` from the dedicated qagame closure plan is now closed, which completes `QG-P2`. The remaining open qagame parity work is focused on scoreboard/intermission serializer recovery (`QG-G03`), the deeper Red Rover controller/death-path tranche (`QG-G04`), and the later queue/spawn/residual tails.

Completed work:

1. Moved ownership of the retail last-alive public alert into the shared `G_NotifyLastAlivePlayer` helper so it now emits the recovered `EV_GLOBAL_TEAM_SOUND` / `GTS_LAST_STANDING` temp entity before sending the lone-survivor centerprint.
2. Routed the A/D, Clan Arena, Freeze, and Red Rover mode-local last-alive wrappers through that shared helper after their mode/state/player-count gates, while leaving `GTS_SURVIVOR_WARNING` attached only to the separate Red Rover survival-bonus broadcast.
3. Tightened the focused qagame/cgame event fixtures so they now pin the shared helper boundary, the per-mode wrapper fan-in, and the existing `lastStandingSound` consumer.

### Task 62: Qagame Freeze round-resolution helper decomposition closure [COMPLETED]
Priority: High
Files: `src/code/game/g_active.c`, `src/code/game/g_client.c`, `src/code/game/g_main.c`, `src/code/game/g_local.h`, `tests/test_game_round_controller_helper_parity.py`, `tests/test_game_native_export_helper_parity.py`, `tests/test_game_helper_seam_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 80% -> after 83%** (Freeze helper decomposition and timeout-edge closure; `QG-P1` complete)

`QG-G05` from the dedicated qagame closure plan is now closed, which completes `QG-P1` as a whole. The remaining open controller-heavy qagame work is now the broader Red Rover machine/interface tranche `QG-G04`, not the shared round-controller core.

Completed work:

1. Fixed the remaining Freeze controller reentrancy hazard by keeping `Freeze_RoundStateTransition` on the raw controller latch while leaving the public `G_FreezeResolveRoundState` helper responsible for expired pending-transition servicing.
2. Cut off thaw accumulation and auto-thaw processing outside the active Freeze round, renamed the warmup-delay cvar update hook to the now-shared `G_RoundHandleWarmupDelayCvarUpdate`, and paused the Freeze-side thaw and spawn-protection timers across timeout resume deltas.
3. Tightened the focused qagame parity fixtures so they now pin the Freeze winner-resolution ordering, the thaw-cutoff edge, the shared warmup-delay rescheduler, the timeout-paused Freeze client timers, and the relocated Red Rover resolver boundary.

### Task 61: Qagame round-controller helper exactness closure [COMPLETED]
Priority: High
Files: `src/code/game/g_active.c`, `src/code/game/g_client.c`, `src/code/game/g_cmds.c`, `src/code/game/g_freeze.c`, `src/code/game/g_team.c`, `src/code/game/g_main.c`, `src/code/game/g_local.h`, `tests/test_game_round_controller_helper_parity.py`, `tests/test_game_native_export_helper_parity.py`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`, `IMPLEMENTATION_PLAN.md`
Parity estimate: **before 78% -> after 80%** (controller helper/readback closure; deeper RR and Freeze decomposition work remains open)

`QG-G01` from the dedicated qagame closure plan is now closed. This task landed the first half of `QG-P1`; the Freeze-side follow-up was completed separately in Task 62, while the deeper Red Rover controller machine and death-path interface still remain under `QG-G04`.

Completed work:

1. Restored standalone Clan Arena, Freeze, and Red Rover pending-transition resolvers, exported the new helper surface through `g_local.h`, and routed the affected CA/FZ/RR helper callers plus the Freeze thaw-progress visibility export through those readback helpers instead of raw `level.roundState`.
2. Added a dedicated Clan Arena controller transition lane, shared CA/Freeze pending-exit latching, and timeout-pause coverage for round-controller timers so deciding-round roundlimit/timelimit/mercylimit checks now evaluate after the score update instead of before it.
3. Aligned Freeze active-round timeout resolution with the committed HLIL living-count and living-health tiebreak path, refreshed the qagame mapping/closure-plan notes, and tightened the focused controller/native-export parity regressions around the recovered helper boundaries.

### Task 60: UI final runtime confirmation closure [COMPLETED]
Priority: High
Files: `src/code/cgame/cg_main.c`, `tools/packaging/ui_bundle_manifest.json`, `scripts/ui/retail_ui_corpus.py`, `tests/test_ui_menu_files.py`, `tests/test_ui_src_panel_parity.py`, `tests/test_cgame_displaycontext_parity.py`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`, `docs/build-pipeline.md`, `docs/ui/scripting-guide.md`, `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`
Parity estimate: **before 97% -> after 100%** (runtime evidence and packaging closure)

`UI-P6` from the dedicated UI closure plan is now closed. The remaining work was no longer about source reconstruction alone; it was about proving that the rebuilt UI bundle, cgame runtime, and disabled-service fallback layer held up in a real windowed retail-style session.

Completed work:

1. Fixed the last live runtime blockers for the audited UI flows by staging retail runtime roots correctly inside `pak_uiql.pk3` (`icons/`, `menu/icons/`, `levelshots/`) and by aligning cgame cursor registration with committed retail evidence (`ui/assets/3_cursor3.tga` instead of the non-retail `selectcursor` path).
2. Hardened the retail corpus materializer so manifest-scope changes refresh the cached extracted corpus instead of silently reusing a stale subset, then rebuilt the UI bundle and refreshed the live `cgamex86.dll` and `pak_uiql.pk3` runtime artifacts.
3. Captured a new final runtime evidence set at `artifacts/ui_validation/logs/ui_runtime_evidence_20260406.json`, covering main menu, ingame HUD, spectator, scoreboard, vote flow, and in-game menu states with matching process-bound window captures, supporting logs, and an all-green unified UI parity gate.

### Task 59: UI unified parity gate closure [COMPLETED]
Priority: High
Files: `tests/test_ui_full_parity_gate.py`, `.github/workflows/ui-validation.yml`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`, `docs/ui/scripting-guide.md`, `docs/build-pipeline.md`, `docs/reverse-engineering/ui-strings-assets-audit.md`
Parity estimate: **before 92% -> after 97%** (verification and evidence-gating closure; runtime behavior unchanged)

`UI-P5` from the dedicated UI closure plan is now closed. The repo no longer relies on reviewers to infer UI parity state by hand from separate menu tests, overlay manifests, bundle logs, and headless validation output.

Completed work:

1. Added `tests/test_ui_full_parity_gate.py`, which aggregates the current UI gap register (`UI-G01`..`UI-G06`) into one machine-readable report at `artifacts/ui_validation/logs/ui_full_parity_gate.json`, records per-tranche pass or fail or blocked status, and exposes an opt-in strict release mode through `UI_FULL_PARITY_GATE_ENFORCE=1`.
2. Wired the gate into `.github/workflows/ui-validation.yml` after bundle generation and headless validation so CI now publishes a unified tranche-level UI status artifact instead of leaving the parity result fragmented across independent logs.
3. Updated the UI workflow docs and parity plan so contributors know where the unified gate artifact lives, how to run it locally, and why the current non-passing tranches still resolve explicitly to the remaining missing-corpus and bundle-reproducibility gaps rather than to generic test failures.

### Task 58: UI qmenu widget-core ownership-boundary closure [COMPLETED]
Priority: High
Files: `tests/test_ui_menu_files.py`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/ui-qmenu-struct-layouts.md`, `docs/reverse-engineering/ui-mapping-round-2026-04-01.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 86% -> after 92%** (runtime ownership-confidence closure; asset parity unchanged)

`UI-P4` from the dedicated UI closure plan is now closed. The committed retail corpus still does not expose stable standalone owners for the inner qmenu widget-core helper family, but that ambiguity no longer needs to sit in the active gap register as an open runtime risk.

Completed work:

1. Re-ran the targeted qmenu/widget-core ownership pass against the committed HLIL and Ghidra evidence and confirmed the same negative result for `Menu_AddItem`, `Menu_Draw`, `Menu_DefaultKey`, `MField_Draw`, and `ScrollList_Key`: no new alias promotion met the repository's two-signal threshold.
2. Converted the qmenu mapping notes from open-ended uncertainty into an explicit confidence-bounded ownership matrix, recording that the active retail-owned dispatcher/runtime slab above these leaves is already mapped and that the remaining helper family should stay source-backed until stronger retail evidence appears.
3. Added a structural regression that locks the closure language across the qmenu note, the mapping round summary, and the UI parity plan so future edits cannot silently reopen `UI-G04` without updating the documented evidence position.

### Task 57: UI disabled-service menu fallback closure [COMPLETED]
Priority: High
Files: `src/code/ui/ui_main.c`, `src/code/ui/ui_shared.c`, `tests/test_ui_menu_files.py`, `tests/test_platform_services.py`, `.github/workflows/ui-validation.yml`, `docs/ui/scripting-guide.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 80% -> after 86%** (service-disabled menu routing and verification closure; asset parity unchanged)

`UI-P3` from the dedicated UI closure plan is now closed. The remaining disabled-service gap was not the engine-side browser stubs themselves; it was that retail menu scripts reached those verbs through `exec web_*`, bypassing the UI-side fallback logic and leaving part of the offline menu flow implicit instead of explicit.

Completed work:

1. Added a writable UI-side `exec` interception seam so disabled-overlay builds now catch retail `web_showBrowser` and `web_changeHash` script verbs before they hit the inert host stubs, routing the retail main-menu open path into `ql_bridge_browser` when bridge scripts are available and otherwise surfacing a native `error_popmenu` fallback instead of a silent dead end.
2. Kept in-game disabled-service control flow deterministic by swallowing `web_changeHash` and non-main `web_showBrowser` calls locally when the overlay is unavailable, preserving the native companion panels already opened by the read-only menu scripts (`ingame_about`, join controls, settings surfaces) rather than letting the UI depend on live browser services.
3. Added focused structural coverage for the disabled-service routing matrix plus the connect-screen and advertisement wait-screen paths, and widened the UI validation workflow so CI now runs the menu/service parity tests alongside the overlay parity checks.

### Task 56: UI overlay-first runtime strategy closure [COMPLETED]
Priority: High
Files: `scripts/ui/write_retail_ui_overrides.py`, `tests/test_ui_src_panel_parity.py`, `tests/fs_searchpath_harness.c`, `tests/test_fs_search_paths.py`, `.github/workflows/ui-validation.yml`, `docs/ui/scripting-guide.md`, `docs/reverse-engineering/ui-strings-assets-audit.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 72% -> after 80%** (overlay packaging and verification closure; runtime menu logic unchanged)

`UI-P2` from the dedicated UI closure plan is now closed. The repo now treats the overlay as a first-class, testable runtime layer rather than a best-effort side artifact.

Completed work:

1. Hardened `scripts/ui/write_retail_ui_overrides.py` so the overlay manifest now records deterministic per-file size and SHA-256 data, the active drift file list, explicit overlay policy metadata, and stale-file cleanup evidence whenever old overlay entries are removed.
2. Tightened `tests/test_ui_src_panel_parity.py` so CI pins the repo to either the current known `src/ui` drift set or a future approved zero-drift state, and added a synthetic overlay test that verifies hash output plus stale-file cleanup proofs without depending on the local retail corpus checkout.
3. Extended the filesystem search-path harness and `tests/test_fs_search_paths.py` to prove the supported runtime contract directly: a `pak_ui_src_retail_overlay.pk3` layer mounted from `fs_homepath` outranks the lower-priority base UI bundle and `FS_FOpenFileRead` logs the overlay package as the winning source for drift targets.
4. Wired the UI overlay parity test into the UI validation workflow trigger surface and refreshed the overlay policy docs so contributors mount the overlay from `fs_homepath` instead of relying on same-directory PK3 ordering.

### Task 55: UI retail corpus preflight and inventory closure [COMPLETED]
Priority: High
Files: `scripts/ui/retail_ui_corpus.py`, `scripts/ui/check_retail_ui_corpus.py`, `scripts/ui/write_retail_ui_overrides.py`, `tools/build_ui_bundle.sh`, `tests/conftest.py`, `tests/test_ui_src_panel_parity.py`, `tests/test_ui_menu_files.py`, `docs/ui/scripting-guide.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 68% -> after 72%** (deterministic corpus validation, inventorying, and verification uplift; runtime behavior unchanged)

`UI-P1` from the dedicated UI closure plan is now closed. The retail corpus is still absent in this checkout, but the repo no longer hard-fails ambiguously when that happens: the missing-corpus path is now explicit, machine-readable, and bundled into the normal UI tooling.

Completed work:

1. Added shared retail corpus validation and inventory helpers plus the `scripts/ui/check_retail_ui_corpus.py` entry point, which validates the manifest-tracked `baseq3` inputs and writes the deterministic `artifacts/ui_bundle/ui_retail_inventory.json` snapshot.
2. Routed `tools/build_ui_bundle.sh` through the new preflight so bundle generation now reports all missing required retail inputs in one pass before packaging instead of dying on the first missing file, and refreshed the overlay manifest path so the override generator carries the same corpus-availability status.
3. Updated the UI panel-drift tests and the one retail-backed menu test to run in strict compare mode only when the retail corpus exists, while emitting actionable skip/warn behavior when it is absent and still asserting the new preflight/reporting path.

### Task 54: Qagame full parity audit and closure-plan publication [COMPLETED]
Priority: High
Files: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 76% -> after 78%** (confidence/documentation uplift; runtime behavior unchanged)

Completed work:

1. Performed a full `qagame` parity audit against the committed HLIL/Ghidra references, the live `qagame` mapping ledger, and the current gameplay/transport seams in writable source.
2. Published a dedicated qagame closure plan document that enumerates the full remaining gap register (`QG-G01`..`QG-G10`) and ties each gap to evidence-backed retail helper families (round controllers, alerts, score serializers, Red Rover, tournament queue, spawn/loadout, and timer-layout tails).
3. Broke the closure path into six execution phases (`QG-P1`..`QG-P6`) with explicit exit criteria and tranche-by-tranche parity uplift targets, so qagame parity can be closed deterministically instead of by ad-hoc mapping passes.

### Task 53: UI full parity audit and closure-plan publication [COMPLETED]
Priority: High
Files: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, `docs/reverse-engineering/ui-full-parity-audit-and-implementation-plan-2026-04-05.md`
Parity estimate: **before 68% -> after 70%** (confidence/documentation uplift; runtime behavior unchanged)

Completed work:

1. Performed a full `ui` parity audit against the committed HLIL/Ghidra references, the current source/runtime UI surfaces, and the focused UI test/bundle suite.
2. Published a dedicated closure plan document that enumerates the current UI gap register (`UI-G01`..`UI-G06`), execution phases, acceptance criteria, and tranche-by-tranche parity targets from 68% to 100%.
3. Broke the closure path into small executable backlog tasks (`UI-P1`..`UI-P6`) so UI parity can be tracked and closed incrementally under repository constraints (read-only `src/ui`, service gating behind `QL_BUILD_ONLINE_SERVICES`).

### Task 52: Cgame browser leaf-owner closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_main.c`, `src/code/cgame/cg_local.h`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-A3` was the last open writable `cgame` lane. The runtime surface, parser/bootstrap seam, focus/hover owners, and simple browser verbs were already source-owned, but the remaining draw/control/script/capture leaves still only existed implicitly under the shared `ui_shared.c` runtime.

Completed work:

1. Restored the remaining browser leaf-owner wrappers in `cg_newdraw.c` for list metrics, fade/transition/orbit and advert verbs, overlay activation/cinematic shutdown, multi/preset/bind/slider/text/model draw leaves, and the remaining control-key or capture helpers while preserving the shared `ui_shared.c` implementations underneath.
2. Routed the browser widget draw dispatcher through the new cgame-owned leaf painters and exported the preset/layout refresh plus overlay-activation bridge so the live open path in `cg_main.c` now re-enters cgame owners instead of calling `Menus_OpenByName` directly.
3. Extended `tests/test_cgame_displaycontext_parity.py` to pin the remaining browser owner surface directly, including the new cross-file helper exports and the widget draw dispatcher.
4. Closed `CG-A3`, the broader `CG-A` lane, and the last open writable `cgame` lane in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`.

### Task 51: Cgame browser runtime surface closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_draw.c`, `src/code/cgame/cg_screen.c`, `src/code/cgame/cg_local.h`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-A1` still carried the last behavioral browser-runtime gap after the earlier parser, overlay, focus, and simple-script slices landed. The writable source already had the bootstrap wrappers and focused-overlay helpers, but the live draw path still painted browser roots through raw `Menu_Paint*` calls and the key path still skipped the captured-overlay hit test that retail `Display_HandleKey` performs before falling back to the focused root.

Completed work:

1. Added explicit cgame-owned runtime wrappers in `cg_newdraw.c` for captured-overlay lookup, out-of-bounds click dispatch, widget-state allocation, root or widget frame paint, per-root draw dispatch, and the top-level browser overlay frame pump.
2. Updated `cg_draw.c` and `cg_screen.c` so cached overlays, scoreboard/stats menus, the spectator `joingame_menu`, and the generic HUD browser pass now route through `CG_DrawBrowserOverlayTree` or `CG_DrawBrowserOverlays` instead of painting through raw `Menu_Paint*` calls.
3. Tightened the browser parity regression in `tests/test_cgame_displaycontext_parity.py` so the new runtime surface is pinned directly: captured-overlay key dispatch, cgame-owned widget allocation and draw wrappers, the cached-overlay and join-game draw callsites, and the replacement of the raw `Menu_PaintAll()` browser pass in `CG_Draw2D`.
4. Closed `CG-A1` in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, leaving only the direct-owner follow-up tranche `CG-A3` open in the browser lane.

### Task 50: Cgame Red Rover survival-bonus broadcast closure [COMPLETED]
Priority: Low
Files: `src/code/game/g_client.c`, `tests/test_cgame_event_transport_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-C2` was down to one retail-backed Red Rover seam. Freeze thaw transport, the `EV_INFECTED` single-recipient temp entity, and the cgame-side `GTS_SURVIVOR_WARNING` consumer were already in place, but qagame still deferred the matching survival-bonus broadcast instead of emitting the recovered retail global-team-sound payload.

Completed work:

1. Replaced the stale deferred-broadcast comment in `g_client.c::G_RRApplySurvivalBonus` with the retail `G_BroadcastGlobalTeamSound( vec3_origin, GTS_SURVIVOR_WARNING, -1, TEAM_BLUE, 0 )` emit path immediately before `CalculateRanks()`.
2. Extended `tests/test_cgame_event_transport_parity.py` so the Red Rover survival-bonus helper is now pinned to the survivor print plus the retail `EV_GLOBAL_TEAM_SOUND` payload, and the client-side `GTS_SURVIVOR_WARNING` consumer remains locked to `survivorWarningSound`.
3. Refreshed `docs/reverse-engineering/qagame-mapping.md` and `docs/reverse-engineering/cgame-mapping.md` so both sides now record the same `EV_GLOBAL_TEAM_SOUND` / `GTS_SURVIVOR_WARNING` / `TEAM_BLUE` evidence chain for the survival-bonus alert.
4. Closed `CG-C2` and the broader `CG-C` lane in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, leaving `CG-A1` as the only remaining open cgame lane.

### Task 49: Cgame browser runtime-state and simple script-owner closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_newdraw.c`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The browser lane still had one compact ownership-only seam immediately below the earlier overlay wrappers: cgame had named focus and hover leaves, but the rect-hit, script-runner, cvar-gating, widget-lookup, item show-hide, and simple browser verb helpers were still implicit in shared UI calls instead of preserved as direct retail owners.

Completed work:

1. Restored the cgame-owned browser runtime helpers in `cg_newdraw.c` for rect hit tests, name or group matching, widget lookup, script dispatch, enable/show cvar gating, and named item visibility, keeping the verified `ui_shared.c` helpers underneath where the retail bodies are still shared.
2. Rebuilt the local `CG_SetBrowserFocus`, `CG_BrowserMouseEnter`, and `CG_BrowserMouseLeave` bodies on top of those owners so the live browser focus and hover seam no longer collapses straight through `Item_SetFocus`, `Item_MouseEnter`, or `Item_MouseLeave`.
3. Added the adjacent simple browser command owners `CG_BrowserScriptShow`, `CG_BrowserScriptHide`, `CG_BrowserScriptOpen`, `CG_BrowserScriptConditionalOpen`, `CG_BrowserScriptClose`, `CG_BrowserScriptToggle`, and `CG_BrowserScriptSetFocus`, then locked the whole slice in `tests/test_cgame_displaycontext_parity.py` and the browser parity ledger as `CG-A3b`.

### Task 48: Freeze temp-entity event-band validation refresh [COMPLETED]
Priority: Low
Files: `tests/test_game_native_export_helper_parity.py`, `tests/test_cgame_event_transport_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/qagame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-C2` still carried a stale Freeze-side compatibility note after the direct temp-entity payload work landed. The writable source already used the recovered `EV_THAW_PLAYER`, `EV_THAW_TICK`, and `EV_INFECTED` paths, but the focused regressions and parity ledgers still left the Freeze thaw-band closure under-specified on the cgame side.

Completed work:

1. Refreshed `tests/test_game_native_export_helper_parity.py` so the Freeze visibility helper now guards the live `ET_EVENTS + EV_THAW_TICK` boundary instead of the removed synthetic alias, and updated the adjacent native-import-count assertions to the current `GAME_LEGACY_IMPORT_COUNT` / `GAME_NATIVE_IMPORT_COUNT` contract already present in source.
2. Added cgame-side structural coverage in `tests/test_cgame_event_transport_parity.py` and extended `docs/reverse-engineering/cgame-mapping.md` so the thaw-complete and thaw-progress consumers are tracked explicitly on the client side rather than only in qagame notes.
3. Corrected `docs/reverse-engineering/qagame-mapping.md` so the Freeze thaw-progress note now records the real `EV_THAW_TICK` band and the Red Rover death-path note now refers to the retail `EV_INFECTED` single-recipient temp entity rather than the retired `QL_EV_INFECTED` wording.
4. Narrowed `CG-C2` in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` by closing the Freeze thaw-band sub-slice and leaving the open event-band work focused on the still-deferred Red Rover survival-bonus broadcast and related later consumers.

### Task 47: Cgame browser overlay and focus direct-owner closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_main.c`, `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_screen.c`, `src/code/cgame/cg_local.h`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The open `CG-A` lane still had a compact ownership-only slice beneath the broader browser-runtime gap: the shared menu runtime already carried the verified overlay lookup, open-close, preset refresh, focus, hover, and cursor-walk behavior, but cgame still lacked the direct owners that the retail map names around that seam and still reached a few live callers through raw `Menus_*ByName` helpers.

Completed work:

1. Restored the cgame-owned browser boundary wrappers in `cg_main.c` and `cg_newdraw.c` for overlay lookup/open-close, preset-label refresh, widget-position refresh, focus clear-set, hover state, mouse-move dispatch, and previous-next cursor walking while deliberately keeping the verified `ui_shared.c` bodies underneath instead of cloning the full browser runtime.
2. Routed the live cgame consumers through those owners by moving the scoreboard-selection cache to `CG_FindBrowserOverlayByName` and by switching the spectator `joingame_menu` open-close seam in `cg_screen.c` over to `CG_FindBrowserOverlayByName`, `CG_OpenBrowserOverlayByName`, and `CG_CloseBrowserOverlayByName`.
3. Extended `tests/test_cgame_displaycontext_parity.py` and refreshed the browser parity notes so this direct-owner tranche is tracked as closed under `CG-A3a`, while the broader behavioral browser-runtime lane `CG-A1` stays open.

### Task 46: Cgame playerstate and prediction transition validation closure [COMPLETED]
Priority: Low
Files: `tests/test_cgame_snapshot_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-C3` still had one remaining validation-only seam after the direct event-payload cleanup landed. The writable source already looked retail-aligned in `cg_playerstate.c` and `cg_predict.c`, but the parity ledger still lacked focused coverage for the transition ordering, reward gating, crosshair-hit latch, and the final prediction handoff back into `CG_TransitionPlayerState`.

Completed work:

1. Extended `tests/test_cgame_snapshot_parity.py` to cover the remaining retail-backed transition chain: the prediction interpolation fallbacks, the snapshot-side non-predicted `CG_TransitionPlayerState` gate, `CG_CheckPlayerstateEvents`, `CG_RecordCrosshairHitFeedback`, `CG_CheckLocalSounds`, and the final `CG_TransitionPlayerState` ordering.
2. Revalidated against the committed retail mapping notes that the source still preserves the `( armor >> 6 ) + 1` crosshair-hit bucket clamp, the client-follow teleport/reset and respawn gates, the non-intermission/non-spectator local-sound gate, and the final ammo/event/duck transition order after the direct event-payload cleanup.
3. Refreshed `docs/reverse-engineering/cgame-mapping.md` and `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` so `CG-C3` is tracked as closed, leaving only the later event-band realignment `CG-C2` open in the `CG-C` lane.

### Task 45: Cgame retail event payload slot alignment [COMPLETED]
Priority: Medium
Files: `src/code/game/q_shared.h`, `src/code/qcommon/msg.c`, `src/code/game/g_utils.c`, `src/code/game/g_combat.c`, `src/code/game/g_client.c`, `src/code/game/g_main.c`, `src/code/game/g_team.c`, `src/code/game/g_weapon.c`, `src/code/cgame/cg_event.c`, `tests/test_cgame_event_transport_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-C1` still carried the last source-era entity-state bridges after the damage-plum helper landed. The writable source was close behaviorally, but qagame and cgame were still routing single-recipient temp entities and global-team-sound payloads through the old GPL field choices instead of the recovered retail offsets shown in HLIL.

Completed work:

1. Restored the recovered retail payload slots across the shared `entityState_t` seam by reusing the matching `0x5C`, `0x94`, `0xAC`, `0xB0`, `0xC0`, and `0xC4` offsets already present in the source layout and by adding the missing `0xE0` `retailEventData` slot plus message serialization.
2. Updated qagame emitters so `EV_DAMAGEPLUM`, `EV_INFECTED`, `EV_AWARD`, and every `EV_GLOBAL_TEAM_SOUND` producer publish recipient, award, weapon, tracked-client, team, and point/index data through those recovered retail slots instead of the older `clientNum`, `eventParm`, `otherEntityNum`, and `generic1` bridge fields.
3. Tightened `cg_event.c` and `tests/test_cgame_event_transport_parity.py` so cgame now reads the retail payload slots directly, and refreshed the cgame parity ledgers so `CG-C1` is tracked as closed while only the later event-band realignment and follow-up validation notes remain open.

### Task 44: Cgame placement metric ownerdraw direct-owner closure [COMPLETED]
Priority: Low
Files: `src/code/cgame/cg_newdraw.c`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining Appendix B placement-owner gap had narrowed to retail ownership rather than missing behavior. The shared placement metric builder was already backed by the recovered score and scorestats transports, but the ping, total accuracy, per-weapon, pickup, and medal scorebox slots still collapsed through the generic metric path instead of preserving the retail direct-owner wrappers.

Completed work:

1. Restored the remaining retail-named placement scorebox wrappers in `cg_newdraw.c` for ping, total accuracy, per-weapon frag/hit/shot/damage/accuracy, pickup counts and averages, and medal totals, with the recovered ping warning tint thresholds preserved in the dedicated ping owner.
2. Routed `CG_DrawPlacementMetricOwnerDraw` through those direct owners while keeping `CG_DrawPlacementMetricTextOwnerDraw` as the verified shared text builder underneath, so the visible scorebox behavior stays on the retail transport but the ownership split now matches the retail map.
3. Added focused structural coverage in `tests/test_cgame_displaycontext_parity.py` and refreshed the cgame mapping plus parity-plan ledgers so the last non-browser Appendix B placement-owner tranche is tracked as closed.

### Task 43: Cgame client-info context refresh validation [COMPLETED]
Priority: Low
Files: `src/code/cgame/cg_predict.c`, `src/code/cgame/cg_snapshot.c`, `src/code/cgame/cg_servercmds.c`, `tests/test_cgame_snapshot_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-C3` still had one narrow validation seam after the source-side refresh queue landed: the focused parity coverage and ledger did not yet describe how follow/team context changes, local-player configstring updates, and snapshot handoff now share the same deferred model-override refresh path.

Completed work:

1. Locked the prediction-side `CG_UpdateClientInfoContext` queue behavior and the snapshot-side `CG_RefreshClientInfoContext` handoff in `tests/test_cgame_snapshot_parity.py`, including the local-player `CS_PLAYERS` configstring route through `cg_servercmds.c`.
2. Revalidated that the refresh seam only re-enters `CG_ApplyModelOverrides` and `CG_LoadDeferredPlayers` on snapshot transition instead of rebuilding every client slot inline or forcing immediate refreshes from `CG_QueueClientInfoContextRefresh`.
3. Refreshed `docs/reverse-engineering/cgame-mapping.md` and `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` so this client-info refresh sub-slice is tracked as closed under `CG-C3`, while the remaining staged event-transport bridges stay open.

### Task 42: Cgame browser parser wrapper closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_main.c`, `src/code/cgame/cg_local.h`, `src/code/ui/ui_shared.h`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

`CG-A2` had narrowed into an ownership problem instead of a missing behavior implementation. The shared menu runtime already carried the exact keyword-hash and parser bodies retail maps under the browser seam, but cgame still reached them only indirectly through `String_Init()` and `Menu_New()`, leaving the browser bootstrap surface impossible to track as a cgame-owned parity slice.

Completed work:

1. Added explicit cgame-owned wrapper owners for browser overlay init, item/menu keyword-hash setup, and item/menu parse entry points while keeping the verified shared `ui_shared.c` implementations underneath instead of cloning that parser logic.
2. Routed the cgame menu-loader path through those wrapper owners when opening `menudef` blocks, and re-entered the shared keyword-hash builders through `CG_InitBrowserRuntime` so the browser bootstrap seam is explicit at the cgame boundary.
3. Tightened the focused browser parity tests and refreshed the cgame mapping plus parity-plan ledger so `CG-A2` is tracked as closed as a deliberate shared-runtime reuse seam, while the broader browser behavior lane `CG-A1` remains open.

### Task 41: Cgame damage-plum transport closure [COMPLETED]
Priority: Medium
Files: `src/code/game/g_combat.c`, `src/code/cgame/cg_event.c`, `tests/test_cgame_event_transport_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The open `CG-C1` lane still carried one compact but user-visible transport gap: qagame was publishing `EV_DAMAGEPLUM` through the older entity-event path, so cgame had to guess the weapon from predicted state and keep a GPL `eventParm` fallback instead of consuming the retail temp-entity payload directly.

Completed work:

1. Restored the retail-style `G_AddDamagePlum` helper in `g_combat.c`, publishing `EV_DAMAGEPLUM` as a single-recipient temp entity for the attacking client and staging the damage in `s.time` plus the translated retail weapon in `s.weapon`.
2. Tightened `cg_event.c` so `CG_GetRetailDamagePlumDamage` and `CG_GetRetailDamagePlumWeapon` consume those staged retail fields directly instead of falling back to GPL `eventParm` transport or predicted-weapon state.
3. Added focused structural coverage in `tests/test_cgame_event_transport_parity.py` and refreshed the cgame parity ledgers so the damage-plum branch is tracked as closed while the remaining `CG-C1` recipient/global-team-sound bridges stay open.

### Task 40: Cgame competitive scorebox direct-owner closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_newdraw.c`, `tests/test_cgame_spectator_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining competitive-HUD Appendix B gap was no longer behavioral uncertainty; HLIL already separated the local/team score wrapper and the two duel status labels, but the current source still folded those ownerdraws through generic helpers. That left the visible behavior close to retail while still missing the direct owner split carried by the retail function map.

Completed work:

1. Restored the direct `CG_DrawScoreValue` wrapper in `cg_newdraw.c` and routed `CG_PLAYER_SCORE`, `CG_RED_SCORE`, and `CG_BLUE_SCORE` through it.
2. Restored `CG_DrawSpectatorPrimaryStatus` and `CG_DrawSpectatorSecondaryStatus`, with a shared builder that chooses `LEADS`, `TRAILS`, `TIED`, `READY`, or `NOT READY` from the retail duel/intermission conditions instead of the older generic `"Ready"` / `"-"` fallback.
3. Added focused structural coverage in `tests/test_cgame_spectator_parity.py` and refreshed the cgame parity ledgers so the Appendix B direct-owner trio is tracked as closed.

### Task 39: Cgame identity-backed social mute closure [COMPLETED]
Priority: Low
Files: `src/code/cgame/cg_consolecmds.c`, `src/code/cgame/cg_main.c`, `src/code/cgame/cg_servercmds.c`, `src/code/client/cl_cgame.c`, `tests/test_cgame_scoreboard_social_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `CG-E2` note had become stale. The writable source already carried the native cgame mute imports and the host-side identity set, but the parity ledger and the focused social regression still described the older client-slot mute toggle fallback as if the private callback seam were missing.

Completed work:

1. Revalidated the retail social mute path and confirmed `CG_ClientMute_f` now forwards the recovered identity words through `trap_QL_ToggleClientMute`, while the scoreboard and chat consumers refresh their per-slot cache via `trap_QL_IsClientMuted`.
2. Tightened `tests/test_cgame_scoreboard_social_parity.py` so it guards the identity-backed cgame wrapper, the scoreboard/chat mute lookups, and the host-side `cl_cgame.c` muted-identity import slab instead of the removed local toggle behavior.
3. Refreshed `docs/reverse-engineering/cgame-mapping.md` and `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, marked `CG-E2` complete, and closed the `CG-E` lane now that the last social sidecar fallback note is gone.

### Task 38: Cgame identity transport sidecar closure [COMPLETED]
Priority: Low
Files: `src/code/cgame/cg_main.c`, `tests/test_cl_console_cgame_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `CG-E1` gap was not a missing producer implementation in the writable source; it was an unresolved assumption risk around the copied transport discriminator in `CG_CopyClientIdentity`. Retail clearly copies the word at `0x10A42400`, but the committed cgame/player parser evidence only rebuilds the adjacent identity-word pair plus avatar cache, and the recovered host overlay consumer only branches on the low or high identity words.

Completed work:

1. Made the observed retail ABI explicit in `cg_main.c` by zeroing `identityTransport` inside `CG_CopyClientIdentity` while keeping the recovered identity-word pair and display or clean-name copies intact.
2. Tightened `tests/test_cl_console_cgame_parity.py` so the identity export contract is guarded directly and the existing native tail-slot assertions match the retained wrapper form already used by `vmMain`.
3. Refreshed `docs/reverse-engineering/cgame-mapping.md` and `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` so `CG-E1` is tracked as closed on the strength of the committed corpus instead of an invented transport enum.

### Task 37: Cgame teamsize player-count transport closure [COMPLETED]
Priority: Medium
Files: `src/code/game/g_main.c`, `src/code/cgame/cg_servercmds.c`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-mapping.md`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The last open `CG-B1` gap was no longer the player-count math itself; it was the live transport. Retail cgame carries `teamsize` and `g_teamSizeMin` string anchors in `CG_ParseServerinfo`, but the current source still depended on a best-effort dual-key lookup while qagame never published a live serverinfo-facing teamsize value. That left the intro/status ownerdraw cap vulnerable to drifting stale after admin or vote-driven teamsize changes.

Completed work:

1. Added a serverinfo-facing `teamsize` legacy alias for `g_teamSizeMin` in `g_main.c`, so the existing runtime now republishes live teamsize changes through the transport cgame already expects without promoting `g_teamSizeMin` itself into the public serverinfo slab.
2. Tightened `CG_ParseServerinfo` in `cg_servercmds.c` to consume the live `teamsize` key directly instead of carrying the older best-effort `teamsize` then `g_teamSizeMin` fallback path.
3. Extended `tests/test_cgame_displaycontext_parity.py` to lock the new qagame alias and the single-key cgame parser seam, then refreshed `docs/reverse-engineering/cgame-mapping.md` and `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` so `CG-B1` and the `CG-B` lane are tracked as closed.

### Task 36: Cgame player-cylinder configstring transport closure [COMPLETED]
Priority: Medium
Files: `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The open `CG-B1` lane had drifted into a mixed note: the shared player-count cap is still only a best-effort serverinfo reconstruction, but the player-cylinder toggle already had committed retail transport evidence on both sides. The local `cg_servercmds.c` seam now reads `CS_PLAYER_CYLINDERS` directly, so the remaining parity work was to lock that boundary in tests and split the ledger so the still-unresolved player-count cap transport stands alone.

Completed work:

1. Added a focused structural regression in `tests/test_cgame_displaycontext_parity.py` that requires `CG_ParsePlayerCylindersConfigString` to read `CS_PLAYER_CYLINDERS`, mirror the parsed toggle through `cg_playerCylinders`, and re-enter from both `CG_SetConfigValues` and `CG_ConfigStringModified`.
2. Locked out the older `CG_ParseServerinfo` fallback by asserting the `g_playerCylinders` serverinfo key and its direct `cg_playerCylinders` mirror are no longer present in that parser.
3. Split the parity ledger in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` so the player-cylinder transport is tracked as closed under `CG-B1a`, while `CG-B1` now only covers the still-open player-count cap key recovery.

### Task 35: Cgame client-preview direct-owner closure [COMPLETED]
Priority: Low
Files: `src/code/cgame/cg_newdraw.c`, `src/code/cgame/cg_players.c`, `tests/test_cgame_ownerdraw_text_parity.py`, `tests/test_cgame_displaycontext_parity.py`, `tests/test_cgame_announcer_timer_helper_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `CG-E4` slice had narrowed to two mapped retail owner names that the source still carried only as merged internals: the player-preview draw leaf under the first-place/tracked-player widgets, and the packed torso/dead-body color leaf inside the shared player render seam.

Completed work:

1. Rebuilt `CG_DrawClientModelPreview` in `cg_newdraw.c` as the retail boxed 3D preview scene beneath the first-place and tracked-player wrappers, including the tagged legs/torso/head assembly, attached weapon or barrel, optional grapple ammo, and the preview-only light pair, while retaining the profile-icon fallback only for missing model data.
2. Restored `CG_ResolveClientModelColorBytes` in `cg_players.c` so the torso/dead-body packed RGBA path has a direct retail owner before the broader per-part color application continues into the existing legs/head helpers.
3. Updated the focused parity tests and closure notes so `CG-E4` now records the real retail-style preview reconstruction instead of a placeholder icon-wrapper description, without changing the higher-priority social transport status.

### Task 34: Cgame Attack and Defend round-scoreboard owner parity closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_draw.c`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `CG-B3` gap had narrowed to one retail-owned HUD seam: `CG_DrawADRoundScoreboard`. The dedicated `scores_ad` parser was already present in `cg_servercmds.c`, and the source already had a named warmup-panel helper in `cg_draw.c`, but that owner still needed the retail `0x10011A90` geometry tightened before the bookkeeping could honestly close.

Completed work:

1. Tightened `CG_DrawADRoundScoreboard` in `cg_draw.c` to the recovered retail warmup-panel geometry: the 240x48 background, the active-team label slab, the active-round cell highlight, the centered 10-column round-history strip, and the corrected score-column placement.
2. Updated the focused structural regression in `tests/test_cgame_displaycontext_parity.py` so it locks the recovered `Round` / `Red` / `Blue` / `Score` strip, the active highlight slabs, the retained `Match Point` / `Last Chance` / `Red Wins! Good Game` status seam, and the warmup-panel callsite.
3. Refreshed `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` to describe the retail panel geometry explicitly while keeping `CG-B3` closed and `CG-B`'s remaining direct-owner appendix entry at `None`.

### Task 33: Cgame world-item respawn timer parity closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_ents.c`, `src/code/cgame/cg_main.c`, `src/code/cgame/cg_local.h`, `src/code/game/g_items.c`, `tests/test_cgame_displaycontext_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `CG-D2` gap had narrowed to one retail draw seam that the current source still lacked as a named owner: `CG_DrawItemRespawnTimer`. The queued-world-marker trio was already present in `cg_draw.c`, but cgame still needed the timer media family, the early `CG_Item` callsite, and qagame-backed respawn duration transport to close the slice cleanly.

Completed work:

1. Registered the retail `gfx/2d/timer/*` shader family in cgame, including the item icons plus the `slice5` / `slice7` / `slice12` / `slice24` wedge variants and their `_current` overlays.
2. Restored `CG_DrawItemRespawnTimer` in `cg_ents.c`, wired `CG_Item` through it before the later `cg_skipItems` or `EF_NODRAW` exits, and kept a narrow stock-duration fallback so older emitters still land on the retail 25/35/60/120-second item buckets.
3. Published respawn deadline or duration state from qagame through `entityState_t.time` and `time2`, added a focused structural regression in `tests/test_cgame_displaycontext_parity.py`, and marked `CG-D2` closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`.

### Task 32: `bg_misc` pickup seam closure [COMPLETED]
Priority: Low
Files: `tests/bg_misc_validation_harness.c`, `tests/test_bg_misc_validation_fixtures.py`, `tests/test_bg_misc_runtime_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining `BG-B` work was explicitly a validation and boundary-bookkeeping problem rather than an identified behavior hole: the source already carried the mapped pickup helpers, but the ledger still lacked enough executable proof to treat the merged shared-item seam as closed.

Completed work:

1. Added a dedicated `bg_misc` C harness that exercises `BG_FindItemForPowerup`, `BG_PlayerTouchesItem`, and `BG_CanItemBeGrabbed` without dragging in the full game runtime.
2. Expanded the focused pytest fixtures to validate the invulnerability-holdable remap, the full Team Arena rune and team-flag lookup routes, normal-versus-flag pickup reach, dropped-self weapon lockout timing, owned-weapon/ammo-pack gating, small-health and megahealth upper bounds, and representative CTF team-item pickup rules.
3. Marked both `BG-B1` and `BG-B2` closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, documenting that the current `BG_FindItemForPowerup` / `BG_PlayerTouchesItem` / `BG_CanItemBeGrabbed` family is now treated as a verified deliberate merge until a later retail diff proves otherwise.

### Task 31: Cgame POI width-clamp parity closure [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_draw.c`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, `tests/test_cgame_poi_parity.py`

The POI lane still carried one open behavioral note even though the hidden retail cvar names, defaults, and the width-falloff window were already recoverable from HLIL. The remaining gap was that the source still described the clamp as an approximation and had no focused guard against those constants drifting.

Completed work:

1. Rechecked the hidden POI cvar registrations against HLIL and confirmed the retail defaults remain `cg_poiMinWidth = 16.0` and `cg_poiMaxWidth = 32.0`.
2. Confirmed the source keeps the same recovered `256..768` linear width falloff in `CG_POIMarkerSizeForOrigin` and updated the source note to treat that seam as exact instead of approximate.
3. Added a focused structural regression test and marked `CG-D1` closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`.

### Task 30: Cgame armor-tiered configstring parity closure [COMPLETED]
Priority: Medium
Files: `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, `docs/reverse-engineering/cgame-mapping.md`, `tests/test_cgame_displaycontext_parity.py`

The direct source-owned `CG_ParseArmorTieredConfigString` parser had already landed in `cg_servercmds.c`, but the parity ledger still tracked the slice as open and the mapping note still described that helper as absent from the current source tree.

Completed work:

1. Confirmed `CG_ParseArmorTieredConfigString` remains a dedicated retail parser boundary in `cg_servercmds.c`, reading `CS_SERVER_SETTINGS_INFO_A`, mirroring the toggle through `cg_armorTiered`, and routing through both `CG_SetConfigValues` and `CG_ConfigStringModified`.
2. Added a focused structural regression test so the armor-tiering toggle does not drift back into `CG_ParseServerinfo` or broader server-settings parsing.
3. Marked `CG-B4` closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` and corrected the stale mapping note in `docs/reverse-engineering/cgame-mapping.md`.

### Task 29: Step-jump and public step-slide boundary validation [COMPLETED]
Priority: Medium
Files: `tests/test_step_jump_gate_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

The remaining open `BG-A` work after the air-control fix was not a behavioral hole so much as a bookkeeping problem: the source keeps the retail step or jump seam merged into local wrappers, while the retail binary still exposes adjacent leaves and the public one-argument `PM_StepSlideMove` boundary.

Completed work:

1. Tightened the step-jump surface checks so the configurable `PM_StepSlideMoveWithStepHeight` helper is explicitly verified to stay private to `bg_slidemove.c` while all public callers still go through the classic `PM_StepSlideMove( qboolean gravity )` seam.
2. Recorded the existing runtime fixtures around supported or unsupported air-step probing, crouch-step takeoff, and the rechecked general step-jump gate as the closure evidence for the merged source path.
3. Marked `BG-A2` and `BG-A3` closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`, which closes the `BG-A` lane as a whole.

### Task 28: PQL/CPMA air-control retail parity validation [COMPLETED]
Priority: High
Files: `src/code/game/bg_pmove.c`, `tests/test_pmove_air_control_runtime_parity.py`, `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md`

Retail HLIL still needed one more pass on the Quake Live alternate air-control bundle: the source carried the right constants, but the reverse-air steering path and the regression surface around bundle selection, wishspeed clamp, and double-jump reuse were not yet proven end to end.

Completed work:

1. Corrected `PM_AirControl` so the planar-speed rescale survives the non-positive dot path, matching the retail CPM-style helper instead of collapsing reverse-air movement to unit speed.
2. Added an executable movement harness in `tests/test_pmove_air_control_runtime_parity.py` that validates retail bundle promotion from stock settings, preservation of non-stock overrides, air-stop accel on reverse input, pure-strafe `wishSpeed` clamp, and the one-shot air double-jump path.
3. Marked the `BG-A1` slice as closed in `docs/reverse-engineering/cgame-bg-parity-implementation-plan.md` now that the remaining behavioral delta is resolved and regression-covered.

### Task 20: Match-flow configstring parity [COMPLETED]
Priority: High
Files: `src/code/game/g_match_state.c`, `src/code/game/g_main.c`, `src/code/game/g_spawn.c`, `src/code/cgame/cg_servercmds.c`, `src/code/cgame/cg_draw.c`, `src/code/cgame/cg_scoreboard.c`, `src/code/cgame/cg_newdraw.c`

Retail HLIL showed dedicated configstring handling for sudden-death and ready-up state that the repo only partially mirrored.

Completed work:

1. Published `CS_SUDDENDEATH_STATUS` from qagame.
2. Parsed `CS_SUDDENDEATH_STATUS`, `CS_READYUP_STATUS`, and `CS_WARMUP_READY` in cgame.
3. Routed ready-up deadline and warmup readiness counts into the warmup overlay.
4. Switched HUD sudden-death state to the runtime flag instead of the spawn-delay configuration flag.

### Task 25: Cgame particle module parity cleanup [COMPLETED]
Priority: Medium
Files: `src/code/cgame/cg_marks.c`, `src/code/cgame/cg_particles.c`, cgame build manifests

Retail HLIL shows a compact client particle subsystem: a 1024-slot arena, an `explode1`-only animation registry, and a `CG_ParticleExplosion` path that seeds animated rocket sprites at half-alpha. The repo had drifted into a split state where the compiled runtime lived in `cg_marks.c` while the standalone `cg_particles.c` copy carried older Wolf-style expansion data that was not wired into the build.

Completed work:

1. Removed the duplicate particle runtime block from `cg_marks.c` and restored `cg_particles.c` as the compiled owner across the cgame build manifests.
2. Reduced the shader animation registry to the retail-backed `explode1` entry and restored the 1024-particle arena size recorded in HLIL.
3. Aligned `CG_ParticleExplosion` with the retail alpha and case-insensitive animation lookup behavior used by the rocket explosion path.

### Task 26: Native game-module import/export parity [COMPLETED]
Priority: Critical
Files: `src/code/qcommon/vm.c`, `src/code/client/cl_cgame.c`, `src/code/client/cl_ui.c`, `src/code/server/sv_game.c`, `src/code/cgame/*`, `src/code/game/*`, `src/code/ui/*`, platform DLL loaders, export-validation tooling

Retail Quake Live native DLLs do not use the legacy `vmMain` numbering directly. They expose a structured `dllEntry` handshake plus recovered native export-slot layouts that differ from the old Q3 VM ABI.

Completed work:

1. Recovered and named the native export-slot tables for `cgame`, `qagame`, and `ui` without renumbering the legacy `vmMain` enums.
2. Restored the structured Quake Live `dllEntry(exports, imports, apiVersion)` seam in the module-side source and platform DLL loaders.
3. Updated native dispatch so engine `VM_Call` numbers map onto the recovered retail export-slot order instead of indexing `dllExports` directly.
4. Split native import-table dispatch from legacy syscall-contract logging so source-built native DLL traffic no longer looks like old VM syscall traffic.
5. Added export-manifest validation and runtime verification proving the rebuilt engine loads source-built native `ui`, `qagame`, and `cgame` DLLs on the normal startup and map paths.

### Task 27: Qagame Red Rover infection-mode reconstruction [COMPLETED]
Priority: Medium
Files: `src/code/game/g_active.c`, `src/code/game/g_client.c`, `src/code/game/g_cmds.c`, `src/code/game/g_local.h`, `src/code/game/g_main.c`, `src/code/game/g_team.c`

Retail HLIL still diverged from the source Red Rover infection path on the core team-role split, the carryover infected-slot bookkeeping, and the private infection notification flow.

Completed work:

1. Restored the retail infection-team orientation so `TEAM_RED` is the infected side and `TEAM_BLUE` remains the survivor side across spawn, autojoin, and round seeding.
2. Reconstructed the carryover infected-slot latches used by Red Rover seeding and `SetTeam`, including the retail-style round-start reseed back to one promoted infected client.
3. Restored the retail `EV_INFECTED` temp-entity cue plus the death-path `ClientUserinfoChanged` refresh when survivors are converted.
4. Reused the shared last-man-standing centerprint helper for Red Rover infection rounds and aligned the global infection-spread countdown ordering with the retail helper chain.
5. Reconstructed the retail survival-bonus timer/forced-award helper, including the preserved per-round timer state, survivor-only bonus prints, and the score-only rank refresh path.
6. Restored the Red Rover round-complete team-score increment and the delayed complete-state split between next-round restart and the retail tie-aware timelimit/roundlimit exit gate.
7. Mirrored the remaining registered retail Red Rover cvars on the qagame side: `g_rrDeathScorePenalty`, `g_rrInfectedZombieFragBonus`, and `g_rrInfectedZombieHealthBonus`.

## Current highest-priority open work

### Task 21: Native launcher/platform host reconstruction [OPEN]
Priority: Critical
Primary areas: `src/code/client/`, `src/code/qcommon/`, platform bridge layers

The largest remaining parity gap is still the retail `quakelive_steam.exe` host stack. The source tree lacks direct reconstruction for:

1. Steam-backed platform/bootstrap services.
2. Web/Awesomium-style navigation and resource bridge behavior.
3. Launcher-to-engine state publication used by retail menus and platform flows.
4. Strict compatibility validation against retail game DLLs and their exact runtime assumptions, not just the reconstructed source-built DLLs.

Short-term goal:

- identify the smallest vertical slice that removes a real retail behavior gap without requiring a full browser runtime

Completed in this task:

1. Reconstructed the Steam avatar vertical slice in the writable host layers by adding direct SteamFriends/SteamUtils avatar extraction, `steam://avatar/...` resource synthesis for the client-side image cache, and the native cgame avatar-handle bridge used by retail scoreboards and player cards.
2. Reconstructed the mapped advertisement-bridge activation/state seam in the writable host layers by replacing the inert UI/cgame advert callbacks with client-side bridge bookkeeping and by routing advert-cell fallback shaders through the existing Steam resource cache so `steam://` advert content reaches the renderer through the same host path as other Quake Live Steam-backed UI assets.
3. Reconstructed the mapped Steam overlay and manual workshop command surface in the writable host layers by restoring `clientviewprofile` / `clientfriendinvite` through player `steamid` configstrings plus `ActivateGameOverlayToUser`, and by restoring the `steam_downloadugc`, `steam_subscribeugc`, and `steam_unsubscribeugc` operator commands through shared SteamUGC wrapper helpers.
4. Reconstructed the mapped Steam lobby bootstrap and adjacent social wrapper seam in the writable host layers by restoring `lobby_autoconnect`, `steam_maxLobbyClients`, and `connect_lobby` in the client host, and by adding shared SteamMatchmaking/SteamFriends/SteamUserStats wrappers for lobby create/join/chat/invite/user-stats flows.
5. Reconstructed the mapped Steam rich-presence/connect handoff seam in the writable host layers by adding the shared SteamFriends `SetRichPresence` wrapper, restoring the retail main-menu `status = "At the main menu"` bootstrap write, and adding the client-owned rich-presence join and game-server-change handoff helpers that route through the immediate `connect` path and password cvar.
6. Reconstructed the mapped Steam lobby control and game-start status seam in the writable host layers by adding shared SteamMatchmaking wrappers for `LeaveLobby` and owner-gated `SetLobbyServer`, and by restoring the retail `status = "Playing a match"` rich-presence transition on the first active client snapshot.
7. Reconstructed the mapped Steam game-server frame seam in the writable host layers by adding shared `SteamGameServer` heartbeat/public-IP wrappers and routing `SV_Frame` through the existing `SV_SteamServerNetworkingFrame` owner instead of the client callback pump.
8. Reconstructed the mapped Steam game-server bootstrap identity seam in the writable host layers by adding the shared `SteamGameServer` get-SteamID wrapper, restoring `sv_referencedSteamworks` plus the `0x2CA` / `0x2CB` server SteamID publication path in `SV_SpawnServer`, and restoring heartbeat enable/disable ownership in `SV_SpawnServer` / `SV_Shutdown`.
9. Reconstructed the mapped Steam game-server metadata publication seam in the writable host layers by adding the shared `SteamGameServer` `SetKeyValue` wrapper, restoring the spawn-time serverinfo publication path in `SV_SpawnServer`, and restoring the dirty-`CVAR_SERVERINFO` Steam republish order in `SV_Frame`.
10. Reconstructed the mapped Steam game-server bootstrap hostname/account seam in the writable host layers by restoring the Steam persona-based `sv_hostname` default path, registering `sv_setSteamAccount`, and adding shared `SteamGameServer` wrappers for the dedicated, logon, product, and game-dir bootstrap slots.
11. Reconstructed the mapped Steam game-server published-state seam in the writable host layers by adding shared `SteamGameServer` wrappers for game description, max slots, bot count, server/map name, passworded state, single-key rule writes, and per-player Steam user-data publication, then restoring the `SteamServer_UpdatePublishedState` owner across `SV_SpawnServer` and `SV_Frame`.
12. Reconstructed the mapped Steam game-server game-tags seam in the writable host layers by registering `sv_tags`, adding the shared `SteamGameServer` `SetGameTags` wrapper, and restoring the cvar-owned retail tag builder for gametype, cheats, instagib, gravity, vampiric, infected, quadhog, and appended custom `sv_tags` values.
13. Reconstructed the mapped Steam game-server init/UGC ownership seam in the writable host layers by adding shared `SteamGameServer_Init` / `SteamGameServer_Shutdown` / init-state wrappers, moving the one-time dedicated/logon/product/game-dir bootstrap into `common.c` startup/shutdown ownership, and selecting `SteamGameServerUGC` for dedicated-server workshop calls while the retail game-server path is active.
14. Reconstructed the mapped `net_restart` host lifetime seam in the writable engine layers by promoting the common Steam game-server bootstrap helper for shared use and restoring the retail restart order of Steam game-server shutdown, Win32 network reconfiguration, and common-owner Steam game-server reinitialization.
15. Reconstructed the host-side native return-contract seam by normalizing `GAME_CLIENT_CONNECT` denial strings into engine-owned storage across direct connect, map restart, and spawn-time reconnect owners, and by tightening `UI_usesUniqueCDKey()` to treat any non-zero native return as `qtrue`.
16. Reconstructed the adjacent native `qboolean` return-contract band by normalizing UI/cgame/server console-command query owners and the `UI_IS_FULLSCREEN` draw gate so non-zero native returns become explicit `qtrue` values in the host.
17. Reconstructed the adjacent native `qboolean` argument-contract band by normalizing the `UI_INIT` in-game flag, the `CG_DRAW_ACTIVE_FRAME` demo flag, and the shared UI/cgame key-event `down` fanout into explicit `qboolean` values before the host dispatches into native modules.
18. Reconstructed the central native VM/export `qboolean` contract seam in `vm.c` by normalizing the documented UI, cgame, and qagame boolean args/results at the host dispatch boundary instead of forwarding raw int-sized truth values through the native export switch.
19. Reconstructed the strict native loader export-table validation seam in `vm.c` by checking the recovered structured DLL slot counts for `ui`, `cgame`, and `qagame`, rejecting missing required export pointers up front while preserving the observed retail null cgame slot.
20. Reconstructed the central native import/syscall `qboolean` contract seam by normalizing documented UI, cgame, and qagame boolean args/results inside `CL_UISystemCallsImpl`, `CL_CgameSystemCallsImpl`, and `SV_GameSystemCallsImpl` instead of forwarding raw int-sized truth values into engine-side handlers.
21. Reconstructed the strict native import-slab surface for `ui` and `cgame` by zero-filling their Quake Live native import tables, preserving explicit recovered retail rows and the documented source-only compatibility tail, and leaving unrecovered retail gaps null instead of masking them behind a generic stub.
22. Reconstructed the module-side native syscall `qboolean` contract seam by normalizing documented UI, cgame, and qagame boolean args/results inside `ui_syscalls.c`, `cg_syscalls.c`, and `g_syscalls.c` instead of leaving the public DLL trap surface to rely on raw integer truthiness.
23. Reconstructed the cgame native export tail return-contract seam by routing the chat-field and speaking-state tail slots through explicit integer-contract wrappers in `cg_main.c` and tightening `vm.c` to consume those slots as integer returns instead of relying on float/pointer ABI coercion across the native export boundary.
24. Reconstructed the UI native key-event export contract seam by routing both `vmMain` and `UI_NATIVE_EXPORT_KEY_EVENT` through an explicit retained `key/down/time` wrapper in `ui_main.c` and tightening `vm.c` to normalize the `down` flag instead of calling a two-argument helper through a raw three-int ABI cast.
25. Reconstructed the remaining module-side native export `qboolean` adapter seam by routing the UI init/connect-screen slots, the cgame draw/key slots, and the qagame init/shutdown/client-connect slots through explicit retained wrappers so both `vmMain` and the recovered export tables publish the same normalized boolean and pointer contracts the host already dispatches.
26. Reconstructed the retail launcher/resource-interceptor fallback seam by routing launcher URI reads through the existing `fs_webpath` / screenshot rewrite owner in `files.c`, preserving `web.pak` priority in `cl_webpak.c`, and extending the cached URI shader bridge so `steam://`, HTTP-like, and screenshot-backed launcher resources share one retained cache path in `cl_steam_resources.c`.
27. Reconstructed the retail browser cache/reload registration seam by restoring the `web_zoom = "100"` and `web_console = "0"` cvar surface from `QLWebHost_RegisterCommands`, and by routing `web_clearCache` / `web_reload` through retained URI-cache invalidation instead of leaving them as log-only browser stubs.
28. Reconstructed the retail Steam client auth-ticket lifetime seam by adding the missing `CancelAuthTicket` platform wrapper, retaining the issued client ticket handle in `ql_auth.c`, and cancelling that handle from `CL_Disconnect` so disconnect and error cleanup no longer leave the retail ticket lifetime owner absent from writable source.
29. Reconstructed the remaining source-side cgame native import wrapper seam by exposing the recovered retail-only cvar, filesystem, advert, text, mirror, mute, and avatar helpers through `cg_syscalls.c` / `cg_local.h`, matching the existing engine-side native import slab without inventing new legacy Q3 syscall numbers.

Remaining work after Task 26:

1. Validate the engine against the retail `cgamex86.dll`, `qagamex86.dll`, and `uix86.dll` binaries and document any import or return-value mismatches that still only work for source-built DLLs.
2. Close any residual ownership, restart, or lifetime differences in native module calls where retail binaries may expect stricter host behavior than the reconstructed source currently exercises.
3. Reconstruct the launcher/bootstrap/platform surfaces needed for retail main-menu flow, server-browser flow, and network or auth hand-off behavior.
4. Keep UI/menu compatibility work focused on engine-side tolerance and writable bridge layers because the retail asset/UI stack is still missing and `src/ui/` remains read-only.

### Task 22: UI/menu asset and compatibility remediation [OPEN]
Priority: High
Primary areas: engine-side UI compatibility and documentation

Fresh runtime verification still reports many missing retail UI assets plus `ui/hud.menu` compatibility warnings.

Constraints:

- `src/ui/` is read-only
- retail menu/assets cannot be reconstructed by freely editing the UI VM tree in this repo

Actionable work:

1. Improve engine-side tolerance for retail menu constructs where possible.
2. Audit which missing assets are true parity blockers versus harmless warnings.
3. Document the runtime-visible gaps that remain because the retail UI asset stack is absent.

Completed in this task:

1. Restored the retail native UI export-table seam in the writable engine/UI surface by adding `UI_RefreshDisplayContext`, `Menus_AnyVisible`, `UI_ForEachArenaName`, and `UI_DrawAdvertisementWaitScreen` parity helpers outside the read-only `src/ui/` tree.
2. Restored the missing source-side `UI_CDKeyMenu` wrapper layer in `src/code/ui/ui_cdkey.c`, wiring the legacy public entry points back to the generated bridge credential menu and re-adding the missing `ui.q3asm` source manifest plus `ui.vcxproj` source entry.
3. Restored the retail `UI_ConsoleCommand` wrappers for `listPlayerModels`, `menu_open`, and `menu_close` in the writable `src/code/ui/` runtime surface.
4. Restored the retail-only `UI_CROSSHAIR_COLOR` and `UI_VOTESTRING` ownerdraw paths in `src/code/ui/ui_main.c`, including the numbered crosshair-color palette control.
5. Restored the retail `UI_STARTING_WEAPONS` ownerdraw path in `src/code/ui/ui_main.c`, including the loadout-mask icon strip and queued-primary preview sourced from `CS_LOADOUT_MASK` and `cg_weaponPrimaryQueued`.
6. Restored the retail advert compatibility seam in the writable UI runtime by adding `cellId`/`defaultContent` parsing, `activateAdvert`, advert-cell shader setup or refresh helpers, and the `UI_ADVERT` draw path outside the read-only `src/ui/` tree.
7. Restored retail item-level `font` compatibility in the writable UI runtime by adding `ItemParse_font`, explicit item font buckets, and font-aware text measurement or paint callbacks so the read-only Quake Live menu scripts no longer depend on GPL-era scale heuristics alone.
8. Restored the retail `toggle` script command in the writable UI runtime by mirroring the named-menu open or close branch recorded in the retail script command table and HLIL.
9. Aligned the retail `setplayermodel` and `setplayerhead` script handlers with the mapped `model` and `headmodel` cvar targets instead of the older GPL team-model cvars.
10. Restored the retail `precision`, `cvara`, `cvarInt`, `cvarPreset`, and `cvarPresetList` parser/runtime slice in the writable UI runtime, including preset-list synchronization, preset application, slider-color dispatch, and precision-aware cvar text formatting for the read-only Quake Live option menus.
11. Restored the retail `UI_SERVER_SETTINGS` ownerdraw in the writable UI runtime, consuming the currently mirrored `CS_SERVERINFO`, `CS_PMOVE_SETTINGS`, and `CS_CUSTOM_SETTINGS` surfaces for gametype, limit, movement, Instagib, and modified-weapon panel rows while leaving the undocumented retail `0x2A9` / `0x2AA` configstring backend as the remaining gap.
12. Restored the retail `UI_NEXTMAP` ownerdraw in the writable UI runtime by fetching the undocumented `0x29A` next-map configstring slot first and falling back to the mirrored `CS_ROTATION_TITLES` payload or cached rotation metadata until the exact backend publisher is recovered.
13. Restored the native `uix86.dll` project seam for `Debug|Win32` and `Release|Win32` by wiring `ui.def` back into the linker settings and re-enabling the native UI source set so the built DLL exports `vmMain` and `dllEntry` instead of linking as a near-empty stub.
14. Closed the native UI loader-validation gap by fixing the full-source `ui_main.c` / credential-bridge compile blockers so the engine now loads `build\win32\Debug\bin\baseq3\uix86.dll` directly during the normal windowed validation pass instead of rejecting it and falling back to the retail asset DLL.
15. Restored the retail `backgroundSize`, `cvarTest2`/`3`/`4`, `showCvar2`/`3`/`4`, and `hideCvar2`/`3`/`4` parser/runtime slice in the writable UI runtime, and widened the shared menu item bank so the shipped read-only Quake Live menus no longer desync after the old 96-item ceiling is exceeded.
16. Removed the source-only startup `gameinfo.txt` bootstrap from `_UI_Init` and added a bounded `UI_LoadBestScores` guard so missing retail `gameinfo.txt` assets no longer degrade into `games/(null)_0.game` / `demos/(null)_0.dm_*` filesystem probes during validated UI startup.
17. Closed the retail `UI_SERVER_SETTINGS` backend gap by reconstructing the `0x2A9` / `0x2AA` info-string publishers, replacing the old source-only `g_customSettings` bit walk with the retail mask layout, and aligning the writable UI ownerdraw with the recovered rows and Race icon suppression rules.
18. Removed the source-only `VM_CallNativeExports(ui)` trace spam from the engine VM bridge and aligned the writable UI `ui_browserAwesomium` registration default with the build-disabled online-services policy so validated startup logs no longer report a local cvar default mismatch.
19. Restored the retail `CG_DrawTeammatePOIs` seam in `src/code/cgame/cg_draw.c` by projecting visible teammates through the classic HUD path, clamping the name or location slab with the retail `..` trim behavior, and appending the recovered health, armor, flag, powerup, and task markers backed by the existing cgame status surfaces.
20. Restored the retail same-team crosshair target vitals seam in `CG_DrawCrosshairNames`, including the `0/1/2` `cg_drawCrosshairTeamHealth` mode behavior, the `0.26` name scale, and the centered `health / armor` readout driven by `cg_drawCrosshairTeamHealthSize`.
21. Reconstructed the retail fixed `CG_DrawTeamInfo` slab in `src/code/cgame/cg_draw.c`, restoring the top-anchored 16px icon cadence, 22px row step, clipped name and location text, carry and task icons, and health or armor bar presentation with a bounded score-row fallback when the team-info transport is absent.
22. Restored the classic lower-right `CG_DrawPowerups` / `CG_DrawLowerRight` seam in `src/code/cgame/cg_draw.c`, rebuilding the retail 3-second powerup popup around the mirrored `cg.powerupActive` and `cg.powerupTime` fields, the `%i:%i%i` timer text, the `x%i` stacked-powerup suffix, and the lower-right `cg_drawTeamOverlay == 2` branch.
23. Restored the retail classic-HUD `CG_DrawSpeedometer` seam in `src/code/cgame/cg_draw.c`, adding the 128-sample speed history ring, the recovered graph-mode split, and the numeric speed label ahead of the legacy lower-right stack while keeping the existing ownerdraw text helper intact.
24. Restored the retail classic-HUD `CG_DrawInputCmds` seam across `src/code/cgame/cg_draw.c`, `src/code/game/q_shared.h`, `src/code/qcommon/msg.c`, and `src/code/game/g_active.c`, mirroring the live or followed command bytes into `playerState_t`, serializing them through the snapshot delta stream, and drawing the recovered `gfx/2d/race/cmd_*` arrow slab ahead of the classic speedometer.
25. Added a committed Ghidra-readable UI reference header plus a separate `uix86` machine-generated source-recreation export path under `references/reverse-engineering/ghidra/uix86/`, keeping Ghidra output out of the hand-authored `src-re/ui/` workspace while preserving the symbol-map-driven rename workflow.

### Task 23: Ownerdraw/stat payload completion and validation [IN PROGRESS]
Priority: High
Primary areas: `src/code/game/`, `src/code/cgame/`, runtime validation harnesses

Large parts of the scorestats and ownerdraw pipeline are already in place. Remaining work is focused on the last retail-aligned payload details and keeping runtime fixtures honest.

Open subtasks:

1. [x] Finish the high-confidence per-player/per-team field mappings that were still using placeholders or reduced proxy shapes in `PLAYER_STATS`, including `MAX_STREAK`, the nested `DAMAGE` object, the broader retail pickup taxonomy, `ITEM_TIMING`, flag-color pickup counts, `HOLY_SHITS`, `TEAM_JOIN_TIME`, the retail `WIN` / `LOSE` outcome fields, aborted-rank sentinels, and removal of the source-only `TIMEHELD` object.
2. Compare additional runtime captures against retail-aligned expectations where HLIL alone is ambiguous.
3. Keep the debug-ownerdraw assertion path current as payload shape evolves.

## Secondary work

### Task 24: Gameplay validation sweep [OPEN]
Priority: Medium
Primary areas: physics, race, gametype-specific rules

The movement and gameplay code is no longer the top parity risk, but it still needs targeted retail validation.

Subtasks:

1. [x] Validate Attack & Defend round-controller parity against retail HLIL and the `qagame` symbol mapping after the latest gameplay-side changes.
2. [x] Restore the recovered retail award-configstring block and the init-side spawn-point count helper after the follow-up qagame parity pass.
3. Re-run focused Race checks after major gameplay-side changes.
4. Continue verifying match-flow sequencing against HLIL whenever state-machine code changes.
5. [x] Capture the shared `pmove` regressions with focused tests instead of relying on broad manual inspection, including jump timing, circle-strafe friction, step-jump gating, unsupported air-step suppression, and double-jump reuse.

### Task 25: Qagame behavioral parity closure execution [COMPLETED]
Priority: High
Primary areas: `src/code/game/*`, qagame↔cgame transport boundaries, focused gameplay fixtures

The dedicated qagame audit and plan in `docs/reverse-engineering/qagame-full-parity-audit-and-implementation-plan-2026-04-05.md` is now fully closed. The remaining qagame work is no longer in the active gap register; it is runtime verification and lower-confidence annotation cleanup.

Completed subtasks:

1. Executed `QG-P1` through `QG-P6` and closed the full `QG-G01`..`QG-G10` gap register.

### Task 30: Source-built game-module residual parity closure [COMPLETED]
Priority: High
Primary areas: `tools/build_ui_bundle.py`, `tools/build_ui_bundle.sh`, `tests/test_ui_src_panel_parity.py`, parity docs
Parity estimate: **before 99.5% -> after 100%** (`GM-P3` and `GM-P4` complete; `GM-G05` closed)

The refreshed combined audit in `docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-09.md` now shows the source-built module layer at a fully green baseline. `GM-P1` through `GM-P4` are complete: the shared native-wrapper seam passes `tests/test_platform_services.py` (`41 passed`), cgame is `170 passed`, qagame is `91 passed, 5 skipped`, UI is `49 passed, 6 skipped`, and the tracked UI parity-gate artifact reports `overall_status: pass`.

This task only closes the source-built DLL lane. Strict retail-facing module
parity is tracked separately under Task 31.

Completed work:

1. Added a portable Python UI bundle runner at `tools/build_ui_bundle.py`, kept the existing Python corpus/overlay/font tools as the build source of truth, and converted `tools/build_ui_bundle.sh` into a thin compatibility shim.
2. Updated the clean-artifact rebuild parity test to call the portable entry point directly, which closes the Windows Microsoft-Bash-launcher failure mode without changing bundle contents.
3. Rebuilt the bundle artifacts, reran the full four-command module validation set, refreshed the UI full-parity gate artifact to `pass`, and closed the module-layer residual gap register.

### Task 31: Strict retail game-module parity closure [COMPLETED]
Priority: High
Primary areas: `src/code/cgame/*`, `src/code/game/*`, `src/code/ui/*`, `src/code/client/*`, `src/code/server/*`, parity docs
Parity estimate: **before 96.5% -> after 100%** (`GMR-P1`..`GMR-P5` complete)

The refreshed retail-facing audit in
`docs/reverse-engineering/game-module-parity-audit-and-implementation-plan-2026-04-09.md`
now closes the combined module layer at **100%** strict retail parity for the
module register. The source-built DLL lane is green, and the remaining
live-map blocker is explicitly delegated to the renderer audit rather than left
as an open module gap.

`GMR-P1` retail DLL validation is now closed. The tracked retail probe loads
retail `uix86.dll`, `qagamex86.dll`, and `cgamex86.dll` from the Steam profile
root under the reconstructed host, and the remaining live-map shortfall is
explicitly bounded to the renderer-owned `R_LoadMD3` failure on retail
`models/weapons3/hmg/hmg.md3`.

`GMR-P2` is now closed as well. Retail qagame/cgame `pstats` transport is
mirrored end to end in writable source, with qagame accepting `pstats` and
cgame routing both `acc` and `pstats` through the recovered shared 15-slot
cache path.

`GMR-P3` is now closed too. The retail `CG_Player` path applies a post-`tag_head`
world transform driven by `g_playerheadScale` and `g_playerheadScaleOffset`,
and writable source now mirrors that origin/axis math under the same
first-person guard while the focused cgame parity suite locks the helper and
call-site placement structurally.

`GMR-P4` is now closed as well. The retained launcher/resource fallback owner
chain stays available for audited offline `ui`/`cgame` flows even when live
online services are disabled, so local `web.pak`, `fs_webpath`, screenshot,
and non-Steam URI resource loads no longer depend on the missing retail
launcher host.

`GMR-P5` is now closed too. The final module parity gate, the top-level
ledgers, the dedicated UI audit, and the native/build pipeline notes now all
agree on the same strict-retail module closure state, and the live validation
baseline has been refreshed on the current tree.

Completed work in this task:

1. Closed `GMR-P1` through `GMR-P4`, removing every active runtime and
   host-adjacent module gap from the strict-retail register.
2. Re-ran the source-built module suites, the shared platform-service seam, and
   the tracked retail runtime probe on the current tree.
3. Reconciled the module parity ledgers so the repo consistently distinguishes
   source-built DLL closure from strict retail module parity closure while now
   marking the strict-retail module layer closed as well.

## Verification expectations after gameplay/client changes

When code changes can affect startup or runtime stability:

1. Build `Debug|x86`.
2. Run a normal launch pass with logging enabled.
3. Confirm active startup markers in `build\\win32\\Debug\\bin\\baseq3\\qconsole.log`.
4. Capture both a process-bound screenshot and an engine screenshot when possible.
5. Run a forced-crash probe to confirm dump generation still works.

## Working priority order

1. Native launcher/platform host reconstruction.
2. Strict retail game-module validation and residual `cgame` exactness closure.
3. Ownerdraw/stat payload completion and runtime validation.
4. Targeted gameplay validation sweeps.
