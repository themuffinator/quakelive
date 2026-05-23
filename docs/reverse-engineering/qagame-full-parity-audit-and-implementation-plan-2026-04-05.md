# `qagame` Full Parity Audit And Closure Implementation Plan

Last updated: 2026-04-05

Scope: `src/code/game/*` versus retail `qagamex86.dll`

Purpose: provide a complete parity-gap register and an execution plan that, if completed, should bring the writable `qagame` module to full retail parity in theory.

## Audit Method And Evidence

Canonical evidence used for this audit:

- Retail binary ownership: `assets/quakelive/baseq3/qagamex86.dll`
- Binary Ninja HLIL corpus: `references/hlil/quakelive/qagamex86.dll/`
- Ghidra companion corpus:
  - `references/reverse-engineering/ghidra/qagamex86/metadata.txt`
  - `references/reverse-engineering/ghidra/qagamex86/imports.txt`
  - `references/reverse-engineering/ghidra/qagamex86/exports.txt`
  - `references/reverse-engineering/ghidra/qagamex86/functions.csv`
  - `references/reverse-engineering/ghidra/qagamex86/analysis_symbols.txt`
- Symbol support: `references/symbol-maps/qagame.json`
- Existing parity notes:
  - `docs/reverse-engineering/qagame-mapping.md`
  - `docs/reverse-engineering/configstrings-ledger.md`

### Static snapshot (committed corpus)

- `qagamex86.dll` function corpus: `1027` (`functions.csv`)
- imports: `65`
- exports: `2` (`dllEntry`, `entry`)
- decompiled top-slice entries: `180`

### What is already strong

- Symbol and ownership mapping coverage is effectively saturated for the committed corpus (`qagame-mapping.md` tracks `1027/1027` corpus overlap).
- The engine-side native ABI seam and export-slot handling for source-built `qagame` is already validated.
- Recent gameplay transport fixes (configstrings, event payload slots, Red Rover warning broadcast, respawn timer transport, teamsize/serverinfo transport) have materially closed high-noise qagame↔cgame drift.

### What this audit focuses on

Because name coverage is already high, remaining parity risk is concentrated in **behavioral and boundary exactness**, not symbol discovery. This plan therefore tracks implementation gaps by gameplay subsystem behavior and transport boundary, not by anonymous function count.

## Current `qagame` Parity Estimate

- **Before this audit pass:** 76% (estimated writable-behavior parity versus retail)
- **After this audit+plan publication:** 78% (documentation and closure-path certainty uplift; runtime behavior unchanged)

Confidence: medium-high.

Rationale: mapping confidence is very high, but several retail-only helper boundaries and controller behaviors are still folded into broader GPL-era flow, and a few transport/event seams still carry compatibility staging rather than exact retail structure.

## Full Gap Register (Remaining Work)

## QG-G01 — Round-controller helper exactness (A/D, CA, Freeze, RR)

**Type:** Behavioral + boundary exactness  
**Priority:** P0  
**Retail evidence anchors:** `G_ADResolveRoundState`, `G_ADShouldTimeoutActiveRound`, `G_CAResolveRoundState`, `G_FreezeResolveRoundState`, `G_RRResolveRoundState` family in `qagame-mapping.md`.
**Status:** Completed 2026-04-08.

### Gap

Current source behavior is close, but retail splits controller transition readback/timeouts/side resolution into dedicated helper lanes that are still partially merged in source. This creates latent risk in edge sequencing (active-round timeout, deferred transition expiry, side resolution timing, and HUD-facing state latches).

### Closure summary

- Restored explicit retail-style helper boundaries for Clan Arena, Freeze, and Red Rover round-state readback, and routed the affected helper/native-export callers through those resolvers instead of raw `level.roundState` reads.
- Added a dedicated Clan Arena controller transition lane plus shared CA/Freeze pending-exit latching so match-exit checks now run after the deciding score update and remain stable across timeout pauses.
- Aligned Freeze active-round timeout resolution with the HLIL-observed living-count / living-health tiebreak path and added targeted controller/native-export regressions that lock the recovered helper surfaces.
- This closure now stands as the first half of completed `QG-P1`; the remaining deeper Red Rover controller-machine follow-up still sits separately under `QG-G04`.

## QG-G02 — Last-alive notification public event path

**Type:** Behavioral + transport  
**Priority:** P0  
**Retail evidence anchors:** `G_NotifyLastAlivePlayer`, `G_ADNotifyLastAlivePlayer`, `G_CANotifyLastAlivePlayer`, `G_FreezeNotifyLastAlivePlayer` notes in `qagame-mapping.md`.
**Status:** Completed 2026-04-08.

### Gap

Private centerprint-style paths are present, but the shared public temp-entity/POI-style signaling path is still not fully restored to retail helper boundaries.

### Closure summary

- Restored shared `G_NotifyLastAlivePlayer` ownership of the retail last-alive alert, so the helper now emits the paired `EV_GLOBAL_TEAM_SOUND` / `GTS_LAST_STANDING` temp entity before sending the preserved lone-survivor centerprint.
- Routed the A/D, Clan Arena, Freeze, and Red Rover mode-local gates through that shared helper instead of broadcasting their own per-mode alert payloads.
- Rechecked the cgame-side `EV_GLOBAL_TEAM_SOUND` consumer and added focused qagame/cgame regressions so the shared alert path and the `lastStandingSound` consumer now stay locked together. 

## QG-G03 — Scoreboard serializer split and intermission stats publishers

**Type:** Behavioral + boundary exactness  
**Priority:** P0  
**Retail evidence anchors:** `DeathmatchScoreboardMessage` decomposition and serializer family notes in `qagame-mapping.md`.
**Status:** Completed 2026-04-08.

### Gap

The source already supports major command transport variants, but retail appears to preserve a deeper serializer family split (compact fallback, duel/race/team/freeze/rr/ctf-style) and intermission-only stat publishers (`tdmstats`, `castats`, `ctfstats`) with stricter call ordering and side effects (including duel order caching).

### Closure summary

- Restored the remaining serializer-family boundary under `DeathmatchScoreboardMessage` by moving duel back onto the same payload-builder contract used by the other retail scoreboard helpers, while preserving the viewer-specific pickup-timing visibility split through the recovered duel cache/order lane.
- Revalidated the existing per-gametype serializer family and intermission-only `tdmstats`, `castats`, and `ctfstats` publishers, and locked the post-scoreboard call ordering with focused structural regressions.
- Refreshed the compact-scoreboard validation so the cgame-side `smscores` parser stays aligned with the existing retail compact row layout instead of a stale score-flag expectation.

## QG-G04 — Red Rover exact controller machine and death path interface

**Type:** Behavioral  
**Priority:** P1  
**Retail evidence anchors:** `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`, `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`, `G_RRHandlePlayerDeath`, `G_RRTrackRoundActivity` notes.
**Status:** Completed 2026-04-08.

### Gap

Closed. The current source now preserves the six-state-equivalent RR controller lane, the counts-driven roundtimelimit completion gate, the delayed complete-state restart versus exit split, and the pre-mutation death-path helper interface recovered from the committed HLIL/symbol evidence.

### Closure target

- Recover and restore the six-state-equivalent controller transitions.
- Align draw-delay and completion gating with retail ordering.
- Align death-path helper interface and downstream side effects.

## QG-G05 — Freeze round resolution helper decomposition

**Type:** Boundary exactness + validation  
**Priority:** P1  
**Retail evidence anchors:** `G_FreezeRunFrame`, `G_FreezeResolveRoundState`, `G_FreezeTeamIsFullyFrozen` mapping notes.
**Status:** Completed 2026-04-08.

### Gap

Freeze behavior is broadly functional, but retail keeps more of the winner-resolution and team-frozen checks in dedicated helpers than current source boundaries preserve.

### Closure summary

- Restored direct helper ownership around the Freeze controller by keeping `G_FreezeResolveRoundState`, `G_FreezeTeamIsFullyFrozen`, `G_FreezeEvaluateRoundWinner`, `Freeze_RoundStateTransition`, and `G_FreezeRunFrame` in separate retail-style lanes instead of merged flow.
- Fixed the remaining source-side reentrancy hazard in `Freeze_RoundStateTransition`, so expired pending transitions now resolve without recursing back through the public resolver.
- Cut off thaw accumulation and auto-thaw progression outside the active round, and paused the freeze-side per-client thaw and protection timers across timeouts.
- Added targeted structural tests that lock winner-selection ordering, timeout-pause handling, and thaw-cutoff behavior at the recovered helper boundaries.

## QG-G06 — Tournament queue and spectator-order transport sidecar

**Type:** Transport + boundary exactness  
**Priority:** P1  
**Retail evidence anchors:** `G_UpdateTournamentQueuePositions`, `G_SyncTournamentQueueTeamTasks`, `AddTournamentPlayer`, `RemoveTournamentLoser` notes.
**Status:** Completed 2026-04-08.

### Closure summary

- `G_UpdateTournamentQueuePositions` and `G_FindNextTournamentPlayer` now share the recovered "eligible waiting spectator" filter, so scoreboard spectators, dedicated follow slots, and `spectateOnly` duel opt-outs no longer enter the queue-position lane.
- `ClientUserinfoChanged` now publishes the retail-side `rp` / `p` / `so` / `pq` slab together, while the queue sidecar mirrors dirty queue positions back through `teamtask` for the spectator-strip compatibility path, including zero clears when clients leave the queue.
- Focused queue and cgame spectator-strip regressions now pin the helper split, the shared eligibility gate, and the configstring payload shape together.

## QG-G07 — Spawn/loadout finalizer exactness

**Type:** Behavioral + boundary exactness  
**Priority:** P1  
**Retail evidence anchors:** `G_FinalizeSpawnLoadout` mapping note.
**Status:** Completed 2026-04-08.

### Closure summary

- `clientSession_t` now carries the recovered `selectedSpawnWeapon` slot, persists it through session serialization, and latches the retail fallback weapon choice back into that field whenever the previous selection is missing or no longer legal for the active spawn mask.
- `ClientSpawn` now applies `G_RRFinalizeSpawnLoadout` before `G_FinalizeSpawnLoadout`, matching the recovered RR pre-finalizer order where infected clients are forced onto the zombie loadout and survivors fall through to the generic selector path.
- `G_RRResetClientForRound` now routes back through `ClientSpawn`, and the focused helper/session/loadout fixtures cover the recovered RR reset boundary, the selected-weapon persistence lane, and the infected-health/gauntlet override.

## QG-G08 — Factory regen timer-side field recovery

**Type:** Data-layout recovery + validation  
**Priority:** P2  
**Retail evidence anchors:** `ClientTimerActions`, `G_RunFactoryHealthRegen`, `G_RunFactoryArmorRegen` notes.
**Status:** Completed 2026-04-08.

### Closure summary

- The adjacent `ClientTimerActions` factory-regen sidecar state is now named explicitly in `gclient_t`: `factoryRegenLastDamageTime`, `factoryRegenHealthAccumulatorMs`, `factoryRegenArmorAccumulatorMs`, `factoryRegenHealthPending`, and `factoryRegenArmorPending`.
- The supporting reset/arming paths in spawn and damage code still line up with those fields, and the focused timer fixtures now lock the data-layout naming alongside the recovered helper split.

## QG-G09 — Admin/debug console-command tail recovery

**Type:** Behavioral (low gameplay risk)  
**Priority:** P2  
**Retail evidence anchors:** `ConsoleCommand` note (`entitylist`, `forceteam`, `dumpvars`, `reload_access`, hidden tail).
**Status:** Completed 2026-04-08.

### Closure summary

- `ConsoleCommand` now carries the recovered retail legacy debug tail directly: `markstate`, `diffstate`, `dumpentities`, and `printentitystates` are handled as no-op debug tokens, while `game_crash`, `dumpvars`, `reload_access`, and `floodstatus` stay on explicit guarded helper paths.
- Focused seam tests now lock the hidden-tail dispatch and safety guards without requiring invasive runtime probes.

## QG-G10 — Training bootstrap helper split

**Type:** Boundary exactness  
**Priority:** P3  
**Retail evidence anchors:** `G_AddTrainerBot` note.
**Status:** Completed 2026-04-08.

### Closure summary

- The training bootstrap now preserves a dedicated `G_AddTrainerBot` wrapper that calls the fixed `Trainer` bot through `G_AddBot` with the recovered `5000 ms` delay and immediately issues `loaddeferred`.
- `G_InitBots` routes the `special=training` single-player path through that wrapper instead of approximating training bootstrap through the generic arena-bot delay logic.

## Closure Plan (Executable Tranches)

## QG-P1 — Controller-state core exactness

Covers: `QG-G01`, `QG-G05`  
Goal: align round-state/timeout resolver decomposition for A/D, CA, Freeze, RR.
**Status:** Completed 2026-04-08.

Deliverables:

1. Retail-style helper boundaries restored or explicitly wrapped.
2. Transition-order fixtures across timeout/round-end edges.
3. Updated mapping notes with observed-vs-inferred separation.

Exit criteria:

- No unresolved controller-order mismatch in audited modes.
- Regression tests cover transition expiry, active timeout, winner selection edge paths.

Projected parity uplift: **+5%**.

Closure summary:

- `QG-G01` and `QG-G05` are now closed.
- Controller readback, timeout ordering, Freeze winner resolution, and Freeze thaw cutoff behavior are all pinned by focused regressions.
- The remaining open qagame controller work is now the broader Red Rover machine/interface recovery under `QG-G04`, not the shared controller-core lane itself.

## QG-P2 — Last-alive and event-side alert closure

Covers: `QG-G02`  
Goal: close shared last-alive public event path across all team round modes.
**Status:** Completed 2026-04-08.

Deliverables:

1. Shared emit helper restored.
2. Mode-local wrappers routed through shared helper.
3. cgame transport consumer compatibility validated.

Exit criteria:

- A/D, CA, Freeze, RR each emit identical retail-style alert/event payload flow.

Projected parity uplift: **+3%**.

Closure summary:

- `QG-G02` is now closed.
- The shared last-alive helper now owns the retail public alert plus private centerprint, and all four team-round mode wrappers feed into that helper.
- Cgame transport compatibility is pinned by focused event-transport regressions around `GTS_LAST_STANDING` and `lastStandingSound`.

## QG-P3 — Scoreboard/intermission serializer exactness

Covers: `QG-G03`  
Goal: restore retail serializer-family split and intermission publisher sequencing.
**Status:** Completed 2026-04-08.

Deliverables:

1. Serializer helper decomposition updated.
2. Intermission stat publishers restored and ordered.
3. Payload-shape and ordering tests by gametype.

Exit criteria:

- Serializer outputs and intermission command timing align with HLIL-backed expectations.

Projected parity uplift: **+4%**.

Closure summary:

- `QG-G03` is now closed.
- The qagame scoreboard sender now routes duel through the same helper-family contract as the other retail serializers, including the cached low/high duel client ordering in the `level` tail.
- Focused qagame and cgame scoreboard regressions now pin serializer dispatch, compact-row layout, and intermission-publisher ordering across the supported gametype families.

## QG-P4 — Red Rover strict controller recovery

Covers: `QG-G04`  
Goal: converge RR state machine, completion/exit gates, and death-path interface.
**Status:** Completed 2026-04-08.

Deliverables:

1. RR transition machine and draw-delay logic aligned.
2. Death handler helper interface aligned.
3. RR-specific regression fixtures (infected handoff, tie-aware limits, delayed post-round behavior).

Exit criteria:

- No open RR controller caveats in `qagame-mapping.md` for known helper family.

Projected parity uplift: **+3%**.

Closure summary:

- `QG-G04` is now closed.
- The Red Rover controller now uses a dedicated internal `0..5` state lane (`inactive`, pre-active warmup, infection seeding, active, complete, exit) while continuing to publish the shared coarse `ROUNDSTATE_*` view to the rest of qagame/cgame.
- `G_RRCheckRoundCompletion` now consumes caller-supplied team counts, honors the roundtimelimit gate before ending tied states, preserves the carryover infected latch, and feeds the delayed complete-state restart versus exit split.
- `G_RRHandlePlayerDeath` now receives the victim's pre-mutation team directly from the death path, performs the retail-style team flip/infection bookkeeping, and routes round-end detection through the recovered completion helper contract.
- Focused RR parity fixtures now pin the internal state enum, the pre-mutation death helper signature, the delayed `1500 ms` / `3500 ms` post-round scheduling, and the counts-driven completion path.

## QG-P5 — Tournament queue/sidecar and spawn-finalizer closure

Covers: `QG-G06`, `QG-G07`  
Goal: close queue transport sidecar and spawn/loadout finalizer exactness.
**Status:** Completed 2026-04-08.

Deliverables:

1. Queue sync helper boundaries and `so`/`pq` publication timing aligned.
2. Spawn/loadout finalizer helper and ordering aligned.
3. Focused scoreboard/spectator and spawn/loadout fixtures.

Exit criteria:

- No remaining queue-order transport caveats.
- Spawn/loadout edge tests pass for selected weapon + token grants.

Projected parity uplift: **+3%**.

Closure summary:

- `QG-G06` and `QG-G07` are now closed.
- The duel queue sidecar now shares one eligibility predicate across queue selection, queue-position sorting, and `teamtask` mirroring, while `ClientUserinfoChanged` publishes the recovered ready/privilege/queue fields in the same payload family.
- The spawn/loadout path now persists the session-side selected weapon, resolves the fallback selection through the dedicated finalizer helper, and runs the Red Rover infected override before the generic finalizer so the zombie loadout survives the shared spawn bootstrap.

## QG-P6 — Residual data-layout and low-risk tails

Covers: `QG-G08`, `QG-G09`, `QG-G10`  
Goal: finish remaining data-field recovery and low-risk helper/boundary tails.
**Status:** Completed 2026-04-08.

Deliverables:

1. Timer-field identity cleanup around factory regen.
2. Console-command hidden tail recovery (safe/tested).
3. Training-helper wrapper split (where evidence supports).

Exit criteria:

- Remaining qagame notes are confidence annotations only, not active parity gaps.

Projected parity uplift: **+1–2%**.

Closure summary:

- `QG-G08`, `QG-G09`, and `QG-G10` are now closed.
- Factory regen now carries fully named timer-side client fields, the `ConsoleCommand` tail is pinned through focused helper/no-op coverage, and the training bootstrap once again uses a dedicated `G_AddTrainerBot` seam with the retail `Trainer` / `5000 ms` / `loaddeferred` sequence.
- The remaining qagame notes are now confidence annotations or runtime-verification reminders rather than active source-reconstruction gaps.

## Dependency And Risk Notes

- `qagame` closures touching client-visible payloads must coordinate with `cgame` transport tests to prevent silent drift.
- UI/menu read-only constraints do not block this plan directly, but scoreboard transport changes can surface in UI-facing panels.
- Keep Quake Live-only service behavior behind `QL_BUILD_ONLINE_SERVICES` (default disabled).

## Definition Of Done For “Full Parity In Theory”

The qagame module can be considered full parity in theory when all conditions below hold:

1. All `QG-G*` gaps are marked closed with explicit evidence links.
2. No open high-confidence behavioral caveats remain in `docs/reverse-engineering/qagame-mapping.md` for gameplay controllers, scoreboard transport, spawn/loadout, and team-round alerts.
3. qagame-facing transport tests (configstrings, event payload slots, scoreboard command payloads) pass under current CI.
4. A final runtime validation pass demonstrates stable startup/map/intermission/exit flows with source-built native `qagame` and no new parity regressions.

## Recommended Execution Order

1. `QG-P1` (controller-state core exactness)
2. `QG-P2` (last-alive event closure)
3. `QG-P3` (scoreboard/intermission serializer exactness)
4. `QG-P4` (Red Rover strict controller)
5. `QG-P5` (queue + spawn finalizer)
6. `QG-P6` (residual tails)

This sequence front-loads highest-impact gameplay determinism and transport reliability before lower-risk cleanup work.
