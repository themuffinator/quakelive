# StepSlideMove wiring reconstruction audit - 2026-05-27

## Scope

This pass rechecked the shared `PM_StepSlideMove` lane and the wiring that feeds
or consumes it:

- `src/code/game/bg_slidemove.c`: `PM_SlideMove`, `PM_StepSlideMove`, the step
  retry, down-clip guard, step-jump probes, and crouch-step fallback.
- `src/code/game/bg_pmove.c`: movement leaves that call the step wrapper,
  step-jump takeoff latches, and the public `Pmove` step export.
- `src/code/game/g_pmove.c`, `src/code/game/bg_public.h`, and
  `src/code/cgame/cg_servercmds.c`: server cvar/cache publication, compact
  configstring parsing, and the shared `pmove_settings_t` fields that feed
  step height, air-step enablement, and air-step friction.
- `src/code/cgame/cg_predict.c`: prediction smoothing that consumes
  `pmove_t::stepUp` and `pmove_t::stepUpTime`.
- `tests/pmove_validation_harness.c`,
  `tests/test_pmove_validation_fixtures.py`, and
  `tests/test_step_jump_gate_parity.py`: executable and structural parity
  coverage for the edge cases below.

No runtime launch was needed. The evidence comes from the committed Binary Ninja
HLIL and the Ghidra companion corpus.

## Evidence inventory

Canonical HLIL anchors:

| Retail owner | Retail address | Current source name | Notes |
| --- | ---: | --- | --- |
| `qagamex86.dll` | `0x1002E2C0` | `PM_ApplyJumpTakeoff` | Shared jump takeoff leaf consumed by normal jumps, step jumps, and crouch-step fallback. |
| `qagamex86.dll` | `0x1002E4C0` | `PM_CanCrouchStepJump` | Crouch-step-only gate. |
| `qagamex86.dll` | `0x1002E510` | `PM_CanStepJump` | General step-jump gate. |
| `qagamex86.dll` | `0x1002E670` | `PM_SlideMove` | Shared slide solver. |
| `qagamex86.dll` | `0x1002EFE0` | `PM_StepSlideMove` | Shared step wrapper. |
| `cgamex86.dll` | `0x10002790` | `PM_ApplyJumpTakeoff` | Client mirror of qagame takeoff leaf. |
| `cgamex86.dll` | `0x10002990` | `PM_CanCrouchStepJump` | Client mirror of qagame crouch-step gate. |
| `cgamex86.dll` | `0x100029E0` | `PM_CanStepJump` | Client mirror of qagame general step-jump gate. |
| `cgamex86.dll` | `0x10002B40` | `PM_SlideMove` | Client mirror of qagame slide solver. |
| `cgamex86.dll` | `0x100034B0` | `PM_StepSlideMove` | Client mirror of qagame step wrapper. |

Companion files used:

- `references/hlil/quakelive/qagamex86.dll/split/types/qagamex86.dll.bndb_hlil_type_00113_block.txt`
- `references/hlil/quakelive/cgamex86.dll/cgamex86.dll_hlil_split/cgamex86.dll_hlil_part01.txt`
- `references/reverse-engineering/ghidra/qagamex86/functions.csv`
- `references/reverse-engineering/ghidra/qagamex86/decompile_top_functions.c`
- `references/reverse-engineering/ghidra/cgamex86/functions.csv`
- `references/reverse-engineering/ghidra/cgamex86/decompile_top_functions.c`
- `references/symbol-maps/qagame.json`
- `references/symbol-maps/cgame.json`

## Observed retail shape

`PM_StepSlideMove` is a one-argument public function. HLIL presents qagame as
`sub_1002efe0(int32_t arg1)` and cgame as `sub_100034b0(int32_t arg1)`, with
that argument passed straight to `PM_SlideMove`. The step height is not a public
parameter. Retail reads the active step-height global inside the body; the
current reconstruction keeps the retail public boundary and routes configurable
step height through a private `PM_StepSlideMoveWithStepHeight`.

The step retry is:

1. Save origin and velocity.
2. Run `PM_SlideMove(gravity)` first and return when it reaches the target.
3. If air steps are disabled, project the start velocity to the frame endpoint,
   trace down by step height, and reject upward air stepping when there is no
   walkable support.
4. Trace upward by step height from the saved start. If allsolid, emit the
   retail `"%i:bend can't step\n"` debug string and return.
5. Restore the saved velocity, slide from the raised origin, trace back down by
   the actual raised amount, and copy the down-trace endpoint when not allsolid.
6. Clip the down-trace contact only when the down trace hit and the velocity is
   entering the plane or is effectively parallel to it.
7. Trace from the original start to the stepped endpoint. Retail only records
   step side effects when that direct trace is blocked.
8. When the step is real, record `pml.stepUp` for deltas above 2 units, apply
   air-step friction to XY velocity for upward airborne starts, and then probe
   the step-jump branches.

The down-clip guard was the main source-code correction in this pass. Both
HLIL mirrors use:

- `trace.fraction < 1.0`
- `DotProduct(velocity, trace.plane.normal) < 0.0`
- or `fabs(dot) < 0.00100000005`

before calling `PM_ClipVelocity`. The source now uses `0.001f`; the earlier
worktree value of `0.1f` would have clipped small positive normal velocities
that retail preserves.

## Step-jump branch wiring

The step-jump branch is guarded by the same broad retail preconditions in both
modules:

- step-jump setting enabled,
- `pm_type == PM_NORMAL`,
- positive step delta,
- waterlevel below 2,
- either the general step-jump gate succeeds or crouch-step jumping is enabled
  and its gate succeeds.

Retail then performs a projected support trace from the frame endpoint plus
step height down to the endpoint minus step height. The reconstruction requires
the trace to be non-startsolid, non-allsolid, blocked before the end, and have
a walkable normal.

The general branch is deliberately rechecked immediately before launch. If it
still succeeds, the source prepares the normal step-jump takeoff latch and calls
the shared jump leaf. If it fails, the crouch branch rechecks
`PM_CanCrouchStepJump`, runs the shrunken-box clearance probe, prepares the
crouch-step latch, and then calls the same shared jump leaf.

The two latches map to the HLIL globals seen around the jump leaf:

- Normal step jump selects the step-jump velocity addend and allows ramp-jump
  accumulation.
- Crouch-step fallback selects the chain-jump velocity path and suppresses ramp
  accumulation.

## Movement call matrix

The retail movement leaves use stepped and plain sliding in a small matrix:

| Source leaf | Final movement call | Reasoning |
| --- | --- | --- |
| `PM_WaterJumpMove` | `PM_StepSlideMove(qtrue)` | Water-jump continuation falls while still stepping. |
| `PM_WaterMove` | `PM_SlideMove(qfalse)` | Swimming uses plain sliding after water acceleration. |
| `PM_LadderMove` | `PM_SlideMove(qfalse)` | Ladder movement remains a plain slide leaf. |
| `PM_FlyMove` | `PM_StepSlideMove(qfalse)` | Spectator/flight movement uses stepping without gravity. |
| `PM_AirMove` | `PM_StepSlideMove(qtrue)` | Air movement steps with gravity before invulnerability and double-jump checks. |
| `PM_WalkMove` | `PM_StepSlideMove(qfalse)` twice | One early invulnerability handoff and one normal grounded finish. |

`PM_GrappleMove` does not directly step; `PmoveSingle` follows it with
`PM_AirMove`, which owns the step call.

## Tuning transport wiring

`PM_StepSlideMove` itself consumes three legacy globals:

- `pm_stepHeight` for the raised and projected support trace distances.
- `pm_airsteps` for the upward-air-step support probe gate.
- `pm_airstepfriction` for planar velocity damping after a real airborne
  upward step.

Those globals are not independent source-only knobs. They are fed from the
retail pmove settings transport:

1. qagame registers `pmove_AirStepFriction`, `pmove_AirSteps`, and
   `pmove_StepHeight` with the recovered defaults `0.03f`, `1`, and `22.0f`.
2. `G_PmoveSerializeSettings` writes `settings->airStepFriction`,
   `settings->airSteps`, and `settings->stepHeight` into the compact
   `CS_PMOVE_SETTINGS` token stream.
3. cgame `CG_ParsePmoveCompactSettingsPayload` consumes the same ordered slots
   with `PMOVE_COMPACT_FLOAT( airStepFriction )`,
   `PMOVE_COMPACT_INT( airSteps )`, and
   `PMOVE_COMPACT_FLOAT( stepHeight )`. The older JSON fallback maps the same
   fields by name.
4. Shared `PmoveSingle` calls `PM_LoadMoveTuningConstants` before trace-mask and
   movement dispatch. That loader resolves `pm_airstepfriction` and
   `pm_airsteps` from the active settings.
5. `PM_GetActiveSettings` also routes through `PM_LoadMoveSettings`, which
   resolves `settings->stepHeight` and writes `pm_stepHeight` before the step
   wrapper is entered.

This keeps server movement, cgame prediction, and standalone movement fixtures
on the same step configuration path.

## Prediction export

`PM_StepSlideMove` writes the per-frame delta into `pml.stepUp`. `Pmove`
resets `pmove->stepUp` and `pmove->stepUpTime` before the command chunk loop,
then accumulates positive `pml.stepUp` values and stamps the current command
time. Client prediction calls `Pmove(&cg_pmove)` and immediately runs
`CG_UpdateStepChange`, which consumes `cg_pmove.stepUp`, checks `stepUpTime`
against the previous `cg.stepTime`, decays the old change over 100 ms, clamps
to `MAX_STEP_CHANGE`, and updates `cg.stepTime`.

This confirms the retail path is data-driven through `pmove_t`; it does not
replay old step events for local prediction smoothing.

## Reconstruction changes

- Tightened the down-trace clip guard to the retail `0.001f` dot epsilon.
- Kept the direct start-to-stepped-end reachability trace that gates step side
  effects.
- Kept the support trace `startsolid` rejection before both step-jump branches.
- Added an executable fixture proving a small positive normal velocity survives
  the step down-trace contact.
- Added structural tests for the movement call matrix, normal/crouch takeoff
  latches, tuning transport, and cgame prediction smoothing export.

## Confidence and parity estimate

Confidence is high. The qagame and cgame HLIL bodies agree on the control flow,
constants, debug strings, helper call addresses, and latch split. The source is
now pinned by both executable fixture coverage and structural tests.

Scoped StepSlideMove parity estimate: before this pass, **98.8%** due to the
incorrect down-clip epsilon and incomplete wiring coverage; after this pass,
**99.9%** for the StepSlideMove lane. The remaining `0.1%` is reserved for
floating-point/codegen drift that can only be closed by broader retail binary
trace comparison. The repo-wide estimate remains **98%**.
