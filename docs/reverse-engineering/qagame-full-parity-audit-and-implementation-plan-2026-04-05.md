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

### Gap

Current source behavior is close, but retail splits controller transition readback/timeouts/side resolution into dedicated helper lanes that are still partially merged in source. This creates latent risk in edge sequencing (active-round timeout, deferred transition expiry, side resolution timing, and HUD-facing state latches).

### Closure target

- Restore explicit retail-style helper boundaries for each mode's state resolver and timeout predicates.
- Align transition ordering and latch readback timing with HLIL-observed call flow.
- Add targeted tests that lock transition-order invariants and timeout edge cases.

## QG-G02 — Last-alive notification public event path

**Type:** Behavioral + transport  
**Priority:** P0  
**Retail evidence anchors:** `G_NotifyLastAlivePlayer`, `G_ADNotifyLastAlivePlayer`, `G_CANotifyLastAlivePlayer`, `G_FreezeNotifyLastAlivePlayer` notes in `qagame-mapping.md`.

### Gap

Private centerprint-style paths are present, but the shared public temp-entity/POI-style signaling path is still not fully restored to retail helper boundaries.

### Closure target

- Reconstruct shared `G_NotifyLastAlivePlayer`-equivalent emit path.
- Route A/D, CA, Freeze, and RR last-alive triggers through shared + mode-local helpers exactly as retail separates them.
- Verify cgame consumers still receive identical payloads across all round modes.

## QG-G03 — Scoreboard serializer split and intermission stats publishers

**Type:** Behavioral + boundary exactness  
**Priority:** P0  
**Retail evidence anchors:** `DeathmatchScoreboardMessage` decomposition and serializer family notes in `qagame-mapping.md`.

### Gap

The source already supports major command transport variants, but retail appears to preserve a deeper serializer family split (compact fallback, duel/race/team/freeze/rr/ctf-style) and intermission-only stat publishers (`tdmstats`, `castats`, `ctfstats`) with stricter call ordering and side effects (including duel order caching).

### Closure target

- Rebuild serializer helper decomposition to match retail boundaries.
- Validate payload field order and per-gametype inclusion rules against HLIL.
- Lock intermission-only stat publish points and ordering with targeted tests.

## QG-G04 — Red Rover exact controller machine and death path interface

**Type:** Behavioral  
**Priority:** P1  
**Retail evidence anchors:** `G_RRCheckRoundCompletion`, `G_RRCheckExitRules`, `G_RRResolveAutoJoinTeam`, `G_RRSeedInfectionTeams`, `G_RRHandlePlayerDeath`, `G_RRTrackRoundActivity` notes.

### Gap

Major RR behavior is present, but retail still appears to carry a stricter multi-state controller with exact draw-delay/connected-count gates and a fuller death-path argument contract.

### Closure target

- Recover and restore the six-state-equivalent controller transitions.
- Align draw-delay and completion gating with retail ordering.
- Align death-path helper interface and downstream side effects.

## QG-G05 — Freeze round resolution helper decomposition

**Type:** Boundary exactness + validation  
**Priority:** P1  
**Retail evidence anchors:** `G_FreezeRunFrame`, `G_FreezeResolveRoundState`, `G_FreezeTeamIsFullyFrozen` mapping notes.

### Gap

Freeze behavior is broadly functional, but retail keeps more of the winner-resolution and team-frozen checks in dedicated helpers than current source boundaries preserve.

### Closure target

- Restore direct helper ownership where behavior is currently merged.
- Validate no behavior drift at winner/tie transitions and thaw cutoff edges.

## QG-G06 — Tournament queue and spectator-order transport sidecar

**Type:** Transport + boundary exactness  
**Priority:** P1  
**Retail evidence anchors:** `G_UpdateTournamentQueuePositions`, `G_SyncTournamentQueueTeamTasks`, `AddTournamentPlayer`, `RemoveTournamentLoser` notes.

### Gap

Retail serializes additional duel queue fields (`so`, `pq`) and mirrors queue ordering back through compatibility channels more explicitly than current GPL-derived queue flow.

### Closure target

- Restore helper boundaries for queue-position syncing.
- Preserve retail field publication/update timing.
- Verify cgame spectator-strip expectations stay aligned.

## QG-G07 — Spawn/loadout finalizer exactness

**Type:** Behavioral + boundary exactness  
**Priority:** P1  
**Retail evidence anchors:** `G_FinalizeSpawnLoadout` mapping note.

### Gap

Source includes equivalent behavior pieces, but retail appears to centralize spawn weapon selection, token parsing, ammo/weapon-mask seeding, and post-spawn cleanup in a tighter finalizer chain.

### Closure target

- Reconstruct explicit finalize helper boundary.
- Align selected weapon and token parser sequencing.
- Add fixtures for factory/loadout edge combinations.

## QG-G08 — Factory regen timer-side field recovery

**Type:** Data-layout recovery + validation  
**Priority:** P2  
**Retail evidence anchors:** `ClientTimerActions`, `G_RunFactoryHealthRegen`, `G_RunFactoryArmorRegen` notes.

### Gap

High-level regen behavior is recovered, but adjacent timer accumulators/latches still include partially unidentified client-state fields.

### Closure target

- Resolve adjacent timer field identities (notably around currently tracked `gclient` offsets near `+0x500/+0x50C` references).
- Remove residual descriptive placeholders once confidence is high.
- Lock with deterministic timer fixtures.

## QG-G09 — Admin/debug console-command tail recovery

**Type:** Behavioral (low gameplay risk)  
**Priority:** P2  
**Retail evidence anchors:** `ConsoleCommand` note (`entitylist`, `forceteam`, `dumpvars`, `reload_access`, hidden tail).

### Gap

Main console-command routes are known, but hidden debug/admin tail handling remains partially unresolved.

### Closure target

- Recover remaining retail command fallthrough logic.
- Keep dangerous commands behind existing safety guardrails.
- Add non-invasive command-dispatch tests.

## QG-G10 — Training bootstrap helper split

**Type:** Boundary exactness  
**Priority:** P3  
**Retail evidence anchors:** `G_AddTrainerBot` note.

### Gap

Training-map bootstrap exists functionally in broader init flow; retail keeps a dedicated helper wrapper.

### Closure target

- Reintroduce dedicated training helper boundary where evidence is clear.
- Preserve existing behavior while matching call-shape and sequencing.

## Closure Plan (Executable Tranches)

## QG-P1 — Controller-state core exactness

Covers: `QG-G01`, `QG-G05`  
Goal: align round-state/timeout resolver decomposition for A/D, CA, Freeze, RR.

Deliverables:

1. Retail-style helper boundaries restored or explicitly wrapped.
2. Transition-order fixtures across timeout/round-end edges.
3. Updated mapping notes with observed-vs-inferred separation.

Exit criteria:

- No unresolved controller-order mismatch in audited modes.
- Regression tests cover transition expiry, active timeout, winner selection edge paths.

Projected parity uplift: **+5%**.

## QG-P2 — Last-alive and event-side alert closure

Covers: `QG-G02`  
Goal: close shared last-alive public event path across all team round modes.

Deliverables:

1. Shared emit helper restored.
2. Mode-local wrappers routed through shared helper.
3. cgame transport consumer compatibility validated.

Exit criteria:

- A/D, CA, Freeze, RR each emit identical retail-style alert/event payload flow.

Projected parity uplift: **+3%**.

## QG-P3 — Scoreboard/intermission serializer exactness

Covers: `QG-G03`  
Goal: restore retail serializer-family split and intermission publisher sequencing.

Deliverables:

1. Serializer helper decomposition updated.
2. Intermission stat publishers restored and ordered.
3. Payload-shape and ordering tests by gametype.

Exit criteria:

- Serializer outputs and intermission command timing align with HLIL-backed expectations.

Projected parity uplift: **+4%**.

## QG-P4 — Red Rover strict controller recovery

Covers: `QG-G04`  
Goal: converge RR state machine, completion/exit gates, and death-path interface.

Deliverables:

1. RR transition machine and draw-delay logic aligned.
2. Death handler helper interface aligned.
3. RR-specific regression fixtures (infected handoff, tie-aware limits, delayed post-round behavior).

Exit criteria:

- No open RR controller caveats in `qagame-mapping.md` for known helper family.

Projected parity uplift: **+3%**.

## QG-P5 — Tournament queue/sidecar and spawn-finalizer closure

Covers: `QG-G06`, `QG-G07`  
Goal: close queue transport sidecar and spawn/loadout finalizer exactness.

Deliverables:

1. Queue sync helper boundaries and `so`/`pq` publication timing aligned.
2. Spawn/loadout finalizer helper and ordering aligned.
3. Focused scoreboard/spectator and spawn/loadout fixtures.

Exit criteria:

- No remaining queue-order transport caveats.
- Spawn/loadout edge tests pass for selected weapon + token grants.

Projected parity uplift: **+3%**.

## QG-P6 — Residual data-layout and low-risk tails

Covers: `QG-G08`, `QG-G09`, `QG-G10`  
Goal: finish remaining data-field recovery and low-risk helper/boundary tails.

Deliverables:

1. Timer-field identity cleanup around factory regen.
2. Console-command hidden tail recovery (safe/tested).
3. Training-helper wrapper split (where evidence supports).

Exit criteria:

- Remaining qagame notes are confidence annotations only, not active parity gaps.

Projected parity uplift: **+1–2%**.

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
